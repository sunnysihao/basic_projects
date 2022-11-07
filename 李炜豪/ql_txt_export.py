# -*- coding: utf-8 -*- 
# @Time : 2022/11/7
# @Author : zhangsihao@basicfinder.com
"""
"""
import os
import jsonlines
import json
from tqdm import tqdm


def list_files(in_path: str, suffix_match: str):
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


def ex_txt(json_path, txt_path):
    final_data = []
    resule_file = os.path.join(os.path.dirname(json_path), 'result.jsonl')
    for file in tqdm(list_files(json_path, '.json')):
        json_content = load_json(file)
        results = json_content['result']['data']
        num_id = 0
        anno = []
        for result in results:
            label = result['label'][0]['label']
            start = result['start']
            end = result['end']
            box = {"id": num_id, "label": label, "start_offset": start, "end_offset": end}
            anno.append(box)
            num_id += 1
        file_name = os.path.splitext(os.path.basename(file))[0]
        txt_file = os.path.join(txt_path, file_name + '.txt')
        with open(txt_file, 'r', encoding='utf-8') as tf:
            txt_data = tf.read()
        one_line = {
            "text": txt_data,
            "entities": anno
        }
        final_data.append(one_line)
    with open(resule_file, 'w', encoding='utf-8') as of:
        for entry in final_data:
            json.dump(entry, of, ensure_ascii=False)
            of.write('\n')


if __name__ == '__main__':
    json_path = r"C:\Users\EDY\Downloads\下载结果_json_44682_112502_20221107135125\qilin000.zip\qilin"
    txt_path = r"D:\Desktop\Project file\李伟豪\qilin"
    ex_txt(json_path, txt_path)
