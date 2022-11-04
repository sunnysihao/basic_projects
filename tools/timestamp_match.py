"""
功能:根据文件名时间戳对齐点云和图像文件(以点云文件为基准，取时间最近的图像文件，重命名为pcd文件名)
使用方法:python timestamp_match.py "pcd文件夹路径" "图片文件夹路径"
"""
import os
import shutil
from tqdm import tqdm


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_list.append(file)
    return file_list


def is_float(src_str):
    try:
        float(src_str)
        r = True
    except:
        r = False
    return r


def match_with_timestamp(pcd_folder: str, jpg_folder: str):
    print("************************************")
    timestamp_check = True
    pcd_file = list_files(pcd_folder)
    for f1 in pcd_file:
        timestamp_check = is_float(os.path.splitext(f1)[0])
    img_file = list_files(jpg_folder)
    for f2 in img_file:
        timestamp_check = is_float(os.path.splitext(f2)[0])
    if timestamp_check:
        for pcd_folder in tqdm(pcd_file):
            pcd_prefix = os.path.splitext(pcd_folder)[0]
            dict = {k: eval(pcd_prefix) - eval(os.path.splitext(k)[0]) for k in img_file}
            value = 0
            img_key, diff_val = min(dict.items(), key=lambda x: abs(value - x[1]))
            src_img = os.path.join(jpg_folder, img_key)
            new_img_path = os.path.join(os.path.dirname(jpg_folder), f'new_images_of_{os.path.basename(jpg_folder)}')
            if not os.path.exists(new_img_path):
                os.makedirs(new_img_path)
            new_img = os.path.join(new_img_path, pcd_prefix + '.jpg')
            shutil.copyfile(src_img, new_img)
    else:
        print("文件名不符合时间戳格式，无法进行时序对齐")


if __name__ == '__main__':
    # pcd_folder = input("请输入pcd文件夹路径:\n")
    # image_folder = input("请输入需要做时序同步的文件夹路径:\n")
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('pcd_folder', type=str)
    parser.add_argument('image_folder', type=str)
    args = parser.parse_args()
    pcd_folder = args.pcd_folder
    image_folder = args.image_folder

    # pcd_folder = r"D:\Desktop\Project file\刘晓龙\军事科学院\新建文件夹\新建文件夹\jskxy_upload_file_0923\3d_url"
    # image_folder = r"D:\Desktop\3548_2048\3548_2048\3d_img0"
    match_with_timestamp(pcd_folder, image_folder)
    input("已完成，按任意键退出")

