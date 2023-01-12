# -*- coding: utf-8 -*- 
# @Time : 2023/1/12
# @Author : zhangsihao@basicfinder.com
"""
望石科技13775模板coco导出脚本
"""
import os
from os.path import join, basename, dirname, splitext, exists
import json
from tqdm import tqdm
from datetime import datetime


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


def main(result_folder):
    for file in list_files(result_folder, '.json'):
        jc = load_json(file)
        x_line = []
        y_line = []
        objects = jc['result']['data']
        for obj in objects:
            tool_type = obj['type']
            if tool_type == 'line':
                cds = obj['coordinate']
                x1 = cds[0]['x']
                y1 = cds[0]['y']
                x2 = cds[1]['x']
                y2 = cds[1]['y']
                if abs(x1-x2) < 1 and abs(y1-y2) > 1:
                    x_line.append((x1+x2)/2)
                elif abs(x1-x2) > 1 and abs(y1-y2) < 1:
                    y_line.append((y1+y2)/2)
                else:
                    err_str =

            else:
                continue

        for obj in objects:
            tool_type = obj['type']
            if tool_type == 'rect':
                label = obj['label'][0]
                if not label:
                    label = 'block'
                else:
                    label = label

