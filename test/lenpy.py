# -*- coding: utf-8 -*- 
# @Time : 2022/11/16
# @Author : zhangsihao@basicfinder.com
"""
"""

import os
from tqdm import tqdm
import json
import shutil


def list_files(in_path: str, match):
    file_name_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == match:
                file_name_list.append(os.path.splitext(os.path.basename(file))[0])
    return file_name_list


path = r"D:\Desktop\basic_projects"
print(len(list_files(path, '.py')))