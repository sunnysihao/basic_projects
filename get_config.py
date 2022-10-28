# _*_ coding=: utf-8 _*_
# _*_ coding=: utf-8 _*_
import os
import json
import numpy as np
from numpy.linalg import inv
import re


def get_cam_param_from_txt(txt_path: str):
    with open(txt_path, 'r', encoding='utf-8') as f:
        line_list = []
        for line in f.readlines():
            if re.findall(r'-?\d+\.\d*', line):
                li = [float(k) for k in re.findall(r'-?\d+\.\d*', line)]
                line_list.append(li)
            else:
                continue
        #line_list = np.asarray(line_list)
    return line_list


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list


def modify_cam(name_path: str, config_path: str):
    for file in list_files(name_path):
        with open(os.path.join(config_path, file + ".json"), '+a', encoding='utf-8') as f:
            f.write(json.dumps(data))


if __name__ == "__main__":
    txt_data = get_cam_param_from_txt(r"D:\Desktop\数据\5-27\20220510外参.txt")
    print(txt_data)
    cam_int_front = txt_data[0:3]
    cam_ext_front = np.asarray(txt_data[3:7]).flatten().tolist()
    cam_int_left = txt_data[7:10]
    cam_ext_left = np.asarray(txt_data[10:14]).flatten().tolist()
    cam_int_right = txt_data[14:17]
    cam_ext_right = np.asarray(txt_data[17:21]).flatten().tolist()
    cam_int_back = txt_data[21:24]
    cam_ext_back = np.asarray(txt_data[24:]).flatten().tolist()

    data = {
        "3d_img0": {
            "camera_internal": {
                "fx": cam_int_front[0][0],
                "cx": cam_int_front[0][2],
                "cy": cam_int_front[1][1],
                "fy": cam_int_front[1][2]

            },
            "camera_external": cam_ext_front
        },
        "3d_img1": {
            "camera_internal": {
                "fx": cam_int_left[0][0],
                "cx": cam_int_left[0][2],
                "cy": cam_int_left[1][1],
                "fy": cam_int_left[1][2]
            },
            "camera_external": cam_ext_left
        },
        "3d_img2": {
            "camera_internal": {
                "fx": cam_int_right[0][0],
                "cx": cam_int_right[0][2],
                "cy": cam_int_right[1][1],
                "fy": cam_int_right[1][2]
            },
            "camera_external": cam_ext_right
        },
        "3d_img3": {
            "camera_internal": {
                "fx": cam_int_back[0][0],
                "cx": cam_int_back[0][2],
                "cy": cam_int_back[1][1],
                "fy": cam_int_back[1][2]
            },
            "camera_external": cam_ext_back
        }
    }

    name_path = r"D:\Desktop\数据\5-27\20220523-10-58-17\FishEye_Front\image_2"
    config_path = r"D:\Desktop\数据\5-27\20220523-10-58-17\camera_config"

    modify_cam(name_path, config_path)
