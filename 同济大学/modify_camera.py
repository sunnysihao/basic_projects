# _*_ coding=: utf-8 _*_
import os
import json
import numpy as np
from numpy.linalg import inv


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list


def create_external(rotation_list: list, translation_list: list):
    row = [[0, 0, 0, 1]]
    cam_r = np.array(rotation_list)
    cam_t = np.array(translation_list).reshape((3, 1))
    ext = np.hstack((cam_r, cam_t))
    ext = np.vstack((ext, row))
    return ext


ext_r = [[-0.01535546, -0.99984817, 0.00823677],
         [0.02280838, -0.00858586, -0.99970299],
         [0.99962192, -0.01516303, 0.02293675]]
ext_t = [-0.0651113, -0.37164303, 0.14304646]
cam_ext = (create_external(ext_r, ext_t)).T

data = {
            "3d_img0": {
                "camera_internal": {
                    "fx": 640.039533950044,
                    "cx": 245.216833076302,
                    "cy": 189.067845636845,
                    "fy": 645.069442501087
                },
                "camera_external": cam_ext.flatten().tolist()
            },
            "3d_img1": {
                "camera_internal": {
                    "fx": 640.039533950044,
                    "cx": 245.216833076302,
                    "cy": 189.067845636845,
                    "fy": 645.069442501087
                },
                "camera_external": cam_ext.flatten().tolist()
            }
}


def write_json(pcd_path):
    config_path = os.path.join(os.path.dirname(pcd_path), 'camera_config')
    if not os.path.exists(config_path):
        os.mkdir(config_path)
    for file in list_files(pcd_path):
        json_file = os.path.join(config_path, file + '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(data))
pcd_path = r"D:\Desktop\BasicProject\魏宏锐\data_select10\data_select10\pcd"
write_json(pcd_path)
