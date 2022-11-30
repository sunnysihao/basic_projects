# -*- coding: utf-8 -*- 
# @Time : 2022/11/29
# @Author : zhangsihao@basicfinder.com
"""
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


def json2coco(in_dir, category_json):
    images = []
    annotation = []
    categorys = load_json(category_json)['categories']
    category_mapping = {}
    for cate in categorys:
        c_name = cate['name']
        c_id = cate['id']
        category_mapping[c_name] = c_id
    img_id = 0
    box_id = 0
    for file in list_files(in_dir, '.json'):
        file_name = splitext(basename(file))[0]
        jc = load_json(file)
        img_url = jc['data']['image_url']
        folder = rf"{'/'.join(img_url.split('/')[-3:-1])}"
        iw = 1984
        ih = 2806

        boxes = jc['result']['data']
        for box in boxes:
            label = box['label'][0]
            width = box['width']
            height = box['height']
            iw = box['iw']
            ih = box['ih']
            xl = []
            yl = []
            for point in box['coordinate']:
                xl.append(point['x'])
                yl.append(point['y'])
            x0 = min(xl)
            y0 = min(yl)
            anno = {
                "id": box_id,  # 对象ID，因为每一个图像有不止一个对象，所以要对每一个对象编号（每个对象的ID是唯一的）
                "image_id": img_id,  # 对应的图片ID（与images中的ID对应）
                "category_id": category_mapping[label],  # 类别ID（与categories中的ID对应）
                "segmentation": [x0, y0, x0+width, y0, x0+width, y0+height, x0, y0+height],  # 对象的边界点（边界多边形，此时iscrowd=0）。
                # segmentation格式取决于这个实例是一个单个的对象（即iscrowd=0，将使用polygons格式）还是一组对象（即iscrowd=1，将使用RLE格式）
                "area": width*height,  # 区域面积
                "bbox": [x0, y0, width, height],  # 定位边框 [x,y,w,h]
                "iscrowd": 0  # 见下
            }
            annotation.append(anno)
            box_id += 1

        one_image = {
                "id": img_id,
                "width": iw,
                "height": ih,
                "file_name": img_url.split('/')[-1],
                "license": 0,
                "flickr_url": '',  # flickr网路地址
                "coco_url": '',  # 网路地址路径
                "folder": folder,
                "date_captured": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        images.append(one_image)
        img_id += 1

    info = {
        "year": 2022,# 年份
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
    parser.add_argument('category_json', type=str)
    args = parser.parse_args()

    json_dir = args.json_dir
    category_json = args.category_json
    # category_json = r"D:\Desktop\Project_file\田家林\望石智慧\journal\category.json"
    # json_dir = r"D:\Desktop\Project_file\田家林\望石智慧\journal\json_45096_114268_20221129110317 - 副本"
    json2coco(json_dir, category_json)
