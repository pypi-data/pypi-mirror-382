from typing import Dict, List, Tuple

import numpy as np

from ..math.geometry import rotations_slerp
from ..system.logging import logger

__all__ = ['pose_interpolation']


def pose_interpolation(
    poses: List[Dict],
    ts_start: float,
    ts_end: float,
    precision: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    @param poses: list of pose dict [{timestamp, transform-matrix, ...}, ...]
    @param [start, stop]: interpolate timestamp range
    @param precision: poses timestamp precision [power of 10]
    """
    if poses[0]['timestamp'] - precision > ts_start or \
           poses[-1]['timestamp'] + precision < ts_end:
        logger.error(f'could not find pose[{poses[0]["timestamp"]}, {poses[-1]["timestamp"]}] '\
                     f'within timestamp range [{ts_start}, {ts_end}, {precision}]')
        return None, None

    # find poses within the range
    key_indices = np.asarray([i for i, pose in enumerate(poses)
        if ts_start - precision - 1e-6 < pose['timestamp'] < ts_end + precision + 1e-6])

    key_timestamps = np.asarray([int(poses[i]['timestamp'] / precision) for i in key_indices])
    # if precision not enough, key_stamps will have dupicates
    non_dup_key_timestamps, non_dup_indices = np.unique(key_timestamps, return_index=True)
    non_dup_key_indices = key_indices[non_dup_indices]

    timestamps_interped = np.arange(non_dup_key_timestamps[0], non_dup_key_timestamps[-1])

    key_translations = np.array([poses[ind]['lidar_translation'] for ind in non_dup_key_indices])
    key_rotations = np.array([poses[ind]['lidar_rotation'] for ind in non_dup_key_indices])

    interped_translations = np.vstack(
        [np.interp(timestamps_interped, key_timestamps, trans)
         for trans in key_translations.T]).T

    interped_rotations = rotations_slerp(timestamps_interped, key_timestamps, key_rotations)

    timestamps_interped_sec = timestamps_interped * precision
    # ts_in_range_mask = (timestamps_interped_sec > ts_start - precision) & \
    #                    (timestamps_interped_sec < ts_end + precision)

    interp_poses = np.asarray([np.eye(4)] * len(timestamps_interped_sec))
    interp_poses[:, :3, 3] = interped_translations
    interp_poses[:, :3, :3] = interped_rotations

    return interp_poses, timestamps_interped_sec
