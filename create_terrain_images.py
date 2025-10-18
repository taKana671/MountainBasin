import numpy as np
import cv2

from mask.shapes.line_generator import LineMask
from mask.shapes.circle_generator import CircleMask
from utils import output_image
from heightmap_generator.masking import Masking


def create_ground_mask(size=129):
    v = 20

    points = [
        [(v, v), (size - v, size - v)],
        [(v, size - v), (size - v, v)]
    ]

    LineMask.output_image(
        points, gaussian_kernel=3, height=129, width=129, line_thickness=2, with_suffix=False
    )


def create_ground_mask2(size=129):
    v = 5

    points = [
        [(v, v), (size - v, size - v)],
        [(v, size - v), (size - v, v)],
        [(v, v), (size - v, v)],
        [(v, v), (v, size - v)],
        [(size - v, v), (size - v, size - v)],
        [(v, size - v), (size - v, size - v)]
    ]

    line_maker = LineMask(size, size)
    img = line_maker.create_bg_image()
    img = line_maker.blur(img, kernel=3)
    line_maker.create_lines(img, points, thickness=2)
    output_image.output(img, 'ground2', with_suffix=False)


def create_height_map(size=129):
    mask = CircleMask(size, size)
    mask_img = mask.create_bg_image()
    mask.create_circle(mask_img, radius=38, thickness=15)
    mask_img = mask.blur(mask_img, 31)
    output_image.output(mask_img, 'circle_mask', with_suffix=False)
    Masking.fractal_simplex_noise(mask_img, size=size, with_suffix=False)


def modify_heightmap(heightmap_path='masked_image.png', mask_path='circle_mask.png'):
    # Read heightmap image file.
    heightmap = cv2.imread(heightmap_path)
    h, w = heightmap.shape[:2]

    # Aline height to 100.
    heightmap = np.where(heightmap >= 100, 100, heightmap)
    output_image.output(heightmap, 'heightmap', with_suffix=False)

    # Combine heightmap and circle images.
    circle_img = cv2.imread(mask_path)
    circle_img = 255 - circle_img

    arr = np.zeros((h, w, 4), dtype=np.uint8)
    arr[:, :, 3] = np.where(heightmap[:, :, 0] < 5, 255, 0)
    arr[:, :, 2] = np.where(heightmap[:, :, 0] >= 100, 255, arr[:, :, 2])
    arr[:, :, 0] = np.where((heightmap[:, :, 0] >= 5) & (heightmap[:, :, 0] < 100), circle_img[:, :, 0] * 0.8, arr[:, :, 0])
    arr[:, :, 1] = np.where((heightmap[:, :, 0] >= 5) & (heightmap[:, :, 0] < 100), 255 - circle_img[:, :, 0] * 0.8, arr[:, :, 1])

    output_image.output(arr, 'attributes', with_suffix=False)
    output_image.output(arr[:, :, :3], 'attributes_no_alpha', with_suffix=False)


if __name__ == '__main__':
    create_ground_mask(129)
    create_ground_mask2(129)
    create_height_map(129)
    modify_heightmap()