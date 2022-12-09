# -*- coding: utf-8 -*- 
# @Time : 2022/11/29
# @Author : zhangsihao@basicfinder.com
"""
"""
import fitz
import os
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor


def list_files(in_path: str, match):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == match:
                file_list.append(os.path.join(root, file))
    return file_list


def pdf2img(file):
    file_name = os.path.splitext(os.path.basename(file))[0]
    pdf = fitz.open(file)
    trans = fitz.Matrix(2.5, 2.5).prerotate(int(0))
    for i in tqdm(range(pdf.page_count)):
        page = pdf[i]
        pm = page.get_pixmap(matrix=trans, alpha=False)
        save_path = os.path.join(os.path.dirname(os.path.dirname(file)), 'wszh_upload_images', file_name)
        if not os.path.exists(save_path):
            os.makedirs(save_path, exist_ok=True)
        image = os.path.join(save_path, f"{file_name}_{i}.png")
        pm.save(image)


if __name__ == '__main__':
    pdf_dir = r"D:\Desktop\Project_file\田家林\望石2\dod第二批\dod第二批\journal\journal2"
    files = list_files(pdf_dir, '.pdf')
    with ProcessPoolExecutor() as executor:
        executor.map(pdf2img, files)
