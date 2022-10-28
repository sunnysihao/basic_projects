# @Time    : 2022/10/21
# @Author  : zhangsihao@basicfinder.com

import os
from tqdm import tqdm
import json


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


def write_new_json(old_json_dir: str, check_file: str):
    label_list = []
    mark_error = []
    detection = {}
    for file in tqdm(list_files(old_json_dir)):
        annotation = []
        json_content = load_json(file)
        img_url = json_content['data']['image_url']
        image_name = os.path.basename(img_url)
        data_id = json_content['data_id']
        result_data = json_content['result']['data']
        img_width = json_content['result']['resourceinfo']['width']
        img_height = json_content['result']['resourceinfo']['height']
        abandon_value = json_content['result']['info'][0]['value']
        if not abandon_value:
            abandon = 'no'
        else:
            abandon = 'yes'
        for line in result_data:
            line_id = line['id']
            label = line['label']
            category = line['category']
            int_id = line['intId']
            coordinate = line['coordinate']
            points = []
            for point in coordinate:
                x = point['x']
                y = point['y']
                points.append([x, y])
            if len(label) == 1:
                line_label = label[0]
                label_list.append(line_label)
            else:
                one_label_err = f"作业id:{data_id}-{int_id}号 | 未标注ignore"
                mark_error.append(one_label_err)
                continue
            label_attrs = line['labelAttrs']
            if not label_attrs:
                ignore = 'no'
            else:
                if label_attrs[0]['value'] == 'yes':
                    ignore = 'yes'
                else:
                    ignore = 'no'

            box = {
                "id": line_id, #对象 ID
                "track_id": -1,#预留字段，暂无意义，固定取值为-1
                "struct_type": "parsing",#标注类型，车道线标注取值为“parsing”
                "attrs": {   #标注对象属性
                    "type": line_label,#类别
                    "ignore": ignore#ignore 属性
                    },
                "data": points,
                "point_attrs": ["null"]*len(points) # 关键点属性，预留字段，固定取值为 null，数组大小与 data 大小一致。
            }
            annotation.append(box)

        image_data = {
            "image_key": image_name,
            "video_name": "",#预留字段，暂无意义，固定取值为空字符串
            "video_index": "",#预留字段，暂无意义，固定取值为空字符串
            "width": img_width,#图片宽度
            "height": img_height,#图片高度
            "abandoned": abandon, #默认为"no"
            "parsing": annotation   #标注对象数组，全图无标注对象时，数组为空
        }

        with open(file, 'w', encoding='utf-8') as rf:
            rf.write(json.dumps(image_data))

    label_set = set(label_list)
    detection["总标签数"] = f"{len(label_list)}"
    for one_label in label_set:
        detection[f"{one_label}"] = label_list.count(one_label)
    detection_info = {
        "count_label": detection,
        "marking_errors": mark_error
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

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('old_json_dir', type=str)
    parser.add_argument('check_file', type=str)
    args = parser.parse_args()

    old_json_dir = args.old_json_dir
    check_file = args.check_file

    # old_json_dir = r"D:\Desktop\BasicProject\尚莉莉\理想\下载结果_json_44249_110767_20221024100510\全景分割.zip - 副本"
    # check_file = r"D:\Desktop\BasicProject\尚莉莉\理想\下载结果_json_44249_110767_20221024100510\全景分割.zip - 副本\check_file.json"

    write_new_json(old_json_dir, check_file)
