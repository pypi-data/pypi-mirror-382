from typing import Dict, List

import numpy as np

from ..math import (boxes_to_corners_3d, convert_boxes, convert_points,
                    in_range_pos_neg_pi, rotation_3d_in_axis)
from ..system.logging import logger
from .pose import pose_interpolation


__all__ = ['static_compensation', 'filter_points_by_range', 'voxel_grid_filter']


def static_compensation(
    points: np.ndarray,
    poses: List[Dict],
    boxes: np.ndarray = None,
    relative_ratio: float = 0.5,
    target_timestamp: float = None,
    precision: float = 4e-3,            # best fit, don't change
) -> Dict[str, np.ndarray]:
    """
    @param poses: list of ego vehicle poses [{timestamp, translation, rotation, velo}, ...]
    @param target_stamp: compensate to this timestamp
    @param precision: minimum timestamp
    """
    if points.shape[1] < 4:
        logger.error(f'points shape[1] should > 4, but got {points.shape}')
        return

    point_timestamps = points[:, 4]
    start_timestamp = point_timestamps.min()

    # if end_timestamp - start_timestamp < 0.05 or end_timestamp - start_timestamp > 0.2:
    #     logger.error(f'abnormal points timestamp: min {start_timestamp}, max {end_timestamp}, diff {end_timestamp - start_timestamp}')
    #     return
    end_timestamp = start_timestamp + 0.1

    if target_timestamp is None:
        target_timestamp = start_timestamp + (end_timestamp - start_timestamp) * relative_ratio

    interped_poses, interped_timestamps = \
        pose_interpolation(poses, start_timestamp, end_timestamp, precision)

    if interped_poses is None:
        return

    min_indx = np.argmin(np.fabs(interped_timestamps - target_timestamp))
    target_pose = interped_poses[min_indx]

    _sector_slopes, N, M = [], len(interped_timestamps), 10000
    unit_indices = (point_timestamps - start_timestamp) / precision
    _, unique_inv = np.unique(np.round(unit_indices).astype(int), return_inverse=True)

    _compensated_points = []
    for indx in range(N):
        sliced_points = points[unique_inv == indx]
        if len(sliced_points) > 0:
            _sector_slopes.append(np.median(np.arctan2(*sliced_points[:, 1::-1].T)))
            _compensated_points.append(convert_points(sliced_points, [interped_poses[indx], target_pose]))
    compensated_points = np.vstack(_compensated_points)

    if boxes is None:
        compensated_boxes = None
    else:
        # 360 only !!
        sector_slopes = np.asarray(_sector_slopes)

        slopes_piviot = np.linspace(np.pi * 2, 0, N, endpoint=False)
        proposed_slopes = np.stack([in_range_pos_neg_pi(slopes_piviot - np.pi * 2 * i / M) for i in range(M)])

        # timestamp related slopes
        best_fit_slopes = proposed_slopes[np.median(np.fabs(np.sin(
            proposed_slopes[:, :len(sector_slopes)] / 2) - np.sin(sector_slopes / 2)), axis=1).argmin()]

        corners_points = boxes_to_corners_3d(boxes).reshape(-1, 3)
        corners_slopes = np.arctan2(*corners_points[:, 1::-1].T)
        centers_slopes = np.arctan2(*boxes[:, 1::-1].T)

        fit_slopes_corners_set = np.fabs(np.sin(corners_slopes / 2)[None] - np.sin(best_fit_slopes / 2 - np.pi / N)[:, None]).argmin(axis=0)
        fit_slopes_centers_set = np.fabs(np.sin(centers_slopes / 2)[None] - np.sin(best_fit_slopes / 2 - np.pi / N)[:, None]).argmin(axis=0)

        compensated_boxes, _compensated_corners = np.hstack([boxes, np.zeros((len(boxes), 1))]), corners_points.copy()
        for i, pose in enumerate(interped_poses):
            sliced_corners = corners_points[fit_slopes_corners_set == i]
            if len(sliced_corners) > 0:
                _compensated_corners[fit_slopes_corners_set == i] = \
                    convert_points(sliced_corners, [pose, target_pose])

            sliced_boxes = boxes[fit_slopes_centers_set == i]
            if len(sliced_boxes) > 0:
                compensated_boxes[fit_slopes_centers_set == i, 6] = \
                    convert_boxes(sliced_boxes, [pose, target_pose])[:, 6]

                compensated_boxes[fit_slopes_centers_set == i, -1] = np.round(
                    interped_timestamps[i] - precision * (
                        centers_slopes[fit_slopes_centers_set == i] - best_fit_slopes[i]
                    ) * N / (np.pi * 2), 6) * 1e6

        compensated_corners = _compensated_corners.reshape(-1, 8, 3)
        compensated_boxes[:, :3] = compensated_corners.mean(axis=1)[:, :3]

        rotated_corners = rotation_3d_in_axis(
            compensated_corners - compensated_boxes[:, None, :3], -compensated_boxes[:, 6])

        compensated_boxes[:, 3] = np.fabs(rotated_corners[:, [0, 1, 4, 5], 0] - 
                                          rotated_corners[:, [2, 3, 6, 7], 0]).mean(axis=1)
        compensated_boxes[:, 4] = np.fabs(rotated_corners[:, [0, 3, 4, 7], 1] - 
                                          rotated_corners[:, [1, 2, 5, 6], 1]).mean(axis=1)

        # [plt.plot(rotated_corners[i,:,0], rotated_corners[i,:,1],'o') for i in range(len(rotated_corners))]
        # plt.show()
        # import pdb; pdb.set_trace()

    # import matplotlib.pyplot as plt
    # plt.plot(np.arange(N), best_fit_slopes, 'o')
    # plt.plot(np.arange(N), sector_slopes, '.')
    # plt.show()
    # from common.visualization import show_o3d
    # show_o3d(points, {'boxes3d': boxes})
    # show_o3d(compensated_points, {'boxes3d': compensated_boxes})
    # import pdb; pdb.set_trace()

    return dict(
        points=compensated_points,
        pose=target_pose,
        timestamp=target_timestamp,
        boxes=compensated_boxes,
    )


def filter_points_by_range(
    points: np.ndarray,
    bev_range: List[float],
    ego_mask_range: List[float] = None,
) -> np.ndarray:
    """
    @param range: [xy-radius, x-front, z-max, z-min]
    """
    distance_mask = (points[:, 0] > bev_range[0]) & (points[:, 1] > bev_range[1]) & \
                    (points[:, 2] > bev_range[2]) & \
                    (points[:, 0] < bev_range[3]) & (points[:, 1] < bev_range[4]) & \
                    (points[:, 2] < bev_range[5])

    if ego_mask_range is not None:
        distance_mask &= (points[:, 0] < ego_mask_range[0]) | \
                         (points[:, 1] < ego_mask_range[1]) | \
                         (points[:, 0] > ego_mask_range[2]) | \
                         (points[:, 1] > ego_mask_range[3])

    return points[distance_mask], distance_mask


def voxel_grid_filter(points: np.ndarray, leaf_size: float = 0.1):
    """ """
    downsampled = np.unique(np.round(points[:, :3] / leaf_size, 0), axis=0)
    downsampled = downsampled * leaf_size + leaf_size / 2
    return downsampled
