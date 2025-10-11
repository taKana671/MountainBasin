import math
import sys
from typing import NamedTuple

from panda3d.bullet import BulletWorld, BulletDebugNode, BulletSphereShape
from panda3d.core import Vec3, Vec2, Vec4, Point3, Quat, Camera
from panda3d.core import NodePath, TransformState
from panda3d.core import load_prc_file_data
from panda3d.core import AntialiasAttrib
from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from direct.showbase.InputStateGlobal import inputState

from scene import Scene, Model
from characters.walker import Walker


load_prc_file_data("", """
    textures-power-2 none
    gl-coordinate-system default
    window-title Panda3D Mountain Basin
    filled-wireframe-apply-shader true
    stm-max-views 8
    stm-max-chunk-count 2048""")


class Adjust(NamedTuple):

    direction: int
    axis_pt: Vec3


class CustomCamera:

    def __init__(self, tracking_target, pos, look_at, display_region=None):
        self.display_region = Vec4(0, 1, 0, 1) if display_region is None else display_region
        self.target = tracking_target
        self.look_at = look_at
        self.setup_camera(pos)
        base.accept('aspectRatioChanged', self.calc_aspect_ratio)

    def calc_aspect_ratio(self):
        props = base.win.get_properties()
        window_size = props.get_size()

        region_w = self.display_region.y - self.display_region.x
        region_h = self.display_region.w - self.display_region.z
        display_w = int(window_size.x * region_w)
        display_h = int(window_size.y * region_h)

        gcd = math.gcd(display_w, display_h)
        w = display_w / gcd
        h = display_h / gcd
        aspect_ratio = w / h

        self.camera.node().get_lens().set_aspect_ratio(aspect_ratio)


class TrackingCamera(CustomCamera):

    def __init__(self, tracking_target, pos, look_at, display_region=None):
        super().__init__(tracking_target, pos, look_at, display_region)
        self.sweep_shape = BulletSphereShape(0.5)
        self.adjust = None

    def setup_camera(self, pos):
        display_region = base.win.make_display_region(self.display_region)
        self.camera = NodePath(Camera('tracking_camera'))
        self.camera.node().get_lens().set_fov(90)
        self.camera.node().get_lens().set_near(0.1)
        display_region.set_camera(self.camera)

        self.camera.reparent_to(base.render)
        self.camera.set_pos(pos)
        self.camera.look_at(self.look_at)

    def calc_distance(self, vec):
        vec.set_z(0)
        dist = vec.length()
        vec.normalize()
        return dist

    def track(self, dt):
        camera_pos = self.camera.get_pos()
        target_pos = self.target.get_pos()

        if self.adjust:
            next_pos = self.get_circular_motion_pos(
                camera_pos, self.adjust.direction * 100 * dt, self.adjust.axis_pt)

            if not self.shoot_a_ray(next_pos, target_pos, Model.TUNNEL.mask):
                self.adjust = None

            self.camera.set_pos(next_pos)
        else:
            next_pos = None
            vec = target_pos - camera_pos
            dist = self.calc_distance(vec)

            if dist > 5.0:
                next_pos = camera_pos + vec * (dist - 5.0)

            if dist < 3.0:
                next_pos = camera_pos - vec * (3.0 - dist)

            # To prevent the camera from going through the tunnel 3D models, adjust the next position.
            if next_pos:
                if result := self.predict_collision(camera_pos, next_pos, Model.TUNNEL.mask):
                    normal = result.get_hit_normal()
                    correction_dist = self.calc_distance(normal)

                    if dist > 5.0:
                        next_pos = next_pos + normal * correction_dist

                    if dist < 3.0:
                        next_pos = next_pos - normal * correction_dist

                if result := self.shoot_a_ray(next_pos, target_pos, Model.TUNNEL.mask):
                    axis_pt = result.get_hit_pos()
                    direction = self.find_moving_direction(camera_pos, target_pos, axis_pt)
                    next_pos = self.get_circular_motion_pos(camera_pos, direction * 100 * dt, axis_pt)
                    self.adjust = Adjust(direction, axis_pt)

                self.camera.set_pos(next_pos)

        self.camera.look_at(self.look_at)

    def shoot_a_ray(self, from_pos, to_pos, mask):
        if (result := base.world.ray_test_closest(from_pos, to_pos, mask)).has_hit():
            return result

    def get_circular_motion_pos(self, current_pos, angle, axis_pt):
        q = Quat()
        q.set_from_axis_angle(angle, Vec3.up())
        r = q.xform(current_pos - axis_pt)
        next_pos = axis_pt + r
        return next_pos

    def find_moving_direction(self, camera_pos, walker_pos, axis_pt):
        for i in range(36):
            for direction in [-1, 1]:
                angle = 10 * (i + 1) * direction
                next_pos = self.get_circular_motion_pos(camera_pos, angle, axis_pt)

                if not self.shoot_a_ray(next_pos, walker_pos, Model.TUNNEL.mask):
                    return direction

    def predict_collision(self, from_pos, to_pos, mask):
        from_ts = TransformState.make_pos(from_pos)
        to_ts = TransformState.make_pos(to_pos)

        if (result := base.world.sweep_test_closest(
                self.sweep_shape, from_ts, to_ts, mask, 0.0)).has_hit():
            return result


