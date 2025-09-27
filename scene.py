import numpy as np

from panda3d.bullet import BulletRigidBodyNode, BulletSoftBodyNode
from panda3d.bullet import BulletConvexHullShape, BulletHeightfieldShape, ZUp
from panda3d.bullet import BulletTriangleMeshShape, BulletTriangleMesh
from panda3d.bullet import BulletHelper
from panda3d.core import NodePath, PandaNode
from panda3d.core import Vec3, Point3, BitMask32, LColor
from panda3d.core import Filename, PNMImage
from panda3d.core import Shader
from panda3d.core import TextureStage, TransformState
from panda3d.core import GeoMipTerrain
from panda3d.core import GeomNode, GeomVertexFormat
from shapes import Box, Cylinder, Plane


class Tunnel(NodePath):

    def __init__(self, length=15., width=7., wall_height=6., thickness=1.2):
        super().__init__(BulletRigidBodyNode('tunnel'))
        self.length = length
        self.width = width
        self.thickness = thickness
        self.wall_height = wall_height

        self.node().set_mass(0)
        self.set_collide_mask(BitMask32.bit(1))
        self.create_model()

    def assemble(self, parent, model, pos, hpr):
        mesh = BulletTriangleMesh()
        mesh.add_geom(model.node().get_geom(0))
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        self.node().add_shape(shape, TransformState.make_pos_hpr(pos, hpr))

        model.set_pos_hpr(pos, hpr)
        model.reparent_to(parent)

    def create_model(self):
        root_wall = NodePath('door_wall')
        root_wall.reparent_to(self)

        # The wall of a tunnel
        wall = Box(
            depth=self.length,
            width=self.width,
            height=self.wall_height,
            thickness=self.thickness,
            open_front=True,
            open_back=True,
            open_top=True,
            open_bottom=True).create()

        self.assemble(root_wall, wall, Point3(0, 0, 0), Vec3(0, 0, 0))

        # The top of the tunnel
        radius = self.width / 2
        y = self.length / 2
        z = self.wall_height / 2

        top = Cylinder(
            radius=radius,
            inner_radius=radius - self.thickness,
            height=self.length,
            ring_slice_deg=180).create()

        self.assemble(root_wall, top, Point3(0, y, z), Vec3(180, -90, 0))

        tex = base.loader.load_texture('textures/9-19-20k-300x300.jpg')
        root_wall.set_texture(tex)


class Ground(NodePath):

    def __init__(self, w=129, d=129, segs_w=43, segs_d=43):
        super().__init__(BulletRigidBodyNode('ground'))
        self.node().set_mass(0)
        self.set_collide_mask(1)
        self.create_model(w, d, segs_w, segs_d)

    def create_model(self, w, d, segs_w, segs_d):
        self.model = Plane(w, d, segs_w, segs_d).create()

        mesh = BulletTriangleMesh()
        mesh.add_geom(self.model.node().get_geom(0))
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        self.node().add_shape(shape)

        self.model.set_pos(Point3(0, 0, 0))
        self.model.reparent_to(self)

        shader = Shader.load(Shader.SL_GLSL, 'shaders/ground_v.glsl', 'shaders/ground_f.glsl')
        self.set_shader(shader)
        # self.set_shader_input("camera", base.camera)

        textures = [
            ['textures/tex_moss.png', 10],
            ['textures/rock_04.jpg', 30],
            ['terrain/ground_mask.png', None]
        ]

        for i, (img_file, scale) in enumerate(textures):
            ts = TextureStage(f'ts{i}')
            ts.set_sort(i)

            if scale:
                self.set_shader_input(f'tex_ScaleFactor{i}', scale)

            tex = base.loader.load_texture(img_file)
            self.set_texture(ts, tex)

        self.set_shader_input('tex_attribute', base.loader.load_texture('terrain/heightmap.png'))


class Terrain(NodePath):

    def __init__(self):
        super().__init__(BulletRigidBodyNode('terrain'))
        self.file_path = 'terrain/heightmap.png'
        self.height = 80

        self.node().set_mass(0)
        self.set_collide_mask(BitMask32.bit(1))
        shape = BulletHeightfieldShape(base.loader.load_texture(self.file_path), self.height, ZUp)
        shape.set_use_diamond_subdivision(True)
        self.node().add_shape(shape)
        self.make_geomip_terrain()

    def make_geomip_terrain(self):
        img = PNMImage(Filename(self.file_path))
        self.terrain = GeoMipTerrain('geomip_terrain')
        self.terrain.set_heightfield(self.file_path)
        self.terrain.set_border_stitching(True)
        # self.terrain.setBruteforce(True)

        self.terrain.set_block_size(8)
        self.terrain.set_min_level(2)
        self.terrain.set_focal_point(base.camera)

        size_x, size_y = img.get_size()
        x = (size_x - 1) / 2
        y = (size_y - 1) / 2

        pos = Point3(-x, -y, -(self.height / 2))
        self.root = self.terrain.get_root()
        self.root.set_sz(self.height)
        self.root.set_pos(pos)

        self.terrain.generate()
        self.root.reparent_to(self)

        shader = Shader.load(Shader.SL_GLSL, 'shaders/terrain_v.glsl', 'shaders/terrain_f.glsl')
        self.root.set_shader(shader)
        # self.root.clear_texture()
        self.root.set_shader_input("camera", base.camera)

        textures = [
            ['textures/tex_rock.png', 10],
            ['textures/grass_02.png', 10],
            ['textures/tex_cracked.png', 10],
            ['textures/tex_moss.png', 10],
            ['textures/rock_04.jpg', 30],
            ['terrain/ground_mask.png', None]
        ]

        for i, (img_file, scale) in enumerate(textures):
            ts = TextureStage(f'ts{i}')
            ts.set_sort(i)

            if scale:
                self.root.set_shader_input(f'tex_ScaleFactor{i}', scale)

            tex = base.loader.load_texture(img_file)
            self.root.set_texture(ts, tex)

        self.root.set_shader_input('tex_attribute', base.loader.load_texture('terrain/attributes.png'))


class Scene:

    def __init__(self, world):
        self.world = world
        self.scene = NodePath('scene')
        self.scene.reparent_to(base.render)

        self.terrain = Terrain()
        self.terrain.reparent_to(self.scene)
        self.world.attach(self.terrain.node())
        self.terrain.set_z(-12)

        z = -49.4

        tunnels = [
            Point3(0.089979745, -39.261665, z),  # angle: 0
            Point3(23.209034, -23.172128, z),    # angle: 45
            Point3(31.165838, -0.0605596, z),    # angle: 90
            Point3(23.421295, 22.43706, z),      # angle: 135
            Point3(-0.065003, 36.80987, z),      # angle: 180
            Point3(-23.492284, 23.602266, z),    # angle: 225
            Point3(-39.154972, 0.032763533, z),  # angle: 270
            Point3(-29.590984, -30.589447, z)    # angle: 315
        ]

        for i, pos in enumerate(tunnels):
            hpr = Vec3(i * 45, 0, 0)
            tunnel = Tunnel()
            tunnel.set_pos_hpr(pos, hpr)
            tunnel.reparent_to(self.scene)
            self.world.attach(tunnel.node())  

        self.ground = Ground()
        self.ground.reparent_to(self.scene)
        self.world.attach(self.ground.node())
        # self.ground.set_pos(Point3(0, 0, -52))
        self.ground.set_pos(Point3(0, 0, -52.01))
