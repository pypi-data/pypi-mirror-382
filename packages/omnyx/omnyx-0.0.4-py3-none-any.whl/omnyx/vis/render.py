from typing import List, Tuple

import cv2
import numpy as np

from ..math import COLORMAP_BOX_BGR_INT, COLORMAP_JET_BGR_INT

__all__ = ['draw_points', 'draw_lines', 'draw_poly_lines', 
           'draw_box2d', 'draw_box3d_edges', 'draw_texts',
           'draw_instances_2d']

CV_FONT = cv2.FONT_HERSHEY_SIMPLEX

def draw_points(
    image: np.ndarray,
    points2d: np.ndarray,
    color: int = None,
    thickness: int = 4,
) -> np.ndarray:
    assert image.dtype == np.uint8
    image_template = image.copy()
    if color is None:
        for pt in points2d:
            cv2.circle(img=image, center=tuple(pt[:2]), radius=thickness,
                       color=COLORMAP_JET_BGR_INT[pt[-1]], thickness=-1)
    else:
        points_color = COLORMAP_BOX_BGR_INT[color]
        for pt in points2d:
            cv2.circle(img=image, center=tuple(pt[:2]), radius=thickness,
                       color=points_color, thickness=-1)
    return cv2.addWeighted(image, 0.6, image_template, 0.4, 0)


def draw_lines(
    image: np.ndarray,
    points2d: np.ndarray,
    color: int = -1,
    thickness: int = 4,
) -> np.ndarray:
    assert image.dtype == np.uint8
    if isinstance(color, (int, list)):
        pt_color = color if isinstance(color, list) else COLORMAP_BOX_BGR_INT[color]
        for pt1, pt2 in points2d:
            cv2.line(img=image, pt1=tuple(pt1), pt2=tuple(pt2),
                    color=pt_color, thickness=thickness)
    else:
        for i, (pt1, pt2) in enumerate(points2d):
            cv2.line(img=image, pt1=tuple(pt1), pt2=tuple(pt2),
                    color=color[i], thickness=thickness)
    return image


def draw_poly_lines(
    image: np.ndarray,
    points2d: np.ndarray,
    color: int = -1,
    thickness: int = 4,
) -> np.ndarray:
    assert image.dtype == np.uint8
    if isinstance(color, int):
        pt_color = COLORMAP_BOX_BGR_INT[color]
        for i in range(1, len(points2d)):
            cv2.line(img=image, pt1=tuple(points2d[i - 1, :2]), pt2=tuple(points2d[i, :2]),
                     color=pt_color, thickness=thickness)
    else:
        for i in range(1, len(points2d)):
            cv2.line(img=image, pt1=tuple(points2d[i - 1, :2]), pt2=tuple(points2d[i, :2]),
                     color=COLORMAP_BOX_BGR_INT[color[i]], thickness=thickness)
    return image


def draw_box2d(
    image: np.ndarray,
    boxes2d: np.ndarray,
    color: int = -1,
    thickness: int = None,
) -> None:
    assert image.dtype == np.uint8
    H, W = image.shape[:2]
    if thickness is None:
        thickness = int(np.sqrt(H * W)) // 240
    image_template = image.copy()

    if isinstance(color, int):
        box_color = COLORMAP_BOX_BGR_INT[color]
        for box2d in np.atleast_2d(boxes2d):
            cv2.rectangle(image, tuple(box2d[:2]), tuple(box2d[2:]),
                          color=box_color, thickness=thickness)
    else:
        for i in range(len(boxes2d)):
            cv2.rectangle(image, tuple(boxes2d[i][:2]), tuple(boxes2d[i][2:]),
                          color=COLORMAP_BOX_BGR_INT[color[i]], thickness=thickness)

    return cv2.addWeighted(image, 0.6, image_template, 0.4, 0)


