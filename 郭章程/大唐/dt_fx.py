# -*- coding: utf-8 -*- 
# @Time : 2022/11/15
# @Author : zhangsihao@basicfinder.com
"""
大唐移动点云标注反显数据预处理
"""
import os
import json
import shutil
from nanoid import generate
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


def create_config_file(camera_config_file: str, view_num: int):
    one_data = {
        "camera_internal": {
            "fx": 1295,
            "cx": 973,
            "cy": 570,
            "fy": 1296
        },
        "camera_external": [1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0]
    }
    data = {}
    for i in range(view_num):
        data[f"3d_img{i}"] = one_data
    with open(camera_config_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data))


def is_float(src_str):
    try:
        float(src_str)
        r = True
    except:
        r = False
    return r


def match_with_timestamp(pcd_folder: str, jpg_folder: str):
    print("************************************")
    timestamp_check = True
    pcd_files = list_files(pcd_folder, '.pcd')
    for f1 in pcd_files:
        timestamp_check = is_float(os.path.splitext(os.path.basename(f1))[0])
    img_file = list_files(jpg_folder, '.jpg')
    for f2 in img_file:
        timestamp_check = is_float(os.path.splitext(os.path.basename(f2))[0])
    if timestamp_check:
        for pcd_folder in tqdm(pcd_files):
            pcd_prefix = os.path.splitext(os.path.basename(pcd_folder))[0]
            dict = {k: eval(pcd_prefix) - eval(os.path.splitext(os.path.basename(k))[0]) for k in img_file}
            value = 0
            img_key, diff_val = min(dict.items(), key=lambda x: abs(value - x[1]))
            src_img = os.path.join(jpg_folder, img_key)
            new_img_path = os.path.join(os.path.dirname(jpg_folder), 'images')
            if not os.path.exists(new_img_path):
                os.makedirs(new_img_path)
            new_img = os.path.join(new_img_path, pcd_prefix + '.jpg')
            shutil.copyfile(src_img, new_img)
    else:
        print("文件名不符合时间戳格式，无法进行时序对齐")

id_info = []
def write_json(in_path, frame_count):
    global id_info
    ori_json_path = os.path.join(in_path, 'label')
    ori_pcd_path = os.path.join(in_path, 'point')
    old_img_path = os.path.join(in_path, 'img')
    match_with_timestamp(ori_pcd_path, old_img_path)
    ori_img_path = os.path.join(in_path, 'images')
    out_path = os.path.join(in_path, 'upload_files')
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
        for file in set_file:
            file_name = os.path.splitext(os.path.basename(file))[0]
            ori_pcd_file = os.path.join(ori_pcd_path, file_name + '.pcd')
            set_pcd_path = os.path.join(out_path, dir_name, '3d_url')
            if not os.path.exists(set_pcd_path):
                os.makedirs(set_pcd_path, exist_ok=True)
            new_pcd_file = os.path.join(set_pcd_path, file_name + '.pcd')
            shutil.copyfile(ori_pcd_file, new_pcd_file)
            ori_img_file = os.path.join(ori_img_path, file_name + '.jpg')
            set_img_path = os.path.join(out_path, dir_name, '3d_img0')
            if not os.path.exists(set_img_path):
                os.makedirs(set_img_path, exist_ok=True)
            new_img_file = os.path.join(set_img_path, file_name + '.jpg')
            shutil.copyfile(ori_img_file, new_img_file)
            set_cfg_path = os.path.join(out_path, dir_name, 'camera_config')
            if not os.path.exists(set_cfg_path):
                os.makedirs(set_cfg_path, exist_ok=True)
            new_cfg_file = os.path.join(set_cfg_path, file_name + '.json')
            create_config_file(new_cfg_file, 1)

            jc = load_json(file)
            for obj in jc:
                track_name = box_num
                box_num += 1
                track_id = generate(size=16)
                id_info.append(track_id)
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
                    "classType": '',
                    "attrs": {
                        "degree": degree
                    },
                    "frame": frame
                }
                result_data.append(box)

            url = {
                "3d_url": file_name + '.pcd',
                "3d_img0": file_name + '.jpg',
                "camera_config": file_name + '.json'
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
        print(rf"{out_path}\{dir_name}")




if __name__ == '__main__':
    i_path = r"D:\Desktop\Project_file\郭章程\大唐\补标数据demo\补标数据demo\成都园区测试场\雷达"
    # in_path = input("请输入路径:\n")
    for n in ['1', '2', '3', '4']:
        in_path = os.path.join(i_path, n)
        print("*********反显数据保存路径*********")
        write_json(in_path, 10)
    id_info_file = os.path.join(i_path, 'ids_info.json')
    jc = {
        "ids": id_info
    }
    with open(id_info_file, 'w', encoding='utf-8') as idf:
        json.dump(jc, idf)
    print(f"**********反显框保存路径**********\n{id_info_file}")
    input("已完成，按任意键退出")
