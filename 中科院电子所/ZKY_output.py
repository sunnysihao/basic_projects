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


def write_result(json_dir: str):
    result_path = os.path.join(json_dir, 'kitti_results')
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    empty_label_l = []
    for file in tqdm(list_files(json_dir)):
        line_data = []
        json_content = load_json(file)
        data_id = json_content['data_id']
        fram_number = json_content['data']['frameNumber'] + 1
        boxs = json_content['result']['data']
        for box in boxs:
            int_id = box['intId']
            cby = box['cBy']
            if not box['classType']:
                err_str = f"作业id:{data_id}---第{fram_number}帧---{int_id}号框标签为空,创建人{cby}"
                empty_label_l.append(err_str)
                label = 'null'
            else:
                if box['classType'] == 'Delivery tricycle':
                    label = 'deliveryTricycle'
                else:
                    label = box['classType']
            truncated = 0
            occluded = 0
            length = box['3Dsize']['x']
            width = box['3Dsize']['y']
            height = box['3Dsize']['z']
            b_alpha = box['3Drotation']['z']
            r_y = alpha_in_pi(b_alpha)
            x, y, z = box['3Dcenter'].values()
            if not sum([x, y, z]):
                continue
            else:
                theta = alpha_in_pi(- (math.atan2(y, x) + math.pi/2))
                scal = "0 0 0 0"
                size = f"{height:.2f} {width:.2f} {length:.2f}"
                box_center = f"{x:.2f} {y:.2f} {z:.2f}"
                string = f"{label} {truncated} {occluded} {theta:.2f} {scal} {size} {box_center} {r_y:.2f}\n"
                line_data.append(string)

        new_file = os.path.join(result_path, os.path.splitext(os.path.basename(file))[0] + '.txt')
        with open(new_file, 'w', encoding='utf-8') as f:
            f.writelines(line_data)
    err_file = os.path.join(json_dir, "empty labels.txt")
    with open(err_file, 'w', encoding='utf-8') as ef:
        ef.writelines(empty_label_l)


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
    result_json_path = r"C:\Users\EDY\Downloads\json_42390_95010,95011,96852_20220818102204"
    # result_json_path = input("请输入路径:\n")

    write_result(result_json_path)

    input("已完成，安任意键退出")
