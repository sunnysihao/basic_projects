# -*- coding: utf-8 -*- 
# @Time : 2023/1/11
# @Author : zhangsihao@basicfinder.com
"""
Bunch all jobs in one json file, the url retains only the filename
"""
import os
import json


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


def main(result_json):
    result_data = []
    jc = load_json(result_json)
    for rt in jc:
        result = rt['result']
        url = rt['data']['image_url'].split('/')[-1]

        one = {
            "data": {
                "image_url": url
            },
            "result": result
        }
        result_data.append(one)
    with open(result_json, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=1)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('result_json', type=str)
    args = parser.parse_args()

    result_json = args.result_json
    # result_json = r"C:\Users\EDY\Downloads\Download tasks_json_21580_18431_20230111074911 - 副本.json"
    main(result_json)
