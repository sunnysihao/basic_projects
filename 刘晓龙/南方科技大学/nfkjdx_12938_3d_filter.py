# _*_ coding=: utf-8 _*_
# @Time    : 2022/10/26
# @Author  : zhangsihao@basicfinder.com
"""
功能：南方卡机大学过滤掉点数不足10个点的结果，导出一作业一结果，针对平台'json(一作业一结果)'脚本打包的数据进行过滤导出。
"""
import json
import os
from tqdm import tqdm


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_list.append(os.path.join(root, file))
            else:
                continue
    return file_list


# 读取json文件内容返回python类型的对象
def load_json(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def write_json(in_path: str, check_file: str):
    box_filter_count = 0
    rect_filter_count = 0
    filter_info = []
    for file in tqdm(list_files(in_path)):
        filter_box = []
        json_content = load_json(file)
        json_data = json_content['data']
        data_id = json_content['data_id']
        boxs = json_content['result']['data']
        result_info = json_content['result']['info']
        result_data_deleted = json_content['result']['data_deleted_file']
        boxes = []
        for box in boxs:  # 读取每个3D框数据
            track_id = box['trackId']
            track_name = box['trackName']
            obj_type = box['objType']
            point_num = box['pointN']
            if obj_type == 'rect':
                continue
            else:
                if point_num < 10:
                    filter_box.append(track_id)
                    filter_str = f"data_id:{data_id} | box_name:{track_name} | points_number:{point_num} | " \
                                 f"The number of points is less than 10, and the relevant results have been filtered"
                    filter_info.append(filter_str)
                else:
                    continue
        for box in boxs:  # 读取每个3D框数据
            track_id = box['trackId']
            obj_type = box['objType']
            if track_id in filter_box:
                if obj_type == '3d':
                    box_filter_count += 1
                else:
                    rect_filter_count += 1
                continue
            else:
                boxes.append(box)

        result_json = {
            "data": json_data,
            "result": {
                "data": boxes,
                "info": result_info,
                "data_deleted_file": result_data_deleted
            },
            "data_id": data_id
        }

        with open(file, 'w', encoding='utf-8') as nf:
            nf.write(json.dumps(result_json))

    detection_info = {
        "filter_count": {
            "3d": box_filter_count,
            "rect": rect_filter_count
        },
        "filter_info": filter_info
    }
    if not os.path.exists(check_file):
        with open(check_file, 'w', encoding='utf-8') as df:
            df.write(json.dumps(detection_info))
    else:
        with open(check_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            detection_content = json.loads(content)
            detection_content['detection_info'] = detection_info
            with open(check_file, 'w', encoding='utf-8') as df:
                df.write(json.dumps(detection_content))


if __name__ == "__main__":
    # import argparse
    #
    # parser = argparse.ArgumentParser()
    # parser.add_argument('result_in_path', type=str)
    # parser.add_argument('check_file', type=str)
    # args = parser.parse_args()
    #
    # result_json_path = args.result_in_path
    # check_file = args.check_file
    check_file = r"C:\Users\EDY\Downloads\下载结果_json_43407_106118_20221018153414\detection.check.json"
    result_json_path = r"C:\Users\EDY\Downloads\下载结果_json_43407_106118_20221018153414\新建文件夹 - 副本"
    write_json(result_json_path, check_file)
