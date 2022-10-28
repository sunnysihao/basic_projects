# _*_ coding=: utf-8 _*_
import os
import json
import numpy as np
from numpy.linalg import inv


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':  # 只读取.json后缀的文件
                file_list.append(file)
            else:
                continue
    return file_list


def load_json(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


# 老点云工具相机参数转新点云工具相机参数
def convert_parameters_old_to_new(camera_config_path: str):
    result_path = os.path.join(camera_config_path, '../new_camera_config')
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    for file in list_files(camera_config_path):
        json_file = os.path.join(camera_config_path, file)
        json_content = load_json(json_file)
        num = len(json_content)
        data = {}
        for i in range(num):
            cam_int = json_content[f"3d_img{i}"]['camera_internal']
            cam_ext = json_content[f"3d_img{i}"]['camera_external']
            cam_ext = np.asarray(cam_ext).reshape((4, 4))
            cam_ext = inv(inv(cam_ext)).T
            one_data = {
                    "camera_internal": cam_int,
                    "camera_external": cam_ext.flatten().tolist()
            }
            data[f"3d_img{i}"] = one_data
        with open(os.path.join(result_path, file), 'w', encoding='utf-8') as f:
            f.write(json.dumps(data))


cam_path = r"D:\Desktop\BasicProject\毛岩\20220712144116_Sunny_City_Day_4205"
convert_parameters_old_to_new(cam_path)
