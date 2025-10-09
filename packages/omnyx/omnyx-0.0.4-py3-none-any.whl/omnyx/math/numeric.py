import numpy as np

__all__ = ['embedded_mask', 'truncate_max', 'frequency_filter',
           'crop_then_interp', 'smooth_curve', 'in_range_pos_neg_pi',
           'angle_diff']


def embedded_mask(mask1: np.ndarray, mask2: np.ndarray) -> np.ndarray:
    """
    @param mask1: boolean / indexing [N1->N2]
    @param mask2: boolean / indexing [N2->N3]
    return mask1[mask2] [N1->N3]
    """
    N = len(mask1)
    nested_mask = np.zeros(N, dtype=bool)
    nested_mask[np.arange(N, dtype=int)[mask1][mask2]] = True
    return nested_mask


def truncate_max(array: np.ndarray, max_value: float) -> np.ndarray:
    truncated_array = array.copy()
    truncated_array[array > max_value] = max_value
    return truncated_array / max_value


def frequency_filter(array: np.ndarray, min_freq: int = 5):
    _array = array.astype(int).copy()

    def _cal_freq(__array: np.ndarray):
        freq, pre = [], 0
        for cur in range(len(__array)):
            if __array[cur] != __array[pre]:
                freq.extend((cur - pre) * [cur - pre])
                pre = cur
        freq.extend((cur - pre + 1) * [cur - pre + 1])
        return np.asarray(freq, dtype=int)

    cur_freq = _cal_freq(_array)
    cur_min_freq = min(cur_freq)

    while cur_min_freq < min_freq and cur_min_freq != len(array):
        cur_val = _array[cur_min_freq == cur_freq][0]
        _array[cur_min_freq == cur_freq] = cur_val ^ 1
        cur_freq = _cal_freq(_array)
        cur_min_freq = min(cur_freq)

    return _array


def crop_then_interp(array: np.ndarray, array_mask: np.ndarray):
    _array = np.atleast_2d(array)
    _, N = _array.shape

    indices = np.arange(N)
    return np.stack([
        np.interp(indices, indices[array_mask], arr[array_mask])
        for arr in _array], axis=0)


def smooth_curve(data_np: np.ndarray, kernel_size: int):
    window = np.ones(kernel_size) / kernel_size
    _data_np = np.atleast_2d(data_np)
    _, N = _data_np.shape

    smoothed = np.stack([np.convolve(
        np.hstack([[_data[0]] * (kernel_size // 2), _data,
                   [_data[-1]] * (kernel_size - kernel_size // 2)]),
        window, mode='valid') for _data in _data_np], axis=0)
    return smoothed[:, :N]


def in_range_pos_neg_pi(data_np: np.ndarray):
    return (data_np + np.pi) % (np.pi * 2) - np.pi


def angle_diff(angle1, angle2):
    """ N1, N2 """
    _angle1 = np.atleast_1d(angle1)
    _angle2 = np.atleast_1d(angle2)
    assert len(_angle1.shape) < 2 or len(_angle2.shape) < 2
    _diff = (_angle1 - _angle2 + np.pi) % (np.pi * 2) - np.pi
    return _diff[0] if len(_diff) == 1 else _diff
