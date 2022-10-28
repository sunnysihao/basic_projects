# _*_ coding=: utf-8 _*_
# -*- coding: utf-8 -*-
# 解压zip文件
import zipfile
import os
import sys

# reload(sys)
# sys.setdefaultencoding('gbk')  # 如遇到无法识别中文而报错使用


# 将zip文件解压处理，并放到指定的文件夹里面去

def unzip_file(zip_file_name, destination_path):
    archive = zipfile.ZipFile(zip_file_name, mode='r')
    for file in archive.namelist():
        archive.extract(file, destination_path)


a = "D:\Desktop\BasicProject\youdao"  # zipfile 的路径
b = "D:\Desktop\BasicProject\youdao_unzip"  # 解压到路径unzip下


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.zip':
                file_list.append(os.path.join(root, file))
    return file_list


# 入口函数
def main(a_path):
    for file in list_files(a_path):

    fn = zipfile_name(a)
    for file in fn:
        unzip_file(file, b)


if __name__ == "__main__":
    main()
    print("done")

# zipfile解压中文zip文件会导致乱码，解决方案是要修改python库中的zipfile.py
# 将文件中所有的'cp437'字符替换为'gbk'
