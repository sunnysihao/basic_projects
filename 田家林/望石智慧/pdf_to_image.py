# -*- coding: utf-8 -*- 
# @Time : 2022/11/29
# @Author : zhangsihao@basicfinder.com
"""
"""
import fitz
import os
import json
from tqdm import tqdm


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


def pdf2img(pdf_dir):
    for file in tqdm(list_files(pdf_dir, '.pdf')):
        file_name = os.path.splitext(os.path.basename(file))[0]
        pdf = fitz.open(file)
        trans = fitz.Matrix(2.5, 2.5).prerotate(int(0))
        for i in range(pdf.page_count):
            page = pdf[i]
            pm = page.get_pixmap(matrix=trans, alpha=False)
            save_path = os.path.join(os.path.dirname(pdf_dir), 'wszh_upload_images', file_name)
            if not os.path.exists(save_path):
                os.makedirs(save_path, exist_ok=True)
            image = os.path.join(save_path, f"{file_name}_{i}.png")
            pm.save(image)


if __name__ == '__main__':
    pdf_dir = r"D:\Desktop\Project_file\田家林\望石智慧\journal\journal"
    pdf2img(pdf_dir)
