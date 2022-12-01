# -*- coding: utf-8 -*- 
# @Time : 2022/11/30
# @Author : zhangsihao@basicfinder.com
"""
"""
import json
import os
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


def split_folder(result_file: str):
    empty_label = []
    no_result = []
    not_polygon = []
    check_file = os.path.join(os.path.dirname(result_file), 'check_info.json')
    json_data = load_json(result_file)
    dataset_name = json_data['datasetName']
    json_content = json_data['contents']
    if not json_content:
        print("This file has no annotation result")
    else:
        for j1 in tqdm(json_content, desc=f"{dataset_name}", unit='frame'):
            file_name = os.path.splitext(j1['name'])[0]
            save_path = os.path.join(os.path.dirname(result_file), dataset_name)
            if not os.path.exists(save_path):
                os.mkdir(save_path)
            results = j1['data']['results']
            if not results:
                no_result_str = f"{dataset_name} / {file_name} | has no annotated results"
                no_result.append(no_result_str)
                continue
            else:
                save_json_file = os.path.join(save_path, file_name + '.json')
                annotation = []
                for result in results:
                    boxes = result['objects']
                    for box in boxes:
                        obj_type = box['objType']
                        if obj_type == 'polygon':
                            label = box['classType']
                            frontid = box['frontId']
                            if not label:
                                no_label_str = f"{dataset_name} / {file_name}  | Some object no label selected"
                                empty_label.append(no_label_str)
                                continue
                            else:
                                coordinate = box['coordinate']
                                box = {
                                    "objType": 'polygon',
                                    "coordinate": coordinate,
                                    "classType": label,
                                    "attrs": box['attrs'],
                                    "color": box['color'],
                                    "frontId": frontid
                                }
                                annotation.append(box)
                        else:
                            no_label_str = f"{dataset_name} / {file_name} | Some object not a polygon"
                            not_polygon.append(no_label_str)
                            continue
                    if not annotation:
                        continue
                    else:
                        result_json = {
                            "Annotation": annotation
                        }
                        with open(save_json_file, 'w', encoding='utf-8') as f:
                            json.dump(result_json, f, ensure_ascii=False)

    check_content = {
        "No_annotated_results": no_result,
        "empty_label": empty_label,
        "not_a_polygon": not_polygon
    }
    with open(check_file, 'w', encoding='utf-8') as cf:
        cf.write(json.dumps(check_content, ensure_ascii=False))

if __name__ == '__main__':
    result_file = input("Please enter the path of the JSON file exported by the platform\n")
    # result_file = r"C:\Users\EDY\Downloads\1. 오류 발생 json 샘플\1. 坷幅 惯积 json 基敲\林_厚_绊加_103331_N09楷林2-20221102065148.json"
    split_folder(result_file)
    input("***Complete***\nPress any key to exit")



