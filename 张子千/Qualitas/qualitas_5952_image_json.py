import json
import os
import time


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


check_info = []
visual_categories = [
    {"id": 1, "name": "Cracking", "color": "#0000cd"},
    {"id": 2, "name": "Water damage and stains", "color": "#e63995"},
    {"id": 3, "name": "Sky", "color": "#708090"},
    {"id": 4, "name": "Issues at joints", "color": "#6a5acd"},
    {"id": 5, "name": "Rusting", "color": "#d2691e"},
    {"id": 6, "name": "Irregularly placed items", "color": "#36bf36"},
    {"id": 7, "name": "Windows, doors, openings", "color": "#f8f8ff"},
]
categories_mapping = {
    "Cracking": 1,
    "Water damage and stains": 2,
    "Sky": 3,
    "Issues at joints": 4,
    "Rusting": 5,
    "Irregularly placed items": 6,
    "Windows, doors, openings": 7
}

def trans_format(json_content):
    img_url = json_content['data']['image_url']
    data_time = float(img_url.split('/')[1])
    file_name = os.path.basename(img_url)
    img_id = os.path.splitext(file_name)[0]
    data_id = json_content['data_id']
    img_w = json_content['result']['resourceinfo']['width']
    img_h = json_content['result']['resourceinfo']['height']
    boxes = []

    for box in json_content['result']['data']:
        box_id = box['id']
        int_id = box['intId']
        label0 = box['label']
        if not label0:
            err_str = f"作业ID:{data_id}-{int_id}框无标签"
            check_info.append(err_str)
            continue
        else:
            label = label0[0]
        area = box['area']
        width = box['width']
        height = box['height']
        coordinate = box['coordinate']
        x_l = []
        y_l = []
        for point in coordinate:
            x_l.append(point['x'])
            y_l.append(point['y'])
        x = min(x_l)
        y = min(y_l)
        # c_time = float(str(box['cTime'])[:10])
        box = {
            "id": box_id,
            "image_id": img_id,
            "visual-category_id": categories_mapping[label],
            "business-category_id": "",
            "area": area,
            "bbox": [x, y, width, height],
        }
        boxes.append(box)

    result_json = {
        "info": {},
        "visual-categories": visual_categories,
        "business-categories": [],
        "annotations": boxes,
        "images": [
            {
                "id": img_id,
                "width": img_w,
                "height": img_h,
                "file_name": file_name,
                "folder": img_url,
                "date_captured": ""
            }
        ]
    }
    return result_json


def main(json_dir: str, check_file: str):
    for file in list_files(json_dir):
        json_content = load_json(file)
        result_json = trans_format(json_content)
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(result_json, f)
    check_content = {
        "marking_check": check_info
    }
    if not os.path.exists(check_file):
        with open(check_file, 'w', encoding='utf-8') as cf:
            cf.write(json.dumps(check_content))
    else:
        with open(check_file, 'r', encoding='utf-8-sig') as of:
            of_content = json.loads(of.read())
            of_content["marking_errors"] = check_content
        with open(check_file, 'w', encoding='utf-8') as cf:
            cf.write(json.dumps(of_content))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('json_dir', type=str)
    parser.add_argument('check_file', type=str)
    args = parser.parse_args()

    json_dir = args.json_dir
    check_file = args.check_file
    # check_file = r"C:\Users\EDY\Downloads\Download tasks_json_21441_18233_20221019013158\10 guozi.rar - 副本\check file.json"
    # json_dir = r"C:\Users\EDY\Downloads\Download tasks_json_21441_18233_20221019013158\10 guozi.rar - 副本"
    main(json_dir, check_file)
