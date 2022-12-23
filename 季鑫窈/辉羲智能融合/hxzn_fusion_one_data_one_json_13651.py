# -*- coding: utf-8 -*- 
# @Time : 2022/11/28
# @Author : zhangsihao@basicfinder.com
"""
"""
import os
import json
from tqdm import tqdm


class_type_mapping = {
    "小型车": 'car',
    "货车": 'truck',
    "分节车": 'split_vehicle',
    "公交车": 'bus',
    "三轮车": 'tricycle',
    "异形车": 'special_vehicle',
    "人": 'pedestrian',
    "有人的两轮车": 'cyclist',
    "无人的两轮车": 'bicycle',
    "动物": 'animal',
    "车辆附属物": 'attach_vehicle',
    "VRU的附属物": 'attach_vru',
    "杆子 栏杆": 'banner',
    "锥桶 水桶": 'cone',
    "立柱": 'pillar',
    "水马": 'barrier',
    "交通警示栏": 'fence_on_road',
    "相邻的障碍物": 'merged',
    "本车道": '0',
    "对向车道": '1',
    "遮挡": 'camera_invisible',
    "车辆": 'vehicle',
    "附属物": 'attachment',
    "静态障碍物": 'static_object',
    "忽略框": 'ignore',
    "道路施工围栏": 'stop_fence',
    "Hard": 'Hard'
}


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_list.append(os.path.join(root, file))
    return file_list


def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def update_json(json_dir: str, check_file: str):
    null_err = []
    miss_attr = []
    for file in tqdm(list_files(json_dir)):
        json_content = load_json(file)
        data = json_content['data']
        data_id = json_content['data_id']
        ext = json_content['ext']
        boxes = json_content['result']['data']
        info = json_content['result']['info']
        data_deleted_file = json_content['result']['data_deleted_file']
        box_data = []
        for box in boxes:
            int_id = box['trackName']
            frame_number = box['frame'] + 1
            mark_dir = {
                "job_id": data_id,
                "frame_number": frame_number,
                "box_id": int_id
            }
            box['mark_dir'] = mark_dir
            attrs = box['attrs']
            class_type = box['classType']
            if class_type in ['ignore', '忽略框', 'Hard']:
                continue
            elif not class_type:
                null_str = f"作业ID:{data_id} - 第{frame_number}帧 - {int_id}号框无标签"
                null_err.append(null_str)
                continue
            else:
                obj_type = box['objType']
                class_type = box['classType']
                box['classType'] = class_type_mapping[class_type]
                if obj_type == '3d':
                    if attrs:
                        x, y, z = box['center3D'].values()
                        nx, ny, nz = box['size3D'].values()
                        if not x or not y or not z or not nx or not ny or not nz:
                            null_str = f"作业ID:{data_id} - 第{frame_number}帧 - {int_id}号框有null值"
                            null_err.append(null_str)
                            continue
                        else:
                            new_attrs = {}
                            nk = False
                            need_key = ['车辆', 'VUR', 'VRU', '附属物', '静态障碍物']
                            for attr_k, attr_v in attrs.items():
                                if attr_k in need_key:
                                   nk = True
                                else:
                                    nk = nk
                                if attr_k == 'VUR':
                                    new_attrs['VRU'] = attr_v
                                elif attr_v == '本车道':
                                    new_attrs[attr_k] = '0'
                                elif attr_v == '对向车道':
                                    new_attrs[attr_k] = '1'
                                else:
                                    new_attrs[attr_k] = attr_v

                            if nk:
                                box['attrs'] = new_attrs
                                box_data.append(box)
                            else:
                                attr_err = f"作业ID:{data_id} - 第{frame_number}帧 - {int_id}号框缺少属性"
                                miss_attr.append(attr_err)
                                continue
                    else:
                        attr_err = f"作业ID:{data_id} - 第{frame_number}帧 - {int_id}号框缺少属性"
                        miss_attr.append(attr_err)
                        continue
                else:
                    if attrs:
                        new_attrs = {}
                        nk = False
                        need_key = ['车辆', 'VUR', 'VRU', '附属物', '静态障碍物']
                        for attr_k, attr_v in attrs.items():
                            if attr_k in need_key:
                               nk = True
                            else:
                                nk = nk
                            if attr_k == 'VUR':
                                new_attrs['VRU'] = attr_v
                            elif attr_v == '本车道':
                                new_attrs[attr_k] = '0'
                            elif attr_v == '对向车道':
                                new_attrs[attr_k] = '1'
                            else:
                                new_attrs[attr_k] = attr_v

                        if nk:
                            box['attrs'] = new_attrs
                            box_data.append(box)
                        else:
                            attr_err = f"作业ID:{data_id} - 第{frame_number}帧 - {int_id}号框缺少属性"
                            miss_attr.append(attr_err)
                            continue
                    else:
                        attr_err = f"作业ID:{data_id} - 第{frame_number}帧 - {int_id}号框缺少属性"
                        miss_attr.append(attr_err)
                        continue

        result = {
            "data": box_data,
            "info": info,
            "data_deleted_file": data_deleted_file
        }
        new_content = {
            "data": data,
            "result": result,
            "data_id": data_id,
            "ext": ext
        }
        with open(file, 'w', encoding='utf-8') as nf:
            nf.write(json.dumps(new_content, ensure_ascii=False))
    detection_info = {
        "has_nan": null_err,
        "missing_attributes": miss_attr
    }
    if not os.path.exists(check_file):
        with open(check_file, 'w', encoding='utf-8') as df:
            df.write(json.dumps(detection_info, indent=1))
    else:
        with open(check_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            detection_content = json.loads(content)
            detection_content['detection_info'] = detection_info
            with open(check_file, 'w', encoding='utf-8') as df:
                df.write(json.dumps(detection_content, indent=1))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('json_dir', type=str)
    parser.add_argument('check_file', type=str)
    args = parser.parse_args()

    json_dir = args.json_dir
    check_file = args.check_file

    # json_dir = r"C:\Users\EDY\Downloads\下载结果_json_45210_114668_20221223175018"
    # check_file = r"C:\Users\EDY\Downloads\下载结果_json_45210_114668_20221223175018\check file.json"
    update_json(json_dir, check_file)
