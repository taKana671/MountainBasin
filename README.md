# TorusShapedTerrain

I previously attempted to create a terrain with holes in [TerrainWithHole](https://github.com/taKana671/TerrainWithHole), but I wasn't entirely satisfied with the results, so I decided to try again in this repository.
The terrain was created from a heightmap where noise was processed into a torus shape and adjusted to form steep cliffs. From this heightmap, generated a colormap with an alpha channel, and used this colormap and shaders to make holes in terrain by hiding the areas where I wanted to create them.

Additionally, I rewrote the program multiple times to prevent the camera from going through the 3D models and characters from clipping through tunnels or terrain.

The heightmap was generated using the repository  [TextureGenerator](https://github.com/taKana671/TextureGenerator), and the skybox was created using the repository [skybox](https://github.com/taKana671/skybox),.

# Requirements

* Panda3D 1.10.15

# Environment

* Python 3.12
* Windows11
