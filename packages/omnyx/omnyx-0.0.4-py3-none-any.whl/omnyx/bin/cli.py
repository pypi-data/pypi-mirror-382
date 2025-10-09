from argparse import ArgumentParser
from pathlib import Path
from typing import List

import numpy as np
from tqdm import tqdm

import omnyx


class OmnyxInterface:

    def __init__(self):
        parser = ArgumentParser()
        parser.add_argument('command', type=str)
        parser.add_argument('filepath', type=Path)

        options = parser.parse_args()
        getattr(self, options.command)(**vars(options))

    @staticmethod
    def show_points(filepath: Path, **whatever):
        omnyx.show_o3d(omnyx.read_points(filepath))

    @staticmethod
    def chery_one_frame(
        frame_id: str,
        annotation_info: omnyx.ClipInfo,
        ego_poses: List,
        project_lidar: bool,
    ):
        frame_info = annotation_info.frames[frame_id]
        camera_names = omnyx.CHERY_SENSOR_TYPE_CAMERA if project_lidar \
            else [omnyx.SensorName(sensor) for sensor in frame_info.objects \
                if omnyx.SensorName(sensor) in omnyx.CHERY_SENSOR_TYPE_CAMERA]

        ego_locs = [] if frame_info.lidar2slam is None else [
            omnyx.convert_points(np.asarray([[0., 0., 0.], [1., 0., 0.]]),
            [pose, frame_info.lidar2slam]) for pose in ego_poses]

        proj_boxes3d = {
            camera_name: omnyx.boxes3d_to_camera2d(
                frame_info.lidar_boxes3d() if project_lidar else
                    frame_info.camera_boxes3d(),
                    annotation_info.calibrations[camera_name])
            for camera_name in camera_names
        }

        return omnyx.show_bev_with_camera(
            clip_name=annotation_info.clip_name,
            frame_info=frame_info,
            calibration=annotation_info.calibrations,
            boxes_info=dict(
                boxes3d=frame_info.lidar_boxes3d(),
                texts=frame_info.track_ids().astype(str),
                velos=frame_info.lidar_velos3d(),
                edges3d={camera_name: proj_boxes3d[camera_name]['edges2d']
                    for camera_name in camera_names},
                labels3d={camera_name: frame_info.obj_types()[proj_boxes3d[camera_name]['mask_in_image']]
                    for camera_name in camera_names},
                boxes2d={camera_name: frame_info.camera_boxes2d(camera_name).astype(int)
                    for camera_name in camera_names},
                texts2d={camera_name: frame_info.track_ids(camera_name).astype(str)
                    for camera_name in camera_names},
            ),
            polygons_info={'key_points': ego_locs},
            # main_lidar=MAIN_LIDAR_COMPENSATED,
        )

    @classmethod
    def chery_format(cls, annotation_path: str, project_lidar: bool = False, **kwargs) -> bool:
        annotation_info = omnyx.get_chery_info(anno_path=annotation_path, **kwargs)
        ego_poses = [ann.lidar2slam for ann in annotation_info.frames.values()]

        return omnyx.multi_process_thread(cls.zdrive_one_frame,
            [[frame_id, annotation_info, ego_poses, project_lidar] for frame_id
             in annotation_info.frames], nprocess=1)

    @staticmethod
    def qcraft_one_frame(
        frame_id: int,
        clip_info: omnyx.ClipInfo,
        # ego_poses: List,
        project_lidar: bool,
    ):
        frame_info = clip_info.frames[frame_id]

        concat_pts = []
        for sensor_name, sensor_path in frame_info.sensor_filepaths.items():
            if sensor_name in omnyx.QCRAFT_SENSOR_TYPE_LIDAR:
                concat_pts.append(omnyx.read_points(sensor_path))
        frame_info.sensor_filepaths[omnyx.CHERY_MAIN_SENSOR_LIDAR] = np.vstack(concat_pts)

        # ego_locs = [] if frame_info.lidar2slam is None else [
        #     omnyx.convert_points(np.asarray([[0., 0., 0.], [1., 0., 0.]]),
        #     [pose, frame_info.lidar2slam]) for pose in ego_poses]

        # proj_boxes3d = {
        #     camera_name: omnyx.boxes3d_to_camera2d(
        #         frame_info.lidar_boxes3d() if project_lidar else
        #             frame_info.camera_boxes3d(),
        #             clip_info.calibrations[camera_name])
        #     for camera_name in camera_names
        # }

        return omnyx.show_bev_with_camera(
            clip_name=clip_info.clip_name,
            frame_info=frame_info,
            calibration=clip_info.calibrations,
            boxes_info=dict(
                boxes3d=frame_info.lidar_boxes3d(omnyx.CHERY_MAIN_SENSOR_LIDAR),
                # labels3d={camera_name: frame_info.obj_types()[omnyx.proj_boxes3d[camera_name]['mask_in_image']]
                #     for camera_name in camera_names},
            ),
            camera_names=omnyx.OBJECT_SUBTYPE_TO_TYPE
        )

    @classmethod
    def show_qcraft(
        cls,
        filepath: Path,
        project_lidar: bool = False,
        **whatever
    ):
        clip_info = omnyx.get_qcraft_info(filepath)
        # ego_poses = [info.lidar2slam for info in clip_info.frames.values()]

        visualizations = omnyx.multi_process_thread(cls.qcraft_one_frame,
            [[frame_id, clip_info, project_lidar] for frame_id in clip_info.frames],
            nprocess=8, progress_desc='write image')
        video_writer = omnyx.VideoWriter(f'output/{clip_info.clip_name}.mp4')
        [video_writer.write(f) for f in tqdm(visualizations, desc='write video')]
        video_writer.close()


if __name__ == '__main__':
    OmnyxInterface()