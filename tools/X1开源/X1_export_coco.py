# -*- coding: utf-8 -*-
"""
Script to convert Xtreme standard format to coco format for Xtreme V0.55 image annotation
"""
import os
from os.path import join, basename, dirname, splitext, exists
import json
import zipfile
import cv2
import numpy as np
from tqdm import tqdm
from datetime import datetime


def list_files(in_path: str, match: str):
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


def unzip_file(zip_src, dst_dir):
    r = zipfile.is_zipfile(zip_src)
    if r:
        fz = zipfile.ZipFile(zip_src, 'r')
        for file in fz.namelist():
            fz.extract(file, dst_dir)
    else:
        print('This is not zip')


def coco_converter(dst_dir: str):
    result_path = join(dst_dir, os.listdir(dst_dir)[0], 'result')
    data_path = join(dst_dir, os.listdir(dst_dir)[0], 'data')
    export_path = join(dst_dir, os.listdir(dst_dir)[0], 'coco_result')
    if not exists(export_path):
        os.mkdir(export_path)
    images = []
    annotation = []
    categorys = []
    category_mapping = {}

    img_id = 0
    box_id = 0
    cat_id = 1
    for file in tqdm(list_files(result_path, '.json'), desc='progress'):
        file_name = basename(file)
        data_file = join(data_path, file_name)
        result_content = load_json(file)
        data_content = load_json(data_file)
        img_width = data_content['width']
        img_height = data_content['height']

        img_url = data_content['imageUrl']

        for result in result_content:
            objects = result['objects']
            for obj in objects:
                class_name = obj['className']
                if class_name not in category_mapping.keys():
                    category_mapping[class_name] = cat_id
                    category = {
                        "id": cat_id,
                        "name": class_name,
                        "supercategory": "",
                        "attributes": {}
                    }
                    categorys.append(category)
                    cat_id += 1
                score = obj['modelConfidence']
                tool_type = obj['type']
                if tool_type == 'RECTANGLE':
                    points = obj['contour']['points']
                    xl = []
                    yl = []
                    for point in points:
                        xl.append(point['x'])
                        yl.append(point['y'])
                    x0 = min(xl)
                    y0 = min(yl)
                    width = max(xl)-x0
                    height = max(yl)-y0
                    attributes = {}
                    class_values = obj['classValues']
                    for cv in class_values:
                        attributes[cv['name']] = cv['value']
                    anno = {
                        "id": box_id,
                        "image_id": img_id,
                        "category_id": category_mapping[class_name],
                        "segmentation": [],
                        "score": score,
                        "area": width*height,
                        "bbox": [x0, y0, width, height],
                        "iscrowd": 0,
                        "attributes": attributes
                    }
                    annotation.append(anno)
                    box_id += 1
                elif tool_type == 'POLYGON':
                    segmentation = []
                    coordinate = []
                    points = obj['contour']['points']
                    for point in points:
                        coordinate.append([int(point['x']), int(point['y'])])
                        segmentation.append(point['x'])
                        segmentation.append(point['y'])
                    mask = np.zeros((img_height, img_width), dtype=np.int32)
                    cv2.fillPoly(mask, [np.array(coordinate)], 1)
                    aera = int(np.sum(mask))
                    attributes = {}
                    class_values = obj['classValues']
                    for cv in class_values:
                        attributes[cv['name']] = cv['value']
                    anno = {
                        "id": box_id,
                        "image_id": img_id,
                        "category_id": category_mapping[class_name],
                        "segmentation": segmentation,
                        "score": score,
                        "area": aera,
                        "bbox": [],
                        "iscrowd": 0,
                        "attributes": attributes
                    }
                    annotation.append(anno)
                    box_id += 1
                elif tool_type == 'POLYLINE':
                    keypoints = []
                    points = obj['contour']['points']
                    for point in points:
                        keypoints.append(point['x'])
                        keypoints.append(point['y'])
                        keypoints.append(2)

                    attributes = {}
                    class_values = obj['classValues']
                    for cv in class_values:
                        attributes[cv['name']] = cv['value']
                    anno = {
                        "id": box_id,
                        "image_id": img_id,
                        "category_id": category_mapping[class_name],
                        "segmentation": [],
                        "bbox": [],
                        "keypoints": keypoints,
                        "num_keypoints": len(points),
                        "score": score,
                        "iscrowd": 0
                    }
                    annotation.append(anno)
                    box_id += 1

        one_image = {
                "id": img_id,
                "license": 0,
                "file_name": img_url.split('/')[-1],
                "xtreme1_url": "",
                "width": img_width,
                "height": img_height,
                "date_captured": None
        }
        images.append(one_image)
        img_id += 1

    info = {
        "contributor": "",
        "date_created": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "description": 'Basic AI Xtreme1 dataset datasetname exported to COCO format (https://github.com/basicai/xtreme1)',
        "url": "https://github.com/basicai/xtreme1",
        "year": datetime.today().year,
        "version": "0.5.5",
    }

    final_json = {
        "info": info,
        "licenses": [],
        "images": images,
        "annotations": annotation,
        "categories": categorys
    }
    save_json = join(export_path, 'coco_results.json')
    with open(save_json, 'w', encoding='utf-8') as jf:
        json.dump(final_json, jf, indent=1, ensure_ascii=False)


def main(zip_src: str, dst_dir: str):
    unzip_file(zip_src, dst_dir)
    coco_converter(dst_dir)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('zip_src', type=str, help='The path of the zip file')
    parser.add_argument('dst_dir', type=str, help='The export folder')
    args = parser.parse_args()

    zip_src = args.zip_src
    dst_dir = args.dst_dir
    # zip_src = r"C:\Users\EDY\Downloads\t1024-20221222083506.zip"
    # dst_dir = r"C:\Users\EDY\Downloads\output"
    main(zip_src, dst_dir)