def draw_box3d_edges(
    image: np.ndarray,
    edges2d: np.ndarray,
    color: int = -1,
    thickness: int = 4,
) -> np.ndarray:
    """
    @param edges_3d: (N, 14-Edges, Keypoints, Dim)
    """
    assert image.dtype == np.uint8
    image_template = image.copy()

    if isinstance(color, int):
        box_color = COLORMAP_BOX_BGR_INT[color]
        for edges in edges2d:
            for interped_line in edges:
                for i in range(1, len(interped_line)):
                    cv2.line(image,
                             tuple(interped_line[i - 1][:2]),
                             tuple(interped_line[i][:2]),
                             color=box_color, thickness=thickness)
    else:
        for j in range(len(edges2d)):
            for interped_line in edges2d[j]:
                for i in range(1, len(interped_line)):
                    cv2.line(image,
                             tuple(interped_line[i - 1][:2]),
                             tuple(interped_line[i][:2]),
                             color=COLORMAP_BOX_BGR_INT[color[j]], thickness=thickness)

    return cv2.addWeighted(image, 0.6, image_template, 0.4, 0)


def draw_texts(
    image: np.ndarray,
    texts: List[str],
    poses2d: List[Tuple] = None,
    boxes2d: np.ndarray = None,
    color: int = -1,
    fontscale: int = 4,
    thickness: int = 6
) -> np.ndarray:
    """ """
    assert image.dtype == np.uint8
    text_color = COLORMAP_BOX_BGR_INT[color] if isinstance(color, int) else color

    if poses2d is not None:
        for i, pos in enumerate(poses2d):
            cv2.putText(image, texts[i], tuple(pos), CV_FONT,
                        fontScale=fontscale, color=text_color,
                        thickness=thickness)
    elif boxes2d is not None:
        for i, box2d in enumerate(np.atleast_2d(boxes2d)):
            cv2.putText(image, texts[i], (box2d[0] + int((box2d[2] - box2d[0]) * 0.01), box2d[1]),
                CV_FONT, fontScale=fontscale,
                color=text_color, thickness=thickness)
    else:
        top_left_pos = [10, 18 * thickness]
        for text in texts:
            cv2.putText(image, text, tuple(top_left_pos), CV_FONT,
                        fontScale=fontscale, color=text_color,
                        thickness=thickness)
            top_left_pos[1] += 30 * fontscale

    return image


def draw_instances_2d(
    image: np.ndarray = None,
    edges3d: np.ndarray = None,
    labels3d: np.ndarray = None,
    boxes2d: np.ndarray = None,
    labels2d: np.ndarray = None,
    texts: np.ndarray = None,
    flip_horizontal: bool = False,
) -> np.ndarray:
    """
    @param box3d: (N, 14-Edges, Keypoints, Dim)
    @param box2d: (N, 4) left-top-right-bot
    @param flip_horizontal: [u, v] -> [W - u, v]
    """
    H, W = image.shape[:2]
    image = image if image.dtype == np.uint8 else image.astype(np.uint8)

    if edges3d is not None:
        _labels3d = -1 if labels3d is None else labels3d
        image = draw_box3d_edges(image, edges3d, color=_labels3d, thickness=int(np.sqrt(H * W)) // 200)

    if flip_horizontal:
        image = np.ascontiguousarray(image[:, ::-1])

    if boxes2d is not None and len(boxes2d) > 0:
        _boxes2d = np.atleast_2d(boxes2d).astype(int)
        _labels2d = -1 if labels2d is None else labels2d
        if flip_horizontal:
            box2d_template = _boxes2d.copy()
            _boxes2d[:, [0, 2]] = W - box2d_template[:, [0, 2]]
        image = draw_box2d(image, _boxes2d, color=_labels2d, thickness=int(np.sqrt(H * W)) // 200)

    if texts is not None:
        if boxes2d is not None:
            _boxes2d = boxes2d
        elif edges3d is not None:
            N, E, K, D = edges3d.shape
            _edges3d = edges3d.reshape(N, E * K, D)[..., :2]
            _boxes2d = np.hstack([_edges3d.min(axis=1), _edges3d.max(axis=1)]).astype(int)

        if flip_horizontal:
            box2d_template = _boxes2d.copy()
            _boxes2d[:, [0, 2]] = W - box2d_template[:, [0, 2]]

        draw_texts(image, texts, boxes2d=_boxes2d,
                   fontscale=int(np.sqrt(H * W)) // 720,
                   thickness=int(np.sqrt(H * W)) // 300)

    return image
