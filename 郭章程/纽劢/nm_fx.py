# -*- coding: utf-8 -*- 
# @Time : 2022/11/15
# @Author : zhangsihao@basicfinder.com
"""
纽劢点云融合连续帧反显数据预处理
"""
import os
from tqdm import tqdm
import json
import shutil
import uuid


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


def copy_file(ori_path, out_path, dir_name, final_dir, file_name, suffix):
    ori_file = os.path.join(ori_path, file_name + suffix)
    set_file_path = os.path.join(out_path, dir_name, final_dir)
    if not os.path.exists(set_file_path):
        os.makedirs(set_file_path, exist_ok=True)
    new_file = os.path.join(set_file_path, file_name + suffix)
    shutil.copyfile(ori_file, new_file)


def write_json(in_path, frame_count):
    ori_json_path = os.path.join(in_path, 'label')
    ori_pcd_path = os.path.join(in_path, 'pcd')
    out_path = os.path.join(os.path.dirname(in_path), 'upload_files')
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    set = 0
    files = list_files(ori_json_path, '.json')
    for i in range(0, len(files), frame_count):
        box_num = 0
        frame = 0
        urls = []
        result_data = []
        dir_name = f"set{set:02d}"
        set_file = files[i:i+frame_count]
        for file in tqdm(set_file):
            file_name = os.path.splitext(os.path.basename(file))[0]
            copy_file(ori_pcd_path, out_path, dir_name, '3d_url', file_name, '.pcd')
            for fd in ['3d_img0', '3d_img1', '3d_img2', '3d_img3', '3d_img4', '3d_img5']:
                copy_file(ori_pcd_path, out_path, dir_name, fd, file_name, '.png')

            jc = load_json(file)
            for obj in jc:
                track_name = box_num
                box_num += 1
                track_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, str(track_name)))
                psr = obj['psr']
                center = psr['position']
                rotation = psr['rotation']
                size = psr['scale']
                label = obj['obj_type']
                degree = obj['flag']

                box = {
                    "objType": "3d",
                    "trackId": track_id,
                    "trackName": track_name,
                    "center3D": center,
                    "rotation3D": rotation,
                    "size3D": size,
                    "classType": label,
                    "attrs": {
                        "degree": degree
                    },
                    "frame": frame
                }
                result_data.append(box)

            url = {
                "3d_url": file_name + '.pcd'
            }
            urls.append(url)
            frame += 1

        final_data = {
            "data": {
                "urls": urls
            },
            "result": {
                "data": result_data,
                "info": []
            }
        }

        ai_result_path = os.path.join(out_path, dir_name, 'ai_result')
        if not os.path.exists(ai_result_path):
            os.makedirs(ai_result_path, exist_ok=True)

        ai_result_file = os.path.join(ai_result_path, dir_name + '.json')

        with open(ai_result_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f)
        set += 1


if __name__ == '__main__':
    in_path = r"D:\Desktop\Project_file\郭章程\雷达\雷达"
    write_json(in_path, 10)
