from pathlib import Path
from shutil import copy, copytree, rmtree
from typing import List

import numpy as np

from ..system.logging import logger
from .read_file import *
from .write_file import *


def read_points(filepath: Path, **kwargs) -> np.ndarray:
    """ """
    _filepath = filepath if isinstance(filepath, Path) else Path(filepath)
    ext_dict = {
        '.pcd': read_points_pcd,
    }
    return ext_dict[Path(_filepath).suffix](_filepath, **kwargs)


def mkdir(dirpath: Path, verbose: bool = False) -> Path:
    _dirpath = dirpath if isinstance(dirpath, Path) else Path(dirpath)
    if not _dirpath.exists():
        _dirpath.mkdir(parents=True, exist_ok=True)
        if verbose:
            logger.info(f'make directory {_dirpath.resolve()}')
    return _dirpath


def lsdir(dirpath: Path, pattern: str = '*', return_str=False) -> List[Path]:
    _dirpath = dirpath if isinstance(dirpath, Path) else Path(dirpath)
    path_type = str if return_str else Path
    return sorted([path_type(n) for n in _dirpath.glob(pattern)])


def emptydir(dirpath: Path, verbose: bool = True) -> Path:
    _dirpath = dirpath if isinstance(dirpath, Path) else Path(dirpath)
    if verbose:
        logger.info(f'empty directory {_dirpath}')
    if not _dirpath.exists():
        _dirpath = mkdir(_dirpath, exist_ok=True)

    for _dir in lsdir(_dirpath):
        if _dir.is_symlink() or _dir.is_file():
            _dir.unlink()
        elif _dir.is_dir():
            rmdir(_dir, verbose=False)
    return _dirpath


def rmdir(dirpath: Path, verbose: bool = False) -> Path:
    _dirpath = dirpath if isinstance(dirpath, Path) else Path(dirpath)
    if _dirpath.exists():
        if verbose:
            logger.info(f'remove directory {_dirpath}')
        if _dirpath.is_dir():
            emptydir(_dirpath, verbose=False)
            rmtree(_dirpath)
        else:
            _dirpath.unlink()
    return _dirpath


def cpdir(dirpath: Path, tgtpath: Path, verbose: bool = False) -> Path:
    _dirpath = dirpath if isinstance(dirpath, Path) else Path(dirpath)
    _tgtpath = tgtpath if isinstance(tgtpath, Path) else Path(tgtpath)
    if _dirpath.exists():
        if verbose:
            logger.info(f'copy filepath {_dirpath} to {tgtpath}')
        if _tgtpath.exists():
            rmdir(_tgtpath)
        if _dirpath.is_dir():
            copytree(_dirpath, tgtpath)
        else:
            copy(_dirpath, tgtpath)
    return _tgtpath