# -*- coding = utf-8 -*-
import os
import numpy as np


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.obj':
                file_name = os.path.splitext(file)[0]
                file_list.append(os.path.join(root, file))
            else:
                continue
    return file_list


def obj_to_pcd(obj_dir: str):
    pcd_path = os.path.join(os.path.dirname(obj_dir), '3d_url')
    if not os.path.exists(pcd_path):
        os.mkdir(pcd_path)
    for file in list_files(obj_dir):
        points_l = []
        with open(file, 'rb') as of:
            file_name = os.path.splitext(os.path.basename(file))[0]
            for line in of.readlines():
                s_line = line.decode().split()
                if not s_line:
                    continue
                else:
                    if s_line[0] == 'v':
                        x = s_line[1]
                        y = s_line[2]
                        z = s_line[3].strip('\n').strip('\r')
                        points_l.append([x, y, z])
                    else:
                        continue
        points = np.array(points_l)
        pcd_file = os.path.join(pcd_path, file_name + '.pcd')
        with open(pcd_file, 'w', encoding='ascii') as pf:
            point_num = points.shape[0]
            heads = [
                '# .PCD v0.7 - Point Cloud Data file format',
                'VERSION 0.7',
                'FIELDS x y z',
                f'SIZE 4 4 4',
                'TYPE F F F',
                f'COUNT 1 1 1',
                f'WIDTH {point_num}',
                'HEIGHT 1',
                'VIEWPOINT 0 0 0 1 0 0 0',
                f'POINTS {point_num}',
                'DATA ascii'
            ]
            pf.write('\n'.join(heads))
            for i in range(point_num):
                string_point = '\n' + str(points[i, 0]) + ' ' + str(points[i, 1]) + ' ' + str(points[i, 2])
                pf.write(string_point)


obj_dir = r"C:\Users\Administrator\Downloads\归档(1)"
obj_to_pcd(obj_dir)
