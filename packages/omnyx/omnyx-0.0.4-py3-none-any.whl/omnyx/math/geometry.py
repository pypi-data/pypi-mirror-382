from functools import reduce
from typing import List

import numpy as np
from scipy.spatial.transform import Rotation

__all__ = [
    'quaternion_to_rotvec', 'quaternion_to_rotmat', 'rotmat_to_quaternion', 'rotvec_to_quaternion',
    'rotmat_to_rotvec', 'rotvec_to_rotmat', 'transform_matrix', 'transform_offset',
    'convert_points', 'convert_boxes', 'convert_velos', 'rotations_slerp'
]


def quaternion_to_rotvec(quaternion: List[float], scalar_first: bool = False) -> np.ndarray:
    """
    scalar_first False: [qx, qy, qz, qw]
    scalar_first True: [qw, qx, qy, qz]
    """
    _quat = quaternion[1:] + quaternion[:1] if scalar_first else quaternion
    return Rotation.from_quat(_quat).as_rotvec()


def quaternion_to_rotmat(quaternion: List[float], scalar_first: bool = False) -> np.ndarray:
    """
    scalar_first False: [qx, qy, qz, qw]
    scalar_first True: [qw, qx, qy, qz]
    """
    _quat = quaternion[1:] + quaternion[:1] if scalar_first else quaternion
    return Rotation.from_quat(_quat).as_matrix()


def rotmat_to_quaternion(matrix: np.ndarray) -> np.ndarray:
    """
    return quaterion [qx, qy, qz, qw]
    """
    return Rotation.from_matrix(matrix).as_quat()


def rotvec_to_rotmat(roll: float = 0, pitch: float = 0, yaw: float = 0) -> np.ndarray:
    """ """
    return Rotation.from_rotvec([roll, pitch, yaw]).as_matrix()


def rotvec_to_quaternion(roll: float = 0, pitch: float = 0, yaw: float = 0) -> np.ndarray:
    """
    Convert roll, pitch, yaw to quaternion

    return [qx, qy, qz, qw]
    """
    return Rotation.from_rotvec([roll, pitch, yaw]).as_quat()


def rotmat_to_rotvec(matrix: np.ndarray) -> np.ndarray:
    """
    return [roll, pitch, yaw]
    """
    return Rotation.from_matrix(matrix).as_rotvec()


def transform_matrix(translation: np.ndarray = np.array([0, 0, 0]),
                     rotation: np.ndarray = np.array([0, 0, 0, 1]),
                     inverse: bool = False) -> np.ndarray:
    """
    Convert pose to transformation matrix

    @param translation: <np.float32: 3>. Translation in x, y, z.
    @param rotation: Rotation in quaternions (ri rj rk, w).
    @param inverse: Whether to compute inverse transform matrix.
    return: <np.float32: 4, 4>. Transformation matrix.
    """
    vector_T, _rotation = np.asarray(translation), np.asarray(rotation)
    matrix_R = quaternion_to_rotmat(rotation) if _rotation.shape == (4,) else _rotation

    tm = np.eye(4)
    if inverse:
        rot_inv = matrix_R.T
        tm[:3, :3] = rot_inv
        tm[:3, 3] = rot_inv.dot(-vector_T)
    else:
        tm[:3, :3] = matrix_R
        tm[:3, 3] = vector_T
    return tm


def transform_matrix_inverse(matrix: np.ndarray) -> np.ndarray:
    """
    return np.linalg.inv(matrix)
    """
    matrix_inv = np.eye(4)
    matrix_inv[:3, :3] = matrix[:3, :3].T
    matrix_inv[:3, 3] = matrix_inv[:3, :3].dot(-matrix[:3, 3].T)
    return matrix_inv


