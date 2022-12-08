# -*- coding: utf-8 -*- 
# @Time : 2022/12/8
# @Author : zhangsihao@basicfinder.com
"""
韩国客户X1-V0.5版本反显至V0.6结果转换脚本
"""
import json
import os
from tqdm import tqdm


def list_files(in_path: str, suffix_match):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == suffix_match:
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
        for j1 in json_content:  # 遍历一个dataset下的单帧结果及连续帧整体
            dir_name = j1['name']
            save_path = os.path.join(os.path.dirname(result_file), dir_name)
            if not os.path.exists(save_path):
                os.mkdir(save_path)
            one_file_data = j1['data']  #
            frame_count = 0
            for obj in tqdm(one_file_data, desc=f"{dir_name}", unit='frame'):
                frame_count += 1
                pcd_url = obj['pointCloud']
                file_name = os.path.splitext(os.path.basename(pcd_url))[0]
                save_json_file = os.path.join(save_path, file_name + '.json')
                results = obj['results']
                if not results:
                    no_result_str = f"{dataset_name} / {dir_name} / {file_name}(frame_number:{frame_count}) | has no annotated results"
                    no_result.append(no_result_str)
                    continue
                else:
                    objects = []
                    for result in results:
                        boxes = result['objects']
                        for box in boxes:
                            if 'classType' and 'trackName' in box.keys():
                                obj_type = box['objType']
                                if obj_type == '3d':
                                    label = box['classType']
                                    track_name = box['trackName']
                                    if not label:
                                        no_label_str = f"{dataset_name} / {dir_name} / {file_name}(frame_number:{frame_count}) / object name:{track_name} | No label selected"
                                        empty_label.append(no_label_str)
                                        continue
                                    else:
                                        size = box['size3D']
                                        center = box['center3D']
                                        rotation = box['rotation3D']
                                        box = {
                                            "type": "3D_BOX",  # 2D_BOX 2D_RECT
                                            "trackId": track_id,
                                            "trackName": track_name,
                                            "classValues": [{
                                                "id": attr_id,
                                                "pid": None,
                                                "pvalue": None,
                                                "name": '',
                                                "value": attr_type,
                                                "alias": '',
                                                "isLeaf": True
                                            }],
                                            "contour": {
                                                "points": [],
                                                "pointN": pointN,
                                                "size3D": size,
                                                "center3D": center,
                                                "rotation3D": rotation
                                            },

                                        }
                                        objects.append(box)
                                else:
                                    continue
                            else:
                                no_label_str = f"{dataset_name} / {dir_name} / {file_name}(frame_number:{frame_count}) | Only model tags"
                                only_model.append(no_label_str)
                                continue

                if not objects:
                    continue
                else:
                    result_json = {
                        "version": "1.0",
                        "sourceType": "EXTERNAL_GROUND_TRUTH ",
                        "objects": objects
                    }
                    with open(save_json_file, 'w', encoding='utf-8') as f:
                        json.dump(result_json, f, ensure_ascii=False)
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




