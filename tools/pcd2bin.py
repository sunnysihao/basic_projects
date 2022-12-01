# -*- coding: utf-8 -*- 
# @Time : 2022/12/1
# @Author : zhangsihao@basicfinder.com
"""
"""
import os
import numpy as np
from load_pcd_points import load_pc_data


def read_pcd(filepath):
    points = load_pc_data(filepath)
    return np.array(points[:, 0:4])


def convert(pcdfolder, binfolder):
    current_path = os.getcwd()
    ori_path = os.path.join(current_path, pcdfolder)
    file_list = os.listdir(ori_path)
    des_path = os.path.join(current_path, binfolder)
    if os.path.exists(des_path):
        pass
    else:
        os.makedirs(des_path)
    for file in file_list:
        (filename, extension) = os.path.splitext(file)
        velodyne_file = os.path.join(ori_path, filename) + '.pcd'
        pl = read_pcd(velodyne_file)
        pl = pl.reshape(-1, 4).astype(np.float32)
        velodyne_file_new = os.path.join(des_path, filename) + '.bin'
        pl.tofile(velodyne_file_new)


if __name__ == "__main__":
    pcd_folder = r"D:\Desktop\Project_file\刘晓龙\军事科学院\jskxy_upload_dataset_0927 - 副本\3d_url"
    bin_folder = r"D:\Desktop\Project_file\刘晓龙\军事科学院\jskxy_upload_dataset_0927 - 副本\bin"
    convert(pcd_folder, bin_folder)