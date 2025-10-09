from functools import partial
from os import environ
from pathlib import Path
from re import compile
from shutil import copyfile
from typing import Dict, List, Tuple

import numpy as np

from ...fileio import check_filepath, lsdir, read_json, write_json
from ...math import *
from ...sensor import calculate_camera_fov
from ...system import logger, multi_process_thread, timestamp_to_time_of_date
from ..rules import pose_sanity_check
from ..typedef import *

__all__ = ['get_chery_info']

CHERY_SENSOR_CALIB_EXTRINSICS = {
    SensorName.chery_camera_front_center: ['extrinsics/lidar2camera', 'lidar2frontwide'],
    SensorName.chery_camera_front_center_tele: ['extrinsics/lidar2camera', 'lidar2frontmain'],
    SensorName.chery_camera_front_left: ['extrinsics/lidar2camera', 'lidar2leftfront'],
    SensorName.chery_camera_front_right: ['extrinsics/lidar2camera', 'lidar2rightfront'],
    SensorName.chery_camera_rear_left: ['extrinsics/lidar2camera', 'lidar2leftrear'],
    SensorName.chery_camera_rear_right: ['extrinsics/lidar2camera', 'lidar2rightrear'],
    SensorName.chery_camera_rear_center: ['extrinsics/lidar2camera', 'lidar2rearmain'],
    SensorName.chery_camera_omni_left: ['extrinsics/lidar2camera', 'lidar2fisheyeleft'],
    SensorName.chery_camera_omni_rear: ['extrinsics/lidar2camera', 'lidar2fisheyerear'],
    SensorName.chery_camera_omni_front: ['extrinsics/lidar2camera', 'lidar2fisheyefront'],
    SensorName.chery_camera_omni_right: ['extrinsics/lidar2camera', 'lidar2fisheyeright'],
    SensorName.chery_lidar_top: ['extrinsics/lidar2imu', 'lidar2imu'],
    SensorName.chery_lidar_left_blind: ['extrinsics/lidar2lidar', 'left2mainlidar'],
    SensorName.chery_lidar_front_blind: ['extrinsics/lidar2lidar', 'front2mainlidar'],
    SensorName.chery_lidar_right_blind: ['extrinsics/lidar2lidar', 'right2mainlidar'],
    SensorName.chery_lidar_rear_blind: ['extrinsics/lidar2lidar', 'rear2mainlidar'],
}

CHERY_SENSOR_CALIB_INTRINSICS = {
    SensorName.chery_camera_front_center: ['intrinsics', 'front_wide_camera'],
    SensorName.chery_camera_front_center_tele: ['intrinsics', 'front_main_camera'],
    SensorName.chery_camera_front_left: ['intrinsics', 'left_front_camera'],
    SensorName.chery_camera_front_right: ['intrinsics', 'right_front_camera'],
    SensorName.chery_camera_rear_left: ['intrinsics', 'left_rear_camera'],
    SensorName.chery_camera_rear_right: ['intrinsics', 'right_rear_camera'],
    SensorName.chery_camera_rear_center: ['intrinsics', 'rear_main_camera'],
    SensorName.chery_camera_omni_left: ['intrinsics', 'fisheye_left_camera'],
    SensorName.chery_camera_omni_rear: ['intrinsics', 'fisheye_rear_camera'],
    SensorName.chery_camera_omni_front: ['intrinsics', 'fisheye_front_camera'],
    SensorName.chery_camera_omni_right: ['intrinsics', 'fisheye_right_camera'],
}


def parse_3d_od_anno_info(anno_dict: Dict, info_prefix: str) -> List:
    return dict(
        lidar0=anno_dict['annotated_info']\
                        [info_prefix]\
                        ['annotated_info']\
                        ['3d_object_detection_info']\
                        ['3d_object_detection_anns_info'])


def parse_3d_gop_anno_info(anno_dict: Dict) -> List:
    return dict(
        lidar0=anno_dict['annotated_record_info']\
                        ['annotated_info']\
                        ['3d_object_detection_info']\
                        ['3d_object_detection_anns_info'])


def parse_23d_od_anno_info(anno_dict: Dict) -> List:
    return dict(
        lidar0=anno_dict['annotated_info']\
                       ['3d_object_annotated_info']\
                       ['annotated_info']\
                       ['3d_object_detection_info']\
                       ['3d_object_detection_anns_info'],
        **anno_dict['annotated_info']\
                   ['2d_object_annotated_info']\
                   ['annotated_info'])


def parse_interped_od_anno_info(anno_dict: Dict) -> List:
    return dict(
        lidar0=anno_dict['annotated_info']\
                       ['3d_city_object_detection_annotated_info']\
                       ['annotated_info']\
                       ['3d_object_detection_info']\
                       ['3d_object_detection_anns_info'],
        **{k: v['objects'] for k, v in anno_dict['annotated_info']\
                   ['2d_city_object_detection_annotated_info']\
                   ['annotated_info'].items()})


def parse_3d_lane_anno_info(anno_dict: Dict) -> List:
    if 'annotated_info' in anno_dict:
        if '3d_lane_annotated_info' in anno_dict['annotated_info']:
            return anno_dict['annotated_info']['3d_lane_annotated_info']['annotated_info']['lines']
        elif '3d_lane_clip_annotated_info' in anno_dict['annotated_info']:
            return anno_dict['annotated_info']['3d_lane_clip_annotated_info']['annotated_info']['lines']
        else:
            return anno_dict['annotated_info']['lines']
    elif 'annotated_record_info' in anno_dict:
        return anno_dict['annotated_record_info']['annotated_info']['lines']
    else:
        return []