class TerrainCamera(CustomCamera):

    def __init__(self, tracking_target, pos, look_at, display_region=None):
        super().__init__(tracking_target, pos, look_at, display_region)
        self.before_mouse_pos = None

    def setup_camera(self, pos):
        self.camera_root = NodePath('terrain_camera')
        self.camera_root.reparent_to(self.target)
        self.camera = base.make_camera(base.win, displayRegion=self.display_region)
        self.camera.reparent_to(self.camera_root)
        self.camera.set_pos(pos)
        self.camera.look_at(self.look_at)

    def rotate_camera(self, mouse_pos, dt):
        if self.before_mouse_pos:
            angle = Vec3()

            if (delta := mouse_pos.x - self.before_mouse_pos.x) < 0:
                angle.x += 180
            elif delta > 0:
                angle.x -= 180

            if (delta := mouse_pos.y - self.before_mouse_pos.y) < 0:
                angle.z -= 180
            elif delta > 0:
                angle.z += 180

            angle *= dt
            self.camera_root.set_hpr(self.camera_root.get_hpr() + angle)

        self.before_mouse_pos = Vec2(mouse_pos.xy)


class BasinTerrain(ShowBase):

    def __init__(self):
        super().__init__()
        self.disable_mouse()
        self.render.set_antialias(AntialiasAttrib.MAuto)

        self.world = BulletWorld()
        self.world.set_gravity(Vec3(0, 0, -9.81))
        self.debug = self.render.attach_new_node(BulletDebugNode('debug'))
        self.world.set_debug_node(self.debug.node())

        # create character
        self.walker = Walker()
        self.walker.reparent_to(self.render)
        self.walker.set_pos(Point3(0.0, 0.0, -49.5))

        # create floater
        self.floater = NodePath('floater')
        self.floater.set_z(3.0)
        self.floater.reparent_to(self.walker)

        # create custom camera
        self.camera_controller = TrackingCamera(
            self.walker, Point3(0, -5, -47), self.floater)

        # ##### when rotate by dragging#####
        # self.custom_camera = TerrainCamera(self.render, Point3(160, -160, 10), Point3(0, 0, 0))
        # self.camera_root = NodePath('camera_root')
        # self.camera_root.reparent_to(self.render)
        # self.camera.set_pos(Point3(30, -30, 100))
        # self.camera.look_at(Point3(0, 0, 10))
        # self.camera.reparent_to(self.camera_root)
        # #################################

        self.scene = Scene(self.world)
        self.target = None
        self.dragging = False

        inputState.watch_with_modifiers('forward', 'arrow_up')
        inputState.watch_with_modifiers('backward', 'arrow_down')
        inputState.watch_with_modifiers('left', 'arrow_left')
        inputState.watch_with_modifiers('right', 'arrow_right')

        self.accept('p', self.print_info)
        self.accept('d', self.toggle_debug)
        self.accept('escape', sys.exit)

        self.accept('mouse1', self.mouse_click)
        self.accept('mouse1-up', self.mouse_release)
        self.taskMgr.add(self.update, 'update')

        self.accept('x', self.positioning, ['x', 1])
        self.accept('shift-x', self.positioning, ['x', -1])
        self.accept('y', self.positioning, ['y', 1])
        self.accept('shift-y', self.positioning, ['y', -1])
        self.accept('z', self.positioning, ['z', 1])
        self.accept('shift-z', self.positioning, ['z', -1])
        self.accept('h', self.positioning, ['h', 1])
        self.accept('shift-h', self.positioning, ['h', -1])

    def positioning(self, key, direction):
        if self.target:
            distance = 0.1
            angle = 2
            pos = Point3()
            hpr = Vec3()

            match key:
                case 'x':
                    pos.x = distance * direction

                case 'y':
                    pos.y = distance * direction

                case 'z':
                    pos.z = distance * direction

                case 'h':
                    hpr.x = angle * direction

            pos = self.target.get_pos() + pos
            hpr = self.target.get_hpr() + hpr
            self.target.set_pos_hpr(pos, hpr)

    def print_info(self):
        if self.target:
            print(f'target pos: {self.target.get_pos()}')
            print(f'target hpr: {self.target.get_hpr()}')

        print(f'walker pos: {self.walker.get_pos()}')
        # rel_pos = self.walker.get_pos(self.scene.terrain.root)
        # block_pos = self.scene.terrain.terrain.get_block_from_pos(rel_pos.x, rel_pos.y)
        # print(block_pos)

    def toggle_debug(self):
        # self.scene.terrain.toggle_wireframe()
        if self.debug.is_hidden():
            self.debug.show()
        else:
            self.debug.hide()

    def control_walker(self):
        direction = Vec2()

        if inputState.is_set('forward'):
            direction.set_y(-1)

        if inputState.is_set('backward'):
            direction.set_y(1)

        if inputState.is_set('left'):
            direction.set_x(1)

        if inputState.is_set('right'):
            direction.set_x(-1)

        return direction

    def mouse_click(self):
        self.dragging = True
        self.dragging_start_time = globalClock.get_frame_time()

    def mouse_release(self):
        self.dragging = False
        self.before_mouse_pos = None

    def update(self, task):
        dt = globalClock.get_dt()
        direction = self.control_walker()
        self.walker.update(dt, direction)

        if direction.y:
            self.camera_controller.track(dt)

        # ##### when rotate by dragging#####
        # if self.mouseWatcherNode.has_mouse():
        #     mouse_pos = self.mouseWatcherNode.get_mouse()

        #     if self.dragging:
        #         if globalClock.get_frame_time() - self.dragging_start_time >= 0.2:
        #             self.custom_camera.rotate_camera(mouse_pos, dt)
        # ##################################

        self.world.do_physics(dt)
        return task.cont


if __name__ == '__main__':
    app = BasinTerrain()
    app.run()