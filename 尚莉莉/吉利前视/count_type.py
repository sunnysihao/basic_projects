# _*_ coding=: utf-8 _*_
import os
import json
from tqdm import tqdm


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_list.append(os.path.join(root, file))
    return file_list


def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content

txt_data = []
polygon_txt = []

def counttype(path):
    label_list = []
    point_c = 0
    rect_c = 0
    ply_c = 0
    wheel_num = 0
    for file in tqdm(list_files(path)):
        json_content = load_json(file)
        fs = json_content['markResult']['features']
        for f in fs:
            label = f['properties']['content']['label']
            label_list.append(label)
    # print(set(label_list))
            mt = f['geometry']['type']
            if mt == 'rect':
                rect_c += 1
            elif mt == 'Point':
                point_c += 1
            elif mt == 'polygon':
                ply_c += 1

            if 'Wheel' in label.split('/'):
                wheel_num += 1

    line = f"| 矩形框(不含车轮框):{rect_c-wheel_num} " \
           f"| 点:{point_c} " \
           f"| 车轮框:{wheel_num} " \
           f"| 多边形:{ply_c} |\n"
    return line


def count_with_dir(o_path):
    dir_list = []
    for file in list_files(o_path):
        dir_list.append(os.path.dirname(file))

    path_list = set(dir_list)
    return path_list


path = r"D:\Desktop\BasicProject\尚莉莉\吉利前视\统计结果1021"

counttype(path)
txt_f = r"D:\Desktop\BasicProject\尚莉莉\吉利前视\统计结果1021\count.txt"

p_l = count_with_dir(path)
for one_p in p_l:
    line = counttype(one_p)
    one_dir = f"{one_p}********{line}"
    txt_data.append(one_dir)

with open(txt_f, 'w') as tf:
    tf.writelines(txt_data)


