# _*_ coding=: utf-8 _*_
import os
import json
import numpy as np
from numpy.linalg import inv


cam_ext_rear_L =  [[0.84987638, 0.52690984, -0.00872648, 0.71828008],
                    [-0.00557727, -0.00756506, -0.99995583, 0.90903584],
                    [-0.52695259, 0.84988752, -0.00349065, -1.50795477],
                    [0.,         0.,         0.,         1.        ]]
cam_ext_rear_L = inv(np.asarray(cam_ext_rear_L)).flatten().tolist()
# arr3 = inv(cam_ext_rear_L)
# arr3 = arr3.flatten()
# cam_r_l = arr3.tolist()
# cam_r_l = []
# for k3 in arr3:
#     for j3 in k3:
#         cam_r_l.append(j3)

data = {"3d_img0": {
        "camera_internal": {
            "fx": 975.0054237,
            "cx": 952.64164155,
            "cy": 636.51671482,
            "fy": 975.41367408
    },
        "camera_external": cam_ext_rear_L
  }
}

def list_files(in_path:str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list

def modify_cam(name_path:str, config_path:str):
    for file in list_files(name_path):
        with open(os.path.join(config_path, file + "r_l.json"), '+a', encoding='utf-8') as f:
            f.write(json.dumps(data))

if __name__ == "__main__":

    name_path = r"D:\BasicProject\任从辉\纽劢_相机参数标定\3d_img0"
    config_path = r"D:\BasicProject\任从辉\纽劢_相机参数标定\camera_comfig"

    modify_cam(name_path, config_path)
