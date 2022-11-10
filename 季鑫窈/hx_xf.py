# -*- coding: utf-8 -*- 
# @Time : 2022/11/10
# @Author : zhangsihao@basicfinder.com
"""
"""
import os
import json
from tqdm import tqdm


def list_files(in_path: str, match):
    file_name_list = []
    for root, _, files in os.walk(in_path):
        for file in tqdm(files):
            if os.path.splitext(file)[-1] == match:
                file_name_list.append(os.path.splitext(os.path.basename(file))[0])
    return file_name_list


jf = r"D:\Desktop\Project file\季鑫窈\辉曦智能\name_list_set3.json"
r_dir = r"C:\Users\EDY\Downloads\下载结果_json_43957_more_20221110140712\third_20220927.zip\third_20220927"
namel = list_files(r_dir, '.json')
print(len(namel))
jd = {
    "name": namel
}
with open(jf, 'w') as f:
    json.dump(jd, f)
