# -*- coding: utf-8 -*- 
# @Time : 2022/12/26
# @Author : zhangsihao@basicfinder.com
"""
"""
import pandas as pd
import requests
import os


def save_video(url, save_file):
    rps = requests.get(url, stream=True)
    with open(save_file, 'wb') as f:
        for chunk in rps.iter_content(chunk_size=10240):
            f.write(chunk)


def parse_excel(save_path):
    excel = r"D:\Desktop\Project_file\李伟豪\100条样本试标.xlsx"
    df = pd.read_excel(excel, sheet_name='Sheet1')
    series = df[['author_name', 'title', 'mt_content_link']]
    name_num = 1
    for obj in series.iloc[1:-1]:
        save_file = os.path.join(save_path, f'{name_num:.2d}')
        name_num += 1
        auther = obj['author_name']
        title = obj['title']
        url = obj['mt_content_link']
        save_video(url, save_file)
