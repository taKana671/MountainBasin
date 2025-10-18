# TorusShapedTerrain

I previously attempted to create a terrain with holes in [TerrainWithHole](https://github.com/taKana671/TerrainWithHole), but I wasn't entirely satisfied with the results, so I decided to try again in this repository.
The terrain was created from a heightmap where noise was processed into a torus shape and adjusted to form steep cliffs. From this heightmap, generated a colormap with an alpha channel, and used this colormap and shaders to make holes in terrain by hiding the areas where I wanted to create the holes.
Additionally, I rewrote the program multiple times to prevent the camera from going through the 3D models and characters from clipping through tunnels or terrain.
The skybox was created using the repository [skybox](https://github.com/taKana671/skybox),.

https://github.com/user-attachments/assets/4817cada-e7e2-432e-bbcc-45baba662415

# Requirements

* Panda3D 1.10.15

# Environment

* Python 3.12
* Windows11

# Terrain
The heightmap and mask images were generated using the repository  [TextureGenerator](https://github.com/taKana671/TextureGenerator). 
See: `create_terrain_images.py`

<img width="646" height="679" alt="Image" src="https://github.com/user-attachments/assets/b6e4b2a5-07c4-4186-a7e3-3142d7816a5b" />

<img width="637" height="518" alt="Image" src="https://github.com/user-attachments/assets/2c483963-eb5d-47d0-b43f-3f0d0854dcc1" />

# Character Controls:

* Press [Esc] to quit.
* Press [up arrow] key to go foward.
* Press [left arrow] key to turn left.
* Press [right arrow] key to turn right.
* Press [down arrow] key to go back.
* Press [ D ] key to toggle debug ON and OFF.
  