ANNOTATION_INFO = {
    'ROBO_HIGHWAY_OD_23D': parse_23d_od_anno_info,

    'ROBO_URBAN_OD_3D': partial(parse_3d_od_anno_info, info_prefix='only_3d_city_object_detection_annotated_info'),
    'ROBO_HIGHWAY_OD_3D': partial(parse_3d_od_anno_info, info_prefix='3d_object_detection_annotated_info'),

    'HNOA_URBAN_OD_3D': partial(parse_3d_od_anno_info, info_prefix='3d_city_object_detection_with_fish_eye_annotated_info'),
    'HNOA_HIGHWAY_OD_3D': partial(parse_3d_od_anno_info, info_prefix='3d_highway_object_detection_with_fish_eye_annotated_info'),
    'HNOA_PARKING_OD_3D': partial(parse_3d_od_anno_info, info_prefix='parking_movable_object_detection_annotated_info'),

    'HNOA_GOP_OD_3D': partial(parse_3d_od_anno_info, info_prefix='gop_object_detection_clip_annotated_info'),
    'HNOA_URBAN_GOP_3D': parse_3d_gop_anno_info,
    'HNOA_PARKING_GOP_3D': parse_3d_gop_anno_info,

    'HNOA_TRAFFIC_SIGN': partial(parse_3d_od_anno_info, info_prefix='3d_traffic_sign_clip_annotated_info'),

    'LANE_KEY_POINTS_3D': parse_3d_lane_anno_info,
    'LANE_KEY_POINTS_4D': parse_3d_lane_anno_info,

    'INTERPOLATED_PVB': parse_interped_od_anno_info,
    'REPROJECTED_GOP': parse_interped_od_anno_info,
}

ANNOTATION_TYPE: Dict[str, List[AnnotationType]] = {
    'PVB': [
        AnnotationType.HNOA_URBAN_OD_3D,
        AnnotationType.HNOA_HIGHWAY_OD_3D,
        AnnotationType.HNOA_PARKING_OD_3D,

        AnnotationType.TAXI_HIGHWAY_OD_23D,
        AnnotationType.TAXI_URBAN_OD_3D,
        AnnotationType.TAXI_HIGHWAY_OD_3D,
    ],
    'GOP': [
        AnnotationType.HNOA_URBAN_GOP_3D,
        AnnotationType.HNOA_PARKING_GOP_3D,
        AnnotationType.HNOA_GOP_OD_3D,
    ],
    'LANE3D': [
        AnnotationType.LANE_KEY_POINTS_3D,
        AnnotationType.LANE_KEY_POINTS_4D,
    ]
}

ANNOTATION_ID = {
    AnnotationType.HNOA_URBAN_OD_3D: 15,
    AnnotationType.HNOA_HIGHWAY_OD_3D: 16,
    AnnotationType.HNOA_PARKING_OD_3D: 17,

    AnnotationType.TAXI_HIGHWAY_OD_23D: 3,
    AnnotationType.TAXI_URBAN_OD_3D: 9,
    AnnotationType.TAXI_HIGHWAY_OD_3D: 10,

    AnnotationType.HNOA_GOP_OD_3D: 23,
    AnnotationType.HNOA_URBAN_GOP_3D: 33,
    AnnotationType.HNOA_PARKING_GOP_3D: 36,

    AnnotationType.LANE_KEY_POINTS_3D: 2,
    AnnotationType.LANE_KEY_POINTS_4D: 18,
}


