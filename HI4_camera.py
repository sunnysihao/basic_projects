# _*_ coding=: utf-8 _*_
import os
import json
import numpy as np
from scipy.spatial.transform import Rotation as R
from numpy.linalg import inv

def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list

row = [[0, 0, 0, 1]]
z, y, x = np.pi/180*(-3.0), np.pi/180*(-22.75), 0.0
cam_r = R.from_euler('zyx', [z, y, x]).as_matrix()
cam_t = np.array([[2.04], [0.14], [2.1]])
cam_ext = np.hstack((cam_r, cam_t))
camera_external = (np.vstack((cam_ext, row))).flatten().tolist()
data = {
        "3d_img0": {
            "camera_internal": {
                "fx": 362.5,
                "cx": 320.0,
                "cy": 180.0,
                "fy": 362.5
            },
            "camera_external": camera_external
        }
    }

def write_json(pcd_path):
    result_path = os.path.join(os.path.dirname(pcd_path), 'camera_config')
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    for file in list_files(pcd_path):
        with open(os.path.join(result_path, file + '.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps(data))


if __name__ == "__main__":
    pcd_path = r"D:\Desktop\BasicProject\张子千\3d_url"
    write_json(pcd_path)