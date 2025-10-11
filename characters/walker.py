from enum import Enum, auto

from direct.actor.Actor import Actor
from panda3d.bullet import BulletCapsuleShape, ZUp
from panda3d.bullet import BulletRigidBodyNode, BulletSphereShape
from panda3d.core import BitMask32, NodePath, Vec3
from panda3d.core import TransformState

from scene import Model


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
        self.node().add_shape(shape)
        self.node().set_kinematic(True)

        self.set_collide_mask(BitMask32.bit(2))
        self.set_scale(0.5)
        self.set_h(180)
        base.world.attach(self.node())

        self.actor = Actor(
            'models/ralph/ralph.egg',
            {self.RUN: 'models/ralph/ralph-run.egg',
             self.WALK: 'models/ralph/ralph-walk.egg'}
        )
        self.actor.set_transform(TransformState.make_pos(Vec3(0, 0, -2.5)))
        self.actor.set_name('ralph')
        self.actor.reparent_to(self)

        self.angular_velocity = 60
        self.forward_speed = 10
        self.backward_speed = 5

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
            return hit

    def check_collisions(self, current_pos, next_pos, mask):
        from_pos = TransformState.make_pos(current_pos)
        to_pos = TransformState.make_pos(next_pos)

        if (result := base.world.sweep_test_closest(
                self.sweep_shape, from_pos, to_pos, mask, 0.0)).has_hit():
            return result

    def move(self, dt, direction_y):
        current_pos = self.get_pos()
        speed = self.forward_speed if direction_y < 0 else self.backward_speed
        orientation = self.get_quat(base.render).get_forward()
        next_pos = current_pos + orientation * direction_y * speed * dt

        if not (hit := self.shoot_a_ray(
                current_pos, Vec3(0, 0, -2.5), Model.GROUND.mask)):
            return

        next_pos.z = hit.get_hit_pos().z + 1.5

        if (result := self.check_collisions(
                current_pos, next_pos, Model.TERRAIN.mask | Model.TUNNEL.mask)):

            if result.get_node().get_name().startswith('tunnel'):
                return

            if not (hit := self.shoot_a_ray(
                    next_pos, Vec3(0, 0, -2.5), Model.SENSOR.mask)):
                return

        self.set_pos(next_pos)

    def turn(self, dt, direction_x):
        angle = self.angular_velocity * direction_x * dt
        self.set_h(self.get_h() + angle)

    def update(self, dt, direction):
        motion = None

        if direction.y:
            self.move(dt, direction.y)
            motion = Motions.FORWARD if direction.y < 0 else Motions.BACKWARD

        if direction.x:
            self.turn(dt, direction.x)
            motion = Motions.TURN

        self.play_anim(motion)