class CheryParamParser:

    def __init__(
        self,
        clip_root: Path,
        output_path: Path = None,
        search_global: bool = False,
        calib_root: Path = '/opt/calibrations',
        collect_time: int = 0, # microseconds
        plate_no: str = '',
        **whatever,
    ):
        """
        @param clip_root: path to clip
        @param output_path: path to output
        @param seach_global: whether to use calib params at calib_root
        @param calib_root: path to calibration files
        @param collect_time: collect time of clip
        @param plate_no: plate number of vehicle
        """
        self.clip_root = clip_root
        self.output_path = output_path

        self.collect_time = int(timestamp_to_time_of_date(collect_time * 1e-6, '%Y%m%d%H%M%S'))
        self.plate_no = compile(r'[\u4e00-\u9fa5]').sub('', plate_no)
        self.search_global = search_global
        self.get_clip_info_status()
        logger.debug(f'plate_no {self.plate_no}, collect_time {self.collect_time}')

        self.calib_root = check_filepath(calib_root, strict=True)
        if search_global:
            logger.debug(f'search calibration files from {calib_root}')

    def get_clip_info_status(self):
        """
        get vehicle id & imu height
        """
        self.vehicle_id = VehicleID[self.plate_no]

        if self.vehicle_id is None:
            raise NotImplementedError(f'vehicle id {self.plate_no} not registered')

        imu_height = CHERY_SENSOR_IMU_HEIGHT.get(self.vehicle_id)
        if imu_height is None:
            raise NotImplementedError(f'imu height {self.plate_no} not registered')

        self.imu2ego = transform_matrix([0., 0., imu_height], rotvec_to_rotmat(yaw=-np.pi * 0.5))

    def parse_calib_single(
        self,
        sensor_name: SensorName,
        calibrations: Dict[SensorName, SensorCalib],
    ):
        if sensor_name in CHERY_SENSOR_TYPE_CAMERA:
            calibrations[sensor_name].update(self.parse_intrinsic_camera(sensor_name))
            calibrations[sensor_name].extrinsic_matrix = self.parse_extrinsic_lidar2camera(sensor_name)

        elif sensor_name in CHERY_MAIN_SENSOR_LIDAR:
            calibrations[sensor_name].extrinsic_matrix = self.parse_extrinsic_lidar2ego(sensor_name)
            assert calibrations[sensor_name].extrinsic_matrix is not None

        elif sensor_name in CHERY_SENSOR_TYPE_LIDAR_BLIND:
            calibrations[sensor_name].extrinsic_matrix = self.parse_extrinsic_lidar2lidar(sensor_name)
            if calibrations[sensor_name].extrinsic_matrix is None:
                calibrations.pop(sensor_name)
        else:
            logger.error(f'unknown sensor type {sensor_name}')

    def parse_calib(
        self,
        sensor_names: List[SensorName],
    ) -> Dict[SensorName, SensorCalib]:
        """
        Parse calibration files

        @param sensor_names: names of sensors
        """
        calibrations = {sensor: SensorCalib() for sensor in sensor_names}
        multi_process_thread(self.parse_calib_single,
            [[name, calibrations] for name in sensor_names], nprocess=8,
            pool_func='ThreadPoolExecutor', map_func='map', progress_bar=False)

        calibrations[SensorName.chery_imu] = SensorCalib(extrinsic_matrix=self.imu2ego)
        return calibrations

    def load_json_file(self, json_path: str) -> Path:
        """
        Load localization file path

        @param json_path: path to localization file
        """
        return read_json(self.clip_root / json_path, strict=False)

    def get_extrinsic_path(self, json_path: str, json_name: str) -> Path:
        """
        Get extrinsic calibration file path

        @param yaml_path: path to extrinsic calibration file
        @param yaml_name: name of extrinsic calibration file
        """
        calib_json_path = self.calib_root / json_path / f'{json_name}.json'

        if self.search_global:
            available_calibs = lsdir(self.calib_root / self.vehicle_id.name / json_path)

            min_date_diff, _calib_json_path = np.inf, None
            for _json_path in available_calibs:
                if _json_path.stem.isdigit() and (_json_path / f'{json_name}.json').exists():
                    date_diff = np.abs(int(_json_path.stem) - self.collect_time)
                    if date_diff < min_date_diff:
                        min_date_diff = min(min_date_diff, date_diff)
                        _calib_json_path = _json_path / f'{json_name}.json'

            calib_json_path = _calib_json_path or calib_json_path
            extrinsic_name = json_path.split('/')[1]

            if self.vehicle_id.name == 'B781L6' and extrinsic_name in ['lidar2imu'] \
                and self.collect_time < 20240321000000:
                calib_json_path = self.calib_root / self.vehicle_id.name / \
                    json_path / '20240321000000' / f'{json_name}.json'

            if self.vehicle_id.name == 'B781L6' and extrinsic_name in ['lidar2camera'] \
                and self.collect_time < 20231013000000:
                calib_json_path = self.calib_root / self.vehicle_id.name / \
                    json_path / '20231013000000' / f'{json_name}.json'

        return calib_json_path

    def get_intrinsic_path(self, json_path: str, json_name: str) -> Path:
        """
        get intrinsic calibration file path
        @param json_path: path to intrinsic calibration file
        @param json_name: name of intrinsic calibration file
        """
        calib_json_path = self.calib_root / json_path / f'{json_name}.json'

        if self.search_global:
            available_calibs = lsdir(self.calib_root / self.vehicle_id.name / json_path / json_name, '*.json')

            min_date_diff, _calib_json_path = np.inf, None
            for _json_path in available_calibs:
                if _json_path.stem.isdigit() and _json_path.exists():
                    date_diff = np.abs(int(_json_path.stem) - self.collect_time)
                    if date_diff < min_date_diff:
                        min_date_diff = min(min_date_diff, date_diff)
                        _calib_json_path = _json_path

            calib_json_path = _calib_json_path or calib_json_path

        return calib_json_path

    def parse_intrinsic_camera(self, sensor_name: SensorName) -> Dict:
        """
        parse intrinsic calibration file
        @param sensor_name: name of sensor
        """
        calib_json_path = self.get_intrinsic_path(*CHERY_SENSOR_CALIB_INTRINSICS[sensor_name])
        logger.debug(f'load {sensor_name} intrinsics from {calib_json_path}')

        json_dict = self.load_json_file(calib_json_path)

        if json_dict is None:
            return

        fx, fy, cx, cy = json_dict['K']
        intrinsic_dict = dict(
            distortion_model=json_dict['distortion_model'],
            intrinsic_matrix=np.asarray([[fx, 0, cx], [0, fy, cy], [0, 0, 1]]),
            intrinsic_matrix_scaled=np.asarray([[fx, 0, cx], [0, fy, cy], [0, 0, 1]]),
            distortion=np.asarray(json_dict['D']),
            width=json_dict['width'],
            height=json_dict['height'],
        )

        if intrinsic_dict['distortion_model'] in ['equidistant', 'equi', 'radtan']:
            intrinsic_dict['distortion_model'] = 'pinhole'

        if intrinsic_dict['distortion_model'] == 'fisheye':
            intrinsic_dict['distortion'] = intrinsic_dict['distortion'][:4]

        intrinsic_dict.update(fov=calculate_camera_fov(intrinsic_dict))
        return intrinsic_dict

    def parse_extrinsic_lidar2camera(self, sensor_name: SensorName) -> np.ndarray:
        """
        parse extrinsic calibration file
        @param sensor_name: name of sensor
        """
        calib_json_path = self.get_extrinsic_path(*CHERY_SENSOR_CALIB_EXTRINSICS[sensor_name])
        logger.debug(f'load {sensor_name} to main-lidar extrinsics from {calib_json_path}')

        json_dict = self.load_json_file(calib_json_path)
        if json_dict is None:
            return

        return np.asarray(json_dict['transform'])

    def parse_extrinsic_lidar2lidar(self, sensor_name: SensorName) -> np.ndarray:
        """
        parse extrinsic calibration file
        @param sensor_name: name of sensor
        """
        calib_json_path = self.get_extrinsic_path(*CHERY_SENSOR_CALIB_EXTRINSICS[sensor_name])
        logger.debug(f'load {sensor_name} to main-lidar extrinsics from {calib_json_path}')

        json_dict = self.load_json_file(calib_json_path)
        if json_dict is None:
            return

        lidar2lidar = transform_matrix(
            [
                json_dict['transform']['translation']['x'],
                json_dict['transform']['translation']['y'],
                json_dict['transform']['translation']['z'],
            ], [
                json_dict['transform']['rotation']['x'],
                json_dict['transform']['rotation']['y'],
                json_dict['transform']['rotation']['z'],
                json_dict['transform']['rotation']['w'],
            ],
        )
        return lidar2lidar

    def parse_extrinsic_lidar2ego(self, sensor_name: SensorName) -> np.ndarray:
        """
        parse extrinsic calibration file
        @param sensor_name: name of sensor
        """
        calib_json_path = self.get_extrinsic_path(*CHERY_SENSOR_CALIB_EXTRINSICS[sensor_name])
        logger.debug(f'load {sensor_name} to imu extrinsics from {calib_json_path}')

        json_dict = self.load_json_file(calib_json_path)
        if json_dict is None:
            return

        lidar2imu = transform_matrix(
            [
                json_dict['transform']['translation']['x'],
                json_dict['transform']['translation']['y'],
                json_dict['transform']['translation']['z'],
            ], [
                json_dict['transform']['rotation']['x'],
                json_dict['transform']['rotation']['y'],
                json_dict['transform']['rotation']['z'],
                json_dict['transform']['rotation']['w'],
            ],
        )
        return self.imu2ego @ lidar2imu

    def parse_localizations(
        self,
        lidar2ego: np.ndarray,
        json_path: str = 'localization.json',
    ) -> List[EgoPose]:
        """
        Parse localization file

        @param json_path: path to localization file
        """
        localization_dict = self.load_json_file(json_path)
        if localization_dict is None:
            return None

        poses = []
        for pose_dict in localization_dict:

            timestamp = pose_dict.get('timestamp', pose_dict.get('measurementTime'))

            if timestamp is None:
                continue

            imu_translation = np.asarray([
                pose_dict['pose']['position']['x'],
                pose_dict['pose']['position']['y'],
                pose_dict['pose']['position']['z'],
            ])
            imu_rotation = np.asarray([
                pose_dict['pose']['orientation']['qx'],
                pose_dict['pose']['orientation']['qy'],
                pose_dict['pose']['orientation']['qz'],
                pose_dict['pose']['orientation']['qw'],
            ])
            imu_velocity = np.asarray([
                pose_dict['pose'].get('linear_velocity', pose_dict['pose'].get('linearVelocity'))['x'],
                pose_dict['pose'].get('linear_velocity', pose_dict['pose'].get('linearVelocity'))['y'],
                pose_dict['pose'].get('linear_velocity', pose_dict['pose'].get('linearVelocity'))['z'],
            ])

            imu2utm = transform_matrix(imu_translation, imu_rotation)
            ego2utm = imu2utm @ np.linalg.inv(self.imu2ego)
            lidar2utm = ego2utm @ lidar2ego

            poses.append(EgoPose(
                timestamp=timestamp,
                imu_translation=imu2utm[:3, 3],
                imu_rotation=imu2utm[:3, :3],
                imu_velocity=imu_velocity,
                ego_translation=ego2utm[:3, 3],
                ego_rotation=ego2utm[:3, :3],
                ego_velocity=convert_velos(imu_velocity, np.linalg.inv(ego2utm)),
                lidar_translation=lidar2utm[:3, 3],
                lidar_rotation=lidar2utm[:3, :3],
                lidar_velocity=convert_velos(imu_velocity, np.linalg.inv(lidar2utm)),
            ))
        return sorted(poses, key=lambda pose: pose.timestamp)

    def parse_slam_localizations(
        self,
        lidar2ego: np.ndarray,
        pose0: EgoPose,
        json_path: str = 'corrected_localization.json'
    ) -> List[EgoPose]:
        """
        Parse slam corrected localization file

        @param json_path: path to slam corrected localization file
        """
        localization_dict = self.load_json_file(json_path)
        if localization_dict is None:
            return None

        if isinstance(localization_dict, dict) and 'correct_localization.json' in localization_dict:
            localization_dict = localization_dict['correct_localization.json']

        poses = []
        for pose_dict in localization_dict:
            if 'lidar_localization_pose' in pose_dict:
                lidar_translation = np.asarray([
                    pose_dict['lidar_localization_pose']['position']['x'],
                    pose_dict['lidar_localization_pose']['position']['y'],
                    pose_dict['lidar_localization_pose']['position']['z'],
                ]) + pose0.imu_translation
                lidar_rotation = np.asarray([
                    pose_dict['lidar_localization_pose']['orientation']['x'],
                    pose_dict['lidar_localization_pose']['orientation']['y'],
                    pose_dict['lidar_localization_pose']['orientation']['z'],
                    pose_dict['lidar_localization_pose']['orientation']['w'],
                ])
                timestamp = pose_dict['lidar_localization_pose']['time']

                lidar2utm = transform_matrix(lidar_translation, lidar_rotation)
                ego2utm = lidar2utm @ np.linalg.inv(lidar2ego)
                imu2utm = ego2utm @ self.imu2ego

            else:
                imu_translation = np.asarray([
                    pose_dict['localization_pose']['position']['x'],
                    pose_dict['localization_pose']['position']['y'],
                    pose_dict['localization_pose']['position']['z'],
                ])
                imu_rotation = np.asarray([
                    pose_dict['localization_pose']['orientation']['x'],
                    pose_dict['localization_pose']['orientation']['y'],
                    pose_dict['localization_pose']['orientation']['z'],
                    pose_dict['localization_pose']['orientation']['w'],
                ])
                timestamp = pose_dict['localization_pose']['time']

                imu2utm = transform_matrix(imu_translation, imu_rotation)
                ego2utm = imu2utm @ np.linalg.inv(self.imu2ego)
                lidar2utm = ego2utm @ lidar2ego

            poses.append(EgoPose(
                timestamp=timestamp,
                imu_translation=imu2utm[:3, 3],
                imu_rotation=imu2utm[:3, :3],
                imu_velocity=None,
                ego_translation=ego2utm[:3, 3],
                ego_rotation=ego2utm[:3, :3],
                ego_velocity=None,
                lidar_translation=lidar2utm[:3, 3],
                lidar_rotation=lidar2utm[:3, :3],
                lidar_velocity=None,
            ))

        return sorted(poses, key=lambda pose: pose.timestamp)


