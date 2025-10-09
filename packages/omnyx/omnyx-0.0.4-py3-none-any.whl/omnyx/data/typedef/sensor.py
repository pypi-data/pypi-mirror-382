from .baseclass import _Enum

__all__ = [
    'SensorName',
    'CHERY_MAIN_SENSOR_CAMERA',
    'CHERY_MAIN_SENSOR_LIDAR',
    'CHERY_SENSOR_TYPE_CAMERA',
    'CHERY_SENSOR_TYPE_CAMERA_OMNI',
    'CHERY_SENSOR_TYPE_CAMERA_MAPPING',
    'CHERY_SENSOR_TYPE_LIDAR',
    'CHERY_SENSOR_TYPE_LIDAR_BLIND',
    'QCRAFT_SENSOR_TYPE_CAMERA',
    'QCRAFT_SENSOR_TYPE_CAMERA_OMNI',
    'QCRAFT_SENSOR_TYPE_CAMERA_MAPPING',
    'QCRAFT_SENSOR_TYPE_UNDISTORT_MAPPING',
    'QCRAFT_SENSOR_TYPE_LIDAR',
    'QCRAFT_SENSOR_TYPE_LIDAR_BLIND',
    'SENSOR_TYPE_CAMERA_NAME_SHORT',
]


class SensorName(str, _Enum):
    chery_camera_front_center =     'camera0'
    chery_camera_front_center_tele = 'camera1'
    chery_camera_front_left =       'camera2'
    chery_camera_front_right =      'camera4'
    chery_camera_rear_left =        'camera3'
    chery_camera_rear_right =       'camera5'
    chery_camera_rear_center =      'camera6'

    chery_camera_omni_left =        'camera7'
    chery_camera_omni_rear =        'camera8'
    chery_camera_omni_front =       'camera9'
    chery_camera_omni_right =       'camera10'

    chery_lidar_top =               'lidar0'
    chery_lidar_left_blind =        'lidar1'
    chery_lidar_front_blind =       'lidar2'
    chery_lidar_right_blind =       'lidar3'
    chery_lidar_rear_blind =        'lidar4'
    chery_lidar_front =             'lidar5'

    chery_imu =                     'imu'

    qcraft_camera_front_center =    'CAM_PBQ_FRONT_WIDE'
    qcraft_camera_front_center_110 = 'CAM_PBQ_FRONT_WIDE_RESET_OPTICAL_H110_HR'
    qcraft_camera_front_center_tele = 'CAM_PBQ_FRONT_TELE'
    qcraft_camera_front_center_tele_30 = 'CAM_PBQ_FRONT_TELE_RESET_OPTICAL_H30_HR'
    qcraft_camera_front_left =      'CAM_PBQ_FRONT_LEFT'
    qcraft_camera_front_left_99 =   'CAM_PBQ_FRONT_LEFT_RESET_OPTICAL_H99_HR'
    qcraft_camera_front_right =     'CAM_PBQ_FRONT_RIGHT'
    qcraft_camera_front_right_99 =  'CAM_PBQ_FRONT_RIGHT_RESET_OPTICAL_H99_HR'
    qcraft_camera_rear_left =       'CAM_PBQ_REAR_LEFT'
    qcraft_camera_rear_left_99 =    'CAM_PBQ_REAR_LEFT_RESET_OPTICAL_H99_HR'
    qcraft_camera_rear_right =      'CAM_PBQ_REAR_RIGHT'
    qcraft_camera_rear_right_99 =   'CAM_PBQ_REAR_RIGHT_RESET_OPTICAL_H99_HR'
    qcraft_camera_rear_center =     'CAM_PBQ_REAR'
    qcraft_camera_rear_center_50 =  'CAM_PBQ_REAR_RESET_OPTICAL_H50_HR'

    qcraft_camera_omni_left =       'CAM_PBQ_LEFT_FISHEYE'
    qcraft_camera_omni_rear =       'CAM_PBQ_REAR_FISHEYE'
    qcraft_camera_omni_front =      'CAM_PBQ_FRONT_FISHEYE'
    qcraft_camera_omni_right =      'CAM_PBQ_RIGHT_FISHEYE'

    qcraft_lidar_top =              'LDR_CENTER'
    qcraft_lidar_top_left =         'LDR_FRONT_LEFT'
    qcraft_lidar_top_right =        'LDR_FRONT_RIGHT'
    qcraft_lidar_front =            'LDR_FRONT'

    qcraft_lidar_left_blind =       'LDR_FRONT_LEFT_BLIND'
    qcraft_lidar_front_blind =      'LDR_FRONT_BLIND'
    qcraft_lidar_right_blind =      'LDR_FRONT_RIGHT_BLIND'
    qcraft_lidar_rear_blind =       'LDR_REAR_BLIND'


