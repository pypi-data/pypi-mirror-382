import numba
import numpy as np

__all__ = [
    'boxes2d_to_center_wh', 'center_wh_to_boxes2d', 'rotation_3d_in_axis',
    'boxes_to_corners_3d', 'corners_to_edges_3d', 'corners_to_edges_2d',
    'box_edge_interpolation', 'points_in_rbbox']


def boxes2d_to_center_wh(boxes2d: np.ndarray) -> np.ndarray:
    return np.asarray([
        [(boxes2d[..., 0] + boxes2d[..., 2]) / 2,
         (boxes2d[..., 1] + boxes2d[..., 3]) / 2],
        [np.abs(boxes2d[..., 0] - boxes2d[..., 2]),
         np.abs(boxes2d[..., 1] - boxes2d[..., 3])],
    ]).astype(boxes2d.dtype)


def center_wh_to_boxes2d(center_wh: np.ndarray) -> np.ndarray:
    return np.asarray([
        [center_wh[..., 0] - center_wh[..., 2] / 2,
         center_wh[..., 1] - center_wh[..., 3] / 2],
        [center_wh[..., 0] + center_wh[..., 2] / 2,
         center_wh[..., 1] + center_wh[..., 3] / 2],
    ]).astype(center_wh.dtype)


def rotation_3d_in_axis(points: np.ndarray, angles: np.ndarray, axis: int = 2) -> np.ndarray:
    """
    @param points: [N, 8, 3]
    @param axis: 0 = pitch, 1 = roll, 2 = yaw
    
    """
    rot_sin, rot_cos = np.sin(angles), np.cos(angles)
    ones = np.ones_like(rot_cos)
    zeros = np.zeros_like(rot_cos)

    if axis == 1:
        rot_mat_T = np.stack([
            [rot_cos, zeros, -rot_sin],
            [zeros, ones, zeros],
            [rot_sin, zeros, rot_cos],
        ])
    elif axis == 2 or axis == -1:
        rot_mat_T = np.stack([
            [rot_cos, rot_sin, zeros],
            [-rot_sin, rot_cos, zeros],
            [zeros, zeros, ones],
        ])
    elif axis == 0:
        rot_mat_T = np.stack([
            [zeros, rot_cos, -rot_sin],
            [zeros, rot_sin, rot_cos],
            [ones, zeros, zeros],
        ])
    else:
        raise ValueError("axis should in range")
    return np.einsum("aij,jka->aik", points, rot_mat_T)


def boxes_to_corners_3d(boxes3d: np.ndarray) -> np.ndarray:
    """
          7 -------- 4
         /|         /|
        6 -------- 5 .
        | |        | |
        . 3 -------- 0
        |/         |/   -> x
        2 -------- 1
    @param boxes3d: (N, 7) [x, y, z, dx, dy, dz, heading], (x, y, z) is the box center
    @return (N, 8, 3)
    """
    boxes3d = np.atleast_2d(boxes3d)
    template = np.asarray([[1, 1, -1], [1, -1, -1], [-1, -1, -1], [-1, 1, -1],
                           [1, 1, 1], [1, -1, 1], [-1, -1, 1], [-1, 1, 1]]) * 0.5

    corners3d = boxes3d[:, None, 3:6].repeat(8, 1) * template[None, :, :]
    corners3d = rotation_3d_in_axis(corners3d, boxes3d[:, 6], axis=2)

    corners3d += boxes3d[:, None, :3]
    return corners3d


def corner_to_surfaces_3d(corners):
    """convert 3d box corners from corner function above
    to surfaces that normal vectors all direct to internal.

    Args:
        corners (float array, [N, 8, 3]): 3d box corners.
    Returns:
        surfaces (float array, [N, 6, 4, 3]):
    """
    # box_corners: [N, 8, 3], must from corner functions in this module
    return np.asarray([
        [corners[:, 0], corners[:, 1], corners[:, 2], corners[:, 3]],
        [corners[:, 7], corners[:, 6], corners[:, 5], corners[:, 4]],
        [corners[:, 0], corners[:, 3], corners[:, 7], corners[:, 4]],
        [corners[:, 1], corners[:, 5], corners[:, 6], corners[:, 2]],
        [corners[:, 0], corners[:, 4], corners[:, 5], corners[:, 1]],
        [corners[:, 3], corners[:, 2], corners[:, 6], corners[:, 7]],
    ]).transpose([2, 0, 1, 3])


def corners_to_edges_3d(corners: np.ndarray) -> np.ndarray:
    """
    @param corners (float array, [N, 8, 3]): 3d box corners
    @return edges (float array, [N, 14, 2, 3]):
    """
    return np.asarray([
            [corners[:, 0], corners[:, 1]], [corners[:, 1], corners[:, 2]],
            [corners[:, 2], corners[:, 3]], [corners[:, 3], corners[:, 0]],
            [corners[:, 4], corners[:, 5]], [corners[:, 5], corners[:, 6]],
            [corners[:, 6], corners[:, 7]], [corners[:, 7], corners[:, 4]],
            [corners[:, 0], corners[:, 4]], [corners[:, 1], corners[:, 5]],
            [corners[:, 2], corners[:, 6]], [corners[:, 3], corners[:, 7]],
            [corners[:, 0], corners[:, 5]], [corners[:, 1], corners[:, 4]],
        ]).transpose([2, 0, 1, 3])