class CheryAnnotationParser:
    pass


def get_chery_info(
    clip_path: Path,
    clip_id: str = None,
    obs_path: str = None,
    search_global: bool = True,
    calib_root: Path = Path(f'{__file__}/../../../params/calibrations').resolve(),
    output_path: str = None,
    info_json: str = 'info.json',
    localization_json: str = 'localization.json',
    slam_info_prefix: str = 'static_obj/lidar_slam',
    sensor_names: List[SensorName] = CHERY_SENSOR_TYPE_CAMERA + CHERY_SENSOR_TYPE_LIDAR,
    anno_dir: str = 'annotation',
    anno_type: str = 'PVB',
    anno_subtype: AnnotationType = None,
    anno_path: str = None,
    merge_gop: str = None,
) -> ClipInfo:
    """
    @param clip_path: path to clip
    @param sensor_names: sensor names to be parsed
    @param search_global: whether to search global calib params
    @param calib_root: path to calibration files
    @param output_path: path to save parsed calib params
    @param info_json: path to info.json
    @param localization_json: path to raw localization
    return: parsed clip info
    """
    _clip_path = Path(clip_path).resolve()
    logger.debug(f'checking clip path {_clip_path}')
    clip_json_info = read_json(_clip_path / info_json, strict=False)
    if clip_json_info is None:
        logger.error('failed to find clip info')
        return

    file_parser = CheryParamParser(_clip_path, output_path, search_global, calib_root, **clip_json_info)
    calibrations = file_parser.parse_calib(sensor_names)

    clip_info = ClipInfo(
        vehicle_id=file_parser.vehicle_id,
        weather=clip_json_info['weather'],
        scene=clip_json_info['scene'],
        bag_name='_'.join(clip_json_info['bag_name'].split('_')[1].split('-')[-2:]),
        clip_id=clip_id,
        clip_name=_clip_path.stem,
        clip_path=_clip_path.as_posix(),
        obs_path=obs_path,
        collect_time=clip_json_info['collect_time'],
        calibrations=calibrations,
    )

    clip_info.poses = file_parser.parse_localizations(
        clip_info.calibrations[CHERY_MAIN_SENSOR_LIDAR].extrinsic_matrix,
        localization_json)

    if not pose_sanity_check(clip_info.poses):
        logger.error('failed pose check')
        return

    clip_info.reference_ego_pose = transform_matrix(clip_info.poses[0].ego_translation)
    clip_info.reference_lidar_pose = transform_matrix(clip_info.poses[0].lidar_translation)

    slam_json_path = lsdir(_clip_path / slam_info_prefix, 'lidar0_stitch_config_*.json')
    if len(slam_json_path) == 1:
        clip_info.slam_poses = file_parser.parse_slam_localizations(
            clip_info.calibrations[CHERY_MAIN_SENSOR_LIDAR].extrinsic_matrix,
            clip_info.poses[0], slam_json_path[0])

    frame_path_list = lsdir(clip_path, 'sample_*')
    if len(frame_path_list) != len(clip_json_info['frames']):
        logger.warning(f'update frame list in clip_info.json {clip_path}')
        frame_names = ' '.join([f['frame_name'] for f in clip_json_info['frames']])
        for frame_path in frame_path_list:
            if frame_path.name not in frame_names:
                clip_json_info['frames'].append(dict(
                    frame_name=frame_path.name,
                    lidar_collect=int(frame_path.name.replace('sample_', ''))))

    frames_info = multi_process_thread(_fill_single_frame,
        [[_clip_path, frame_dict, sensor_names, clip_info.poses, clip_info.slam_poses]
        for frame_dict in clip_json_info['frames']], nprocess=8,
        pool_func='ThreadPoolExecutor', map_func='map', progress_bar=False)

    clip_info.frames = {info['lidar_timestamp']: info for info in
        sorted([_ for _ in frames_info if _ is not None],
               key=lambda info: info['lidar_timestamp'])}

    logger.debug(f'{len(clip_info.frames)} frames found')
    if output_path is not None and environ.get('RANK', '0') == '0':
        write_json(output_path / 'info.json', clip_json_info)

    _anno_subtype = anno_subtype or _get_annotation_type(_clip_path, anno_dir, anno_type)
    if _anno_subtype is not None:
        anno_info = read_json((anno_path or _clip_path / anno_dir / \
            _anno_subtype.value) / f'{_clip_path.stem}.json', strict=False)

        if anno_info is not None:
            clip_info.anno_type = _anno_subtype

            multi_process_thread(
                _fill_pvb_gop_anno_frame, [[frame_info, clip_info]
                    for frame_info in anno_info['frames']], nprocess=8,
                pool_func='ThreadPoolExecutor', map_func='map', progress_bar=False)

    if merge_gop is not None and _anno_subtype not in ANNOTATION_TYPE['GOP']:
        gop_info = read_json(merge_gop / f'{_clip_path.stem}.json', strict=False)

        if gop_info is not None:
            max_track_id = max([obj_info.track_id for frame_info in clip_info.frames.values()
                for obj_info in frame_info.objects[CHERY_MAIN_SENSOR_LIDAR]]) if \
            len([_ for frame_info in clip_info.frames.values()
                for _ in frame_info.objects[CHERY_MAIN_SENSOR_LIDAR]]) > 0 else 0

            frame_indices = {f['frame_name']: i for i, f in enumerate(gop_info['frames'])}

            for frame_info in frames_info:
                if frame_info is None:
                    continue
                gop_frame = gop_info['frames'][frame_indices[frame_info['frame_name']]]
                annotated_gop = ANNOTATION_INFO[AnnotationType.REPROJECTED_GOP.name](gop_frame)
                track_ids = [_obj['track_id'] for _obj in annotated_gop[CHERY_MAIN_SENSOR_LIDAR.value]]

                [clip_info.frames[gop_frame['lidar_collect']].objects[SensorName[sensor_name]].extend(
                    _fill_pvb_gop_anno_obj(sensor_name, annotated_gop, track_ids, max_track_id))
                    for sensor_name in annotated_gop if sensor_name in
                    clip_info.frames[gop_frame['lidar_collect']].objects]

    return clip_info


