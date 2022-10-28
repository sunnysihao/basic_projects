# _*_ coding=: utf-8 _*_
import os
import re
import json
import math
import cv2
import numpy as np
from PIL import Image


# 根据路径列出当前路径下所有的文件名(不含后缀名)
def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list

# 将alpha角度取值范围限制在-pi到pi
def alpha_in_pi(alpha):
    pi = math.pi
    return alpha - math.floor((alpha + pi) / (2 * pi)) * 2 * pi

# 读取json文件内容返回python类型的对象
def load_json(json_path:str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content

# 将data数据以平台相机参数格式写入json文件
from numpy.linalg import inv
camera_external = [[0.70204919, -0.71209424, 0.0069802, 1.74226556],
                  [0.01732818, 0.00728312, -0.99982333, 1.16037619],
                  [0.7119176,  0.70204611, 0.01745241, 0.45895293],
                  [0.,         0.,         0.,         1.        ]]
camera_external = np.asarray(camera_external).T
camera_external = inv(np.asarray(camera_external)).flatten().tolist()  # 矩阵取逆
#  行列交换  camera_external = camera_external.T
data = {
    "3d_img0": {
        "camera_internal": {
            "fx": 980.02131904,
            "cx": 965.79191823,
            "cy": 634.48280487,
            "fy": 980.22316059

    },
        "camera_external": camera_external,
        "width": 1920,
        "height": 1280,
        "box_type": "plane"
  },
}

def write_data_to_json(get_name_path:str, data:dict, config_path:str):
    file_list = []
    for root, _, files in os.walk(get_name_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
            with open(os.path.join(config_path, file + ".json"), 'w', encoding='utf-8') as f:
                f.write(json.dumps(data))

# 将鱼眼相机图片展平，恢复畸变
def fish_eye_to_normal_image(camera_internal:list, camera_D:list, fish_image_path:str, save_file_path:str):
    K = np.array(camera_internal)   #相机内参
    D = np.array(camera_D)   #相机畸变参数
    image = Image.open(fish_image_path)
    img = np.asarray(image)
    im = Image.fromarray(cv2.undistort(img, K, D, None, K))
    im.save(save_file_path)


# 从txt文档中提取相机参数,返回array数组
def get_cam_param_from_txt(txt_path:str):
    with open(txt_path, 'r', encoding='utf-8') as f:
        line_list = []
        for line in f.readlines():
            if re.findall(r'-?\d+\.\d*', line) != []:
                li = re.findall(r'-?\d+\.\d*', line)
                line_list.append(li)
            else:
                continue

    return line_list
    #line_array[m,n].flatten()--将二维数组转为一维  array.tolist() --将数组转为列表

# 将四元数和平移向量转化为外参矩阵
from scipy.spatial.transform import Rotation as R

def create_external(translation_list: list, rotation_list: list):
    row = [[0, 0, 0, 1]]
    cam_r = R.from_quat(rotation_list).as_matrix()
    cam_t = np.array(translation_list).reshape((3, 1))
    cam_ext = np.hstack((cam_r, cam_t))
    cam_ext = np.vstack((cam_ext, row)).flatten().tolist()
    return cam_ext

# 写pcd文件头
with open(pcd_path, 'a') as pcd_file:
    point_num = points.shape[0]
    # 定义pcd文件头
    heads = [
        '# .PCD v0.7 - Point Cloud Data file format',
        'VERSION 0.7',
        'FIELDS x y z i',
        'SIZE 4 4 4 4',
        'TYPE F F F F',
        'COUNT 1 1 1 1',
        f'WIDTH {point_num}',
        'HEIGHT 1',
        'VIEWPOINT 0 0 0 1 0 0 0',
        f'POINTS {point_num}',
        'DATA ascii'
    ]
    pcd_file.write('\n'.join(heads))
# 配置命令行参数
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('result_json_path', type=str)
parser.add_argument('output_path', type=str)
args = parser.parse_args()

result_json_path = args.result_json_path
output_path = args.output_path

# 生成单独的每个视角个相机参数json文件
def write_single_config(pcd_path, config_path, x):
    file = list_files(pcd_path)[0]
    single_config = os.path.join(os.path.dirname(config_path), "single_configs")
    if not os.path.exists(single_config):
        os.mkdir(single_config)
    for i in range(x):

        single_data = {
            "3d_img0": data[f'3d_img{i}']
        }
        with open(os.path.join(single_config, file + f'-{i}' + '.json'), 'w', encoding='utf-8') as sf:
            sf.write(json.dumps(single_data))
