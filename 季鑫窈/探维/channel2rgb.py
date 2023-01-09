# -*- coding: utf-8 -*- 
# @Time : 2023/1/9
# @Author : zhangsihao@basicfinder.com
"""
"""
import os
import numpy as np
from load_pcd_points import load_pc_data
from tqdm import tqdm


def list_files(in_path: str, match):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == match:
                file_list.append(os.path.join(root, file))
    return file_list


def write_pcd(file, points):
    with open(file, 'w', encoding='ascii') as pcd_file:
        point_num = points.shape[0]
        heads = [
            '# .PCD v0.7 - Point Cloud Data file format',
            'VERSION 0.7',
            'FIELDS x y z rgb',
            'SIZE 4 4 4 4',
            'TYPE F F F U',
            'COUNT 1 1 1 1',
            f'WIDTH {point_num}',
            'HEIGHT 1',
            'VIEWPOINT 0 0 0 1 0 0 0',
            f'POINTS {point_num}',
            'DATA ascii'
        ]
        pcd_file.write('\n'.join(heads))
        for i in range(point_num):
            string_point = '\n' + str(points[i, 0]) + ' ' + str(points[i, 1]) + ' ' + str(points[i, 2]) + ' ' + str(
                points[i, 3])
            pcd_file.write(string_point)


def main(pcd_dir, new_dir):
    for file in tqdm(list_files(pcd_dir, '.pcd')):
        file_name = os.path.basename(file)
        new_pcd = os.path.join(new_dir, file_name)
        data = load_pc_data(file)
        xyz = data[:, 0:3]
        channel = data[:, 8:9]
        rgb = []
        for c in channel:
            if 1 <= c <= 16 or 65 <= c <= 80:
                rgb.append(16711680)
            else:
                rgb.append(65280)
        points = np.hstack((xyz, np.array(rgb, dtype=np.uint32).reshape((-1, 1))))
        write_pcd(new_pcd, points)


if __name__ == '__main__':
    pcd_dir = r"D:\Data\we_chat_files\WeChat Files\wxid_pzn3n31pjyvc29\FileStorage\File\2023-01\2022-11-19_08-17-14_517_8_seg_0_clip_0_sample_sensor_aligned\2022-11-19_08-17-14_517_8_seg_0_clip_0_sample_sensor_aligned\lidar_top"
    new_dir = r"D:\Data\we_chat_files\WeChat Files\wxid_pzn3n31pjyvc29\FileStorage\File\2023-01\2022-11-19_08-17-14_517_8_seg_0_clip_0_sample_sensor_aligned\2022-11-19_08-17-14_517_8_seg_0_clip_0_sample_sensor_aligned\new"
    main(pcd_dir, new_dir)
