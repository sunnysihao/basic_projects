# -*- coding: utf-8 -*- 
# @Time : 2022/11/30
# @Author : zhangsihao@basicfinder.com
"""
"""
import os
from os.path import join, basename, dirname, splitext, exists
import json
from tqdm import tqdm
import base64


def list_files(in_path: str, match):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if splitext(file)[-1] == match:
                file_list.append(join(root, file))
    return file_list


def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def trans2labelme(json_dir):
    for file in list_files(json_dir, '.json'):
        annotation = []
        jc = load_json(file)
        img_path = r"/basicfinder/www/saas.basicfinder.com/api/resource"
        img_url = jc['data']['image_url']
        img_file = os.path.join(img_path, img_url)
        with open(img_file, 'rb') as img_f:
            img_f_base64 = base64.b64encode(img_f.read())
            img_data = img_f_base64.decode()
        iw = jc['result']['resourceinfo']['width']
        ih = jc['result']['resourceinfo']['height']
        file_name = img_url.split('/')[-1]
        lines = jc['result']['data']
        for line in lines:
            points = []
            for point in line['coordinate']:
                points.append([point['x'], point['y']])
            new_line = {
                "label": "1",
                "points": points,
                "group_id": None,
                "shape_type": "line",
                "flags": {}
            }
            annotation.append(new_line)
        final_data = {
            "version": "5.0.1",
            "flags": {},
            "shapes": annotation,
            "imagePath": file_name,
            "imageData": img_data,
            "imageHeight": iw,
            "imageWidth": ih
        }
        with open(file, 'w', encoding='utf-8') as nf:
            json.dump(final_data, nf, indent=1)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('json_dir', type=str)
    args = parser.parse_args()

    json_dir = args.json_dir
    # json_dir = r"D:\Desktop\Project_file\刘晓龙\华测\车道线\线段标注1122.zip\线段标注1122\强度分布不均匀 - 副本"
    trans2labelme(json_dir)