CHERY_MAIN_SENSOR_CAMERA = SensorName.chery_camera_front_center
CHERY_MAIN_SENSOR_LIDAR = SensorName.chery_lidar_top

CHERY_SENSOR_TYPE_CAMERA_OMNI = [
    SensorName.chery_camera_omni_front,
    SensorName.chery_camera_omni_right,
    SensorName.chery_camera_omni_rear,
    SensorName.chery_camera_omni_left,
]
CHERY_SENSOR_TYPE_LIDAR_BLIND = [
    SensorName.chery_lidar_left_blind,
    SensorName.chery_lidar_front_blind,
    SensorName.chery_lidar_right_blind,
    SensorName.chery_lidar_rear_blind,
]

CHERY_SENSOR_TYPE_CAMERA = [
    SensorName.chery_camera_front_center_tele,
    SensorName.chery_camera_front_left,
    SensorName.chery_camera_front_center,
    SensorName.chery_camera_front_right,
    SensorName.chery_camera_rear_left,
    SensorName.chery_camera_rear_center,
    SensorName.chery_camera_rear_right,
] + CHERY_SENSOR_TYPE_CAMERA_OMNI
CHERY_SENSOR_TYPE_LIDAR = [
    CHERY_MAIN_SENSOR_LIDAR
] + CHERY_SENSOR_TYPE_LIDAR_BLIND
CHERY_SENSOR_TYPE_CAMERA_MAPPING = {
    'camera_front_center': SensorName.chery_camera_front_center,
    'camera_front_center_tele': SensorName.chery_camera_front_center_tele,
    'camera_front_left': SensorName.chery_camera_front_left,
    'camera_front_right': SensorName.chery_camera_front_right,
    'camera_rear_left':  SensorName.chery_camera_rear_left,
    'camera_rear_right': SensorName.chery_camera_rear_right,
    'camera_rear_center': SensorName.chery_camera_rear_center,
    'camera_omni_front': SensorName.chery_camera_omni_front,
    'camera_omni_right': SensorName.chery_camera_omni_right,
    'camera_omni_rear': SensorName.chery_camera_omni_rear,
    'camera_omni_left': SensorName.chery_camera_omni_left,
}

QCRAFT_SENSOR_TYPE_CAMERA_OMNI = [
    SensorName.qcraft_camera_omni_front,
    SensorName.qcraft_camera_omni_right,
    SensorName.qcraft_camera_omni_rear,
    SensorName.qcraft_camera_omni_left,
]
QCRAFT_SENSOR_TYPE_LIDAR_BLIND = [
    SensorName.qcraft_lidar_left_blind,
    SensorName.qcraft_lidar_front_blind,
    SensorName.qcraft_lidar_right_blind,
    SensorName.qcraft_lidar_rear_blind,
]

