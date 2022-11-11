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


def parse_result(json_file, image_file):
    content = load_json(json_file)
    file_name = os.path.basename(json_file)
    iw, ih = Image.open(image_file).size
    result_data = []
    for num in content.keys():
        uuid_accor = file_name + num
        x0, y0, x1, y1 = eval(content[num]['box'])
        w = x1-x0
        h = y1-y0
        txt = content[num]['txt']
        box_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, uuid_accor))
        box = {
            "type": 'rect',
            "id": box_id,
            "color": "",
            "label": [],
            "code": [],
            "category": [],
            "catetips": [],
            "label_id": [],
            "text": txt,
            "labelAttrs": [],
            "width": w,
            "height": h,
            "area": w*h,
            "strokeWidth": 1,
            "points": [
                {
                    "x": x0/iw,
                    "y": y0/ih
                },
                {
                    "x": x1/iw,
                    "y": y0/ih,
                },
                {
                    "x": x1/iw,
                    "y": y1/ih
                },
                {
                    "x": x0/iw,
                    "y": y1/ih
                }
            ],
            "coordinate": [
                {
                  "x": x0,
                  "y": y0
                },
                {
                  "x": x1,
                  "y": y0
                },
                {
                  "x": x1,
                  "y": y1
                },
                {
                  "x": x0,
                  "y": y1
                }
            ],
            "ih": iw,
            "iw": ih
        }
        result_data.append(box)

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
    json_path = os.path.join(total_path, 'json')
    for img_file in tqdm(list_files(img_path, '.jpg')):
        json_file = img_file.replace(img_path, json_path).replace('.jpg', '.json')
        exc_json = img_file.replace('.jpg', '.json')
        if not os.path.exists(json_file):
            data = {}
            print(f"{json_file}不存在")
        else:
            data = parse_result(json_file, img_file)
        with open(exc_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='arg parser')
    parser.add_argument('total_dir', type=str, help='total directory')
    args = parser.parse_args()
    total_path = args.total_dir
    # total_path = r"D:\Desktop\Project file\张旭\新建文件夹"
    main(total_path)
