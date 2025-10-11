from enum import Enum

from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletHeightfieldShape, ZUp
from panda3d.bullet import BulletTriangleMeshShape, BulletTriangleMesh
from panda3d.core import NodePath
from panda3d.core import Vec3, Point2, Point3, BitMask32, LColor
from panda3d.core import Filename, PNMImage
from panda3d.core import Shader
from panda3d.core import TextureStage, TransformState
from panda3d.core import GeoMipTerrain
from panda3d.core import TransparencyAttrib

from shapes import Box, Cylinder, Plane


class Model(Enum):

    TERRAIN = 1
    GROUND = 2
    SENSOR = 3
    TUNNEL = 4

    @property
    def mask(self):
        return BitMask32.bit(self.value)


class ModelRoot(NodePath):

    def __init__(self, name, mask):
        super().__init__(BulletRigidBodyNode(name))
        self.node().set_mass(0)
        self.set_collide_mask(mask)

    def assemble(self, parent, model, pos, hpr):
        mesh = BulletTriangleMesh()
        mesh.add_geom(model.node().get_geom(0))
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        self.node().add_shape(shape, TransformState.make_pos_hpr(pos, hpr))

        model.set_pos_hpr(pos, hpr)
        model.reparent_to(parent)

    def setup_shader(self, parent, vert, frag, textures):
        shader = Shader.load(Shader.SL_GLSL, f'shaders/{vert}', f'shaders/{frag}')
        parent.set_shader(shader)

        for i, (img_file, scale) in enumerate(textures):
            ts = TextureStage(f'ts{i}')
            ts.set_sort(i)

            if scale:
                parent.set_shader_input(f'tex_ScaleFactor{i}', scale)

            tex = base.loader.load_texture(img_file)
            parent.set_texture(ts, tex)


class Tunnel(ModelRoot):

    def __init__(self, name, length, width=7., wall_height=6., thickness=1.2):
        super().__init__(name, Model.TUNNEL.mask)
        self.length = length
        self.width = width
        self.thickness = thickness
        self.wall_height = wall_height
        self.create_model()

        # self.node().deactivation_enabled = False

    def create_model(self):
        tunnel = NodePath('material')
        tunnel.reparent_to(self)

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

        self.assemble(tunnel, wall, Point3(0, 0, 0), Vec3(0, 0, 0))
        wall.set_tex_scale(TextureStage.get_default(), 3, 1)

        # The top of the tunnel
        radius = self.width / 2
        y = self.length / 2
        z = self.wall_height / 2

        top = Cylinder(
            radius=radius,
            inner_radius=radius - self.thickness,
            height=self.length,
            ring_slice_deg=180).create()

        self.assemble(tunnel, top, Point3(0, y, z), Vec3(180, -90, 0))
        top.set_tex_scale(TextureStage.get_default(), 1, 3)

        tunnel.set_texture(base.loader.load_texture('textures/brick_03.jpg'))


class Sensor(ModelRoot):

    def __init__(self, name, w, d):
        super().__init__(name, Model.SENSOR.mask)
        self.set_transparency(TransparencyAttrib.MAlpha)
        self.set_color(LColor(1, 1, 1, 1))
        self.create_model(w, d)

    def create_model(self, w, d):
        sensor = Plane(w, d, int(w), int(d)).create()
        self.assemble(self, sensor, Point3(0, 0, 0), Vec3(0, 0, 0))


class Ground(ModelRoot):

    def __init__(self, name, w=129, d=129, segs_w=43, segs_d=43):
        super().__init__(name, Model.GROUND.mask)
        self.create_model(w, d, segs_w, segs_d)

    def create_model(self, w, d, segs_w, segs_d):
        ground = Plane(w, d, segs_w, segs_d).create()
        self.assemble(self, ground, Point3(0, 0, 0), Vec3(0, 0, 0))

        textures = [
            ['textures/tex_moss.png', 10],
            ['textures/rock_04.jpg', 30],
            ['terrain/ground_mask.png', None]
        ]

        self.setup_shader(self, 'ground_v.glsl', 'ground_f.glsl', textures)
        self.set_shader_input('tex_attribute', base.loader.load_texture('terrain/heightmap.png'))


