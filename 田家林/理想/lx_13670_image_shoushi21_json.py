# -*- coding: utf-8 -*- 
# @Time : 2022/11/28
# @Author : zhangsihao@basicfinder.com
"""
理想13670模板--- 手势21点 导出脚本
"""
import os
import json
from tqdm import tqdm


def list_files(in_path: str, match):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == match:
                file_list.append(os.path.join(root, file))
    return file_list


def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def trans_result(json_dir: str):
    for file in tqdm(list_files(json_dir, '.json')):
        datalist = []
        jc = load_json(file)
        img_url = jc['data']['image_url']
        file_path = '/' + '/'.join(img_url.split('/')[3:-1]) + '/'
        file_name = img_url.split('/')[-1]
        r_data = jc['result']['data']
        for box in r_data:
            obj_type = box['type']
            if obj_type == 'bonepoint':
                nodes = box['nodes']
                points = []
                for node in nodes:
                    code = node['code'][0]
                    coordinate = node['coordinate']
                    x = coordinate[0]
                    y = coordinate[1]
                    point = {
                        "index": code,
                        "x": x,
                        "y": y
                    }
                    points.append(point)
                new_point = {
                    "type": "points",
                    "points": points
                }
                datalist.append(new_point)

            else:
                coordinate = box['coordinate']
                xl = []
                yl = []
                for point in coordinate:
                    xl.append(point['x'])
                    yl.append(point['y'])

                new_box = {
                    "type": "bbox",
                    "points": [min(xl), min(yl), max(xl), max(yl)]
                }
                datalist.append(new_box)
                    
        final_data = {
            "path": file_path,
            "name": file_name,
            "dataList": datalist
            }
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('json_dir', type=str)
    args = parser.parse_args()

    json_dir = args.json_dir
    # json_dir = r"C:\Users\EDY\Downloads\理想手势21点\20221112.zip\20221112\11-x03v-403-1312\1 - 副本"
    trans_result(json_dir)
