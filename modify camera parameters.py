# _*_ coding=: utf-8 _*_
import os
import json
import numpy as np
from numpy.linalg import inv
from tqdm import tqdm
import time


def get_txtdata(json_file):
    ext_r = np.array([[-0.01535546, -0.99984817, 0.00823677],
                        [0.02280838, -0.00858586, -0.99970299],
                        [0.99962192, -0.01516303, 0.02293675]])
    ext_t = np.array([-0.0651113, -0.37164303, 0.14304646]).reshape((3, 1))
    ext = np.hstack((ext_r, ext_t))
    tian = np.array([0, 0, 0, 1])
    cam_ext = np.vstack((ext, tian))
    # cam_ext = inv(cam_ext)
    # cam_ext = cam_ext.T
    # cam_ext = cam_ext.tolist()
    cam_ext_new = cam_ext.flatten().tolist()

    data = {
        "3d_img0": {
            "camera_internal": {
                "fx": 640.039533950044,
                "cx": 245.216833076302,
                "cy": 189.067845636845,
                "fy": 645.069442501087
            },
            "camera_external": cam_ext_new
            }
    }
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f)


def txt2json(name_path: str, to_dir: str):
    print("==> convert files from txt to json...")
    for root, _, file_names in os.walk(name_path):
        for png_file in tqdm(file_names, desc="数据写入进度", unit='file', ncols=100):
            time.sleep(0.5)
            json_file = os.path.join(to_dir, os.path.splitext(png_file)[0] + '.json')
            get_txtdata(json_file)


if __name__ == "__main__":

    print("start")
    txt_path = r"D:\Desktop\Project_file\王满顺\同济大学\新建文件夹\新建文件夹\激光雷达-RGB标定结果.txt"
    name_path = r"D:\Desktop\Project_file\王满顺\同济大学\新建文件夹\新建文件夹\3d_img0"
    to_dir = r"D:\Desktop\Project_file\王满顺\同济大学\新建文件夹\新建文件夹\camera_config"
    get_txtdata(txt_path)
    txt2json(name_path, to_dir)