class Terrain(ModelRoot):

    def __init__(self, name, file_path, height=80):
        super().__init__(name, Model.TERRAIN.mask)
        self.file_path = file_path
        self.height = height
        self.make_geomip_terrain()

    def make_geomip_terrain(self):
        shape = BulletHeightfieldShape(base.loader.load_texture(self.file_path), self.height, ZUp)
        shape.set_use_diamond_subdivision(True)
        self.node().add_shape(shape)

        img = PNMImage(Filename(self.file_path))
        self.terrain = GeoMipTerrain('geomip_terrain')
        self.terrain.set_heightfield(self.file_path)
        self.terrain.set_border_stitching(True)
        # self.terrain.setBruteforce(True)

        self.terrain.set_block_size(8)
        self.terrain.set_min_level(2)
        self.terrain.set_focal_point(base.camera)

        self.size_x, self.size_y = img.get_size()
        x = (self.size_x - 1) / 2
        y = (self.size_y - 1) / 2

        pos = Point3(-x, -y, -(self.height / 2))
        self.root = self.terrain.get_root()
        self.root.set_sz(self.height)
        self.root.set_pos(pos)

        self.terrain.generate()
        self.root.reparent_to(self)

        textures = [
            ['textures/tex_rock.png', 10],
            ['textures/grass_02.png', 10],
            ['textures/tex_cracked.png', 10],
            ['textures/tex_moss.png', 10],
            ['textures/rock_04.jpg', 30],
            ['terrain/ground_mask.png', None]
        ]

        self.root.set_shader_input("camera", base.camera)
        self.setup_shader(self.root, 'terrain_v.glsl', 'terrain_f.glsl', textures)
        self.root.set_shader_input('tex_attribute', base.loader.load_texture('terrain/attributes.png'))
        self.root.set_two_sided(True)


class Scene:

    def __init__(self, world):
        self.world = world

        self.scene = NodePath('scene')
        self.scene.reparent_to(base.render)

        self.create_terrain()
        self.create_ground()
        self.create_tunnels()

    def create_terrain(self):
        self.terrain = Terrain('terrain', 'terrain/heightmap.png')
        self.terrain.reparent_to(self.scene)
        self.world.attach(self.terrain.node())
        self.terrain.set_z(-12)

    def create_ground(self):
        self.ground = Ground('ground', self.terrain.size_x, self.terrain.size_y)
        self.ground.reparent_to(self.scene)
        self.world.attach(self.ground.node())
        self.ground.set_pos(Point3(0, 0, -51))

    def create_tunnels(self):
        tunnel_z = -49.58
        sensor_z = self.ground.get_z() - 0.03

        tunnels = [
            [Point2(26.159046, -26.17214), 38],          # angle: 45
            [Point2(26.321306, 25.33707), 37],           # angle: 135
            [Point2(-26.392295, 26.402277), 38],         # angle: 225
            [Point2(-25.89097, -26.889432), 38],         # angle: 315
        ]

        for i, (xy, length) in enumerate(tunnels):
            hpr = Vec3(45 + 90 * i, 0, 0)
            tunnel = Tunnel(f'tunnel_{i}', length)
            tunnel.set_pos_hpr(Point3(xy, tunnel_z), hpr)
            tunnel.reparent_to(self.scene)
            self.world.attach(tunnel.node())

            # Embed a plain model beneath the ground
            # so characters can pass through the terrain inside the tunnel.
            w = tunnel.width - tunnel.thickness * 2
            sensor = Sensor(f'sensor_{i}', w, length)
            sensor.set_pos_hpr(Point3(xy, sensor_z), hpr)
            sensor.reparent_to(self.scene)
            self.world.attach(sensor.node())
