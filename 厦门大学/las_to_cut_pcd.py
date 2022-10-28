# _*_ coding=: utf-8 _*_
import os
import laspy
import numpy as np


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.las':
                file_name = os.path.splitext(file)[0]
                file_list.append(os.path.join(root, file))
            else:
                continue
    return file_list


def load_las_points(las_file):
    las = laspy.read(las_file)
    # 获取文件头
    header = las.header
    # 点类型
    point_format = las.point_format
    # 属性字段名
    dimension_name = point_format.dimension_names
    # 点集外边框
    mins = header.mins
    maxs = header.maxs
    # 点个数
    point_num = header.point_count
    # 获取坐标和颜色
    las_x = np.array(las.x)
    las_y = np.array(las.y)
    las_z = np.array(las.z)
    las_r = np.array(las.red)
    las_g = np.array(las.green)
    las_b = np.array(las.blue)
    # 堆叠
    points = np.stack([las_x, las_y, las_z], axis=1)  # type(points)--->numpy.ndarray
    colors = np.stack([las_r, las_g, las_b], axis=1)  # type(colors)--->numpy.ndarray

    return points


def write_pcd(pcd_file, points):
    points = np.array(points)

    with open(pcd_file, 'w', encoding='ascii') as pcd_file:
        point_num = points.shape[0]
        heads = [
            '# .PCD v0.7 - Point Cloud Data file format',
            'VERSION 0.7',
            'FIELDS x y z',
            'SIZE 4 4 4',
            'TYPE F F F',
            'COUNT 1 1 1',
            f'WIDTH {point_num}',
            'HEIGHT 1',
            'VIEWPOINT 0 0 0 1 0 0 0',
            f'POINTS {point_num}',
            'DATA ascii'
        ]

        pcd_file.write('\n'.join(heads))
        for i in range(point_num):
            string_point = '\n' + str(points[i, 0]) + ' ' + str(points[i, 1]) + ' ' + str(points[i, 2])
            pcd_file.write(string_point)



def save_pcd(in_path):
    for file in list_files(in_path):
        las = laspy.read(file)
        las_x = np.array(las.x)
        las_y = np.array(las.y)
        las_z = np.array(las.z)
        x_min = min(las_x)
        x_max = max(las_x)
        y_min = min(las_y)
        y_max = max(las_y)
        x_scl = x_min+(x_max-x_min)/2
        y_scl = y_min+(y_max-y_min)/2
        points = np.stack([las_x, las_y, las_z], axis=1)
        # point_all = []
        points_1 = []
        points_2 = []
        points_3 = []
        points_4 = []
        for point in points:
            x, y, z = point
            if x < x_scl and y < y_scl:
                points_1.append(point)
            elif x < x_scl and y > y_scl:
                points_2.append(point)
            elif x > x_scl and y < y_scl:
                points_3.append(point)
            else:
                points_4.append(point)
        # point_all.append(points_1)
        # point_all.append(points_2)
        # point_all.append(points_3)
        # point_all.append(points_4)
        result_path = os.path.join(os.path.dirname(in_path), 'pcd_files')
        if not os.path.exists(result_path):
            os.mkdir(result_path)
        file_1 = os.path.join(result_path, '3_01.pcd')
        write_pcd(file_1, points_1)
        file_2 = os.path.join(result_path, '3_02.pcd')
        write_pcd(file_2, points_2)
        file_3 = os.path.join(result_path, '3_03.pcd')
        write_pcd(file_3, points_3)
        file_4 = os.path.join(result_path, '3_04.pcd')
        write_pcd(file_4, points_4)


in_path = r"D:\Desktop\BasicProject\毛岩\厦门大学\las"
save_pcd(in_path)




