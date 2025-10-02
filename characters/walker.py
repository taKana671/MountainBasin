from enum import Enum, auto

from direct.actor.Actor import Actor
from panda3d.bullet import BulletCapsuleShape, ZUp
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import BulletRigidBodyNode, BulletSphereShape
from panda3d.core import BitMask32, NodePath, Vec3, Point3
from panda3d.core import TransformState



class Motions(Enum):

    FORWARD = auto()
    BACKWARD = auto()
    TURN = auto()


class Walker(NodePath):

    RUN = 'run'
    WALK = 'walk'

    def __init__(self):
        super().__init__(BulletRigidBodyNode('walker'))
        self.sweep_shape = BulletSphereShape(0.5)

        h, w = 6, 1.2
        shape = BulletCapsuleShape(w, h - 2 * w, ZUp)
        # super().__init__(BulletCharacterControllerNode(shape, 0.4, 'wolker'))
        self.node().add_shape(shape)
        self.node().set_kinematic(True)
        self.node().set_ccd_motion_threshold(1e-7)
        self.node().set_ccd_swept_sphere_radius(0.5)

        # self.set_collide_mask(BitMask32.allOn())
        self.set_collide_mask(BitMask32.bit(2))
        # self.set_collide_mask(BitMask32.bit(3) | BitMask32.bit(4))
        self.set_scale(0.5)
        # base.world.attach_character(self.node())
        base.world.attach(self.node())

        self.direction_nd = NodePath('direction')
        self.direction_nd.set_h(180)
        self.direction_nd.reparent_to(self)

        self.actor = Actor(
            'models/ralph/ralph.egg',
            {self.RUN: 'models/ralph/ralph-run.egg',
             self.WALK: 'models/ralph/ralph-walk.egg'}
        )
        self.actor.set_transform(TransformState.make_pos(Vec3(0, 0, -2.5)))
        self.actor.set_name('ralph')
        # self.actor.reparent_to(self)
        self.actor.reparent_to(self.direction_nd)

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

    def shoot_a_ray(self, from_pos, distance, mask):
        to_pos = from_pos + distance

        if (hit := base.world.ray_test_closest(from_pos, to_pos, mask)).has_hit():
            # print(hit.get_node().name)
            return hit

    def check_collisions(self, current_pos, next_pos):
        from_pos = TransformState.make_pos(current_pos)
        to_pos = TransformState.make_pos(next_pos)

        if (result := base.world.sweep_test_closest(
                self.sweep_shape, from_pos, to_pos, BitMask32.bit(1), 0.0)).has_hit():
            print(result.get_node().name)
            return result

    def move(self, dt, direction_y):
        current_pos = self.get_pos()
        speed = 10 if direction_y < 0 else 5
        orientation = self.direction_nd.get_quat(base.render).get_forward()
        next_pos = current_pos + orientation * direction_y * speed * dt

        if not (hit := self.shoot_a_ray(
                current_pos, Vec3(0, 0, -2.5), BitMask32.bit(2))):
            return

        next_pos.z = hit.get_hit_pos().z + 1.5

        if (result := self.check_collisions(current_pos, next_pos)):
            if result.get_node().get_name().startswith('tunnel'):
                return

            if not (hit := self.shoot_a_ray(
                    next_pos, Vec3(0, 0, -2.5), BitMask32.bit(3))):
                return

        self.set_pos(next_pos)

    def turn(self, dt, direction_x):
        angle = 30 * direction_x * dt
        self.direction_nd.set_h(self.direction_nd.get_h() + angle)

    def update(self, dt, direction):
        motion = None

        if direction.y:
            self.move(dt, direction.y)
            motion = Motions.FORWARD if direction.y < 0 else Motions.BACKWARD

        if direction.x:
            self.turn(dt, direction.x)
            motion = Motions.TURN

        self.play_anim(motion)
