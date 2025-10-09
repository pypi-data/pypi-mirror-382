from typing import Callable, Dict, List

import cv2
import matplotlib.pyplot as plt
import numpy as np

from ..data import *
from ..fileio import read_image
from ..sensor import (boxes3d_to_camera2d, resize_image, undistort_image,
                      undistort_points)
from .render import draw_instances_2d, draw_texts
from .viewer_bev import ViewerBev
from .viewer_o3d import ViewerOpen3d

__all__ = ['show_o3d', 'show_bev', 'show_img', 'show_bev_with_camera']


def show_o3d(
    points: List = [],
    boxes_info: List = [],
    polygons_info: List = [],
    zoom: float = 0.36,
    pitch: float = 0.18,
    lookat: List = [3, 0, -3],
    instance: bool = False,
    show_all: bool = False,
    capture: str = None,
    coordinate: str = 'waymo',
    loader_func: Callable = None
) -> None:
    viewer = ViewerOpen3d(points, boxes_info, polygons_info,
                          external_loader_func=loader_func)

    viewer.coordinate = coordinate
    viewer.viewer_zoom = zoom
    viewer.viewer_pitch = pitch
    viewer.lookat = lookat
    viewer.instance = instance

    viewer.show_all(capture) if show_all else viewer.show()
    viewer.close()


def show_bev(
    points: List = [],
    boxes_info: List = [],
    polygons_info: List = [],
    preview_width: int = 3200,
    preview_height: int = None,
    bev_range_front: int = 160,
    bev_range_back: int = 80,
    bev_range_width: int = 100,
    flip: bool = False,
    return_image: bool = False,
    save: str = None,
):
    viewer = ViewerBev(points, boxes_info, polygons_info)
    if preview_width is None:
        viewer.preview_height = preview_height
    elif preview_height is None:
        viewer.preview_width = preview_width
    else:
        raise ValueError('width or height has to be none')

    viewer.bev_range_front = bev_range_front
    viewer.bev_range_back = bev_range_back
    viewer.bev_range_width = bev_range_width
    viewer.flip = flip

    if save is not None:
        viewer.save(save)
    elif return_image:
        return viewer.image
    else:
        return viewer.show()


