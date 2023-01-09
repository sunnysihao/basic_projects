# -*- coding: utf-8 -*- 
# @Time : 2023/1/9
# @Author : zhangsihao@basicfinder.com
"""
"""
import os
from os.path import join, basename, dirname, splitext, exists
import json
from tqdm import tqdm


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


def fx_2d(mosaic_dir, output_dir):
    for label_file in tqdm(list_files(mosaic_dir, '.json')):
        file_name = splitext(basename(label_file))[0]
        img = join(basename(basename(label_file)), 'matrix_img', file_name + '.jpg')
        new_img = join(output_dir, file_name + '.jpg')
        os.rename(img, new_img)
        label_data = load_json(label_file)
        y = 0
        for obj in label_data['annos']:
            int_id = obj['object_id']
            x = 0
