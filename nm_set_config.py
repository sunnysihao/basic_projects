# _*_ coding=: utf-8 _*_
import os
import json
import numpy as np
from numpy.linalg import inv


cam_ext_front_L = [[0.70204919, -0.71209424, 0.0069802, 1.74226556],
                  [0.01732818, 0.00728312, -0.99982333, 1.16037619],
                  [0.7119176,  0.70204611, 0.01745241, 0.45895293],
                  [0.,         0.,         0.,         1.        ]]

cam_ext_front_L = inv(np.asarray(cam_ext_front_L)).flatten().tolist()


cam_ext_front_R = [[-0.69907453, -0.71504029, 0.00349022, -1.75221253],
                    [0.00879186, -0.01347608, -0.99987054, 1.14139241],
                    [0.71499476, -0.69895334, 0.01570732, 0.46858789],
                    [0.,         0.,         0.,         1.        ]]
cam_ext_front_R = inv(np.asarray(cam_ext_front_R)).flatten().tolist()

cam_ext_rear_R = [[-0.81912764, 0.57309086, -0.02442916, -0.60303547],
                  [0.01100701, -0.02687656, -0.99957816, 0.90056827],
                  [-0.57350568, -0.81905099, 0.01570732, -1.562538],
                  [0.,          0.,          0.,         1.        ]]
cam_ext_rear_R = inv(np.asarray(cam_ext_rear_R)).flatten().tolist()

cam_ext_rear_L =  [[0.84987638, 0.52690984, -0.00872648, 0.71828008],
                    [-0.00557727, -0.00756506, -0.99995583, 0.90903584],
                    [-0.52695259, 0.84988752, -0.00349065, -1.50795477],
                    [0.,         0.,         0.,         1.        ]]
cam_ext_rear_L = inv(np.asarray(cam_ext_rear_L)).flatten().tolist()

data = {
    "3d_img0": {
        "camera_internal": {
            "fx": 980.02131904,
            "cx": 965.79191823,
            "cy": 634.48280487,
            "fy": 980.22316059

    },
        "camera_external": cam_ext_front_L
  },
    "3d_img1": {
        "camera_internal": {
            "fx": 980.66916303,
            "cx": 952.59951867,
            "cy": 636.85122204,
            "fy": 980.38756837
    },
        "camera_external": cam_ext_front_R
  },
    "3d_img2": {
        "camera_internal": {
            "fx": 980.86251154,
            "cx": 972.30741465,
            "cy": 631.77040992,
            "fy": 980.15495628
    },
        "camera_external": cam_ext_rear_R
  },
    "3d_img3": {
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

def modify_cam(name_path:str):
    for file in list_files(name_path):
        config_path = os.path.join(os.path.dirname(name_path), 'camera_config')
        if not os.path.exists(config_path):
            os.mkdir(config_path)
        else:
            continue
        with open(os.path.join(config_path, file + ".json"), '+a', encoding='utf-8') as f:
            f.write(json.dumps(data))

if __name__ == "__main__":

    name_path = r"D:\BasicProject\任从辉\纽劢\3d_img0"
    #config_path = r"D:\BasicProject\任从辉\纽劢\camera_config"

    modify_cam(name_path)
