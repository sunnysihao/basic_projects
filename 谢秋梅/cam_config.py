# _*_ coding=: utf-8 _*_
# _*_ coding=: utf-8 _*_
# _*_ coding=: utf-8 _*_
import os
import json
import numpy as np
from numpy.linalg import inv
from scipy.spatial.transform import Rotation as R


def load_json(json_path: str):
    with open(json_path) as f:
        content = f.read()
        json_content = json.load(f)
    return json_content


extrinsic1 = {
    "Tx": -0.1000000015,
    "Ty": 0.1000000015,
    "Tz": 1.6000000238,
    "Rx": -0.200000003,
    "Ry": -5.6999998093,
    "Rz": 0.1000000015
  }
extrinsic2 = {
      "Tx": -0.1000000015,
      "Ty": -0.1000000015,
      "Tz": 1.5,
      "Rx": -1.0,
      "Ry": -8.1000003815,
      "Rz": -0.8000000119
    }
extrinsic3 = {
      "Tx": -0.200000003,
      "Ty": -0.0500000007,
      "Tz": 1.6499999762,
      "Rx": -1.1000000238,
      "Ry": -4.8000001907,
      "Rz": 0.5
    }
extrinsic4 = {
      "Tx": -0.3452911,
      "Ty": 0.0823142,
      "Tz": 1.6255287,
      "Rx": -90.018716995932436,
      "Ry": -0.17601263466418343,
      "Rz": -95.944808011814644
    }

def foo(extrinsic):

    trans = np.array([extrinsic[f"T{k}"] for k in 'xyz'])
    euler = np.deg2rad([extrinsic[f"R{k}"] for k in 'xyz'])
    # rx, ry, rz = euler
    (s1, s2, s3), (c1, c2, c3) = np.sin(euler), np.cos(euler)
    Rwc = np.array([
        [c2 * s3, -s2, c2 * c3],
        [-c1 * c3 + s1 * s2 * s3, s1 * c2, c1 * s3 + s1 * s2 * c3],
        [-s1 * c3 - c1 * s2 * s3, -c1 * c2, s1 * s3 - c1 * s2 * c3],
    ])
    T = np.vstack([
        np.hstack([Rwc.T, -Rwc.T @ trans[:, None]]),  # -rot3.T @
        [[0, 0, 0, 1]]
    ])
    return T

def get_cam_config():
    lidar_ext = np.array([[0, -1, 0, 0],
                        [0, 0, -1, 0],
                        [1, 0, 0, 0],
                        [0, 0, 0, 1]])
    camera_internal = {
        "fx": 2014.3176269531,
        "cx": 970.4075927734,
        "cy": 522.5059814453,
        "fy": 2014.1853027344
    }
    cam_in2 = {
        "cx": 939.937,
        "cy": 533.26039,
        "fx": 1211.68876,
        "fy": 1219.17532,
    }
    # rx = -0.200000003
    # ry = -5.6999998093
    # rz = 0.1000000015
    # row = [[0, 0, 0, 1]]
    # t = np.array([-0.1000000015, 0.1000000015, 1.6000000238]).reshape((3, 1))
    # r = R.from_euler('xzy', [rx, ry, rz], degrees=True).as_matrix()
    # cam_ext = np.hstack((r, t))
    # cam_ext = np.vstack((cam_ext, row))
    # cam_ext = cam_ext @ lidar_ext
    cam_ext = foo(extrinsic1)
    img = {
        "camera_internal": cam_in2,
        "camera_external": inv(np.array([
      0.02958350325013815,
      -0.01162218492264161,
      0.9994947429341855,
      -0.10000000150000002,
      -0.999557277405783,
      -0.0035177688920896566,
      0.029544449346041897,
      0.1000000015,
      0.0031726204607637207,
      -0.99992627234193909,
      -0.01172110744623445,
      2.10949540899544,
      0,
      0,
      0,
      1
    ]).reshape(4, 4)).flatten().tolist()
    }
    return img



def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0].split('.')[0]
            file_list.append(file_name)
    return file_list


def set_config(pcd_path, config_path):
    for file in list_files(pcd_path):
        with open(os.path.join(config_path, file + '.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps(data))

param_file = r"D:\Desktop\BasicProject\谢秋梅\베이직 에이아이 샘플 데이터(상용 자율주행차)_221005\24_105247_220829\24_105247_220829_meta_data.json"
pcd_path = r"D:\Desktop\BasicProject\谢秋梅\data_matic_upload_1013\베이직 에이아이 샘플 데이터(상용 자율주행차)_221005\88_191512_220928\sensor_raw_data\point_cloud"
config_path = r"D:\Desktop\BasicProject\谢秋梅\data_matic_upload_1013\베이직 에이아이 샘플 데이터(상용 자율주행차)_221005\88_191512_220928\sensor_raw_data\camera_config"
img = get_cam_config()
data = {"3d_img0": img}

set_config(pcd_path, config_path)
