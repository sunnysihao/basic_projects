import json
import os
import re
import numpy as np
from tqdm import tqdm
from PIL import Image
from numpy.linalg import inv
from scipy.spatial.transform import Rotation as R


def list_files(in_path: str, suffix_match: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == f'.{suffix_match}':
                file_list.append(os.path.join(root, file))
            else:
                continue
    return file_list


def load_json(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def create_config(pcd_path):
    config = []
    json_file = r"D:\Desktop\BasicProject\谢秋梅\upload data package\camera_config\0_lidar.json"
    json_content = load_json(json_file)
    for name in json_content.keys():
        cam_in = json_content[name]['camera_internal']
        ext = json_content[name]['camera_external']
        cam_ext = inv(np.array(ext).reshape((4, 4))).T.flatten().tolist()
        one_param = {
            "camera_internal": cam_in,
            "camera_external": cam_ext
        }
        config.append(one_param)
    for file in list_files(pcd_path, 'pcd'):
        json_file = file.replace('point_cloud', 'camera_config').replace('.pcd', '.json')
        with open(json_file, 'w', encoding='utf-8') as jf:
            jf.write(json.dumps(config))

create_config(r"D:\Desktop\BasicProject\谢秋梅\upload data package_X1\point_cloud")