def transform_offset(src: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """
    Calculate transform from source pos to reference pos
    """
    return reduce(np.dot, [transform_matrix_inverse(ref), src])


def convert_points(
    points: np.ndarray,
    transform: np.ndarray,
    new_array: bool = True
) -> np.ndarray:
    """
    Transform points from src(current) to ref(target)

    @param points: (N, D)
    @param [src_pose, ref_pose]: [(4, 4), (4, 4)] transformation matrix
        or (4, 4) transformation matrix from src_pose to ref_pose
    """
    points_converted = points.copy() if new_array else points
    if isinstance(transform, List):
        transform = transform_offset(*transform)

    R, T = transform[:3, :3], transform[:3, 3]
    points_converted[:, :3] = np.einsum('ij,jk->ik', points[:, :3], R.T) + T
    if new_array:
        return points_converted


def convert_boxes(
    boxes: np.ndarray,
    transform: np.ndarray,
    coordinate: str = 'waymo'
) -> np.ndarray:
    """
    Transform boxes from src(current) to ref(target)

    @param boxes: (N, D)
    @param transform: (4, 4) transform from src to ref or [src_pose, ref_pose]
    @param coordinate: 'kitti' or 'waymo'
    """
    _boxes = np.asarray(boxes) if not isinstance(boxes, np.ndarray) else boxes
    if len(_boxes) == 0:
        return _boxes
    boxes_converted = np.atleast_2d(_boxes).copy()

    if isinstance(transform, List):
        transform = transform_offset(*transform)

    R, T = transform[:3, :3], transform[:3, 3]
    boxes_converted[:, :3] = np.einsum('ij,jk->ik', boxes_converted[:, :3], R.T) + T

    if coordinate == 'waymo':
        angular_transform = np.arctan2(R[1, 0], R[0, 0])
    elif coordinate == 'kitti':
        angular_transform = np.arcsin(R[2, 0])
    else:
        raise NotImplementedError

    boxes_converted[:, 6] = (boxes_converted[:, 6] + angular_transform + np.pi) % (2 * np.pi) - np.pi

    if boxes_converted.shape[0] == 1 and len(_boxes.shape) == 1:
        boxes_converted = boxes_converted.squeeze(0)
    return boxes_converted


def convert_velos(
    velos: np.ndarray,
    transform: np.ndarray
) -> np.ndarray:
    """
    Transform velos from src(current) to ref(target)

    @param velos: (N, D)
    @param transform: (4, 4) transformation matrix
    return: (N, D)
    """
    _velos = np.asarray(velos) if not isinstance(velos, np.ndarray) else velos
    converted_velos = np.atleast_2d(_velos)

    velos_dim = converted_velos.shape[1]
    if velos_dim == 2:
        converted_velos = np.hstack([converted_velos, np.zeros((len(converted_velos), 1))])

    if isinstance(transform, List):
        transform = transform_offset(*transform)

    R = transform[:3, :3]
    converted_velos = np.einsum('ij,jk->ik', converted_velos, R.T)[:, :velos_dim]

    if converted_velos.shape[0] == 1 and len(_velos.shape) == 1:
        converted_velos = converted_velos.squeeze(0)
    return converted_velos


def rotations_slerp(
    target_stamps: np.ndarray,
    key_stamps: np.ndarray,
    key_rots: np.ndarray
) -> np.ndarray:
    """Interpolate rotations.
    Compute the interpolated rotations at the given `times`.

    @param times : target_stamps
    @return interpolated_rotation : `Rotation` instance
        Object containing the rotations computed at given `times`.
    """
    # Clearly differentiate from self.times property
    compute_times = np.asarray(target_stamps)
    if compute_times.ndim > 1:
        raise ValueError('`times` must be at most 1-dimensional.')

    compute_times = np.atleast_1d(compute_times)

    # side = 'left' (default) excludes t_min.
    ind = np.searchsorted(key_stamps, compute_times) - 1
    # Include t_min. Without this step, index for t_min equals -1
    ind[compute_times == key_stamps[0]] = 0

    if np.any(np.logical_or(ind < 0, ind > len(key_rots[:-1]) - 1)):
        raise ValueError('Interpolation times must be within the range '
                         '[{}, {}], both inclusive.'.format(key_stamps[0], key_stamps[-1]))

    timedelta = np.diff(key_stamps)
    alpha = (compute_times - key_stamps[ind]) / timedelta[ind]

    key_rotations = Rotation.from_matrix(key_rots)
    rotvecs = (key_rotations[:-1].inv() * key_rotations[1:]).as_rotvec()
    key_rotations = key_rotations[:-1]

    target_rots = key_rotations[ind] * Rotation.from_rotvec(rotvecs[ind] * alpha[:, None])

    return target_rots.as_matrix()
