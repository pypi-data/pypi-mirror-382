from typing import List

import numpy as np

# from ...math.geometry import rotmat_to_rotvec
from ..system.logging import logger
from .typedef import EgoPose, ObjectSubType

__all__ = ['pose_sanity_check', 'obstacle_sanity_check']


def pose_sanity_check(poses: List[EgoPose], std_thresh: float = 12.) -> bool:
    """ """
    timestamps_in_second = np.asarray([p['timestamp'] for p in poses], dtype=int)
    seconds, indices = np.unique(timestamps_in_second, return_inverse=True)
    locations = np.asarray([p.imu_translation for p in poses])
    # rotations = np.asarray([rotmat_to_rotvec(p.imu_rotation) for p in poses])

    std_errors = np.linalg.norm([locations[indices == i].std(axis=0)
        for i, _ in enumerate(seconds)], axis=1)

    if std_errors.max() > std_thresh:
        logger.warning(f'abnormal localization {std_errors.max(axis=0)}')
        return False

    return True


def obstacle_sanity_check(obj_size: np.ndarray, obj_type_name: str):
    is_untrust_instance = \
        untrust_type_car(obj_size, obj_type_name) or \
        untrust_type_bus(obj_size, obj_type_name) or \
        untrust_type_pickup_truck(obj_size, obj_type_name) or \
        untrust_type_truck(obj_size, obj_type_name) or \
        untrust_type_construction_vehicle(obj_size, obj_type_name) or \
        untrust_type_trailer(obj_size, obj_type_name) or \
        untrust_type_cement_mixer(obj_size, obj_type_name) or \
        untrust_type_recreational_vehicle(obj_size, obj_type_name) or \
        untrust_type_tricycle(obj_size, obj_type_name) or \
        untrust_type_motorcycle(obj_size, obj_type_name) or \
        untrust_type_bicycle(obj_size, obj_type_name) or \
        untrust_type_person(obj_size, obj_type_name)
    return not is_untrust_instance


def untrust_type_car(obj_size: np.ndarray, obj_type: str) -> bool:
    if obj_type == ObjectSubType.car.name and (
        obj_size[0] > 7.0 or obj_size[0] < 2.2 or \
        obj_size[1] > 2.7 or obj_size[1] < 1.5 or \
        obj_size[2] > 3.5 or obj_size[2] < 1.1):
        logger.debug(f'unusual car size l{obj_size[0]:.2f} w{obj_size[1]:.2f} h{obj_size[2]:.2f}')
        return True
    return False


def untrust_type_bus(obj_size: np.ndarray, obj_type: str) -> bool:
    if obj_type == ObjectSubType.bus.name and (
        obj_size[0] > 15 or obj_size[0] < 4.0 or \
        obj_size[1] > 3.7 or obj_size[1] < 2.1 or \
        obj_size[2] > 4.0 or obj_size[2] < 2.5):
        logger.debug(f'unusual bus size l{obj_size[0]:.2f} w{obj_size[1]:.2f} h{obj_size[2]:.2f}')
        return True
    return False


def untrust_type_pickup_truck(obj_size: np.ndarray, obj_type: str):
    if obj_type == ObjectSubType.pickup_truck.name and (
        obj_size[0] > 7.0 or obj_size[0] < 4.0 or \
        obj_size[1] > 3.0 or obj_size[1] < 1.5 or \
        obj_size[2] > 4.0 or obj_size[2] < 1.5):
        logger.debug(f'unusual pickup_truck size l{obj_size[0]:.2f} w{obj_size[1]:.2f} h{obj_size[2]:.2f}')
        return True
    return False


def untrust_type_truck(obj_size: np.ndarray, obj_type: str):
    if obj_type == ObjectSubType.truck.name and (
        obj_size[0] > 25 or obj_size[0] < 4.0 or \
        obj_size[1] > 4.2 or obj_size[1] < 1.6 or \
        obj_size[2] > 5.0 or obj_size[2] < 1.8):
        logger.debug(f'unusual truck size l{obj_size[0]:.2f} w{obj_size[1]:.2f} h{obj_size[2]:.2f}')
        return True
    return False


