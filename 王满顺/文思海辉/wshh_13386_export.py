# -*- coding: utf-8 -*- 
# @Time : 2022/11/4
# @Author : zhangsihao@basicfinder.com
"""
文思海辉,模板13386,点云连续帧(beta)标注，一帧一结果导出脚本
"""
import os
import json


def list_files(in_path: str, suffix_match: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == suffix_match:
                file_list.append(os.path.join(root, file))
            else:
                continue
    return file_list


def load_json(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        json_content = json.load(f)
    return json_content


