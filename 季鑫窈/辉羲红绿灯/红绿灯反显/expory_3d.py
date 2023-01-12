# -*- coding: utf-8 -*- 
# @Time : 2023/1/12
# @Author : zhangsihao@basicfinder.com
"""
"""
import json
import os
from os.path import  *
from tqdm import tqdm


def list_files(in_path: str, match):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if splitext(file)[-1] == match:
                file_list.append(join(root, file))
    return file_list


def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def main(result_dir, ori_dir, save_dir):
    for file in tqdm(list_files(result_dir, '.json')):
        file_name = basename(file)
        ori_file = join(ori_dir, splitext(file_name)[0], 'label', file_name)
        new_file = join(save_dir, file_name)
        ori_json = load_json(ori_file)
        jc = load_json(file)
        attr_index = {}
        for obj in jc['result']['data']:
            kv = {}
            super = obj['classType']
            kv['super_class'] = super
            int_id = obj['trackName']
            if not int_id:
                int_id = 0
            else:
                int_id = int_id
            attrs = obj['attrs']
            if '小类' in attrs.keys():
                class_type = attrs['小类']
            else:
                class_type = attrs['invisible']
            relevance = attrs.get('Relevance')
            occupied = attrs.get('Occupied')
            group = attrs.get('Group')
            kv['class_type'] = class_type
            kv['relevance'] = relevance
            kv['occupied'] = occupied
            kv['group'] = group
            attr_index[f"{int_id}"] = kv

        head = ori_json['head']
        annos = ori_json['annos']
        new_annos = []
        for anno in annos:
            obj_id = anno['object_id']
            attr_value = attr_index[f'{obj_id}']
            anno["super_class"] = attr_value['super_class']
            anno["class"] = attr_value.get('class_type')
            anno["relevance"] = attr_value.get('relevance')
            anno["occupied"] = attr_value.get('occupied')
            anno["group"] = attr_value.get('group')
            new_annos.append(anno)

        new_json = {
            "head": head,
            "annos": new_annos
        }
        with open(new_file, 'w', encoding='utf-8') as f:
            json.dump(new_json, f)


if __name__ == '__main__':
    result_dir = r"C:\Users\EDY\Downloads\hx_3d\DR7857_20221107110129.zip"
    ori_dir = r"D:\Desktop\Project_file\季鑫窈\辉曦智能\红绿灯新\20230104\origin\DR7857_20221107110129"
    save_dir = r"C:\Users\EDY\Downloads\hx_3d\DR7857_20221107110129_result_3d"
    main(result_dir, ori_dir, save_dir)
