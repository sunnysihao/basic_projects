# _*_ coding=: utf-8 _*_
import os
import re
from tqdm import tqdm


def list_files(in_path: str, suffix_match: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == f'{suffix_match}':
                file_list.append(os.path.join(root, file))
            else:
                continue
    return file_list


def split_file(in_dir):
    img0_path = os.path.join(in_dir, '3d_img0')
    img1_path = os.path.join(in_dir, '3d_img1')
    img2_path = os.path.join(in_dir, '3d_img2')
    pcd_path = os.path.join(in_dir, '3d_url')
    config_path = os.path.join(in_dir, 'camera_config')
    for img_file0 in tqdm(list_files(img0_path, '.png')):
        file_name0 = os.path.basename(img_file0)
        dir_name0 = file_name0.split('-')[0]
        new_path0 = os.path.join(in_dir, dir_name0, '3d_img0')
        if not os.path.exists(new_path0):
            os.makedirs(new_path0)
        new_img0 = os.path.join(new_path0, file_name0)
        os.rename(img_file0, new_img0)

    for img_file1 in tqdm(list_files(img1_path, '.png')):
        file_name1 = os.path.basename(img_file1)
        dir_name1 = file_name1.split('-')[0]
        new_path1 = os.path.join(in_dir, dir_name1, '3d_img1')
        if not os.path.exists(new_path1):
            os.makedirs(new_path1)
        new_img1 = os.path.join(new_path1, file_name1)
        os.rename(img_file1, new_img1)

    for img_file2 in tqdm(list_files(img2_path, '.png')):
        file_name2 = os.path.basename(img_file2)
        dir_name2 = file_name2.split('-')[0]
        new_path2 = os.path.join(in_dir, dir_name2, '3d_img2')
        if not os.path.exists(new_path2):
            os.makedirs(new_path2)
        new_img2 = os.path.join(new_path2, file_name2)
        os.rename(img_file2, new_img2)

    for pcd_file in tqdm(list_files(pcd_path, '.pcd')):
        pcd_name = os.path.basename(pcd_file)
        dir_name = pcd_name.split('-')[0]
        new_path = os.path.join(in_dir, dir_name, '3d_url')
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        new_pcd = os.path.join(new_path, pcd_name)
        os.rename(pcd_file, new_pcd)

    for cfg_file in tqdm(list_files(config_path, '.json')):
        cfg_name = os.path.basename(cfg_file)
        dir_cname = cfg_name.split('-')[0]
        new_cpath = os.path.join(in_dir, dir_cname, 'camera_config')
        if not os.path.exists(new_cpath):
            os.makedirs(new_cpath)
        new_cfg = os.path.join(new_cpath, cfg_name)
        os.rename(cfg_file, new_cfg)


if __name__ == "__main__":
    in_dir = input("请输入路径:\n")
    # in_dir = r"D:\Desktop\BasicProject\胡婷\test"
    split_file(in_dir)
    input("已完成，按任意键退出")
