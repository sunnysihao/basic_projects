# -*- coding: utf-8 -*- 
# @Time : 2023/1/9
# @Author : zhangsihao@basicfinder.com
"""
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


def main(input_dir, output_dir):
    for file in list_files(input_dir, '.json'):
        file_name = os.path.basename(file)
        jc = load_json(file)
        data = []
        for rect in jc['result']['data']:
            try:
                text = rect['text']
            except Exception:
                continue
            coordinate = rect['coordinate']
            xl = []
            yl = []
            for point in coordinate:
                xl.append(point['x'])
                yl.append(point['y'])

            one = {
                "transcription": text,
                "points": [[min(xl), min(yl)], [max(xl), min(yl)], [max(xl), max(yl)], [min(xl), max(yl)]],
                "difficult": False
            }
            data.append(one)
        new_file = os.path.join(output_dir, file_name)
        with open(new_file, 'w', encoding='utf-8') as nf:
            json.dump(data, nf, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', type=str)
    parser.add_argument('output_dir', type=str)
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir
    # input_dir = r"C:\Users\EDY\Downloads\Download tasks_json_21575_18425_20230106075108\crops_label6_center-20230105T131725Z-001.zip\crops_label6_center"
    # output_dir = r"C:\Users\EDY\Downloads\Download tasks_json_21575_18425_20230106075108\crops_label6_center-20230105T131725Z-001.zip\save"
    main(input_dir, output_dir)
