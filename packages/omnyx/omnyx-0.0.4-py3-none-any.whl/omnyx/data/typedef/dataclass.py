from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np

from .annotation import AnnotationType, MotionState, ObjectSubType, ObjectType
from .baseclass import _dict
from .sensor import SensorName
from .vehicle import VehicleID

__all__ = ['SensorCalib', 'EgoPose', 'ObjectInfo', 'FrameInfo', 'ClipInfo']


@dataclass
class SensorCalib(_dict):
    extrinsic_matrix: np.ndarray = None
    intrinsic_matrix: np.ndarray = None
    intrinsic_matrix_scaled: np.ndarray = None
    distortion_model: str = None
    distortion: np.ndarray = None
    width: int = None
    height: int = None
    fov: float = None
    # camera_type: CameraType = None


@dataclass
class EgoPose(_dict):
    timestamp: int          # seconds

    lidar_translation: np.ndarray
    lidar_rotation: np.ndarray
    lidar_velocity: np.ndarray

    imu_translation: np.ndarray
    imu_rotation: np.ndarray
    imu_velocity: np.ndarray

    ego_translation: np.ndarray     # array(3,)
    ego_rotation: np.ndarray        # array(3, 3)
    ego_velocity: np.ndarray        # array(3,)


@dataclass
class ObjectInfo(_dict):
    camera_box2d: np.ndarray = None         # [left, top, right, bottom] N, 4
    undistorted_box2d: np.ndarray = None    # [left, top, right, bottom] N, 4

    camera_box3d: np.ndarray = None         # compensated to camera timestamp
    camera_type: ObjectSubType = None
    camera_feature: np.ndarray = None
    camera_confidence: float = None

    occlusion: float = None
    truncation: bool = None
    iou: float = None                   # projected 3d box ^ 2d box

    lidar_box3d: np.ndarray = None      # [cx, cy, cz, length, width, height, yaw]
    lidar_type: ObjectSubType = None
    lidar_confidence: float = None
    lidar_velo: np.ndarray = None       # [vx, vy]
    lidar_pts_count: int = None
    lidar_pts: np.ndarray = None        # foreground points
    debug_info: dict = None

    obj_type: ObjectType = None
    obj_subtype: ObjectSubType = None
    timestamp: int = None               # object's microseconds

    track_id: int = None
    frame_id: int = None                # same as FrameInfo.lidar_timestamp
    motion_state: MotionState = None

    lane_id: List[int] = None
    cross_lane: str = None

    signal: str = None
    group_id: int = None
    is_group: bool = False
    is_cyclist: bool = None
    is_fake: bool = False


@dataclass
class FrameInfo(_dict):
    clip_name: str = None
    frame_name: str = None
    token: str = None

    camera_timestamp: int = None        # microseconds
    lidar_timestamp: int = None         # microseconds (frame id)

    sensor_timestamps: Dict = None      # microseconds of each sensor
    sensor_filepaths: Dict = None

    lidar2utm: np.ndarray = None
    ego2utm: np.ndarray = None

    lidar2slam: np.ndarray = None
    ego2slam: np.ndarray = None

    lidar_velo: np.ndarray = None
    ego_velo: np.ndarray = None

    objects: Dict = None

    def _objects_attr(self, sensor_name: SensorName, attr: str, dim: int = 1) -> np.ndarray:
        if sensor_name in self.objects:
            attributes = np.asarray([getattr(obj, attr)
                for obj in self.objects[sensor_name] if getattr(obj, attr) is not None])
            if len(attributes) > 0:
                return attributes
        return np.zeros((0, dim)) if dim > 1 else np.zeros(0)

    def lidar_boxes3d(self, lidar_name: SensorName) -> np.ndarray:
        return self._objects_attr(lidar_name, 'lidar_box3d', 7)

    def lidar_velos3d(self, lidar_name: SensorName) -> np.ndarray:
        return self._objects_attr(lidar_name, 'lidar_velo', 3)

    def lidar_confidences(self, lidar_name: SensorName) -> np.ndarray:
        return self._objects_attr(lidar_name, 'lidar_confidence')

    def lidar_types(self, lidar_name: SensorName) -> np.ndarray:
        return np.asarray([obj_type for obj_type in self._objects_attr(lidar_name, 'lidar_type')])

    def camera_boxes2d(self, camera_name: SensorName) -> np.ndarray:
        return self._objects_attr(camera_name, 'camera_box2d', 4)

    def camera_boxes3d(self, camera_name: SensorName) -> np.ndarray:
        return self._objects_attr(camera_name, 'camera_box3d', 7)

    def camera_confidences(self, camera_name: SensorName) -> np.ndarray:
        return self._objects_attr(camera_name, 'camera_confidence')

    def camera_types(self, camera_name: SensorName) -> np.ndarray:
        return np.asarray([obj_type for obj_type in self._objects_attr(camera_name, 'camera_type')])

    def track_ids(self, sensor_name: SensorName) -> np.ndarray:
        return self._objects_attr(sensor_name, 'track_id')

    def obj_types(self, sensor_name: SensorName) -> np.ndarray:
        return self._objects_attr(sensor_name, 'obj_type')

    def obj_subtypes(self, sensor_name: SensorName) -> np.ndarray:
        return self._objects_attr(sensor_name, 'obj_subtype')


@dataclass
class ClipInfo(_dict):
    vehicle_id: VehicleID = None
    weather: str = None
    scene: str = None               # highway, urban, etc.
    bag_name: str = None

    anno_type: AnnotationType = None

    clip_id: str = None             # uuid
    clip_name: str = None
    clip_path: str = None           # local path
    obs_path: str = None            # server path
    collect_time: int = None        # microseconds

    calibrations: Dict[SensorName, SensorCalib] = None
    frames: Dict[int, FrameInfo] = None

    poses: List[EgoPose] = None
    slam_poses: List[EgoPose] = None

    reference_lidar_pose: np.ndarray = None
    reference_ego_pose: np.ndarray = None

    lidar_slam_path: Path = None
