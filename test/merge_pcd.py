# _*_ coding=: utf-8 _*_
import os
from load_pcd_points import load_pc_data
import numpy as np
from tqdm import tqdm


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.pcd':  # 只读取.bin后缀的文件
                file_name = os.path.splitext(file)[0]
                file_list.append(os.path.join(root, file))
            else:
                continue
    return file_list


def merge_points(path):
    p1 = os.path.join(path, 'pcd_files_url')

    for file in tqdm(list_files(p1)):
        save_pcd_file = file.replace('pcd_files_url', 'merge_pcd')
        points = load_pc_data(file)
        for j in ['pcd_files1', 'pcd_files2', 'pcd_files3', 'pcd_files4']:
            points2 = load_pc_data(file.replace('pcd_files_url', j))
            points = np.vstack((points, points2))
        # points2 = load_pc_data(file.replace('pcd_files_url', 'pcd_files1'))
        # points3 = load_pc_data(file.replace('pcd_files_url', 'pcd_files2'))
        # points4 = load_pc_data(file.replace('pcd_files_url', 'pcd_files3'))
        # points5 = load_pc_data(file.replace('pcd_files_url', 'pcd_files4'))
        # mergepoint = np.stack((points1, points2, points3, points4, points5), axis=2)
        # points = mergepoint[~np.isnan(mergepoint).any(axis=0)]
        with open(save_pcd_file, 'w', encoding='ascii') as pcd_file:
            point_num = points.shape[0]
            heads = [
                '# .PCD v0.7 - Point Cloud Data file format',
                'VERSION 0.7',
                'FIELDS x y z i t',
                'SIZE 4 4 4 4 4',
                'TYPE F F F F F',
                'COUNT 1 1 1 1',
                f'WIDTH {point_num}',
                'HEIGHT 1',
                'VIEWPOINT 0 0 0 1 0 0 0',
                f'POINTS {point_num}',
                'DATA ascii'
            ]
            pcd_file.write('\n'.join(heads))
            for i in range(point_num):
                string_point = '\n' + str(points[i, 0]) + ' ' + str(points[i, 1]) + ' ' + str(
                    points[i, 2]) + ' ' + str(points[i, 3]) + ' ' + str(points[i, 4])
                pcd_file.write(string_point)

path = r"D:\Desktop\Project file\郭章程\point\未合并的"
merge_points(path)
