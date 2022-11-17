# -*- coding: utf-8 -*- 
# @Time : 2022/11/15
# @Author : zhangsihao@basicfinder.com
"""
"""
import os
from tqdm import tqdm
import json
import shutil


def list_files(in_path: str, match):
    file_name_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == match:
                file_name_list.append(os.path.splitext(os.path.basename(file))[0])
    return file_name_list


def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def parse_result(json_file):
    r_data = []
    jc = load_json(json_file)
    for obj in jc:
        track_id =
        track_name =

        frame =

        box = {
            "objType": "3d",
            "trackId": track_id,
            "trackName": track_name,
            "center3D": {
              "x": x,
              "y": y,
              "z": z
            },
            "rotation3D": {
              "x": rx,
              "y": ry,
              "z": rz
            },
            "size3D": {
              "x": length,
              "y": width,
              "z": height
            },
            "frame": frame
        }
        r_data.append(box)
    return r_data


def write_json(in_path, frame_max):
    result_json_path = os.path.join(in_path, 'result_json')
    frame = 0
    set = 1
    urls = []
    result_data = []
    for file in list_files(result_json_path, '.json'):
        file_name = os.path.splitext(os.path.basename(file))[0]

        one_file_data = parse_result(file)
        result_data.append(one_file_data)

        url = {
            "3d_url": file_name + '.pcd',
            "3d_img0": file_name + '.jpg',
            "3d_img1": file_name + '.jpg',
            "camera_config": file_name + '.json',
        }
        urls.append(url)

        frame += 1
        if frame > frame_max:
            final_data = {
                "data": {
                    "urls": urls
                },
                "result": {
                    "data": result_data,
                    "info": []
                }
            }
            out_path = os.path.dirname(in_path)
            dir_name = f"set{set:02d}"
            ai_result_path = os.path.join(out_path, dir_name, 'ai_result')
            if not os.path.exists(ai_result_path):
                os.makedirs(ai_result_path, exist_ok=True)
            ai_result_file = os.path.join(ai_result_path, dir_name + '.json')
            with open(ai_result_file, 'w', encoding='utf-8') as f:
                json.dump(final_data, f)
            frame = 0
            set += 1
            urls = []
            result_data = []
        else:
            continue


if __name__ == '__main__':

