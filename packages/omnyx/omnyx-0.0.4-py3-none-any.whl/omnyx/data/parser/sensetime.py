import json
from pathlib import Path
from typing import Dict

import numpy as np

from ...fileio import check_filepath, read_text
from ...system import multi_process_thread
from ..typedef import *


def get_sensetime_info(
    clip_path: str,
    anno_path: str,
    calibrations: Dict[SensorName, SensorCalib] = None,
) -> ClipInfo:
    _clip_path: Path = check_filepath(clip_path)

    def _fill_obj_anno_frame(_annotation_info_raw: str) -> FrameInfo:
        _annotation_info = json.loads(_annotation_info_raw)

        object_infos = defaultdict(list)
        object_infos[MAIN_SENSOR_LIDAR] = [ObjectInfo(
            lidar_box3d=_obj['bbox3d'][:6] + _obj['bbox3d'][8:],
            lidar_velo=_obj['velocity'],
            lidar_pts_count=_obj['num_lidar_pts'],
            obj_subtype=ObjectSubType[SensetimeType[_obj['label']].name],
            obj_type=SUBTYPE_TO_TYPE[ObjectSubType[SensetimeType[_obj['label']].name]],
            track_id=_obj['id'],
            motion_state=MotionState[_obj['motion_state']],
        ) for _obj in _annotation_info['Objects']]

        [object_infos[SensorName[SensetimeSensorName[camera_name]]].append(
            ObjectInfo(camera_box2d=camera_obj['bbox2d'],
                       camera_box3d=_obj['bbox3d'][:6] + _obj['bbox3d'][8:],
                       obj_subtype=ObjectSubType[SensetimeType[_obj['label']].name],
                       obj_type=SUBTYPE_TO_TYPE[ObjectSubType[SensetimeType[_obj['label']].name]],
                       track_id=_obj['id'],
        )) for _obj in _annotation_info['Objects']
        for camera_name, camera_obj in _obj['info2d'].items() if \
            ObjectSubType[SensetimeType[_obj['label']].name] not in MOVABLE_BICYCLE or \
            (ObjectSubType[SensetimeType[_obj['label']].name] in MOVABLE_BICYCLE and \
             _obj.get('is_cyclist') == True)]

        return FrameInfo(
            frame_name=_annotation_info['timestamp'] * 1e3,
            lidar_timestamp=_annotation_info['timestamp'] * 1e3,
            ego2slam=np.asarray(_annotation_info['ego2global_transformation_matrix']),
            ego_velo=_annotation_info['ego_velocity'],
            sensor_timestamps=dict(**{
                SensorName[SensetimeSensorName[camera_name]]: camera_info['timestamp'] * 1e3
                for camera_name, camera_info in _annotation_info['sensors']['cameras'].items()
            }, **{MAIN_SENSOR_LIDAR: _annotation_info['sensors']['lidar']['car_center']['timestamp']}),
            sensor_filepaths=dict(**{
                SensorName[SensetimeSensorName[camera_name]]:
                _clip_path / camera_info['data_path'].split(_clip_path.name)[-1]
                for camera_name, camera_info in _annotation_info['sensors']['cameras'].items()
            }, **{MAIN_SENSOR_LIDAR:
                _clip_path / _annotation_info['sensors']['lidar']['car_center']['data_path'].split(_clip_path.name)[-1]
            }),
            objects=object_infos,
        )

    anno_info_raw = read_text(anno_path)
    sensors_info = json.loads(anno_info_raw[0])['sensors']
    annotation_info = ClipInfo(
        clip_name=_clip_path.stem,
        calibrations={
            SensorName[SensetimeSensorName[camera_name]]: SensorCalib(
                extrinsic_matrix=np.asarray(camera_calib['extrinsic']),
                intrinsic_matrix=np.asarray(camera_calib['camera_intrinsic']),
                distortion=np.asarray(camera_calib['camera_dist']).flatten(),
                distortion_model='fisheye' if len(camera_calib['camera_dist']) > 0 else 'pinhole',
                fov=calibrations[SensorName[SensetimeSensorName[camera_name]]].fov,
                width=calibrations[SensorName[SensetimeSensorName[camera_name]]].width,
                height=calibrations[SensorName[SensetimeSensorName[camera_name]]].height,
            ) for camera_name, camera_calib in sensors_info['cameras'].items()
        }
    )
    annotation_info.calibrations[MAIN_SENSOR_LIDAR] = calibrations[MAIN_SENSOR_LIDAR]

    frames_info = multi_process_thread(
        _fill_obj_anno_frame, anno_info_raw, nprocess=4,
            pool_func='ThreadPoolExecutor', map_func='map', progress_bar=False)

    annotation_info.frames = {info['lidar_timestamp']: info for info in
        sorted(frames_info, key=lambda frame: frame['lidar_timestamp'])}

    return annotation_info

