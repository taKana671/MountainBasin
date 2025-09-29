import sys
from enum import Enum, auto

from direct.actor.Actor import Actor
import direct.gui.DirectGuiGlobals as DGG
from panda3d.bullet import BulletCapsuleShape, ZUp
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import BulletWorld, BulletDebugNode
from panda3d.core import Vec3, Vec2, Point3, LColor, Vec4, BitMask32
from panda3d.core import TransformState
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import NodePath, TextNode
from panda3d.core import load_prc_file_data
from panda3d.core import OrthographicLens, Camera, MouseWatcher, PGTop
from panda3d.core import TransparencyAttrib, AntialiasAttrib
from direct.gui.DirectGui import DirectEntry, DirectFrame, DirectLabel, DirectButton, OkDialog
from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from direct.showbase.InputStateGlobal import inputState

from scene import Scene


load_prc_file_data("", """
    textures-power-2 none
    gl-coordinate-system default
    window-title Panda3D Avoid Balls
    filled-wireframe-apply-shader true
    stm-max-views 8
    stm-max-chunk-count 2048""")
    # parallax-mapping-samples 3
    # parallax-mapping-scale 0.1""")


class Motions(Enum):

    FORWARD = auto()
    BACKWARD = auto()
    TURN = auto()


class Walker(NodePath):

    RUN = 'run'
    WALK = 'walk'

    def __init__(self):
        h, w = 6, 1.2
        shape = BulletCapsuleShape(w, h - 2 * w, ZUp)
        super().__init__(BulletCharacterControllerNode(shape, 0.4, 'wolker'))

        # self.set_collide_mask(BitMask32.allOn())
        self.set_collide_mask(BitMask32.bit(1))
        self.set_scale(0.5)
        base.world.attach_character(self.node())

        self.actor = Actor(
            'models/ralph/ralph.egg',
            {self.RUN: 'models/ralph/ralph-run.egg',
             self.WALK: 'models/ralph/ralph-walk.egg'}
        )
        self.actor.set_transform(TransformState.make_pos(Vec3(0, 0, -2.5)))
        self.actor.set_name('ralph')
        self.actor.reparent_to(self)

    def play_anim(self, motion):
        match motion:

            case Motions.FORWARD:
                anim = Walker.RUN

            case Motions.BACKWARD:
                anim = Walker.WALK

            case Motions.TURN:
                anim = Walker.WALK

            case _:
                if self.actor.get_current_anim() is not None:
                    self.actor.stop()
                    self.actor.pose(Walker.WALK, 5)
                return

        if self.actor.get_current_anim() != anim:
            self.actor.loop(anim)


class BasinTerrain(ShowBase):

    def __init__(self):
        super().__init__()
        self.disable_mouse()
        self.render.set_antialias(AntialiasAttrib.MAuto)

        self.world = BulletWorld()
        self.world.set_gravity(Vec3(0, 0, -9.81))

        self.debug = self.render.attach_new_node(BulletDebugNode('debug'))
        self.world.set_debug_node(self.debug.node())

        # setup character
        self.walker = Walker()
        self.walker.reparent_to(self.render)
        self.walker.set_pos(Point3(0.0, 0.0, -50.58001))
        self.walker.set_pos(Point3(0.0, 0.0, -48))

        # self.walker.set_pos(8.510511, -58.909461, 100)

        self.floater = NodePath('floater')
        self.floater.set_z(3.0)
        self.floater.reparent_to(self.walker)

        # setup camera
        self.camera.reparent_to(self.walker)
        self.camera.set_pos(Vec3(0, 10, 5))
        self.camera.look_at(self.floater)
        self.camLens.set_fov(90)

        # ##### when rotate by dragging#####
        # self.camera_root = NodePath('camera_root')
        # self.camera_root.reparent_to(self.render)
        # self.camera.set_pos(Point3(30, -30, 100))
        # self.camera.look_at(Point3(0, 0, 10))
        # self.camera.reparent_to(self.camera_root)
        # #################################

        self.scene = Scene(self.world)
        self.target = self.scene.tunnel
        # self.target = None


        self.dragging = False
        self.before_mouse_pos = None

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

    def control_walker(self, dt):
        speed = Vec3(0, 0, 0)
        omega = 0.0
        motion = None

        if inputState.is_set('forward'):
            speed.set_y(-10.0)
            motion = Motions.FORWARD

        if inputState.is_set('backward'):
            speed.set_y(5.0)
            motion = Motions.BACKWARD

        if inputState.is_set('left'):
            omega = 30.0
            motion = Motions.TURN

        if inputState.is_set('right'):
            omega = -30.0
            motion = Motions.TURN

        self.walker.node().set_angular_movement(omega)
        self.walker.node().set_linear_movement(speed, True)
        self.walker.play_anim(motion)

    def mouse_click(self):
        self.dragging = True
        self.dragging_start_time = globalClock.get_frame_time()

    def mouse_release(self):
        self.dragging = False
        self.before_mouse_pos = None

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

    def update(self, task):
        dt = globalClock.get_dt()
        self.control_walker(dt)

        # ##### when rotate by dragging#####
        # if self.mouseWatcherNode.has_mouse():
        #     mouse_pos = self.mouseWatcherNode.get_mouse()

        #     if self.dragging:
        #         if globalClock.get_frame_time() - self.dragging_start_time >= 0.2:
        #             self.rotate_camera(mouse_pos, dt)
        # #####################################

        self.world.do_physics(dt)
        return task.cont


if __name__ == '__main__':
    app = BasinTerrain()
    app.run()