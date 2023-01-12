# -*- coding: utf-8 -*- 
# @Time : 2023/1/9
# @Author : zhangsihao@basicfinder.com
"""
"""
import os
import uuid
from os.path import join, basename, dirname, splitext, exists
import json
import shutil
from tqdm import tqdm
from nanoid import generate


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


def fx_2d(mosaic_dir, output_dir):
    for label_file in tqdm(list_files(mosaic_dir, '.json')):
        result_data = []
        file_name = splitext(basename(label_file))[0]
        img = join(dirname(dirname(label_file)), 'matrix_img', file_name + '.jpg')
        new_img = join(output_dir, file_name + '.jpg')
        result_json = join(output_dir, file_name + '.json')
        shutil.copyfile(img, new_img)
        label_data = load_json(label_file)
        y = 0
        obj_num = len(label_data['annos'])
        iw = 1950
        ih = (obj_num-2)*450+750
        for obj in label_data['annos']:
            int_id = obj['object_id']
            x = 0
            x1 = x+150
            y1 = y+300
            w = 150
            h = 300
            box_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, file_name + str(int_id)))
            box = {
                "type": 'rect',
                "id": box_id,
                "color": "",
                "label": [],
                "code": [],
                "category": [],
                "catetips": [],
                "label_id": [],
                "text": "",
                "labelAttrs": [],
                "width": w,
                "height": h,
                "area": w * h,
                "intId": int_id,
                "points": [
                    {
                        "x": x / iw,
                        "y": y / ih
                    },
                    {
                        "x": x1 / iw,
                        "y": y / ih,
                    },
                    {
                        "x": x1 / iw,
                        "y": y1 / ih
                    },
                    {
                        "x": x / iw,
                        "y": y1 / ih
                    }
                ],
                "coordinate": [
                    {
                        "x": x,
                        "y": y
                    },
                    {
                        "x": x1,
                        "y": y
                    },
                    {
                        "x": x1,
                        "y": y1
                    },
                    {
                        "x": x,
                        "y": y1
                    }
                ],
                "ih": iw,
                "iw": ih
            }
            result_data.append(box)
            y = y+450
            int_id += 1
        data = {
            "data": {
                "image_url": file_name + '.jpg'
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
        with open(result_json, 'w') as f:
            json.dump(data, f)


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


def main():
    dr = ['DR7857_20221107093913', 'DR7857_20221107110129']
    path = r"/tmp/root/model_saas_data/uploadfile/JXY0109 (admin)/zero_20230106/20230104"
    save_path = r"/tmp/root/model_saas_data/uploadfile/JXY0109 (admin)/zero_20230106/20230104/upload_files"
    mosaic = join(path, 'mosaic')
    origin = join(path, 'origin')
    for d in dr:
        src = join(mosaic, d)
        dst = create_folder(src.replace('mosaic', 'upload_files/mosaic'))
        print("开始处理反显2d")
        fx_2d(src, dst)

        src3d = join(origin, d)
        dst3d = create_folder(src3d.replace('origin', 'upload_files/origin'))
        print("开始处理反显3d")
        reconstruct(src3d, dst3d)


if __name__ == '__main__':
    main()


    # mosaic_dir = r"D:\Desktop\Project_file\季鑫窈\辉曦智能\红绿灯新\20230104\mosaic\DR7857_20221107110129"
    # output_dir = r"D:\Desktop\Project_file\季鑫窈\辉曦智能\红绿灯新\20230104\upload_img\DR7857_20221107110129"
    # fx_2d(mosaic_dir, output_dir)
