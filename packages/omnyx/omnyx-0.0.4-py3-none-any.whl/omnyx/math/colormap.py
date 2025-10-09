import numpy as np
from matplotlib import cm

__all__ = ['COLORMAP_BOX', 'COLORMAP_BOX_INT', 'COLORMAP_BOX_BGR', 'COLORMAP_BOX_BGR_INT',
           'COLORMAP_JET', 'COLORMAP_JET_INT', 'COLORMAP_JET_BGR_INT']


def random_colors(num_colors: int, seed: int=69, dtype: str='uint') -> np.array:
    np.random.seed(seed)
    colors_in_string = ['{:06x}'.format(
        np.floor(np.random.rand() * 0x1000000).astype(int)
    ) for _ in range(num_colors)]
    colors_in_string[-1] = 'ffffff'

    colors_in_uint = np.array([
            [int(_c[n * 2:n * 2 + 2], 16) for n in range(3)]
        for _c in colors_in_string])

    if dtype == 'uint':
        return colors_in_uint
    elif dtype == 'float':
        return colors_in_uint / 255.
    else:
        raise ProcessLookupError


COLORMAP_BOX = random_colors(2 ** 14, dtype='float').tolist() # 1=yellow 2=green 3=blue
COLORMAP_BOX_INT = random_colors(2 ** 14, dtype='uint').tolist()

COLORMAP_BOX_BGR = random_colors(2 ** 14, dtype='float')[:, ::-1].tolist()
COLORMAP_BOX_BGR_INT = random_colors(2 ** 14, dtype='uint')[:, ::-1].tolist()

COLORMAP_JET = cm.get_cmap('jet')(np.linspace(0, 1, 256))[:, :3].astype(np.uint8)
COLORMAP_JET_INT = (cm.get_cmap('jet')(np.linspace(0, 1, 256)) * 255)[:, :3].astype(np.uint8)
COLORMAP_JET_BGR_INT = (cm.get_cmap('jet')(np.linspace(0, 1, 256)) * 255)[:, 2::-1].astype(np.uint8)
