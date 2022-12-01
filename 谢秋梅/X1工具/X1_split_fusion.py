# -*- coding: utf-8 -*- 
# @Time : 2022/12/1
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
    only_model = []
    check_file = os.path.join(os.path.dirname(result_file), 'check_info.json')
    json_data = load_json(result_file)
    dataset_name = json_data['datasetName']
    json_content = json_data['contents']
    if not json_content:
        print("This file has no annotation result")
    else:
        for j1 in json_content:
            dir_name = j1['name']
            save_path_box2d = os.path.join(os.path.dirname(result_file), 'results_2.5D', dir_name)
            if not os.path.exists(save_path_box2d):
                os.makedirs(save_path_box2d, exist_ok=True)
            save_path_box3d = os.path.join(os.path.dirname(result_file), 'results_3D', dir_name)
            if not os.path.exists(save_path_box3d):
                os.makedirs(save_path_box3d, exist_ok=True)
            one_file_data = j1['data']
            frame_count = 0
            for obj in tqdm(one_file_data, desc=f"{dir_name}", unit='frame'):
                frame_count += 1
                pcd_url = obj['pointCloud']
                file_name = os.path.splitext(os.path.basename(pcd_url))[0]
                save_json_file_box2d = os.path.join(save_path_box2d, file_name + '.json')
                save_json_file_box3d = os.path.join(save_path_box3d, file_name + '.json')
                results = obj['results']
                if not results:
                    no_result_str = f"{dataset_name} / {dir_name} / {file_name}(frame_number:{frame_count}) | has no annotated results"
                    no_result.append(no_result_str)
                    continue
                else:
                    annotation_2d = []
                    annotation_3d = []
                    for result in results:
                        boxes = result['objects']
                        for box in boxes:
                            if 'classType' and 'trackName' in box.keys():
                                obj_type = box['objType']
                                label = box['classType']
                                track_name = box['trackName']
                                if not label:
                                    no_label_str = f"{dataset_name} / {dir_name} / {file_name}(frame_number:{frame_count}) / object name:{track_name} | No label selected"
                                    empty_label.append(no_label_str)
                                    continue
                                else:
                                    if obj_type == '3d':
                                        size = box['size3D']
                                        center = box['center3D']
                                        rotation = box['rotation3D']
                                        box = {
                                            "obj_id": track_name,
                                            "classType": label,
                                            "attrs": box['attrs'],
                                            "position": center,
                                            "rotation": rotation,
                                            "scale": size
                                            }
                                        annotation_3d.append(box)
                                    elif obj_type == 'box2d':
                                        coordinate = box['points']
                                        frontid = box['frontId']

                                        box2d = {
                                            "objType": 'box2d',
                                            "coordinate": coordinate,
                                            "classType": label,
                                            "attrs": box['attrs'],
                                            "color": '#7dfaf2',
                                            "frontId": frontid
                                        }
                                        annotation_2d.append(box2d)
                                    else:
                                        continue
                            else:
                                no_label_str = f"{dataset_name} / {dir_name} / {file_name}(frame_number:{frame_count}) | Only model tags"
                                only_model.append(no_label_str)
                                continue

                if not annotation_2d and not annotation_3d:
                    continue
                else:
                    result_json_2d = {
                        "Annotation": annotation_2d
                    }
                    with open(save_json_file_box2d, 'w', encoding='utf-8') as f:
                        json.dump(result_json_2d, f, ensure_ascii=False, indent=1)

                    result_json_3d = {
                        "Annotation": annotation_3d
                    }
                    with open(save_json_file_box3d, 'w', encoding='utf-8') as f:
                        json.dump(result_json_3d, f, ensure_ascii=False, indent=1)

    check_content = {
        "No_annotated_results": no_result,
        "empty_label": empty_label,
        "Only_model_tags": only_model
    }
    with open(check_file, 'w', encoding='utf-8') as cf:
        cf.write(json.dumps(check_content, ensure_ascii=False))

if __name__ == '__main__':
    result_file = input("Please enter the path of the JSON file exported by the platform\n")
    # result_file = r"C:\Users\EDY\Downloads\1. 오류 발생 json 샘플\1. 坷幅 惯积 json 基敲\林_厚_绊加_103331_N09楷林2-20221102065148.json"
    split_folder(result_file)
    input("***Complete***\nPress any key to exit")