def corners_to_edges_2d(corners):
    """
    @param corners (float array, [N, 4, 2]): 3d box corners
    @return edges (float array, [N, 4, 2, 2]):
    """
    edges = np.array([
            [corners[:, 0], corners[:, 1]], [corners[:, 1], corners[:, 2]],
            [corners[:, 2], corners[:, 3]], [corners[:, 3], corners[:, 0]]
        ]).transpose([2, 0, 1, 3])
    return edges


def box_edge_interpolation(box_edges: np.ndarray, num_points: int = 10) -> np.ndarray:
    """
    Linear interpolate functions.

    @param bbox_edges: (N, E, 2-keypoints, 3)
    return (N, E, interped-keyponits, 2)
    """
    interped_edges = np.linspace(box_edges[:, :, 0, :],
                                 box_edges[:, :, 1, :], max(num_points, 2))
    return interped_edges.transpose(1, 2, 0, 3)


def points_in_rbbox(points: np.ndarray, rbbox: np.ndarray):
    """ """
    rbbox_corners = boxes_to_corners_3d(np.atleast_2d(rbbox))
    surfaces = corner_to_surfaces_3d(rbbox_corners)
    return points_in_convex_polygon_3d_jit(points[:, :3], surfaces)


def points_in_convex_polygon_3d_jit(points, polygon_surfaces, num_surfaces=None):
    """check points is in 3d convex polygons.
    Args:
        points: [num_points, 3] array.
        polygon_surfaces: [num_polygon, max_num_surfaces,
            max_num_points_of_surface, 3]
            array. all surfaces' normal vector must direct to internal.
            max_num_points_of_surface must at least 3.
        num_surfaces: [num_polygon] array. indicate how many surfaces
            a polygon contain
    Returns:
        [num_points, num_polygon] bool array.
    """
    # max_num_surfaces, max_num_points_of_surface = polygon_surfaces.shape[1:3]
    # num_points = points.shape[0]
    num_polygons = polygon_surfaces.shape[0]
    if num_surfaces is None:
        num_surfaces = np.full((num_polygons,), 9999999, dtype=np.int64)
    normal_vec, d = surface_equ_3d_jitv2(polygon_surfaces[:, :, :3, :])
    # normal_vec: [num_polygon, max_num_surfaces, 3]
    # d: [num_polygon, max_num_surfaces]
    return _points_in_convex_polygon_3d_jit(points, polygon_surfaces, normal_vec, d, num_surfaces).T


@numba.njit
def _points_in_convex_polygon_3d_jit(points, polygon_surfaces, normal_vec, d, num_surfaces=None):
    """check points is in 3d convex polygons.
    Args:
        points: [num_points, 3] array.
        polygon_surfaces: [num_polygon, max_num_surfaces,
            max_num_points_of_surface, 3]
            array. all surfaces' normal vector must direct to internal.
            max_num_points_of_surface must at least 3.
        num_surfaces: [num_polygon] array. indicate how many surfaces
            a polygon contain
    Returns:
        [num_points, num_polygon] bool array.
    """
    max_num_surfaces, max_num_points_of_surface = polygon_surfaces.shape[1:3]
    num_points = points.shape[0]
    num_polygons = polygon_surfaces.shape[0]
    ret = np.ones((num_points, num_polygons), dtype=np.bool_)
    sign = 0.0
    for i in range(num_points):
        for j in range(num_polygons):
            for k in range(max_num_surfaces):
                if k > num_surfaces[j]:
                    break
                sign = (points[i, 0] * normal_vec[j, k, 0] + points[i, 1] * normal_vec[j, k, 1] +
                        points[i, 2] * normal_vec[j, k, 2] + d[j, k])
                if sign >= 0:
                    ret[i, j] = False
                    break
    return ret


@numba.njit
def surface_equ_3d_jitv2(surfaces):
    # polygon_surfaces: [num_polygon, num_surfaces, num_points_of_polygon, 3]
    num_polygon = surfaces.shape[0]
    max_num_surfaces = surfaces.shape[1]
    normal_vec = np.zeros((num_polygon, max_num_surfaces, 3), dtype=surfaces.dtype)
    d = np.zeros((num_polygon, max_num_surfaces), dtype=surfaces.dtype)
    sv0 = surfaces[0, 0, 0] - surfaces[0, 0, 1]
    sv1 = surfaces[0, 0, 0] - surfaces[0, 0, 1]
    for i in range(num_polygon):
        for j in range(max_num_surfaces):
            sv0[0] = surfaces[i, j, 0, 0] - surfaces[i, j, 1, 0]
            sv0[1] = surfaces[i, j, 0, 1] - surfaces[i, j, 1, 1]
            sv0[2] = surfaces[i, j, 0, 2] - surfaces[i, j, 1, 2]
            sv1[0] = surfaces[i, j, 1, 0] - surfaces[i, j, 2, 0]
            sv1[1] = surfaces[i, j, 1, 1] - surfaces[i, j, 2, 1]
            sv1[2] = surfaces[i, j, 1, 2] - surfaces[i, j, 2, 2]
            normal_vec[i, j, 0] = sv0[1] * sv1[2] - sv0[2] * sv1[1]
            normal_vec[i, j, 1] = sv0[2] * sv1[0] - sv0[0] * sv1[2]
            normal_vec[i, j, 2] = sv0[0] * sv1[1] - sv0[1] * sv1[0]

            d[i, j] = (-surfaces[i, j, 0, 0] * normal_vec[i, j, 0] - surfaces[i, j, 0, 1] * normal_vec[i, j, 1] -
                       surfaces[i, j, 0, 2] * normal_vec[i, j, 2])
    return normal_vec, d
