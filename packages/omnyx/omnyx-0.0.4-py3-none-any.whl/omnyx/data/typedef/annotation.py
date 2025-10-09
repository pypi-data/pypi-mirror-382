from .baseclass import _Enum

__all__ = [
    'AnnotationType',
    'ObjectType',
    'ObjectSubType',
    'MotionState',
    'OBJECT_SUBTYPE_TO_TYPE'
]


class AnnotationType(str, _Enum):
    TAXI_HIGHWAY_OD_23D = '23d_object'
    TAXI_URBAN_OD_3D = 'only_3d_city_object_detection'
    TAXI_HIGHWAY_OD_3D = '23d_object_detection'

    HNOA_URBAN_OD_3D = '3d_city_object_detection_with_fish_eye'
    HNOA_HIGHWAY_OD_3D = '3d_highway_object_detection_with_fish_eye'
    HNOA_PARKING_OD_3D = 'parking_movable_object_detection'

    HNOA_GOP_OD_3D = 'gop_object_detection'
    HNOA_URBAN_GOP_3D = 'driving_gop_object_detection'
    HNOA_PARKING_GOP_3D = 'parking_gop_object_detection'

    HNOA_TRAFFIC_SIGN = '23d_traffic_sign'

    LANE_KEY_POINTS_3D = '3d_lane'
    LANE_KEY_POINTS_4D = 'auto_4d_lane'
    PARKING_KEY_POINTS = 'parking_surround_space_detection'

    INTERPOLATED_PVB = 'pvb_10hz'
    REPROJECTED_GOP = 'gop_10hz'


class ObjectType(int, _Enum):
    car = 0
    bus = 1
    truck = 2

    cyclist = 3
    tricyclist = 4
    pedestrian = 5

    cone = 6
    pole = 7
    barrier = 8

    movable = 9
    unmovable = 10


class CameraObjectType(int, _Enum):
    person = 0
    bicycle = 1
    car = 2
    motorcycle = 3
    bus = 5
    truck = 7
    traffic_light = 9


class LidarObjectType(int, _Enum):
    car = 0
    truck = 1
    construction_vehicle = 2
    bus = 3
    tricycle = 4
    motorcycle = 5
    bicycle = 6
    person = 7


class LaneType(int, _Enum):
    single_dash = 0
    single_solid = 1
    road_edge = 2
    dense_wide_dash = 3
    others = 4


class MotionState(str, _Enum):
    uncertain = 0
    stationary = 1
    moving = 2


class ObjectSubType(int, _Enum):
    car = 0
    bus = 1
    truck = 2
    pickup_truck = 3
    trailer = 4
    cement_mixer = 5
    construction_vehicle = 6
    recreational_vehicle = 7
    special_vehicle = 8         # 购物车 婴儿车 轮椅
    unknown_vehicle = 9         # 

    bicycle = 10
    motorcycle = 11
    tricycle = 12

    person = 13
    large_animal = 14
    small_animal = 15

    traffic_cone = 16
    traffic_warning = 17
    warning_post = 18
    construction_sign = 19
    barrier = 20
    anti_collision_barrel = 21

    no_parking_sign = 22
    barrier_gate = 23
    wall_column = 24
    round_column = 25
    lock = 26

    special_pillar = 27
    railing_post = 28
    stone_pier = 29
    trash_bin = 30
    speed_bump = 31
    fire_hydrant_cabinet = 32
    charging_pile = 33

    unknown = -1
    traffic_light = -2
    traffic_sign = -3


OBJECT_SUBTYPE_TO_TYPE = {
    ObjectSubType.car: ObjectType.car,
    ObjectSubType.bus: ObjectType.bus,
    ObjectSubType.truck: ObjectType.truck,
    ObjectSubType.pickup_truck: ObjectType.truck,
    ObjectSubType.trailer: ObjectType.truck,
    ObjectSubType.cement_mixer: ObjectType.truck,
    ObjectSubType.construction_vehicle: ObjectType.truck,
    ObjectSubType.recreational_vehicle: ObjectType.car,
    ObjectSubType.special_vehicle: ObjectType.movable,
    ObjectSubType.unknown_vehicle: ObjectType.movable,

    ObjectSubType.bicycle: ObjectType.cyclist,
    ObjectSubType.motorcycle: ObjectType.cyclist,
    ObjectSubType.tricycle: ObjectType.tricyclist,

    ObjectSubType.person: ObjectType.pedestrian,
    ObjectSubType.large_animal: ObjectType.movable,
    ObjectSubType.small_animal: ObjectType.movable,

    ObjectSubType.traffic_cone: ObjectType.cone,
    ObjectSubType.traffic_warning: ObjectType.cone,
    ObjectSubType.warning_post: ObjectType.cone,
    ObjectSubType.construction_sign: ObjectType.cone,
    ObjectSubType.barrier: ObjectType.cone,
    ObjectSubType.anti_collision_barrel: ObjectType.cone,
    ObjectSubType.no_parking_sign: ObjectType.cone,
    ObjectSubType.barrier_gate: ObjectType.unmovable,
    ObjectSubType.wall_column: ObjectType.unmovable,
    ObjectSubType.round_column: ObjectType.unmovable,
    ObjectSubType.lock: ObjectType.unmovable,

    ObjectSubType.special_pillar: ObjectType.cone,
    ObjectSubType.railing_post: ObjectType.cone,
    ObjectSubType.stone_pier: ObjectType.cone,
    ObjectSubType.trash_bin: ObjectType.cone,
    ObjectSubType.speed_bump: ObjectType.cone,
    ObjectSubType.fire_hydrant_cabinet: ObjectType.cone,
    ObjectSubType.charging_pile: ObjectType.cone,

    ObjectSubType.traffic_light: ObjectType.unmovable,
    ObjectSubType.traffic_sign: ObjectType.unmovable,
    ObjectSubType.unknown: ObjectType.unmovable,
}
