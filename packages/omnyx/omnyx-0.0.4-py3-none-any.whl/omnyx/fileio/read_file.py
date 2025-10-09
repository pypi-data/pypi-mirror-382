import pickle
from functools import wraps
from pathlib import Path
from typing import Any, Callable, List

import numpy as np
import orjson

from ..system.logging import logger

__all__ = [
    'read_pickle', 'read_json', 'read_yaml', 'read_text', 'read_bytes',
    'read_image', 'read_numpy_bin', 'read_points_pcd', 'check_filepath'
]


def check_filepath(func: Callable, *args, **kwargs):
    """
    Ensure filepath type & check if the file exist

    @func (Callable[str]): The function to decorate
    return Callable[Path]: A wrapper function.
    """
    def _check_filepath(filepath: str, *, strict: bool = True, no_warning: bool = False) -> Path:
        _filepath = filepath if isinstance(filepath, Path) else Path(filepath)
        if _filepath.exists():
            return _filepath
        elif not no_warning:
            logger.warning(f"The path {_filepath} does not exist.")
        if strict:
            raise FileNotFoundError(f"The path {filepath} does not exist.")

    @wraps(func)
    def wrapper(filepath: str, *args, strict: bool = True, verbose: bool = False, no_warning: bool = False, **kwargs):
        _filepath = _check_filepath(filepath, strict=strict, no_warning=no_warning)
        if verbose:
            logger.debug('Read file', _filepath.absolute())
        if _filepath is None:
            return None
        return func(_filepath, *args, **kwargs)

    if isinstance(func, (str, Path)):
        return _check_filepath(func, *args, **kwargs)
    return wrapper


@check_filepath
def read_pickle(filepath: Path) -> Any:
    """
    Read content from a pickle file

    @param filepath: path to pickle file
    """
    with open(filepath, 'rb') as f:
        pkl_dict = pickle.load(f)
    return pkl_dict


@check_filepath
def read_json(filepath: Path) -> Any:
    """
    Read jsondict

    @param filepath: path to json file
    """
    return orjson.loads(filepath.read_bytes())


@check_filepath
def read_text(filepath: Path) -> Any:
    """
    Read plain ascii texts

    @param filepath
    """
    return filepath.read_text().splitlines()


@check_filepath
def read_bytes(filepath: Path) -> Any:
    """
    Read file in bytes

    @param filepath
    """
    return filepath.read_bytes().splitlines()


@check_filepath
def read_yaml(filepath: Path) -> Any:
    """
    Read yaml
    
    @param filepath
    """
    import yaml
    return yaml.safe_load(filepath.read_text())


@check_filepath
def read_numpy_bin(filepath: Path, dtype: type = np.float32) -> np.ndarray:
    return np.fromfile(filepath, dtype=dtype)


@check_filepath
def read_image(filepath: Path, flags: int = None) -> np.ndarray:
    import cv2
    return cv2.imread(str(filepath), flags=flags)


@check_filepath
def read_points_pcd(
    filepath: Path,
    fields: List = ['x', 'y', 'z', 'intensity', 'timestamp'],
    viewpoint: bool = False,
) -> np.ndarray:
    from pypcd2 import pypcd
    pcd = pypcd.point_cloud_from_path(filepath)

    pcd_metadata = pcd.get_metadata()
    data_length = len([_ for _ in pcd_metadata['fields'] if _ != '_' and _ in fields])
    data_np = np.zeros((pcd_metadata['width'], data_length), dtype=float)

    for name in pcd_metadata['fields']:
        if name not in fields:
            continue
        data_np[:, fields.index(name)] = pcd.pc_data[name]

    if viewpoint:
        from ..math.geometry import quaternion_to_rotmat, transform_matrix
        return data_np, transform_matrix(
            pcd_metadata['viewpoint'][:3],
            quaternion_to_rotmat(pcd_metadata['viewpoint'][3:]))

    return data_np