def _fill_single_frame(
    clip_path: Path,
    frame_dict: Dict,
    sensor_names: List[SensorName],
    ego_poses: List[EgoPose],
    slam_poses: List[EgoPose], 
):
    sensor_filepaths: Dict[SensorName, Path] = dict()
    sensor_timestamps: Dict[SensorName, int] = dict()
    for sensor in sensor_names:
        filepath = None
        if sensor.value in frame_dict:
            filepath = clip_path / frame_dict['frame_name'] / frame_dict[sensor.value]

        if sensor.value not in frame_dict or not filepath.exists():
            candidate = [p for p in lsdir(clip_path / frame_dict['frame_name'],
                f'{sensor.value}_*.{"jpg" if sensor in CHERY_SENSOR_TYPE_CAMERA else "pcd"}')
                if len(p.stem.replace(sensor.value, '')) == 50]

            if len(candidate) == 1:
                filepath = candidate[0]
                logger.warning(f'update filepath in clip_info.json {filepath}')
                frame_dict[sensor.value] = filepath.name
            else:
                filepath = None
        sensor_filepaths[sensor] = filepath
        if filepath is not None:
            sensor_timestamps[sensor] = int(filepath.stem.split('_')[1])

    if len(sensor_names) != len(sensor_filepaths):
        return

    _camera_collect = sensor_filepaths[CHERY_MAIN_SENSOR_CAMERA].as_posix().split('_')[-2]
    camera_collect = int(_camera_collect)
    if frame_dict.get('camera_collect') != camera_collect:
        frame_dict.update(camera_collect=camera_collect)

    frame_info = FrameInfo(
        clip_name=clip_path.stem,
        frame_name=frame_dict['frame_name'],
        token=frame_dict.get('frame_id'),
        camera_timestamp=camera_collect,
        lidar_timestamp=frame_dict['lidar_collect'], # frame_id
        sensor_timestamps=sensor_timestamps,
        sensor_filepaths=sensor_filepaths,
    )

    if ego_poses is not None:
        curr_pose_raw, _ = _get_closest_pose(ego_poses, frame_dict['lidar_collect'])
        frame_info.lidar2utm = transform_matrix(curr_pose_raw.lidar_translation,
                                                curr_pose_raw.lidar_rotation)
        frame_info.ego2utm = transform_matrix(curr_pose_raw.ego_translation,
                                              curr_pose_raw.ego_rotation)
        frame_info.ego_velo = curr_pose_raw.ego_velocity
        frame_info.lidar_velo = curr_pose_raw.lidar_velocity

    if slam_poses is not None:
        curr_slam_pose, _ = _get_closest_pose(slam_poses, camera_collect)
        frame_info.lidar2slam = transform_matrix(curr_slam_pose.lidar_translation,
                                                 curr_slam_pose.lidar_rotation)
        frame_info.ego2slam = transform_matrix(curr_slam_pose.ego_translation,
                                               curr_slam_pose.ego_rotation)

    return frame_info


