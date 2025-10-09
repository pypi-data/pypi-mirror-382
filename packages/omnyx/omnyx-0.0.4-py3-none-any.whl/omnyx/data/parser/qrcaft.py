from collections import defaultdict
from pathlib import Path
from typing import Dict

import numpy as np

from ...fileio import check_filepath, lsdir, read_json, read_text
from ...math import rotvec_to_rotmat, transform_matrix
from ...sensor import calculate_camera_fov
from ...system import multi_process_thread
from ..typedef import *

__all__ = ['get_qcraft_info']


subtype_mapping = {
    'CAR': ObjectSubType.car,
    'POLE': ObjectSubType.warning_post,
    'PED': ObjectSubType.person,
    'BICYCLIST': ObjectSubType.bicycle,
    'TRICYCLIST': ObjectSubType.tricycle,
    'ROAD_BARRIER': ObjectSubType.barrier,
}


def get_qcraft_info(
    clip_path: str,
    **whatever: Dict,
):
    _clip_path: Path = check_filepath(clip_path)

    filelist = read_text(_clip_path / 'FILELIST')
    calib_params = read_json(_clip_path / 'params/vehicle_params.json')
    lidar_timestamps = read_json(_clip_path / 'timestamp/lidar_timestamp.json')
    camera_timestamps = read_json(_clip_path / 'timestamp/image_timestamp.json')

    annotation_info = ClipInfo(
        clip_name=_clip_path.stem,
        calibrations={},
    )

    lidar_calibs = {calib_info['installation']['lidar_id']: calib_info
        for calib_info in calib_params['lidars']}
    lidar_list = np.unique([filepath.rsplit('/', 1)[0].replace('lidar/', '')
        for filepath in filelist if filepath.startswith('lidar/')])
    for lidar_name in lidar_list:
        extrinsics = lidar_calibs[lidar_name]['installation']['extrinsics']
        annotation_info.calibrations[SensorName[lidar_name]] = SensorCalib(
            extrinsic_matrix=transform_matrix([
                extrinsics['x'], extrinsics['y'], extrinsics['z']],
                rotvec_to_rotmat(extrinsics['roll'], extrinsics['pitch'], extrinsics['yaw'])
            ),
        )

    camera_calibs = {calib_info['installation']['camera_id']: calib_info
        for calib_info in calib_params['cameras']}
    image_list = np.unique([filepath.rsplit('/', 2)[0].replace('image/', '')
        for filepath in filelist if filepath.startswith('image/')])
    for camera_name in image_list:
        if camera_name not in camera_calibs:
            continue
        extrinsics = camera_calibs[camera_name]['installation']['camera_to_vehicle_extrinsics']
        intrinsics = camera_calibs[camera_name]['inherent']['intrinsics']['camera_matrix']
        distortion = camera_calibs[camera_name]['inherent']['intrinsics']['distort_coeffs']

        if distortion.get('p1', 0) == 0 and distortion.get('p2', 0) == 0 and \
           distortion.get('k5', 0) == 0 and distortion.get('k6', 0) == 0:
            distortion_model = 'fisheye'
            distort_coeffs = np.asarray([distortion[k] for k in ['k1', 'k2', 'k3', 'k4']])
        else:
            distortion_model = 'pinhole'
            distort_coeffs = np.asarray([distortion[k] for k in ['k1', 'k2', 'p1', 'p2', 'k3', 'k4', 'k5', 'k6']])

        rot = transform_matrix(rotation=rotvec_to_rotmat(yaw=np.pi / 2)) @ transform_matrix(rotation=rotvec_to_rotmat(pitch=-np.pi / 2))

        annotation_info.calibrations[SensorName[camera_name]] = SensorCalib(
            extrinsic_matrix=rot @ np.linalg.inv(transform_matrix([
                extrinsics['x'], extrinsics['y'], extrinsics['z']],
                rotvec_to_rotmat(extrinsics['roll'], extrinsics['pitch'], extrinsics['yaw']))
            ),
            intrinsic_matrix=np.asarray([[intrinsics['fx'], 0, intrinsics['cx']],
                                         [0, intrinsics['fy'], intrinsics['cy']],
                                         [0, 0, 1]], dtype=float),
            intrinsic_matrix_scaled=np.asarray([[intrinsics['fx'], 0, intrinsics['cx']],
                                         [0, intrinsics['fy'], intrinsics['cy']],
                                         [0, 0, 1]], dtype=float),
            distortion=distort_coeffs,
            distortion_model=distortion_model,
            width=camera_calibs[camera_name]['common']['width'],
            height=camera_calibs[camera_name]['common']['height'],
        )
        annotation_info.calibrations[SensorName[camera_name]].update(
            fov=calculate_camera_fov(annotation_info.calibrations[SensorName[camera_name]])
        )

    def _fill_obj_anno_frame(frame_id: Path):
        object_infos = defaultdict(list)

        frame_name = frame_id.stem
        lidar_anno_info = read_json(_clip_path / 'label/lidar_label' / f'{frame_name}.json')
        # camera_anno_info = read_json(_clip_path / 'label/image_label' / f'{frame_name}.json')

        object_infos[CHERY_MAIN_SENSOR_LIDAR].extend([
            ObjectInfo(
                lidar_box3d=np.asarray([
                    obj_info['x'], obj_info['y'], obj_info['z'],
                    obj_info['length'], obj_info['width'], obj_info['height'],
                    obj_info['heading'],
                ], dtype=float),
                obj_subtype=subtype_mapping[obj_info['category']],
                obj_type=OBJECT_SUBTYPE_TO_TYPE[subtype_mapping[obj_info['category']]],
                track_id=obj_info['object_id'],
            ) for obj_info in lidar_anno_info['labels']
        ])

        return FrameInfo(
            frame_name=frame_name,
            lidar_timestamp=lidar_timestamps[lidar_list[0]][int(frame_name)]['timestamp'],
            sensor_timestamps=dict(
                **{SensorName[camera_name]: camera_timestamps[camera_name][int(frame_name)]['timestamp']
                    for camera_name in image_list if SensorName[camera_name] is not None and camera_name in camera_timestamps
                },
                **{SensorName[lidar_name]: lidar_timestamps[lidar_name][int(frame_name)]['timestamp']
                    for lidar_name in lidar_list
                }),
            sensor_filepaths=dict(
                **{SensorName[camera_name]: _clip_path / 'image' / camera_name / f'raw_image/{frame_name}.jpg'
                    for camera_name in image_list if SensorName[camera_name] is not None
                },
                **{SensorName[lidar_name]: _clip_path / 'lidar' / lidar_name / f'{frame_name}.pcd'
                    for lidar_name in lidar_list if SensorName[lidar_name] is not None
                }),
            objects=object_infos,
        )

    main_lidar_anno_list = lsdir(_clip_path / 'lidar' / lidar_list[0])
    frames_info = multi_process_thread(
        _fill_obj_anno_frame, main_lidar_anno_list, nprocess=1,
        pool_func='ThreadPoolExecutor', map_func='map', progress_bar=False)

    annotation_info.frames = {info['lidar_timestamp']: info for info in
        sorted(frames_info, key=lambda frame: frame['lidar_timestamp'])}

    return annotation_info