def untrust_type_construction_vehicle(obj_size: np.ndarray, obj_type: str) -> bool:
    if obj_type == ObjectSubType.construction_vehicle.name and (
        obj_size[0] > 18 or obj_size[0] < 4.0 or \
        obj_size[1] > 4.5 or obj_size[1] < 1.6 or \
        obj_size[2] > 5.0 or obj_size[2] < 1.8):
        logger.debug(f'unusual construction_vehicle size l{obj_size[0]:.2f} w{obj_size[1]:.2f} h{obj_size[2]:.2f}')
        return True
    return False


def untrust_type_trailer(obj_size: np.ndarray, obj_type: str) -> bool:
    # if obj_type == ObjectSubType.trailer.name and (
    # ):
    #     return True
    return False


def untrust_type_cement_mixer(obj_size: np.ndarray, obj_type: str) -> bool:
    if obj_type == ObjectSubType.cement_mixer.name and (
        obj_size[0] > 18 or obj_size[0] < 7.0 or \
        obj_size[1] > 4.5 or obj_size[1] < 2.0 or \
        obj_size[2] > 5.0 or obj_size[2] < 3.6):
        logger.debug(f'unusual cement_mixer size l{obj_size[0]:.2f} w{obj_size[1]:.2f} h{obj_size[2]:.2f}')
        return True
    return False


def untrust_type_recreational_vehicle(obj_size: np.ndarray, obj_type: str) -> bool:
    # if obj_type == ObjectSubType.recreational_vehicle.name and (
    # ):
    #     return True
    return False


def untrust_type_tricycle(obj_size: np.ndarray, obj_type: str) -> bool:
    if obj_type == ObjectSubType.tricycle.name and (
        obj_size[0] > 4.5 or obj_size[0] < 1.8 or \
        obj_size[1] > 1.8 or obj_size[1] < 0.8 or \
        obj_size[2] > 2.2 or obj_size[2] < 0.8):
        logger.debug(f'unusual tricycle size l{obj_size[0]:.2f} w{obj_size[1]:.2f} h{obj_size[2]:.2f}')
        return True
    return False


def untrust_type_motorcycle(obj_size: np.ndarray, obj_type: str) -> bool:
    if obj_type == ObjectSubType.motorcycle.name and (
        obj_size[0] > 3.0 or obj_size[0] < 1.0 or \
        obj_size[1] > 1.6 or obj_size[1] < 0.3 or \
        obj_size[2] > 2.0 or obj_size[2] < 0.9):
        logger.debug(f'unusual motorcycle size l{obj_size[0]:.2f} w{obj_size[1]:.2f} h{obj_size[2]:.2f}')
        return True
    return False


def untrust_type_bicycle(obj_size: np.ndarray, obj_type: str) -> bool:
    if obj_type == ObjectSubType.bicycle.name and (
        obj_size[0] > 2.2 or obj_size[0] < 0.8 or \
        obj_size[1] > 1.3 or obj_size[1] < 0.4 or \
        obj_size[2] > 2.0 or obj_size[2] < 0.8):
        logger.debug(f'unusual bicycle size l{obj_size[0]:.2f} w{obj_size[1]:.2f} h{obj_size[2]:.2f}')
        return True
    return False


def untrust_type_person(obj_size: np.ndarray, obj_type: str) -> bool:
    if obj_type == ObjectSubType.person.name and (
        obj_size[0] > 1.3 or obj_size[0] < 0.3 or \
        obj_size[1] > 1.3 or obj_size[1] < 0.3 or \
        obj_size[2] > 2.0 or obj_size[2] < 0.7):
        logger.debug(f'unusual person size l{obj_size[0]:.2f} w{obj_size[1]:.2f} h{obj_size[2]:.2f}')
        return True
    return False


def untrust_type_traffic_cone(obj_size: np.ndarray, obj_type: str) -> bool:
    if obj_type == ObjectSubType.traffic_cone.name and (
        obj_size[0] > 0.6 or obj_size[0] < 0.2 or \
        obj_size[1] > 0.6 or obj_size[1] < 0.2 or \
        obj_size[2] > 0.6 or obj_size[2] < 0.2):
        logger.debug(f'unusual traffic_cone size l{obj_size[0]:.2f} w{obj_size[1]:.2f} h{obj_size[2]:.2f}')
        return True
    return False