def _fill_pvb_gop_anno_frame(
    annotation_info: Dict,
    clip_info: ClipInfo,
) -> FrameInfo:
    anno_info = ANNOTATION_INFO[clip_info.anno_type.name](annotation_info)
    _recast_annotation(anno_info[CHERY_MAIN_SENSOR_LIDAR.value],
                       annotation_info['frame_name'])
    track_ids = [_obj['track_id'] for _obj in anno_info[CHERY_MAIN_SENSOR_LIDAR.value]]

    if annotation_info['lidar_collect'] in clip_info.frames:
        clip_info.frames[annotation_info['lidar_collect']].update(objects={
            SensorName[sensor_name]: _fill_pvb_gop_anno_obj(sensor_name, anno_info, track_ids)
            for sensor_name in anno_info})


def _fill_pvb_gop_anno_obj(
    sensor_name: str,
    anno_info: Dict[str, List[Dict]],
    track_ids: List,
    track_offset: int = 0
) -> List[ObjectInfo]:
    return [
        ObjectInfo(
            lidar_box3d=anno['obj_center_pos'] + anno['size'] + [quaternion_to_rotvec(anno['obj_rotation'])[2]],
            lidar_velo=anno.get('velocity'),
            # lidar_confidence=anno.get('confidence'),
            lidar_pts_count=anno.get('num_lidar_pts'),
            camera_box3d=anno['obj_center_pos_cam'] + anno['size'] + [quaternion_to_rotvec(anno['obj_rotation_cam'])[2]]
                if anno.get('obj_center_pos_cam') is not None and anno.get('obj_rotation_cam') is not None else None,
            obj_subtype=ObjectSubType[anno['category']],
            obj_type=OBJECT_SUBTYPE_TO_TYPE[ObjectSubType[anno['category']]],
            track_id=anno['track_id'] + track_offset,
            motion_state=None if anno.get('motion_state') is None else MotionState[anno['motion_state']],
            group_id=anno.get('group_id'),
            is_group=anno.get('is_group'),
            is_cyclist=anno.get('is_cyclist', False),
            is_fake=anno.get('is_fake', False),
            cross_lane=anno.get('cross_lane'),
            lane_id=anno.get('lane_id'),
            signal=anno.get('signal'),
        ) if sensor_name == CHERY_MAIN_SENSOR_LIDAR.value else
        ObjectInfo(
            camera_box2d=[
                anno['bbox'][0] - anno['bbox'][2] // 2,
                anno['bbox'][1] - anno['bbox'][3] // 2,
                anno['bbox'][0] + anno['bbox'][2] - anno['bbox'][2] // 2,
                anno['bbox'][1] + anno['bbox'][3] - anno['bbox'][3] // 2,
            ],
            undistorted_box2d=[
                anno['undistort'][0] - anno['undistort'][2] // 2,
                anno['undistort'][1] - anno['undistort'][3] // 2,
                anno['undistort'][0] + anno['undistort'][2] - anno['undistort'][2] // 2,
                anno['undistort'][1] + anno['undistort'][3] - anno['undistort'][3] // 2,
            ] if 'undistort' in anno else None,
            camera_box3d=anno_info[CHERY_MAIN_SENSOR_LIDAR.value][track_ids.index(anno['track_id'])]['obj_center_pos_cam'] + \
                        anno_info[CHERY_MAIN_SENSOR_LIDAR.value][track_ids.index(anno['track_id'])]['size'] + \
                        [quaternion_to_rotvec(anno_info[CHERY_MAIN_SENSOR_LIDAR.value][track_ids.index(anno['track_id'])]['obj_rotation_cam'])[2]]
                if anno_info[CHERY_MAIN_SENSOR_LIDAR.value][track_ids.index(anno['track_id'])].get('obj_center_pos_cam') is not None and \
                    anno_info[CHERY_MAIN_SENSOR_LIDAR.value][track_ids.index(anno['track_id'])].get('obj_rotation_cam') is not None else None,
            # camera_confidence=anno.get('confidence'),
            obj_subtype=ObjectSubType[anno_info[CHERY_MAIN_SENSOR_LIDAR.value][track_ids.index(anno['track_id'])]['category']],
            obj_type=OBJECT_SUBTYPE_TO_TYPE[ObjectSubType[anno_info[CHERY_MAIN_SENSOR_LIDAR.value][track_ids.index(anno['track_id'])]['category']]],
            track_id=anno['track_id'] + track_offset,
            occlusion=anno.get('occlusion'),
            truncation=anno.get('truncation'),
        ) for anno in anno_info[sensor_name]]


