# -*- coding: utf-8 -*- 
# @Time : 2022/11/16
# @Author : zhangsihao@basicfinder.com
"""
"""
# -*- coding: utf-8 -*-
# @Time : 2022/11/10
# @Author : zhangsihao@basicfinder.com
"""
"""
import os
import json
import uuid
from tqdm import tqdm
from PIL import Image


def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def list_files(in_path: str, match):
    file_name_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == match:
                file_name_list.append(os.path.join(root, file))
    return file_name_list


def load_txt(txt_file):
    with open(txt_file, 'r', encoding='utf-8') as tf:
        return tf.readlines()


def parse_result(txt_file):
    content = load_txt(txt_file)
    file_name = os.path.basename(txt_file)
    iw, ih = 1920, 1080
    result_data = []
    int_id = 1
    for line in content:
        box = line.strip('\n').split(' ')
        label = box[0]
        x = float(box[1])
        y = float(box[2])
        w = float(box[3])
        h = float(box[4])
        x1 = x + w
        y1 = y + h
        box_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, file_name + str(int_id)))
        box = {
            "type": 'rect',
            "id": box_id,
            "color": "",
            "label": [label],
            "code": [label],
            "category": [label],
            "catetips": [label],
            "label_id": [],
            "text": "",
            "labelAttrs": [],
            "width": w,
            "height": h,
            "area": w*h,
            "intId": int_id,
            "points": [
                {
                    "x": x,
                    "y": y
                },
                {
                    "x": x1,
                    "y": y,
                },
                {
                    "x": x1,
                    "y": y1
                },
                {
                    "x": x,
                    "y": y1
                }
            ],
            "coordinate": [
                {
                  "x": x*iw,
                  "y": y*ih
                },
                {
                  "x": x1*iw,
                  "y": y*ih
                },
                {
                  "x": x1*iw,
                  "y": y1*ih
                },
                {
                  "x": x*iw,
                  "y": y1*ih
                }
            ],
            "ih": iw,
            "iw": ih
        }
        result_data.append(box)
        int_id += 1

    data = {
        "data": {
            "image_url": file_name
        },
        "result": {
            "data": result_data,
            "groupinfo": [],
            "resourceinfo": {
                "width": iw,
                "height": ih,
                "rotation": 0
            },
            "data_deleted_file": ""
        }
    }
    return data


def main(total_path):
    img_path = os.path.join(total_path, 'img')
    txt_path = os.path.join(total_path, 'txt')
    match = '.png'
    for img_file in tqdm(list_files(img_path, match)):
        txt_file = img_file.replace(img_path, txt_path).replace(match, '.txt')
        exc_json = img_file.replace(match, '.json')
        if not os.path.exists(txt_file):
            print(f"{txt_file}不存在")
        else:
            data = parse_result(txt_file, img_file)
            with open(exc_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)


def main2(total_path):
    txt_path = os.path.join(total_path, 'txt')
    new_json_path = os.path.join(total_path, 'json')
    match = '.txt'
    for txt_file in tqdm(list_files(txt_path, match)):
        exc_json = txt_file.replace(match, '.json').replace('txt', 'json')
        if not os.path.exists(txt_file):
            print(f"{txt_file}不存在")
        else:
            data = parse_result(txt_file)
            with open(exc_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)


if __name__ == '__main__':
    # import argparse
    # parser = argparse.ArgumentParser(description='arg parser')
    # parser.add_argument('total_dir', type=str, help='total directory')
    # args = parser.parse_args()
    # total_path = args.total_dir
    total_path = r"D:\Desktop\Project_file\张子千\BUNCH Sample images (2)"
    main2(total_path)