def show_bev_with_camera(
    clip_name: str,
    frame_info: FrameInfo,
    calibration: SensorCalib,
    boxes_info: Dict[str, np.ndarray] = None,
    polygons_info: Dict[str, np.ndarray] = None,
    main_lidar: str = CHERY_MAIN_SENSOR_LIDAR,
    camera_names: Dict[str, SensorName] = CHERY_SENSOR_TYPE_CAMERA_MAPPING,
    undistort: bool = False,
    # undistort_boxes2d: bool = False,
    # undistort_boxes3d: bool = False,
    flip_horizontal: bool = False,
    bev_range_front: int = 160,
    bev_range_back: int = 80,
    bev_range_width: int = 100,
    W: int = 600,
    H: int = 360,
):
    """
    @param boxes_info:
        boxes3d ndarray (N, 7)
        texts (N,)
    @param polygons_info:
        key_points (N-lane, (M-keypoints, 2))
        line_types (N,)
    """
    if boxes_info is None:
        boxes_info = dict()

    preview = dict()
    for camera_name, camera_type in camera_names.items():
        camera_frame_path = frame_info.sensor_filepaths.get(camera_type)
        if camera_frame_path is None:
            preview[camera_name] = np.zeros((H, W, 3), dtype=np.uint8)
            continue

        boxes2d, boxes_text2d, boxes_label2d, non_zeros = None, None, None, None
        if 'boxes2d' in boxes_info and camera_type in boxes_info['boxes2d']:
            boxes2d = boxes_info['boxes2d'][camera_type]
            non_zeros = boxes2d.sum(axis=1) != 0
            boxes2d = boxes2d[non_zeros]

            if 'texts2d' in boxes_info and camera_type in boxes_info['texts2d']:
                boxes_text2d = [t for t, b in zip(boxes_info['texts2d'][camera_type], non_zeros) if b]
            if 'labels2d' in boxes_info and camera_type in boxes_info['labels2d']:
                boxes_label2d = [l for l, b in zip(boxes_info['labels2d'][camera_type], non_zeros) if b]

        edges3d, boxes_label3d = None, None
        if 'edges3d' in boxes_info:
            edges3d = boxes_info['edges3d'].get(camera_type)
            if 'labels3d' in boxes_info and camera_type in boxes_info['labels3d']:
                boxes_label3d = boxes_info['labels3d'][camera_type]

        elif 'boxes3d' in boxes_info:
            projections = boxes3d_to_camera2d(boxes_info['boxes3d'], calibration[camera_type])
            edges3d = projections['edges2d']
            if 'labels3d' in boxes_info:
                boxes_label3d = boxes_info['labels3d'][projections['mask_in_image']]

        image = read_image(camera_frame_path)
        # if undistort and camera_name not in SENSOR_TYPE_CAMERA_OMNI:
        #     image = undistort_image(image, calibration[camera_name])

        # if undistort_boxes2d and camera_name not in SENSOR_TYPE_CAMERA_OMNI:
        #     if boxes2d is not None:
        #         boxes2d = undistort_points(boxes2d, calibration[camera_name])

        # if undistort_boxes3d and camera_name not in SENSOR_TYPE_CAMERA_OMNI:
        if edges3d is not None:
            edges3d[..., :2] = undistort_points(edges3d[..., :2], calibration[camera_type])

        preview[camera_name] = resize_image(
            draw_instances_2d(image=image, edges3d=edges3d, labels3d=boxes_label3d,
                              boxes2d=boxes2d, labels2d=boxes_label2d, texts=boxes_text2d,
            # flip_horizontal=(camera_name in SENSOR_TYPE_CAMERA_REAR_VIEW) if flip_horizontal else False,
        ), (W, H))

        timestamp_sec = frame_info.sensor_timestamps[camera_type] * 1e-6
        draw_texts(preview[camera_name],
            [f'{SENSOR_TYPE_CAMERA_NAME_SHORT[camera_type]} {timestamp_sec - timestamp_sec // 1e4 * 1e4:.6f}'],
            [(W // 30, H // 12)], color=[0, 0, 255], fontscale=1.2, thickness=2)

    whiteboard = np.zeros((H, W, 3), dtype=np.uint8)
    draw_texts(whiteboard,
               [f'{clip_name}'],
               [(0, H // 14)], color=[0, 0, 255], fontscale=1, thickness=2)
    draw_texts(whiteboard,
               [f'{frame_info.frame_name}'],
               [(0, H // 14 * 2)], color=[0, 0, 255], fontscale=1, thickness=2)

    for i in range(len(ObjectType)):
        draw_texts(whiteboard, [ObjectType[i].name], [(0, H // 14 * (i + 4))],
                   color=ObjectType[i].value, fontscale=1, thickness=2)

    concat_camera_prime = np.concatenate([
        np.concatenate([whiteboard,
                        preview.pop('camera_front_center_tele')], axis=1),
        np.concatenate([preview.pop('camera_rear_center'),
                        preview.pop('camera_front_center')], axis=1),
        np.concatenate([preview.pop('camera_rear_left'),
                        preview.pop('camera_front_left')], axis=1),
        np.concatenate([preview.pop('camera_front_right'),
                        preview.pop('camera_rear_right')], axis=1),
    ], axis=0)

    concat_camera_omni = np.concatenate([
        preview.pop('camera_omni_front'),
        preview.pop('camera_omni_left'),
        preview.pop('camera_omni_right'),
        preview.pop('camera_omni_rear'),
    ], axis=0)

    bev_points_image = show_bev(frame_info.sensor_filepaths.get(main_lidar),
        boxes_info, polygons_info, flip=True, return_image=True,
        bev_range_front=bev_range_front, bev_range_back=bev_range_back, bev_range_width=bev_range_width,
        preview_width=concat_camera_prime.shape[0])

    return np.concatenate([concat_camera_prime,
                           bev_points_image,
                           concat_camera_omni], axis=1)


def show_img(
    image: np.ndarray,
    bgr2rgb: bool = False
):
    if bgr2rgb:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.imshow(image)
    plt.show()