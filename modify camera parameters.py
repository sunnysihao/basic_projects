# _*_ coding=: utf-8 _*_
import os
import json
import numpy as np
from numpy.linalg import inv
from tqdm import tqdm
import time


def get_txtdata(txt_path: str):
    data_list = []
    with open(txt_path, encoding='utf-8') as f:
        lines = f.readlines()
        for li in lines:
            data_list.append(li.strip("\n").strip("[").strip("]").split(","))
        camera_external = data_list[0:3]
        camera_external = np.asarray(camera_external, dtype=float)
        t = data_list[3:4]
        t = np.asarray(t, dtype=float).reshape((3, 1))
        ext = np.hstack((camera_external, t))
        tian = np.asarray([[0, 0, 0, 1]])
        cam_ext = np.vstack((ext, tian))
        #cam_ext = inv(cam_ext)
        cam_ext = cam_ext.T
        cam_ext = cam_ext.tolist()
        cam_ext_new = []
        for i in range(len(cam_ext)):
            for k in cam_ext[i]:
                cam_ext_new.append(k)
        camera_internal = data_list[-3:]
        camera_internal = np.asarray(camera_internal, dtype=float)

    data = {
        "3d_img0": {
            "camera_internal": {
                "fx": float(camera_internal[0][0]),
                "cx": float(camera_internal[0][2]),
                "cy": float(camera_internal[1][2]),
                "fy": float(camera_internal[1][1])
            },
            "camera_external": cam_ext_new,
            "width": 416,
            "height": 416,
            "box_type": "plane"
            },
        "3d_img1": {
            "camera_internal": {
                "fx": float(camera_internal[0][0]),
                "cx": float(camera_internal[0][2]),
                "cy": float(camera_internal[1][2]),
                "fy": float(camera_internal[1][1])
            },
            "camera_external": cam_ext_new,
            "width": 416,
            "height": 416,
            "box_type": "plane"
        }
    }
    # data["3d_img0"]["camera_external"] = list(map(float,data["3d_img0"]["camera_external"]))
    # data["3d_img1"]["camera_external"] = list(map(float, data["3d_img1"]["camera_external"]))
    return data


def txt2json(name_path: str, to_dir: str):
    print("==> convert files from txt to json...")
    for root, _, file_names in os.walk(name_path):
        for png_file in tqdm(file_names, desc="数据写入进度", unit='file', ncols=100):
            time.sleep(0.5)
            to_path = os.path.join(to_dir, os.path.splitext(png_file)[0])
            with open(to_path+".json", "+a", encoding='utf-8') as f:
                f.write(json.dumps(get_txtdata(txt_path)))


if __name__ == "__main__":

    print("start")
    txt_path = r"D:\Basic\5.12修改内外参数\data_test2(1)_result-2\data_select10\激光雷达-RGB标定结果.txt"
    name_path = r"D:\Basic\5.12修改内外参数\data_test2(1)_result-2\data_select10\3d_img0"
    to_dir = r"D:\Basic\5.12修改内外参数\data_test2(1)_result-2\data_select10\camera_config"
    get_txtdata(txt_path)
    txt2json(name_path, to_dir)
