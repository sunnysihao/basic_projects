# _*_ coding=: utf-8 _*_
import os
import re
import numpy as np
from load_pcd_points import load_pc_data
from tqdm import tqdm
from plyfile import PlyData, PlyElement
import time


class_map = {
    "1": 0,
    "2": 1,
    "3": 2,
    "4": 3,
    "5": 4,
    "6": 5,
    "7": 6,
    "8": 7,
    "9": 8,
    "10": 9,
    "11": 10,
    "12": 11,
    "13": 12
}


def list_dir(in_path: str):
    dir_list = []
    for _dir in os.listdir(in_path):
        if os.path.isdir(os.path.join(in_path, _dir)):
            dir_list.append(_dir)
        else:
            continue
    return dir_list


def list_files_name(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


def merge_txt(txt_dir, merge_dir):
    file_list = []
    for file in list_files_name(txt_dir):
        file_list.append('_'.join(file.split('_')[:-1]))
    file_set = set(file_list)
    for txt_file in file_set:
        for file in list_files_name(txt_dir):
            if re.findall(txt_file, file):
                with open(os.path.join(txt_dir, file + '.txt'), 'r', encoding='utf-8') as f:
                    data = f.read()
                    with open(os.path.join(merge_dir, txt_file + '.txt'), 'a+', encoding='utf-8') as nf:
                        nf.write(data)
            else:
                continue


def write_ply(save_path, pc_data, text=True):

    vertex = np.array(pc_data, dtype=[('x', 'f8'), ('y', 'f8'), ('z', 'f8'),
                                      ('red', 'u1'), ('green', 'u1'), ('blue', 'u1'), ('class', 'u1')])
    # vertex = pc_data[:, 0:3]
    el = PlyElement.describe(vertex, 'vertex')
    # color = PlyElement.describe(np.array(color_data, dtype=[('red', 'u1'), ('green', 'u1'), ('blue', 'u1')]), 'color')
    with open(save_path, 'wb') as bf:
        PlyData([el], byte_order='=').write(bf)


def merge_pcd2ply(in_path):
    for dir in tqdm(list_dir(in_path)):
        t1 = time.time()
        pcd_path = os.path.join(in_path, dir)
        ply_file = pcd_path + '.ply'
        new_pc_data = []
        # color_data = []
        for file in list_files(pcd_path):
            pc_data = load_pc_data(file)
            # pc_data = np.around(pc_data_, decimals=3)
            # xyz_arr = pc_data[:, 0:3]
            # points = np.around(xyz_arr, decimals=3)
            # c_arr_ = pc_data[:, 3]
            # c_arr = c_arr_.reshape(len(c_arr_), 1)
            # pc_arr = np.hstack((points, c_arr))
            for line_obj in pc_data:
                x, y, z, r, g, b, c = line_obj
                class_label = class_map[f'{int(c)}']
                new_line_obj = (x, y, z, int(r), int(g), int(b), class_label)
                # color_line_obj = (int(red), int(green), int(blue))

                # color_data.append(color_line_obj)
                new_pc_data.append(new_line_obj)

        # new_pc_data = np.array(new_pc_data_)
        # point_num = new_pc_data.shape[0]
        t2 = time.time()
        # print(f"读取并转换所有点及颜色数据耗时{t2 - t1}")
        write_ply(ply_file, new_pc_data, text=True)
        t3 = time.time()
        # print(f"写入ply文件耗时{t3 - t2}")

        # if not os.path.exists(ply_file):
        #     with open(ply_file, 'w', encoding='utf-8') as pf:
        #
        #
        #         for i in range(point_num):
        #             string_point = '\n' + str(new_pc_data[i, 0]) + ' ' + str(new_pc_data[i, 1]) \
        #                            + ' ' + str(new_pc_data[i, 2]) + ' ' + str(new_pc_data[i, 3])\
        #                            + ' ' + str(new_pc_data[i, 4]) + ' ' + str(new_pc_data[i, 5])
        #             pf.write(string_point)
        # else:
        #     with open(ply_file, 'a+', encoding='utf-8') as pf2:
        #         for i in range(point_num):
        #             string_point = '\n' + str(new_pc_data[i, 0]) + ' ' + str(new_pc_data[i, 1]) \
        #                            + ' ' + str(new_pc_data[i, 2]) + ' ' + str(new_pc_data[i, 3])\
        #                            + ' ' + str(new_pc_data[i, 4]) + ' ' + str(new_pc_data[i, 5])
        #             pf2.write(string_point)

# txt_dir = r"C:\Users\EDY\Downloads\归档\kitti_39735_82319_20220624163317\1650269876\时旭科技滑块80点云拉框.zip\3d_url"
# merge_dir = r"D:\Desktop\BasicProject\任从辉\时旭"
# merge_txt(txt_dir, merge_dir)

pcd_path = r"D:\Desktop\BasicProject\王满顺\时旭\时旭科技数据\时旭科技数据\sx_data\pcd_files"
merge_pcd2ply(pcd_path)
