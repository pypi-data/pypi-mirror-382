import pickle
from pathlib import Path
from typing import Any, Dict, List

import av
import av.container
import av.video
import numpy as np
import orjson
import yaml

from ..system import logger

__all__ = [
    'write_json', 'write_text', 'write_bytes', 'write_yaml',
    'write_pickle', 'write_image', 'write_points_pcd', 'VideoWriter'
]


def _check_suffix(filepath: str, suffix: str) -> Path:
    """
    Ensure output filename with correct suffix

    return {filepath}.{suffix}
    """
    filepath_pth = Path(filepath)
    if not filepath_pth.suffix or filepath_pth.suffix != suffix:
        filepath = '{}{}'.format(filepath, suffix)
    return Path(filepath)


def write_text(filepath: str, output: Any, verbose: bool = False) -> Any:
    if verbose:
        logger.info(f'write texts file {filepath}')
    return Path(filepath).write_text(output)


def write_bytes(filepath: str, output: Any, verbose: bool = False) -> Any:
    if verbose:
        logger.info(f'write bytes file {filepath}')
    return Path(filepath).write_bytes(output)


def write_json(filepath: str, jsondict: Dict, verbose: bool = False) -> Any:
    _filepath = _check_suffix(filepath, '.json')
    if verbose:
        logger.info(f'write json file {_filepath}')
    return _filepath.write_bytes(orjson.dumps(jsondict,
        option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_INDENT_2))


def write_yaml(filepath: str, yamldict: Dict, verbose: bool = False) -> Any:
    """
    Read yaml

    @param filepath
    """
    _filepath = _check_suffix(filepath, '.yaml')
    if verbose:
        logger.info(f'write yaml file {_filepath}')
    with open(_filepath, 'w') as f:
        yaml.dump(yamldict, f)


def write_pickle(filepath: str, output: Any, verbose: bool = False) -> None:
    _filepath = _check_suffix(filepath, '.pkl')
    if verbose:
        logger.info(f'write pickle file {_filepath}')
    with open(_filepath, 'wb') as f:
        return pickle.dump(output, f)


def write_image(filepath: str, output: Any):
    import cv2
    return cv2.imwrite(filepath, output)


class VideoWriter:

    def __init__(self, filepath: str, fps: int = 10):
        self.filepath = _check_suffix(filepath, '.mp4')

        self.fps = fps
        self.is_closed = False

    def __create_container(self, img_w, img_h):
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self.container = av.container.open(self.filepath, mode='w')
        self.stream = self.container.add_stream(
            codec_name='libx264', rate=self.fps,
            options=dict(crf='23', maxrate='16M', bufsize='32M')
        )
        self.stream.pix_fmt = 'yuv420p'
        self.stream.width = img_w
        self.stream.height = img_h

    def write(self, image: np.ndarray):
        if not hasattr(self, 'container'):
            H, W, _ = image.shape
            self.__create_container(img_w=W, img_h=H)

        frame = av.video.frame.VideoFrame.from_ndarray(image, format="bgr24")
        for packet in self.stream.encode(frame):
            self.container.mux(packet)

    def close(self):
        # do not call close duplicated
        if not hasattr(self, 'container') or self.is_closed:
            return

        for packet in self.stream.encode():
            self.container.mux(packet)

        self.container.close()
        self.is_closed = True

    def __del__(self):
        self.close()


def write_points_pcd(
    filepath: str,
    output: np.ndarray,
    fields: List = ['x', 'y', 'z', 'intensity', 'timestamp'],
    viewpoint: List = None,
    verbose: bool = False
):
    _filepath = _check_suffix(filepath, '.pcd')
    from pypcd.pypcd import (PointCloud, numpy_type_to_pcd_type,
                             save_point_cloud_bin)

    field_map = {
        'x': np.dtype('float32'),
        'y': np.dtype('float32'),
        'z': np.dtype('float32'),
        'intensity': np.dtype('uint8'),
        'timestamp': np.dtype('float64'),
        'ring': np.dtype('uint8'),
    }
    pts_metadata = {
        'version': .7,
        'fields': fields,
        'size': [numpy_type_to_pcd_type[field_map[fname]][1] for fname in fields],
        'type': [numpy_type_to_pcd_type[field_map[fname]][0] for fname in fields],
        'count': [1 for _ in fields],
        'width': len(output),
        'height': 1,
        'viewpoint': [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
        'points': len(output),
        'data': 'binary',
    }

    if viewpoint is not None:
        from ..math.geometry import rotmat_to_quaternion
        pts_metadata.update(viewpoint=np.hstack([
            viewpoint[:3, 3], rotmat_to_quaternion(viewpoint[:3, :3])]).tolist())

    pc_data = np.asarray([tuple(p) for p in output],
        dtype=np.dtype([(f, field_map[f]) for f in fields]))

    pts_obj = PointCloud(pts_metadata, pc_data)
    save_point_cloud_bin(pts_obj, _filepath)
    if verbose:
        logger.info(f'write points file {_filepath}')