QCRAFT_SENSOR_TYPE_CAMERA = [
    SensorName.qcraft_camera_front_center,
    SensorName.qcraft_camera_front_center_tele,
    SensorName.qcraft_camera_front_left,
    SensorName.qcraft_camera_front_right,
    SensorName.qcraft_camera_rear_left,
    SensorName.qcraft_camera_rear_right,
    SensorName.qcraft_camera_rear_center,
] + QCRAFT_SENSOR_TYPE_CAMERA_OMNI
QCRAFT_SENSOR_TYPE_LIDAR = [
    SensorName.qcraft_lidar_top,
    SensorName.qcraft_lidar_left_blind,
    SensorName.qcraft_lidar_front_blind,
    SensorName.qcraft_lidar_right_blind,
    SensorName.qcraft_lidar_rear_blind,
] + QCRAFT_SENSOR_TYPE_LIDAR_BLIND
QCRAFT_SENSOR_TYPE_CAMERA_MAPPING = {
    'camera_front_center': SensorName.qcraft_camera_front_center,
    'camera_front_center_tele': SensorName.qcraft_camera_front_center_tele,
    'camera_front_left': SensorName.qcraft_camera_front_left,
    'camera_front_right': SensorName.qcraft_camera_front_right,
    'camera_rear_left':  SensorName.qcraft_camera_rear_left,
    'camera_rear_right': SensorName.qcraft_camera_rear_right,
    'camera_rear_center': SensorName.qcraft_camera_rear_center,
    'camera_omni_front': SensorName.qcraft_camera_omni_front,
    'camera_omni_right': SensorName.qcraft_camera_omni_right,
    'camera_omni_rear': SensorName.qcraft_camera_omni_rear,
    'camera_omni_left': SensorName.qcraft_camera_omni_left,
}
QCRAFT_SENSOR_TYPE_UNDISTORT_MAPPING = {
    'camera_front_center': SensorName.qcraft_camera_front_center_110,
    'camera_front_center_tele': SensorName.qcraft_camera_front_center_tele_30,
    'camera_front_left': SensorName.qcraft_camera_front_left_99,
    'camera_front_right': SensorName.qcraft_camera_front_right_99,
    'camera_rear_left':  SensorName.qcraft_camera_rear_left_99,
    'camera_rear_right': SensorName.qcraft_camera_rear_right_99,
    'camera_rear_center': SensorName.qcraft_camera_rear_center_50,
    'camera_omni_front': SensorName.qcraft_camera_omni_front,
    'camera_omni_right': SensorName.qcraft_camera_omni_right,
    'camera_omni_rear': SensorName.qcraft_camera_omni_rear,
    'camera_omni_left': SensorName.qcraft_camera_omni_left,
}

SENSOR_TYPE_CAMERA_NAME_SHORT = {
    SensorName.chery_camera_front_center: 'FC',
    SensorName.chery_camera_front_center_tele: 'FT',
    SensorName.chery_camera_front_left: 'FL',
    SensorName.chery_camera_front_right: 'FR',
    SensorName.chery_camera_rear_left: 'RL',
    SensorName.chery_camera_rear_right: 'RR',
    SensorName.chery_camera_rear_center: 'RC',
    SensorName.chery_camera_omni_front: 'OF',
    SensorName.chery_camera_omni_right: 'OR',
    SensorName.chery_camera_omni_rear: 'OR',
    SensorName.chery_camera_omni_left: 'OL',

    SensorName.qcraft_camera_front_center: 'FC',
    SensorName.qcraft_camera_front_center_tele: 'FT',
    SensorName.qcraft_camera_front_left: 'FL',
    SensorName.qcraft_camera_front_right: 'FR',
    SensorName.qcraft_camera_rear_left: 'RL',
    SensorName.qcraft_camera_rear_right: 'RR',
    SensorName.qcraft_camera_rear_center: 'RC',
    SensorName.qcraft_camera_omni_front: 'OF',
    SensorName.qcraft_camera_omni_right: 'OR',
    SensorName.qcraft_camera_omni_rear: 'OR',
    SensorName.qcraft_camera_omni_left: 'OL',

    SensorName.qcraft_camera_front_center_110: 'FC',
    SensorName.qcraft_camera_front_center_tele_30: 'FT',
    SensorName.qcraft_camera_front_left_99: 'FL',
    SensorName.qcraft_camera_front_right_99: 'FR',
    SensorName.qcraft_camera_rear_left_99: 'RL',
    SensorName.qcraft_camera_rear_right_99: 'RR',
    SensorName.qcraft_camera_rear_center_50: 'RC',
}