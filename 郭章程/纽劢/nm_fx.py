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
from nanoid import generate


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


cam_map = {
    "J": 0,
    "I": 1,
    "G": 2,
    "H": 3,
    "E": 4,
    "F": 5
}


def write_json(in_path, frame_count):
    ori_json_path = os.path.join(in_path, 'label')
    ori_pcd_path = os.path.join(in_path, '3d_url')
    ori_cfg_path = os.path.join(in_path, 'camera_config')
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
            copy_file(ori_cfg_path, out_path, dir_name, 'camera_config', file_name, '.json')
            for fd in ['3d_img0', '3d_img1', '3d_img2', '3d_img3', '3d_img4', '3d_img5']:
                ori_img_path = os.path.join(in_path, fd)
                copy_file(ori_img_path, out_path, dir_name, fd, file_name, '.png')

            jc = load_json(file)
            cuboids = jc['frames']
            rects = jc['images']
            for obj in cuboids:
                track_name = box_num
                box_num += 1
                track_id = generate(size=16)
                length, width, height = obj['size']
                rz = obj['theta']
                x, y, z = obj['vehicle_coord']

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
                        "x": 0,
                        "y": 0,
                        "z": rz
                    },
                    "size3D": {
                        "x": length,
                        "y": width,
                        "z": height
                    },
                    "classType": '',
                    "attrs": [],
                    "frame": frame
                }
                result_data.append(box)
            for rect in rects:
                track_name = box_num
                box_num += 1
                track_id = generate(size=16)
                cam = rect['cam']
                h = rect['height']
                w = rect['width']
                x = rect['x']
                y = rect['y']

                box = {
                    "objType": "rect",
                    "trackId": track_id,
                    "trackName": track_name,
                    "points": [
                        {"x": x, "y": y},
                        {"x": x+w, "y": y},
                        {"x": x+w, "y": y+h},
                        {"x": x, "y": y+h}
                    ],
                    "viewIndex": cam_map[cam],
                    "center3D": {
                        "x": 0,
                        "y": 0,
                        "z": 0
                    },
                    "rotation3D": {
                        "x": 0,
                        "y": 0,
                        "z": 0
                    },
                    "size3D": {
                        "x": 0,
                        "y": 0,
                        "z": 0
                    },
                    "classType": '',
                    "attrs": [],
                    "frame": frame
                }
                result_data.append(box)

            url = {
                "3d_url": file_name + '.pcd',
                "3d_img0": file_name + '.png',
                "3d_img1": file_name + '.png',
                "3d_img2": file_name + '.png',
                "3d_img3": file_name + '.png',
                "3d_img4": file_name + '.png',
                "3d_img5": file_name + '.png',
                "camera_config": file_name + '.json',
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
    in_path = r"D:\Desktop\Project_file\郭章程\纽劢\4D-sample\4D-sample"
    write_json(in_path, 10)
