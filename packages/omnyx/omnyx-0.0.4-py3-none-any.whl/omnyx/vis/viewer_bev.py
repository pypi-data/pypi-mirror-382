from pathlib import Path
from typing import Callable, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

from ..fileio import read_points, write_image
from ..math.box import boxes_to_corners_3d, corners_to_edges_2d
from ..sensor.camera import resize_image
from .render import draw_lines, draw_points, draw_poly_lines, draw_texts


class ViewerBev:

    def __init__(
        self,
        lidar_points_list: List[np.ndarray] = [],
        box3d_list: List[Dict[str, np.ndarray]] = [],
        key_points_list: List[Dict[str, np.ndarray]] = [],
        external_loader_func: Callable = None,
    ):
        self.lidar_points_list = {i: v for i, v in enumerate(lidar_points_list
            if isinstance(lidar_points_list, list) else [lidar_points_list])}
        self.box3d_list = {i: v for i, v in enumerate(box3d_list
            if isinstance(box3d_list, list) else [box3d_list])}
        self.key_points_list = {i: v for i, v in enumerate(key_points_list
            if isinstance(key_points_list, list) else [key_points_list])}

        self.__frame_id = 0
        self.__bev_range_front = 120
        self.__bev_range_back = 80
        self.__bev_range_width = 100
        self.__voxel_size = 0.1
        self.__preview_width: int = 3200
        self.__preview_height: int = None
        self.__grid_map_size = np.array([20] * 2)
        self.__flip = False

        self.external_loader_func = external_loader_func

    def _set_viewer(self):
        self._bev_range = np.asarray([self.bev_range_front + self.bev_range_back, self.bev_range_width])
        self._bev_range_back_left = np.asarray([self.bev_range_back, self._bev_range[1] / 2])

        pixel_range = self._bev_range // self.__voxel_size + 1

        self._bev_size = pixel_range.astype(int)
        self._bev_image = np.ones([self._bev_size[1], self._bev_size[0], 3], dtype='uint8') * 30

        if self.__preview_height is not None:
            size_ratio = self._bev_image.shape[1] / self._bev_image.shape[0]
            preview_width = int(self.__preview_height * size_ratio)
            self._preview_size = (preview_width // 2 * 2, self.__preview_height)
        elif self.preview_width is not None:
            size_ratio = self._bev_image.shape[0] / self._bev_image.shape[1]
            preview_height = int(self.preview_width * size_ratio)
            self._preview_size = (self.preview_width, preview_height // 2 * 2)

    def _draw_grid_lines(self) -> bool:
        """ """
        grid_map_back_left = (self._bev_range_back_left // self.__grid_map_size * self.__grid_map_size).astype(int)
        grid_map_back_left_remains = self._bev_range_back_left % self.__grid_map_size

        distance_dash_dot = [np.arange(0, self._bev_size[i], 20) for i in range(2)]
        if self.flip:
            self._flipped = self._flip_image(self._bev_image)

        for grid_map_x in np.arange(0, self._bev_range[0], self.__grid_map_size[0]):
            grid_map_pixel_x = int((grid_map_x + grid_map_back_left_remains[0]) // self.__voxel_size)

            if not self.flip:
                draw_lines(image=self._bev_image, points2d=[[
                    (grid_map_pixel_x, distance_dash_dot[1][i - 1]),
                    (grid_map_pixel_x, distance_dash_dot[1][i])
                    ] for i in range(1, len(distance_dash_dot[1]), 2)],
                    color=[100] * 3, thickness=2)

                draw_texts(image=self._bev_image,
                           texts=['{:d}m'.format(grid_map_x - grid_map_back_left[0])],
                           poses2d=[(grid_map_pixel_x, distance_dash_dot[1][-1])],
                           fontscale=0.9, color=-1, thickness=2)
            else:
                draw_lines(image=self._flipped, points2d=[[
                    (distance_dash_dot[1][i - 1], self._bev_size[0] - grid_map_pixel_x),
                    (distance_dash_dot[1][i], self._bev_size[0] - grid_map_pixel_x)]
                    for i in range(1, len(distance_dash_dot[1]), 2)],
                    color=[100] * 3, thickness=2)
                draw_texts(image=self._flipped,
                           texts=['{:d}m'.format(grid_map_x - grid_map_back_left[0])],
                           poses2d=[(distance_dash_dot[1][-4], self._bev_size[0] - grid_map_pixel_x)],
                           fontscale=0.9, color=-1, thickness=2)

        for grid_map_y in np.arange(0, self._bev_range[1], self.__grid_map_size[1]):
            grid_map_pixel_y = int((grid_map_y + grid_map_back_left_remains[1]) // self.__voxel_size)

            if not self.flip:
                draw_lines(image=self._bev_image, points2d=[[
                    (distance_dash_dot[0][i - 1], grid_map_pixel_y),
                    (distance_dash_dot[0][i], grid_map_pixel_y)
                    ] for i in range(1, len(distance_dash_dot[0]), 2)],
                    color=[100] * 3, thickness=2)
                draw_texts(image=self._bev_image,
                           texts=['{:d}m'.format(grid_map_y - grid_map_back_left[1])],
                           poses2d=[(distance_dash_dot[0][-3], grid_map_pixel_y)],
                           fontscale=0.9, color=-1, thickness=2)
            else:
                draw_lines(image=self._flipped, points2d=[[
                    (self._bev_size[1] - grid_map_pixel_y, distance_dash_dot[0][i - 1]),
                    (self._bev_size[1] - grid_map_pixel_y, distance_dash_dot[0][i])
                    ] for i in range(1, len(distance_dash_dot[0]), 2)],
                    color=[100] * 3, thickness=2)
                draw_texts(image=self._flipped,
                           texts=['{:d}m'.format(grid_map_y - grid_map_back_left[1])],
                           poses2d=[(self._bev_size[1] - grid_map_pixel_y, distance_dash_dot[0][1])],
                           fontscale=0.9, color=-1, thickness=2)

    @staticmethod
    def _flip_image(image: np.ndarray) -> np.ndarray:
        return np.ascontiguousarray(image.transpose(1, 0, 2)[::-1])

    @staticmethod
    def _unflip_image(image: np.ndarray) -> np.ndarray:
        return np.ascontiguousarray(image.transpose(1, 0, 2)[:, ::-1])

    def _euclidean_to_pixel_coorditates(self, points: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """ """
        bev_view_points = points[:, :2] * [1, -1]
        pixel_points, pixel_indices = np.unique(
            (bev_view_points + self._bev_range_back_left) // \
            self.__voxel_size, axis=0, return_index=True)

        pixel_range_mask = (pixel_points[:, 0] >= 0) & (pixel_points[:, 0] < self._bev_size[0]) & \
                           (pixel_points[:, 1] >= 0) & (pixel_points[:, 1] < self._bev_size[1])
        return pixel_points[pixel_range_mask], pixel_indices[pixel_range_mask]

    def _draw_points(self) -> True:
        """
        @param points: (N, >3)
        """
        if self.frame_id not in self.lidar_points_list:
            return False
        points = self.lidar_points_list[self.frame_id]

        if points is None:
            return False

        _points = read_points(points) if isinstance(points, (str, Path)) else np.asarray(points)

        pixel_pts, _ = self._euclidean_to_pixel_coorditates(_points)
        draw_points(self._bev_image, pixel_pts.astype(int), color=-1, thickness=1)
        return True

    def _draw_polygons(self) -> bool:
        if self.frame_id not in self.key_points_list:
            return False
        key_points_dict = self.key_points_list[self.frame_id]

        if key_points_dict is None or 'key_points' not in key_points_dict:
            return False

        for indx, polyline in enumerate(key_points_dict['key_points']):
            pixel_points, _ = self._euclidean_to_pixel_coorditates(polyline)

            line_color = key_points_dict['line_types'][indx] if 'line_types' in key_points_dict else 0
            draw_poly_lines(self._bev_image, pixel_points.astype(int), line_color + 100, thickness=3)

        return True

    def _draw_bboxes3d(self) -> bool:
        if self.frame_id not in self.box3d_list:
            return False
        box3d_dict = self.box3d_list[self.frame_id]

        if box3d_dict is None or 'boxes3d' not in box3d_dict:
            return False

        boxes3d_bev = box3d_dict['boxes3d'].copy()
        boxes3d_bev[:, [1, 6]] = boxes3d_bev[:, [1, 6]] * -1

        if np.prod(boxes3d_bev.shape) == 0:
            return True

        corners_bev = boxes_to_corners_3d(boxes3d_bev)[:, :4, :2]
        corners_pixel = ((corners_bev + self._bev_range_back_left) // self.__voxel_size).astype(int)

        box_bolor, thickness = [0, 0, 255], 3

        for indx, edges_bev in enumerate(corners_to_edges_2d(corners_pixel)):
            box_headings = [[np.vstack([edges_bev[0] * 1.8, edges_bev[2] * 0.2]).mean(axis=0).astype(int),
                             np.vstack([edges_bev[0] * 1.3, edges_bev[2] * 0.7]).mean(axis=0).astype(int)]]
            # draw heading and edges
            draw_lines(self._bev_image, np.vstack([box_headings, edges_bev]), color=box_bolor, thickness=thickness)

            if box3d_dict.get('velos') is not None:
                box_velos = [
                    [np.vstack([2.1 * edges_bev[0], -0.1 * edges_bev[2]]).mean(axis=0).astype(int),
                    (np.vstack([2.1 * edges_bev[0], -0.1 * edges_bev[2]]).mean(axis=0) + \
                     box3d_dict['velos'][indx, :2] / 0.7 * [1, -1]).astype(int)]]
                draw_lines(self._bev_image, box_velos, color=box_bolor, thickness=thickness)

        if box3d_dict.get('texts') is not None:
            if self.flip:
                _flip = self._flip_image(self._bev_image)
                draw_texts(image=_flip,
                    texts=box3d_dict['texts'],
                    poses2d=((corners_pixel[..., ::-1] - [-10, self._bev_size[0]]) * [1, -1]).mean(axis=1).astype(int),
                    fontscale=1.2, color=box_bolor, thickness=thickness)
                self._bev_image = self._unflip_image(_flip)
            else:
                draw_texts(image=self._bev_image,
                    texts=box3d_dict['texts'],
                    poses2d=(corners_pixel + [-10, 0]).mean(axis=1).astype(int),
                    fontscale=1.2, color=box_bolor, thickness=thickness)

        return True

    def _draw_visualizer(self) -> bool:
        self._set_viewer()
        ret = self._draw_points() | self._draw_bboxes3d() | self._draw_polygons()
        # if not ret:
        #     return False
        self._draw_grid_lines()
        return True

    @property
    def frame_id(self) -> int:
        return self.__frame_id

    @frame_id.setter
    def frame_id(self, param: int) -> None:
        self.__frame_id += param

    @property
    def preview_width(self) -> int:
        return self.__preview_width

    @preview_width.setter
    def preview_width(self, width: int) -> None:
        self.__preview_width = width
        self.__preview_height = None

    @property
    def preview_height(self) -> int:
        return self.__preview_height

    @preview_height.setter
    def preview_height(self, height: int) -> None:
        self.__preview_height = height
        self.__preview_width = None

    @property
    def bev_range_front(self) -> int:
        return self.__bev_range_front

    @bev_range_front.setter
    def bev_range_front(self, front: int) -> None:
        self.__bev_range_front = front

    @property
    def bev_range_back(self) -> int:
        return self.__bev_range_back

    @bev_range_back.setter
    def bev_range_back(self, back: int) -> None:
        self.__bev_range_back = back

    @property
    def bev_range_width(self) -> int:
        return self.__bev_range_width

    @bev_range_width.setter
    def bev_range_width(self, width: int) -> None:
        self.__bev_range_width = width

    @property
    def flip(self) -> bool:
        return self.__flip

    @flip.setter
    def flip(self, flip: bool) -> None:
        self.__flip = flip

    @property
    def image(self) -> np.ndarray:
        self._draw_visualizer()
        if self.flip:
            return resize_image(self._flipped, (self._preview_size[1], self._preview_size[0]))
        return resize_image(self._bev_image, self._preview_size)

    def save(self, filename: str) -> bool:
        write_image(filename, self.image)
        return True

    def show(self):
        plt.imshow(self.image[..., ::-1])
        plt.show()
