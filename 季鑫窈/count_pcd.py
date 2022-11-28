# -*- coding: utf-8 -*- 
# @Time : 2022/11/9
# @Author : zhangsihao@basicfinder.com
"""
"""
import os


def list_files(in_path: str, match):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == match:
                file_list.append(os.path.join(root, file))
    return file_list


def main(path):
    print(f"pcd文件总数{len(list_files(path, '.pcd'))}")


if __name__ == '__main__':
    path = r"/tmp/root/model_saas_data/uploadfile/jxy1127 (admin)/mnt"
    main(path)
