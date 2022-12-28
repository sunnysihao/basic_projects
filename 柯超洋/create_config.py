# -*- coding: utf-8 -*- 
# @Time : 2022/12/27
# @Author : zhangsihao@basicfinder.com
"""
"""
import os
import json
import numpy as np
from numpy.linalg import inv


def list_files(in_path: str, match):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == match:
                file_list.append(os.path.join(root, file))
    return file_list


def main():
    txt_path = r"C:\Users\EDY\Downloads\无点云融合\无点云融合\相机参数\calibration"
    cfg_path = r"C:\Users\EDY\Downloads\无点云融合\无点云融合\config.json"
    num = 0
    config = {}
    for file in list_files(txt_path, '.txt'):
        with open(file, 'r') as tf:
            txt = tf.readlines()
            ext = []
            for line in txt[1:5]:
                ext.append([float(x) for x in line.strip('\n').split(' ')[:-1]])
            cam_ext = np.array(ext)
            inter = []
            for line in txt[7:10]:
                inter.append([float(x) for x in line.strip('\n').split(' ')[:-1]])
            cam_in = np.array(inter)
            camera_internal = {
                    "fx": cam_in[0, 0],
                    "fy": cam_in[1, 1],
                    "cx": cam_in[0, 2],
                    "cy": cam_in[1, 2]
                }

            camera_external = cam_ext.flatten().tolist()

        config[f"3d_img{num}"] = {
            "camera_internal": camera_internal,
            "camera_external": camera_external
            }
        num += 1

    with open(cfg_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=1)

if __name__ == '__main__':
    main()

