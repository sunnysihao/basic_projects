# _*_ coding=: utf-8 _*_
import json
import os
import numpy as np
from scipy.spatial.transform import Rotation as R
from numpy.linalg import inv

def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0].split('.')[0]
            file_list.append(file_name)
    return file_list

x, y, z = 1.344815, -1.33410727, 1.10791928
# r = np.array([[1.344815], [-1.33410727], [1.10791928]], dtype=np.double)
r = R.from_euler('xyz', [z, y, x]).as_matrix()
t = np.array([[-0.01874443], [-0.51694852], [-1.09557176]], dtype=np.double)
# t = np.array([[0], [0], [0]])
cam_ext = np.hstack((r, t))
cam_ext = inv(np.vstack((cam_ext, [[0, 0, 0, 1]])))
data = {
            "3d_img0": {
                "camera_internal": {
                    "fx": 2122.75,
                    "cx": 913.64,
                    "cy": 563.34,
                    "fy": 2145.0252
                },
                "camera_external": [
      0.020966383487601045,
      -0.17865204396852205,
      0.98368890303251855,
      1.0721957338098427,
      -0.9997795229379981,
      -0.0026174343054357059,
      0.020833975893364328,
      -0.16844920364020466,
      -0.0011472912966666857,
      -0.98390883532140594,
      -0.17866753342214867,
      -0.6504325850320527,
      0,
      0,
      0,
      1
    ]
            }
        }

def write_json(pcd_path, config_path):
    for file in list_files(pcd_path):
        with open(os.path.join(config_path, file + '.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps(data))

pcd_path =r"D:\Desktop\BasicProject\任从辉\锐明智通\3d_url"
config_path = r"D:\Desktop\BasicProject\任从辉\锐明智通\camera_config"
write_json(pcd_path, config_path)
