# _*_ coding=: utf-8 _*_
import os
import json
from tqdm import tqdm


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


def counttype(path):
    txt_data = []
    for file in tqdm(list_files(path)):
        json_content = load_json(file)
        data_id = json_content['data_id']
        boxes = json_content['result']['data']
        for box in boxes:
            mt = box['type']
            intid = box['intId']
            if mt == 'polygon':
                ply_line = f"{data_id}-{intid}号框\n"
                txt_data.append(ply_line)
            else:
                continue
    return txt_data


def count_with_dir(o_path):
    dir_list = []
    for file in list_files(o_path):
        dir_list.append(os.path.dirname(file))

    path_list = set(dir_list)
    return path_list


path = r"C:\Users\EDY\Downloads\吉利前视0930"
txt_f = r"C:\Users\EDY\Downloads\吉利前视0930\detection_info.txt"
txt = counttype(path)

with open(txt_f, 'w') as tf:
    tf.writelines(txt)


