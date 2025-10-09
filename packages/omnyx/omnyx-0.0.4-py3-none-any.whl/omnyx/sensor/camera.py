from typing import Dict, Tuple

import cv2
import numpy as np

from ..math import (box_edge_interpolation, boxes_to_corners_3d,
                    convert_points, corners_to_edges_3d, embedded_mask,
                    truncate_max)

__all__ = ['resize_image', 'calculate_camera_fov',
           'undistort_image', 'undistort_points', 'project_camera2d',
           'point3d_to_camera2d', 'boxes3d_to_camera2d',
           'edges2d_to_outer2d', 'boxes3d_to_outer2d']


def resize_image(
    image: np.ndarray,
    resize: Tuple[int, int]
) -> np.ndarray:
    """
    Resize an image

    @param image
    @param resize: List or Tuple [width, height]
    """
    return cv2.resize(image, tuple(resize))


def calculate_camera_fov(
    camera_calib: Dict,
) -> Tuple[float, float]:
    """
    Unproject image pixels to world 3d points. Points depth value needed

    @param points_2d (N, 2)
    @param points_z (N,) or Scalar
    @param camera_intrinsics
    return points_3d (N, 3)
    """

    if camera_calib['distortion_model'] == 'pinhole':
        intrinsic_matrix, _ = cv2.getOptimalNewCameraMatrix(
            camera_calib['intrinsic_matrix'],
            camera_calib['distortion'],
            (camera_calib['width'], camera_calib['height']), 0.,
            (camera_calib['width'], camera_calib['height']))

    elif camera_calib['distortion_model'] == 'fisheye':
        intrinsic_matrix = cv2.fisheye.\
            estimateNewCameraMatrixForUndistortRectify(
            camera_calib['intrinsic_matrix'], camera_calib['distortion'],
            (camera_calib['width'], camera_calib['height']),
            None, balance=1.0)

    else:
        raise NotImplementedError(camera_calib['distortion_model'])

    return [2 * np.arctan(camera_calib['width'] / intrinsic_matrix[0, 0] / 2),
            2 * np.arctan(camera_calib['height'] / intrinsic_matrix[1, 1] / 2)]


def undistort_image(
    distorted: np.ndarray,
    camera_calib: Dict,
):

    if camera_calib['distortion_model'] == 'pinhole':
        undistorted = cv2.undistort(
            distorted,
            cameraMatrix=camera_calib['intrinsic_matrix'],
            distCoeffs=camera_calib['distortion'],
            newCameraMatrix=camera_calib['intrinsic_matrix_scaled'])

    elif camera_calib['distortion_model'] == 'fisheye':
        undistorted = cv2.fisheye.undistortImage(
            distorted,
            K=camera_calib['intrinsic_matrix'],
            D=camera_calib['distortion'],
            Knew=camera_calib['intrinsic_matrix_scaled'])

    else:
        raise NotImplementedError(camera_calib['distortion_model'])

    return undistorted


def undistort_points(
    boxes2d: np.ndarray,
    camera_calib: Dict,
) -> np.ndarray:
    if len(boxes2d) == 0:
        return boxes2d

    _boxes2d = boxes2d.reshape(-1, 2).astype(np.float32)

    if camera_calib['distortion_model'] == 'pinhole':
        undistorted = cv2.undistortPoints(_boxes2d[:, None], camera_calib['intrinsic_matrix'],
                                          camera_calib['distortion'],
                                          P=camera_calib['intrinsic_matrix_scaled'])[:, 0]

    elif camera_calib['distortion_model'] == 'fisheye':
        undistorted = cv2.fisheye.undistortPoints(_boxes2d[None],
                                                  camera_calib['intrinsic_matrix'],
                                                  camera_calib['distortion'],
                                                  P=camera_calib['intrinsic_matrix_scaled'])[0]

    else:
        raise NotImplementedError(camera_calib['distortion_model'])

    undistorted[:, 0] = np.clip(undistorted[:, 0], 0, camera_calib['width'] - 1)
    undistorted[:, 1] = np.clip(undistorted[:, 1], 0, camera_calib['height'] - 1)
    return undistorted.reshape(*boxes2d.shape).astype(boxes2d.dtype)


