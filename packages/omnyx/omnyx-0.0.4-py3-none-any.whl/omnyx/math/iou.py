import numba
import numpy as np

__all__ = ['boxes2d_iou']


@numba.jit(nopython=True)
def boxes2d_iou(boxes1: np.ndarray, boxes2: np.ndarray, eps: float=1.0):
    """calculate box iou. note that jit version runs 2x faster than cython
    @param boxes: [N1, 4] [N2, 4] xmin, ymin, xmax, ymax
    return overlaps: [N1, N2] ndarray of overlap between boxes1 and boxes2
    """
    N1, N2 = boxes1.shape[0], boxes2.shape[0]
    overlaps = np.zeros((N1, N2))
    for n2 in range(N2):
        box_area = (boxes2[n2, 2] - boxes2[n2, 0] + eps) * \
                   (boxes2[n2, 3] - boxes2[n2, 1] + eps)
        for n1 in range(N1):
            iw = min(boxes1[n1, 2], boxes2[n2, 2]) - \
                 max(boxes1[n1, 0], boxes2[n2, 0]) + eps
            if iw > 0:
                ih = min(boxes1[n1, 3], boxes2[n2, 3]) - \
                     max(boxes1[n1, 1], boxes2[n2, 1]) + eps
                if ih > 0:
                    ua = (boxes1[n1, 2] - boxes1[n1, 0] + eps) * \
                         (boxes1[n1, 3] - boxes1[n1, 1] + eps) + \
                          box_area - iw * ih
                    overlaps[n1, n2] = iw * ih / ua
    return overlaps
