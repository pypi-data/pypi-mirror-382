from pathlib import Path
from time import sleep, time
from typing import Any, Callable, Dict, List

import numpy as np
import open3d as o3d
from PIL import Image, ImageDraw, ImageFont
from pyquaternion import Quaternion

from ..fileio import read_points, write_points_pcd
from ..math import boxes_to_corners_3d, rotvec_to_rotmat
from ..math.colormap import COLORMAP_BOX, COLORMAP_JET_INT

__all__ = ['ViewerOpen3d']


class ViewerOpen3d:

    def __init__(
        self,
        lidar_points_list: List = [],
        box3d_list: List[Dict] = [],
        key_points_list: List[Dict] = [],
        external_loader_func: Callable = None
    ) -> None:
        self._visualizer = o3d.visualization.VisualizerWithKeyCallback()
        self._visualizer.create_window()
        self._visualizer.register_key_callback(ord('L'), self._go_to_next_frame)
        self._visualizer.register_key_callback(ord('K'), self._go_to_prev_frame)
        # self._visualizer.register_key_callback(ord('S'), self._save_pointcloud)

        self.lidar_points_list = {i: v for i, v in enumerate(lidar_points_list
            if isinstance(lidar_points_list, list) else [lidar_points_list])}
        self.box3d_list = {i: v for i, v in enumerate(box3d_list
            if isinstance(box3d_list, list) else [box3d_list])}
        self.key_points_list = {i: v for i, v in enumerate(key_points_list
            if isinstance(key_points_list, list) else [key_points_list])}

        self.__frame_id = 0
        self.__viewer_zoom: float = 0.48
        self.__viewer_pitch: float = 0.18
        self.__viewer_lookat: List[float] = [3, 0, -3]
        self.__coordinate: str = 'waymo'
        self.__instance: bool = False

        render_opt = self._visualizer.get_render_option()
        render_opt.background_color = np.asarray([0, 0, 0])
        render_opt.point_size = 1
        self.external_loader_func = external_loader_func

    def _go_to_next_frame(self, visualizer: Any) -> None:
        self.frame_id = 1
        if self._draw_visualizer():
            visualizer.update_renderer()
        else:
            self.frame_id = -1

    def _go_to_prev_frame(self, visualizer: Any) -> None:
        self.frame_id = -1
        if self._draw_visualizer():
            visualizer.update_renderer()
        else:
            self.frame_id = 1

    # def _save_pointcloud(self, visualizer: Any) -> None:
    #     write_points_pcd(f'{time()}.pcd', self.points, verbose=True)

    def _draw_visualizer(self) -> bool:
        """
        Draw something on the viewer panel
        """
        if self.external_loader_func is not None and \
            not self.external_loader_func(self, self.frame_id):
            return False

        self._visualizer.clear_geometries()

        ret = self._draw_points() | self._draw_bboxes3d() | self._draw_polygons()
        if not ret:
            return False

        self._draw_axis()
        self._draw_grid_lines()
        self._set_viewer()
        return True

    def _draw_points(self) -> bool:
        """
        @param points: np.ndarray (N, F) [x, y, z, intensity, ...]
        """
        if self.frame_id not in self.lidar_points_list:
            return False
        points = self.lidar_points_list[self.frame_id]

        self.points = read_points(points) if isinstance(points, (str, Path)) else np.asarray(points)
        pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(self.points[:, :3]))

        if self.points.shape[1] > 3:
            if self.instance:  # for point instance segmentation
                intensity = [COLORMAP_BOX[int(i)] for i in self.points[:, -1]]
            else:
                intensity_range = 255 if np.max(self.points[:, 3]) > 1 else 1
                truncation_max_intensiy = 0.48 * intensity_range
                point_colors = self.points[:, 3].copy()
                point_colors[self.points[:, 3] > truncation_max_intensiy] = truncation_max_intensiy
                point_colors = point_colors / truncation_max_intensiy * 255
                intensity = [COLORMAP_JET_INT[int(i)] for i in point_colors]
            pcd.colors = o3d.utility.Vector3dVector(np.array(intensity) / 255.)

        self._visualizer.add_geometry(pcd)
        return True

    def _draw_polygons(self) -> bool:
        """ Draw 3d polygons """
        if self.frame_id not in self.key_points_list:
            return False
        key_points_dict = self.key_points_list[self.frame_id]

        if hasattr(self, 'points'):
            pts_max = self.points[:, :3].max(axis=0)
            pts_min = self.points[:, :3].min(axis=0)

        for indx, polyline in enumerate(key_points_dict['key_points']):
            if hasattr(self, 'points'):
                key_points = polyline[(polyline < pts_max).all(axis=1) & \
                                      (polyline > pts_min).all(axis=1)]
            else:
                key_points = polyline[(polyline < [200, 200, 10]).all(axis=1) & \
                                      (polyline > [-200, -200, -10]).all(axis=1)]

            num_key_points = len(key_points)

            grid_lines = o3d.geometry.LineSet()
            grid_lines.points = o3d.utility.Vector3dVector(key_points)
            grid_lines.lines = o3d.utility.Vector2iVector(
                [[n, n + 1] for n in range(num_key_points - 1)] + 
                [[num_key_points - 1, num_key_points - 1]])

            line_color = key_points_dict['line_types'][indx] if 'line_types' in key_points_dict else 0
            grid_lines.colors = o3d.utility.Vector3dVector([COLORMAP_BOX[line_color]] * num_key_points)
            self._visualizer.add_geometry(grid_lines)

            if 'texts' in key_points_dict:
                for i, key_point in enumerate(key_points):
                    text_pos = key_point[:3] - [0, 0, 0.2]
                    self._put_text(str(i), text_pos)
        return True

    def _draw_bboxes3d(self) -> bool:
        """ 
        Draw 3d bounding boxes in visualization panel

        @param data_dict:
            box3d:  np.ndarray (N, 7) [cx, cy, cz, length, width, height, heading]
            labels: np.ndarray (N,)

        Array of vertices for the 3d box in following order:
              4 -------- 5
             /| \     / /|
            7 -----x-- 6 | H
            | | /     \| |
            | 0 -------- 1    Heading
            |/         |/ L  /
            3 -------- 2
                 W
        """
        if self.frame_id not in self.box3d_list:
            return False
        boxes3d_dict = self.box3d_list[self.frame_id]

        boxes3d = np.atleast_2d(boxes3d_dict['boxes3d'])
        if self.coordinate == 'kitti':
            boxes3d[:, 3:5] = boxes3d[:, [4, 3]]
            boxes3d[:, -1] = (-boxes3d[:, -1] + np.pi * 0.5) % (2 * np.pi) - np.pi

        # bbox_text = box_dict['texts'] if 'texts' in box_dict else None

        bboxes_in_vertex = boxes_to_corners_3d(boxes3d)  # N, 8, 3
        line_indx = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]

        for indx, bbox_vertex in enumerate(bboxes_in_vertex):
            _, width, height = boxes3d[indx, 3:6]
            if width <= 0 or height <= 0:
                continue

            bbox_label = boxes3d_dict['labels'][indx] if 'labels' in boxes3d_dict else -1
            colors = COLORMAP_BOX[int(bbox_label)]

            # draw bbox edges
            bbox = o3d.geometry.LineSet()
            bbox.points = o3d.utility.Vector3dVector(bbox_vertex)
            bbox.lines = o3d.utility.Vector2iVector(line_indx)

            bbox.colors = o3d.utility.Vector3dVector([colors] * len(line_indx))
            self._visualizer.add_geometry(bbox)
            # indicate box heading
            mesh = o3d.geometry.TriangleMesh.create_box(width=width, height=0.001, depth=height)
            mesh.paint_uniform_color(colors)
            mesh.translate(bbox_vertex[0])

            yaw_pi2 = boxes3d[indx, 6] - np.pi / 2
            mesh.rotate(R=rotvec_to_rotmat(yaw=yaw_pi2), center=bbox_vertex[0])
            self._visualizer.add_geometry(mesh)

            # draw text
            if 'texts' in boxes3d_dict:
                text_pos = boxes3d[indx, :3] - [0, 0, height]
                self._put_text(boxes3d_dict['texts'][indx], text_pos, [int(c * 255) for c in colors])

        return True

    def _put_text(self, text: str, text_pos: List, text_color: List = (255, 255, 255),
                  direction=(1, 0, 0), degree=180.0, font='FreeMono.ttf', font_size=100):
        """ 
        Generate a 3D text point cloud used for visualization.
        @param text: content of the text
        @param pos: 3D xyz position of the text upper left corner
        @param direction: 3D normalized direction of where the text faces
        @param degree: in plane rotation of text
        @param font: Name of the font - change it according to your system
        @param font_size: size of the font
        """
        if len(text) == 0:
            return

        font_obj = ImageFont.truetype(font, font_size)
        _, _, right, bottom = font_obj.getbbox(text)
        canvas = Image.new('RGB', (right, bottom), color=(0, 0, 0))
        ImageDraw.Draw(canvas).text((0, 0), text, font=font_obj, fill=tuple(text_color))

        canvas = np.asarray(canvas)
        background_mask = (canvas > 20).any(axis=2)

        indices = np.indices([*canvas.shape[:2], 1])[:, background_mask, 0].reshape(3, -1).T
        text_center = indices.max(axis=0) - indices.min(axis=0)
        indices[:, 1] -= text_center[1] // 2

        pcd = o3d.geometry.PointCloud()
        pcd.colors = o3d.utility.Vector3dVector(canvas[background_mask, :].astype(float) / 255.)
        pcd.points = o3d.utility.Vector3dVector(indices / 100.)

        raxis = np.cross([0.0, 0.0, 1.0], direction)
        if np.linalg.norm(raxis) < 1e-6:
            raxis = (0.0, 0.0, 1.0)
        trans = (Quaternion(axis=raxis, radians=np.arccos(direction[2])) *
                 Quaternion(axis=direction, degrees=degree)).transformation_matrix
        trans[:3, 3] = np.asarray(text_pos)
        pcd.transform(trans)
        self._visualizer.add_geometry(pcd)

    def _draw_axis(self):
        """
        Draw 3D axis indicating current coordinate
        O-X(red)-Y(green)-Z(blue)
        """
        axis_vertex = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]

        axis = o3d.geometry.LineSet()
        axis.points = o3d.utility.Vector3dVector(axis_vertex)
        axis.lines = o3d.utility.Vector2iVector([[0, 1], [0, 2], [0, 3]])
        axis.colors = o3d.utility.Vector3dVector([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

        self._visualizer.add_geometry(axis)

    def _draw_grid_lines(self, max_range: int = 200, interval: int = 20) -> None:
        """
        Draw auxiliary line by fixed distance
        """
        grid_range = np.linspace(-max_range, max_range, max_range * 2 // interval + 1)
        grid_vertex = [[gr,  max_range, 0] for gr in grid_range] + \
                      [[gr, -max_range, 0] for gr in grid_range] + \
                      [[ max_range, gr, 0] for gr in grid_range] + \
                      [[-max_range, gr, 0] for gr in grid_range]
        grid_length = len(grid_range)

        grid_lines = o3d.geometry.LineSet()
        grid_lines.points = o3d.utility.Vector3dVector(grid_vertex)
        grid_lines.lines = o3d.utility.Vector2iVector(
            [[n, n + grid_length] for n in range(grid_length)] + \
            [[n, n + grid_length] for n in range(grid_length*2, grid_length*3)])

        grid_lines.colors = o3d.utility.Vector3dVector([[0.3, 0.3, 0.3]] * grid_length * 2)
        self._visualizer.add_geometry(grid_lines)

    def _set_viewer(self):
        """
        Set viewer where to look at in the beginning
        """
        ctr = self._visualizer.get_view_control()
        ctr.set_lookat(self.lookat)

        rotation = rotvec_to_rotmat(pitch=np.pi * self.viewer_pitch)

        ctr.set_up(rotation[0])
        ctr.set_front(rotation[2])
        ctr.set_zoom(self.viewer_zoom)

    def close(self):
        self._visualizer.destroy_window()

    def show(self):
        self._draw_visualizer()
        self._visualizer.run()

    def show_all(self, capture: str = None) -> None:
        while True:
            if self._draw_visualizer():
                self._visualizer.poll_events()
                if capture is not None:
                    self.capture(capture)
                sleep(0.1)
            else:
                break

    def capture(self, fpath: str) -> None:
        savepath = Path(fpath)
        savepath.mkdir(parents=True, exist_ok=True)

        screenshot_name = '{}/{:.07f}.jpg'.format(fpath, time())
        print(f'capture:', screenshot_name)
        self._visualizer.capture_screen_image(screenshot_name)
        self.__frame_id += 1

    @property
    def frame_id(self) -> int:
        return self.__frame_id

    @frame_id.setter
    def frame_id(self, param: int) -> None:
        self.__frame_id += param

    @property
    def viewer_zoom(self) -> float:
        return self.__viewer_zoom

    @viewer_zoom.setter
    def viewer_zoom(self, param: float) -> None:
        self.__viewer_zoom = param

    @property
    def viewer_pitch(self) -> float:
        return self.__viewer_pitch

    @viewer_pitch.setter
    def viewer_pitch(self, param: float) -> None:
        self.__viewer_pitch = param

    @property
    def lookat(self):
        return self.__viewer_lookat

    @lookat.setter
    def lookat(self, param: List):
        self.__viewer_lookat = param

    @property
    def coordinate(self) -> str:
        return self.__coordinate

    @coordinate.setter
    def coordinate(self, coord: str) -> None:
        self.__coordinate = coord

    @property
    def instance(self) -> bool:
        return self.__instance

    @instance.setter
    def instance(self, boolean: bool) -> None:
        self.__instance = boolean

