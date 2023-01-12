# -*- coding: utf-8 -*- 
# @Time : 2023/1/10
# @Author : zhangsihao@basicfinder.com
"""
"""
import os
from nanoid import generate
from os.path import join, basename, dirname, splitext, exists
import json
import shutil
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


def create_folder(folder_path):
    if not exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
    return folder_path


def reconstruct(src_dir, dst_dir):
    imgs = ['3d_img0', '3d_img1', '3d_img2', '3d_img3', '3d_img4', '3d_img5', '3d_img6']
    cam_dirs = ['CAMERA_FRONT_FAR', 'CAMERA_FRONT_LEFT', 'CAMERA_FRONT_RIGHT', 'CAMERA_FRONT_WIDE',
                'CAMERA_REAR', 'CAMERA_REAR_LEFT', 'CAMERA_REAR_RIGHT']
    for label_file in tqdm(list_files(src_dir, match='.json')):
        file_name = splitext(basename(label_file))[0]
        for i in range(7):
            img = list_files(join(dirname(dirname(label_file)), cam_dirs[i]), '.jpg')[0]
            new_folder = create_folder(join(dst_dir, imgs[i]))
            new_img = join(new_folder, file_name + '.jpg')
            shutil.copyfile(img, new_img)
        pcd = list_files(join(dirname(dirname(label_file)), 'LIDAR_1'), '.pcd')[0]
        n_folder = create_folder(join(dst_dir, '3d_url'))
        new_pcd = join(n_folder, file_name + '.pcd')
        shutil.copyfile(pcd, new_pcd)

        urls = {
            "3d_url": file_name + '.pcd',
            "3d_img0": file_name + '.jpg',
            "3d_img1": file_name + '.jpg',
            "3d_img2": file_name + '.jpg',
            "3d_img3": file_name + '.jpg',
            "3d_img4": file_name + '.jpg',
            "3d_img5": file_name + '.jpg',
            "ai_result": file_name + '.json'
        }

        n_folder = create_folder(join(dst_dir, 'ai_result'))
        result_json = join(n_folder, file_name + '.json')
        trans_result(label_file, result_json, urls)



def trans_result(src_file, dst_file, urls):
    result_data = []
    label_data = load_json(src_file)['annos']
    for obj in label_data:
        int_id = obj['object_id']
        track_id = generate(size=16)
        size = obj['3Dsize']
        box = {
            "objType": "3d",
            "trackId": track_id,
            "trackName": int_id,
            "center3D": obj['3Dcenter'],
            "rotation3D": {
                "x": 0,
                "y": 0,
                "z": size['rz']
            },
            "size3D": {
                "x": size['length'],
                "y": size['width'],
                "z": size['height']
            },
            "classType": '',
            "attrs": []
        }
        result_data.append(box)

    final_data = {
        "data": {
            "urls": urls
        },
        "result": {
            "data": result_data,
            "info": []
        }
    }
    with open(dst_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f)


if __name__ == '__main__':
    src_dir = r"D:\Desktop\Project_file\季鑫窈\辉曦智能\红绿灯新\20230104\origin\DR7857_20221107110129"
    dst_dir = r"D:\Desktop\Project_file\季鑫窈\辉曦智能\红绿灯新\20230104\origin\辉羲3d_upload\DR7857_20221107110129"
    reconstruct(src_dir, dst_dir)
