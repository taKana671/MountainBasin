import numpy as np
import cv2

from mask.shapes.line_generator import LineMask
from mask.shapes.circle_generator import TransparentCircleMask
from mask.utils import output_image


def create_ground_mask(size):
    half = int(size / 2)
    points = [
        [(0, 0), (size, size)],
        [(0, half), (size, half)],
        [(half, 0), (half, size)],
        [(0, size), (size, 0)]
    ]
    LineMask.output_image(points, gaussian_kernel=3, height=129, width=129, line_thickness=2)


def modify_heightmap(file_path):
    # Read image file.
    heightmap = cv2.imread(file_path)
    h, w = heightmap.shape[:2]

    # Aline height to 100.
    heightmap = np.where(heightmap >= 100, 100, heightmap)
    output_image(heightmap, 'heightmap')

    # Create circle image.
    maker = TransparentCircleMask(h, w)
    circle_img = maker.create_bg_image()
    maker.create_circle(circle_img, radius=42)
    circle_img = maker.blur(circle_img, kernel=51)
    # output_image(circle_img, 'circle_mask')

    # Combine heightmap and circle images.
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    arr[:, :, 3] = np.where(heightmap[:, :, 0] < 5, 255, 0)
    arr[:, :, 2] = np.where(heightmap[:, :, 0] >= 100, 255, arr[:, :, 2])
    arr[:, :, 0] = np.where((heightmap[:, :, 0] >= 5) & (heightmap[:, :, 0] < 100), circle_img[:, :, 0], arr[:, :, 0])
    arr[:, :, 1] = np.where((heightmap[:, :, 0] >= 5) & (heightmap[:, :, 0] < 100), 255 - circle_img[:, :, 0], arr[:, :, 1])
    output_image(arr, 'attributes')


if __name__ == '__main__':
    create_ground_mask(129)
    modify_heightmap('island_heightmap_20250915122638.png')