def project_camera2d(
    points_3d: np.ndarray,
    camera_calib: Dict,
    undistorted: bool = False,
) -> np.ndarray:
    """
    Project 3d points to 2d image plane

    @param points_3d: (N, >3)
    @param camera_model: camera model
    return (N, 3)
    """
    points_2d = points_3d.copy()

    if points_3d.shape[0] == 0:
        return points_2d

    points_2d[:, 2] = np.linalg.norm(points_3d, axis=1)

    if undistorted:
        projected_3d = (points_3d[:, :3] / points_3d[:, 2:3]).dot(
            camera_calib['intrinsic_matrix'].T)[:, None, :2]

    elif camera_calib['distortion_model'] == 'pinhole':
        projected_3d, _ = cv2.projectPoints(points_3d[:, None, :3],
                                            np.zeros(3), np.zeros(3),
                                            camera_calib['intrinsic_matrix'],
                                            camera_calib['distortion'])

    elif camera_calib['distortion_model'] == 'fisheye':
        projected_3d, _ = cv2.fisheye.projectPoints(points_3d[:, None, :3],
                                            np.zeros(3), np.zeros(3),
                                            K=camera_calib['intrinsic_matrix'],
                                            D=camera_calib['distortion'])

    else:
        raise NotImplementedError(camera_calib['distortion_model'])

    points_2d[:, :2] = 0 if projected_3d is None else projected_3d.squeeze(1)
    return points_2d