def _get_annotation_type(
    clip_path: Path,
    anno_dir: str = 'annotation',
    anno_type: str = 'PVB'
) -> AnnotationType:
    avaliable_anno_type = [anno_subtype for anno_subtype in ANNOTATION_TYPE[anno_type]
        if (clip_path / anno_dir / anno_subtype.value / f'{clip_path.stem}.json').exists()]

    if len(avaliable_anno_type) == 0:
        logger.error(f'no {anno_type} annotation found for {clip_path.stem}')
        return

    elif len(avaliable_anno_type) > 1:
        logger.warning(f'multiple annotation types found for {clip_path.stem}: {avaliable_anno_type}, '
                       f'use {avaliable_anno_type[0]} by default')

    logger.debug(f'found annotation {avaliable_anno_type[0]} {ANNOTATION_ID.get(avaliable_anno_type[0])}')
    return avaliable_anno_type[0]


def _get_closest_pose(
    poses: List[EgoPose],
    target_timestamp: int,
    coordinate: str = None,
) -> Tuple[EgoPose, int]:
    """
    Get the closest pose to the target timestamp

    @param pose_record: list of ego poses
    @param target_timestamp: target timestamp
    return: closest pose and its index
    """
    pose_timestamps = np.asarray([pose.timestamp for pose in poses])
    closest_ind = np.fabs(pose_timestamps - target_timestamp * 1e-6).argmin()
    this_pose = poses[closest_ind]

    if coordinate is not None:
        this_pose = transform_matrix(
            getattr(poses[closest_ind], f'{coordinate}_translation'),
            getattr(poses[closest_ind], f'{coordinate}_rotation')
        )
    return this_pose, closest_ind


