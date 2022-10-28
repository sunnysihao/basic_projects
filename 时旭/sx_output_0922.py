# _*_ coding=: utf-8 _*_
import json
import os
import math
from tqdm import tqdm
import laspy
import numpy as np


def alpha_in_pi(alpha):
    pi = math.pi
    return alpha - math.floor((alpha + pi) / (2 * pi)) * 2 * pi



def list_files(in_path: str, match):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == match:
                file_list.append(os.path.join(root, file))
    return file_list


def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def write_result(json_dir: str, las_path):
    result_path = os.path.join(json_dir, 'kitti_results')
    empty_l = []
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    json_files = list_files(json_dir, '.json')
    las_files = list_files(las_path, '.las')
    for i in tqdm(range(len(json_files))):
        file = json_files[i]
        las_file = las_files[i]
        # file_name = os.path.basename(file).replace('_6to12', '')
        # las_file_name = '_'.join(file_name.split('_')[: -1]) + '.las'
        # las_file = os.path.join(las_path, file_name.replace('.json', '.las'))
        las = laspy.read(las_file)
        header = las.header
        x_offset = header.x_offset
        y_offset = header.y_offset
        z_offset = header.z_offset
        scale = 0.001
        line_data = []
        json_content = load_json(file)
        # data_id = json_content['data_id']
        boxs = json_content['result']['data']
        for box in boxs:
            # int_id = box['intId']
            length = (box['3Dsize']['height']) * scale
            width = (box['3Dsize']['width']) * scale
            height = (box['3Dsize']['deep']) * scale
            x = ((box['3Dcenter']['x']) * scale) + x_offset - 43.02999999996973
            y = ((box['3Dcenter']['y']) * scale) + y_offset - 273.28000000026077
            z = ((box['3Dcenter']['z']) * scale) + z_offset - 16.630000000000003
            r_y = alpha_in_pi(box['3Dsize']['alpha'])
            o_label = box['attr']['label']
            if not o_label:
                # empty_str = f"作业id:{data_id}---{int_id}号框标签为空\n"
                # empty_l.append(empty_str)
                label = 'null'
            else:
                label = o_label[0]
            label = ''.join(label.split(' '))
            box_center = f"{x:.2f} {y:.2f} {z:.2f}"
            string = f"{label} 0 0 {r_y:.2f} 0 0 0 0 {height:.2f} {width:.2f} {length:.2f} {box_center} {r_y:.2f} 1\n"
            line_data.append(string)

        new_file = os.path.join(result_path, os.path.splitext(os.path.basename(file))[0] + '.txt')
        with open(new_file, 'w', encoding='utf-8') as f:
            f.writelines(line_data)
    empty_label_file = os.path.join(json_dir, 'empty_labels.txt')
    with open(empty_label_file, 'w', encoding='utf-8') as ef:
        ef.writelines(empty_l)


if __name__ == '__main__':
    json_dir = r"D:\Desktop\BasicProject\王满顺\时旭\SX一作业一结果\sx1010\AA_6to12_pcd.zip\AA_6to12_pcd"
    las_path = r"D:\Desktop\BasicProject\王满顺\时旭\SX一作业一结果\las_one"
    write_result(json_dir, las_path)
