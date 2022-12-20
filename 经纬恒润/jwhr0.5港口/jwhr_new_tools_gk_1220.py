# _*_ coding=: utf-8 _*_
# @Time    : 2022/10/20
# @Author  : zhangsihao@basicfinder.com
"""
功能：经纬恒润新私有化平台点云连续帧结果结果导出，针对平台'3D一帧一结果'脚本打包的数据进行转换导出。
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
    count_l = []
    count_box = 0
    marking_error = []
    missing_pcd_file = []
    empty_result_file = []
    for file in tqdm(list_files(in_path)):
        json_content = load_json(file)
        if not json_content:
            empty_result_file.append(f"{file} 无标注结果")
            annotations = []
            with open(file, 'w', encoding='utf-8') as nf:
                nf.write(json.dumps(annotations))
        else:
            if not json_content['result']:
                empty_result_str = f"{file} 无标注结果"
                empty_result_file.append(empty_result_str)
                annotations = []
                with open(file, 'w', encoding='utf-8') as nf:
                    nf.write(json.dumps(annotations))
            else:

                data_id = json_content['data_id']
                boxs = json_content['result']['data']

                annotations = []
                for box in boxs:  # 读取每个3D框数据
                    frame = box['frame'] + 1
                    x, y, z = box['center3D'].values()
                    nx, ny, nz = box['size3D'].values()
                    alpha = box['rotation3D']['z']
                    int_id = box['trackName']
                    box_id = box['trackId']
                    class_type = box['classType']
                    attrs = box['attrs']

                    if class_type == '补框属性':
                        complement = True
                        if not attrs:
                            no_attr_err_str = f"作业ID:{data_id}-第{frame}帧-{int_id}号框补框未选择属性标签"
                            marking_error.append(no_attr_err_str)
                            continue
                        else:
                            label = attrs['Virtual_box']
                        box_data = {
                            "name": label,
                            "bbox_center": [x, y, z],
                            "bbox_size": [nx, ny, nz],
                            "heading": alpha,
                            "complement": complement,
                            "id": int_id,
                            "pkg_id": data_id
                        }
                        annotations.append(box_data)
                        count_box += 1

                    else:
                        complement = False
                        label = class_type

                        box_data = {
                            "name": label,
                            "bbox_center": [x, y, z],
                            "bbox_size": [nx, ny, nz],
                            "heading": alpha,
                            "complement": complement,
                            "id": int_id,
                            "pkg_id": data_id
                        }
                        annotations.append(box_data)
                        count_box += 1
                    count_l.append(label)

                with open(file, 'w', encoding='utf-8') as nf:
                    nf.write(json.dumps(annotations))

    count_info = [f'框总计{count_box}个']
    for one_label in set(count_l):
        count_info.append(f"{one_label}:{count_l.count(one_label)}")
    detection_info = {
        "marking_error": marking_error,
        "count_info": count_info,
        "missing_pcd_file": missing_pcd_file,
        "empty_result_file": empty_result_file
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
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('result_in_path', type=str)
    parser.add_argument('check_file', type=str)
    args = parser.parse_args()

    result_json_path = args.result_in_path
    check_file = args.check_file
    # check_file = r"D:\倍赛\4\4\1662098821\cible_001\lidar_data\lidar - 副本\detection.check.json"
    # result_json_path = r"D:\倍赛\4\4\1662098821\cible_001\lidar_data\lidar - 副本"
    write_json(result_json_path, check_file)