def point3d_to_camera2d(
    points: np.ndarray,
    camera_calib: Dict,
    undistorted: bool = False,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Project 3d points to 2d image pixel indices

    @param points: (N, 4)
    @param camera_calib:
        extrinsic_matrix: (4, 4) np.ndarray lidar2camera
        intrinsic_matrix: (4, 4) np.ndarray
        distortion_model: fisheye
        distortion: (4,) np.ndarray
        width: int
        height: int
    return (N, 4) rows, cols, depth(mm), color
    """
    projected_points = convert_points(points[:, :3], camera_calib['extrinsic_matrix'])
    points_color = np.linalg.norm(points[:, :2], axis=1)

    points_cos_z = projected_points[:, 2] / np.linalg.norm(projected_points[:, [0, 2]], axis=-1)
    mask_in_fov = points_cos_z >= np.cos(camera_calib['fov'][0] * 0.5)

    points_filtered = projected_points[mask_in_fov]
    points_color_filtered = points_color[mask_in_fov]

    if len(points_filtered) == 0:
        return np.zeros((0, 4), dtype=int), np.zeros_like(mask_in_fov, dtype=bool)

    points_2d = project_camera2d(points_filtered, camera_calib, undistorted)
    points_2d[..., 2] *= 10  # m -> dm

    points_color_range = 255 if np.max(points_color_filtered) > 1 else 1
    points_2d = np.hstack([points_2d, 255 * truncate_max(
        points_color_filtered[:, None], 0.2 * points_color_range)])

    mask_in_image = (points_2d[:, 0] > 0) & (points_2d[:, 0] < camera_calib['width']) & \
                    (points_2d[:, 1] > 0) & (points_2d[:, 1] < camera_calib['height'])
    points_2d = points_2d[mask_in_image].astype(int)

    return points_2d, embedded_mask(mask_in_fov, mask_in_image)


def boxes3d_to_camera2d(
    boxes3d: np.ndarray,
    camera_calib: Dict,
    num_edge_interp: int = 32,
    undistorted: bool = False,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Project 3d bounding box corner points to 2d image pixel indices

    @param box3d: (N, 7)
    @param camera_calib:
        extrinsic_matrix: (4, 4) np.ndarray lidar2camera
        intrinsic_matrix: (4, 4) np.ndarray
        distortion_model: fisheye
        distortion: (4,) np.ndarray
        width: int
        height: int
    return (N, 14, K, 3)
    """
    _boxes3d = np.zeros((0, 7)) if len(boxes3d) == 0 else np.atleast_2d(boxes3d)
    box_corners = boxes_to_corners_3d(_boxes3d)
    box_edges = corners_to_edges_3d(box_corners)  # N, 14edges, 2pts, 3dims

    _, E, P, D = box_edges.shape  # N, 14, 2, 3
    K = num_edge_interp

    edges_in_camera = convert_points(box_edges.reshape(-1, D),
        camera_calib['extrinsic_matrix']).reshape(-1, E, P, D)

    edges_in_camera_interp = box_edge_interpolation(edges_in_camera, K)
    edges3d_in_fov, mask_in_fov, mask_untrunc = clip_camera_view_outlier(
        edges_in_camera_interp, camera_calib['fov'])  # N, E, K, D

    edges2d = project_camera2d(edges3d_in_fov.reshape(-1, D), camera_calib, undistorted).reshape(-1, E, K, D)
    edges2d[..., 2] *= 10  # m -> dm

    mask_in_image = (
        (edges2d[..., 0] >= 0) & (edges2d[..., 0] < camera_calib['width']) & \
        (edges2d[..., 1] >= 0) & (edges2d[..., 1] < camera_calib['height'])
    ).reshape(-1, E * K).any(axis=1)

    edges2d = edges2d[mask_in_image].astype(int)
    edges3d = edges3d_in_fov[mask_in_image]

    edges2d[..., 0] = np.clip(edges2d[..., 0], 0, camera_calib['width'] - 1)
    edges2d[..., 1] = np.clip(edges2d[..., 1], 0, camera_calib['height'] - 1)

    mask_in_image = embedded_mask(mask_in_fov, mask_in_image)
    mask_untrunc[~mask_in_image] = False

    return dict(
        edges2d=edges2d,
        edges3d=edges3d,
        mask_in_image=mask_in_image,
        mask_untrunc=mask_untrunc,
    )


def edges2d_to_outer2d(
    edges2d: np.ndarray,
    camera_calib: Dict,
) -> np.ndarray:
    """
    Get the outer 2d box of projected 3d box

    @param edges2d: (N, 14Edge, Keypoints, Dim)
    @param camera_calib:
        extrinsic_matrix: (4, 4) np.ndarray lidar2camera
        intrinsic_matrix: (4, 4) np.ndarray
        distortion_model: fisheye
        distortion: (4,) np.ndarray
        width: int
        height: int
    """
    _, E, K, D = edges2d.shape # N, 12, interped, 4
    # edge_keypoints_2d = edges2d[:, :, K // 2, :].reshape(-1, E, D)[..., :2]
    edge_keypoints_2d = edges2d.reshape(-1, E * K, D)[..., :2]

    # left-top, right-bot
    boxes3d_outer = np.hstack([edge_keypoints_2d.min(axis=1), edge_keypoints_2d.max(axis=1)])

    boxes3d_outer[:, [0, 2]] = np.clip(boxes3d_outer[:, [0, 2]], 0, camera_calib['width'] - 1)
    boxes3d_outer[:, [1, 3]] = np.clip(boxes3d_outer[:, [1, 3]], 0, camera_calib['height'] - 1)

    return boxes3d_outer


def boxes3d_to_outer2d(
    boxes3d: np.ndarray,
    camera_calib: Dict,
):
    """
    Get the outer 2d box of projected 3d box

    @param boxes3d: (N, Dim)
    @param camera_calib:
        extrinsic_matrix: (4, 4) np.ndarray lidar2camera
        intrinsic_matrix: (4, 4) np.ndarray
        distortion_model: fisheye
        distortion: (4,) np.ndarray
        width: int
        height: int
    """
    projected_edges = boxes3d_to_camera2d(boxes3d, camera_calib)
    return dict(
        outer2d=edges2d_to_outer2d(projected_edges['edges2d'], camera_calib),
        mask_in_image=projected_edges['mask_in_image'],
        mask_untrunc=projected_edges['mask_untrunc'],
    )


def clip_camera_view_outlier(
    edges3d_in_camera: np.ndarray,
    camera_fov: Tuple[float, float],
    eps: float = 0.01,
    truncate_thr: float = 0.1,
) -> np.ndarray:
    """
    Interpolate a point whose depth is clip_depth between start point and end point.

    @param edges_in_camera: (N, K, E, 3)
    @param camera_fov: [horizontal rad, vertical rad]
    return filtered(N, 14, 2, 3), filter_indices(N)
    """
    edges_distance = np.linalg.norm(edges3d_in_camera[..., [0, 2]], axis=-1)
    fov_limit_cos = np.cos(camera_fov[0] * 0.5 + eps)
    fov_limit_sin = np.sin(camera_fov[0] * 0.5 + eps)
    N, K, E, _ = edges3d_in_camera.shape

    if N > 0:
        edges_cos_z = edges3d_in_camera[..., 2] / edges_distance # N, K, E
        edges_inside_cos_fov = edges_cos_z >= fov_limit_cos
        # fov_mask = edges_inside_cos_fov.reshape(N, -1).any(axis=1)
        fov_mask = np.sum(edges_inside_cos_fov.reshape(-1, K * E), axis=1) / (K * E) > truncate_thr
        untrunc_mask = edges_inside_cos_fov.reshape(N, -1).all(axis=1)

        project_abs_z = np.fabs(edges3d_in_camera[..., 0]) * fov_limit_cos / fov_limit_sin
        edges3d_in_camera[~edges_inside_cos_fov, 2] = project_abs_z[~edges_inside_cos_fov]
        # edges_distance < 1
        # from common.visualization import show_o3d
        # show_o3d(edges3d_in_camera[fov_mask].reshape(-1, 3))
        # import pdb; pdb.set_trace()
    else:
        fov_mask = np.zeros(N, dtype=bool)
        untrunc_mask = np.zeros(N, dtype=bool)

    edges3d_in_camera[fov_mask, ..., 2] = np.clip(
        edges3d_in_camera[fov_mask, ..., 2], a_min=0., a_max=None)
    return edges3d_in_camera[fov_mask], fov_mask, untrunc_mask
