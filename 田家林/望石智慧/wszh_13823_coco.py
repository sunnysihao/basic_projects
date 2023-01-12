# -*- coding: utf-8 -*- 
# @Time : 2023/1/11
# @Author : zhangsihao@basicfinder.com
"""
望石科技13823模板coco导出脚本
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


def json2coco(in_dir: str):
    images = []
    annotation = []
    categorys = []
    category_mapping = {}

    img_id = 0
    obj_id = 0
    cat_id = 1
    for file in list_files(in_dir, '.json'):
        jc = load_json(file)
        img_url = jc['data']['image_url']
        folder = rf"{'/'.join(img_url.split('/')[-3:-1])}"
        iw = jc['result']['resourceinfo'][0]['width']
        ih = jc['result']['resourceinfo'][0]['height']

        objects = jc['result']['data']
        x_line = []
        y_line = []
        for obj in objects:
            tool_type = obj['type']
            if tool_type == 'line':
                cds = obj['coordinate']
                x1 = cds[0]['x']
                y1 = cds[0]['y']
                x2 = cds[1]['x']
                y2 = cds[1]['y']
                if abs(x1 - x2) < 1 and abs(y1 - y2) > 1:
                    x_line.append((x1 + x2) / 2)
                elif abs(x1 - x2) > 1 and abs(y1 - y2) < 1:
                    y_line.append((y1 + y2) / 2)
                else:
                    err_str =

            else:
                continue
        x_line = sorted(x_line)
        y_line = sorted(y_line)

        for obj in objects:
            tool_type = obj['type']
            if tool_type == 'rect':
                label = obj['label'][0]
                if not label:
                    label = 'block'
                else:
                    label = label
                ocr_text = obj['text']
                if label not in category_mapping.keys():
                    category_mapping[label] = cat_id
                    category = {
                        "id": cat_id,
                        "name": label
                    }
                    categorys.append(category)
                    cat_id += 1

                width = obj['width']
                height = obj['height']
                xl = []
                yl = []
                for point in obj['coordinate']:
                    xl.append(point['x'])
                    yl.append(point['y'])
                bx0 = min(xl)
                by0 = min(yl)
                bx1 = max(xl)
                by1 = max(yl)

                i = 0
                while x_line[i] < bx0:
                    x1 = x_line[i]
                    x2 = x_line[i+1]
                    i += 1
                j = 0
                while y_line[j] < by0:
                    y1 = y_line[j]
                    y2 = y_line[j+1]
                    j += 1

                anno = {
                    "id": obj_id,
                    "image_id": img_id,
                    "category_id": category_mapping[label],
                    "segmentation": [],
                    "area": width*height,
                    "bbox": [x1, y1, x2-x1, y2-y1],
                    "bbox_utf8_string": [bx0, by0, width, height],
                    "iscrowd": 0,
                    "utf8_string": '',
                    "loc": []
                }
                annotation.append(anno)
                obj_id += 1

        one_image = {
                "id": img_id,
                "width": iw,
                "height": ih,
                "file_name": img_url.split('/')[-1],
                "license": 0,
                "flickr_url": '',
                "coco_url": '',
                "folder": folder,
                "date_captured": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        images.append(one_image)
        img_id += 1

    info = {
        "year": '2022',# 年份
        "version": '',# 版本
        "description": 'PDF table annotation', # 数据集描述
        "contributor": 'basicfinder COCO group',# 提供者
        "url": '',# 下载地址
        "date_created": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    final_json = {
        "info": info,
        "licenses": [],
        "images": images,
        "annotations": annotation,
        "categories": categorys
    }
    save_json = join(in_dir, 'results.json')
    with open(save_json, 'w', encoding='utf-8') as jf:
        json.dump(final_json, jf, indent=1)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('json_dir', type=str)
    args = parser.parse_args()

    json_dir = args.json_dir
    # category_json = r"D:\Desktop\Project_file\田家林\望石智慧\journal\category.json"
    # json_dir = r"C:\Users\EDY\Downloads\json_45228_114724_20221205172348\wszh_upload_images - 副本"
    json2coco(json_dir)