def _recast_annotation(
    anno_info: List[Dict],
    frame_name: str
) -> None:
    """ """
    for indx, _object in enumerate(anno_info):
        if _object['category'] == 'barrier':
            length_width_ratio = _object['size'][0] / _object['size'][1]
            if length_width_ratio > 0.91 and length_width_ratio < 1.1:
                logger.debug(f'{frame_name} obj {_object["track_id"]} '
                             f'recast barrier to anti_collision_barrel, l{_object["size"][0]:.1f}, '
                             f'w{_object["size"][1]:.1f}, l:w{length_width_ratio:.1f}')
                _object.update(category='anti_collision_barrel')

        if _object['category'] in ['traffic_warning', 'construction_sign',
                                   'barrier', 'no_parking_sign', 'barrier_gate',
                                   'wall_column', 'round_column', 'lock']:
            yaw = quaternion_to_rotvec(_object['obj_rotation'])[2]
            if _object['size'][0] < _object['size'][1]:
                yaw += np.pi / 2
                _object['size'][0], _object['size'][1] = _object['size'][1], _object['size'][0]

            _object.update(obj_rotation=[float(x) for x in rotvec_to_quaternion(yaw=yaw % np.pi)])

        if _object['category'] == 'truck':
            length = _object['size'][0]
            if length < 6.5:
                logger.debug(f'{frame_name} obj {_object["track_id"]} '
                             f'recast truck to pickup_truck, l{_object["size"][0]:.1f}')
                _object.update(category='pickup_truck')

        if _object['category'] == 'pickup_truck':
            length = _object['size'][0]
            if length > 6.5:
                logger.debug(f'{frame_name} obj {_object["track_id"]} '
                             f'recast pickup_truck to truck, l{_object["size"][0]:.1f}')
                _object.update(category='truck')

        if _object['category'] in ['unknown_unmovable', 'unknown_movable', 'gate']:
            logger.debug(f'{frame_name} obj {_object["track_id"]} '
                         f'recast {_object["category"]} to unknown')
            _object.update(category='unknown')

        if _object['category'] == 'animal':
            logger.debug(f'{frame_name} obj {_object["track_id"]} '
                            f'recast animal to small_animal')
            _object.update(category='small_animal')

        if _object['category'] not in ['bicycle', 'tricycle', 'motorcycle']:
            if _object.get('is_cyclist') is not None:
                logger.debug(f'{frame_name} obj {_object["track_id"]} '
                             f'{_object["category"]} recast is_cyclist to none')
                _object.update(is_cyclist=None)

        if _object['category'] == 'fake_car':
            logger.debug(f'{frame_name} obj {_object["track_id"]} '
                         f'{_object["category"]} recast fake_car to car')
            _object.update(category='car', is_fake=True)

        if _object['category'] == 'fake_person':
            logger.debug(f'{frame_name} obj {_object["track_id"]} '
                         f'{_object["category"]} recast fake_person to person')
            _object.update(category='person', is_fake=True)

        if _object['category'] == 'fake_bicycle':
            logger.debug(f'{frame_name} obj {_object["track_id"]} '
                         f'{_object["category"]} recast fake_bicycle to bicycle')
            _object.update(category='bicycle', is_fake=True)
