# _*_ coding=: utf-8 _*_
# @Time    : 2022/08/04
# @Author  : zhangsihao@basicfinder.com
import json
import os
import math
from tqdm import tqdm


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_list.append(os.path.join(root, file))
    return file_list


# 将alpha角度取值范围限制在-pi到pi
def alpha_in_pi(alpha):
    pi = math.pi
    return alpha - math.floor((alpha + pi) / (2 * pi)) * 2 * pi


# 读取json文件内容返回python类型的对象
def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


empty_l = []


def write_result(json_dir: str):
    result_path = os.path.join(json_dir, 'kitti_results')
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    for file in tqdm(list_files(json_dir)):
        line_data = []
        json_content = load_json(file)
        data_id = json_content['data_id']
        if 'frameNumber' in json_content['data'].keys():
            fram_number = json_content['data']['frameNumber'] + 1
        else:
            fram_number = 0
        boxs = json_content['result']['data']
        for box in boxs:
            truncated = "%.2f" % 0
            occluded = 0
            int_id = box['intId']
            cby = box['cBy']
            length = box['3Dsize']['height']
            width = box['3Dsize']['width']
            height = box['3Dsize']['deep']
            alpha_b = box['3Dsize']['alpha']
            o_label = box['attr']['label']
            if not o_label:
                empty_str = f"作业id:{data_id}---第{fram_number}帧---{int_id}号框标签为空,创建人{cby}\n"
                empty_l.append(empty_str)
                label = 'null'
            else:
                label = o_label[0]
            x, y, z = box['3Dcenter'].values()
            r_y = alpha_in_pi(alpha_b + math.pi/2)
            theta = math.atan2(y, x)
            alpha = alpha_in_pi(r_y - theta)
            x_list = []
            y_list = []
            for one_point in box['points']:
                x_list.append(one_point['x'])
                y_list.append(one_point['y'])
            xmin = min(x_list)
            xmax = max(x_list)
            ymin = min(y_list)
            ymax = max(y_list)
            scal = f"{xmin:.2f} {ymin:.2f} {xmax:.2f} {ymax:.2f}"
            size = f"{height:.2f} {width:.2f} {length:.2f}"
            box_center = f"{x:.2f} {y:.2f} {z:.2f}"
            score = 1
            string = f"{label} {truncated} {occluded} {alpha:.2f} {scal} {size} {box_center} {r_y:.2f} {score}\n"
            line_data.append(string)

        new_file = os.path.join(result_path, os.path.splitext(os.path.basename(file))[0] + '.txt')
        with open(new_file, 'w', encoding='utf-8') as f:
            f.writelines(line_data)
    empty_label_file = os.path.join(json_dir, 'empty_labels.txt')
    with open(empty_label_file, 'w', encoding='utf-8') as ef:
        ef.writelines(empty_l)


if __name__ == "__main__":
    # import argparse
    #
    # parser = argparse.ArgumentParser()
    # parser.add_argument('result_json_path', type=str)
    # parser.add_argument('output_path', type=str)
    # args = parser.parse_args()
    #
    # result_json_path = args.result_json_path
    # output_path = args.output_path
    # result_json_path = r"C:\Users\EDY\Downloads\json_41854_90866,90867_20220803105324\set02_part1\set02_part1\3d_url"
    # result_json_path = r"C:\Users\EDY\Downloads\json_21197_16936_20220804073222"
    result_json_path = input("请输入路径:\n")

    write_result(result_json_path)

    input("已完成，安任意键退出")
