from .baseclass import _Enum

__all__ = ['VehicleID', 'CHERY_SENSOR_IMU_HEIGHT']


class VehicleID(str, _Enum):
    B781L6 =    '揽月_01'
    B550M0 =    '揽月_02'
    B559Q1 =    '艾瑞泽_03'

    AF080 =     'T28_12'
    B8340 =     'T28_14'
    F58584 =    'T28_16'
    BF81597 =   'T28_17'
    FA1583 =    'T28_19'

    B8044 =     'E03_01'
    BDJ0636 =   'E03_05'
    DJ5363 =    'E03_06'
    BQ597 =     'E03_07'
    S106LS =    'E03_08'
    E03309 =    'E03_09'
    E03630 =    'E03_10'


CHERY_SENSOR_IMU_HEIGHT = {
    VehicleID.B781L6: 0.13,         # 揽月
    VehicleID.B550M0: 0.13,         # 揽月
    VehicleID.B559Q1: 0.13,         # 艾瑞泽

    VehicleID.AF080: 0.28,          # T28
    VehicleID.B8340: 0.28,          # T28
    VehicleID.BF81597: 0.28,        # T28
    VehicleID.F58584: 0.28,         # T28
    VehicleID.FA1583: 0.28,         # T28

    VehicleID.B8044: 0.20,          # E03
    VehicleID.BDJ0636: 0.20,        # E03
    VehicleID.DJ5363: 0.20,         # E03
    VehicleID.BQ597: 0.20,          # E03
    VehicleID.S106LS: 0.20,         # E03
    VehicleID.E03309: 0.20,         # E03
    VehicleID.E03630: 0.20,         # E03
}
