# _*_ coding=: utf-8 _*_
import os
import json
from PIL import ImageColor


def list_files(in_path):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_list.append(os.path.join(root, file))
            else:
                continue
    return file_list


def load_json(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def write_txt(in_path):
    for file in list_files(in_path):
        json_content = load_json(file)
        result_data = json_content['result']['data']
        for box in result_data:
            box_id = box['id']
            label = box['attr']['label']
            color = box['attr']['color']
            r, g, b = ImageColor.getcolor(color, 'RGB')

            txt_line = f""
