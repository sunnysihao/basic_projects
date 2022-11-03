# _*_ coding=: utf-8 _*_
import os
import laspy
import numpy as np
from tqdm import tqdm


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
    x = las_x - np.average(las_x)
    las_y = np.array(las.y)
    y = las_y - np.average(las_y)
    las_z = np.array(las.z)
    z = las_z - np.average(las_z)
    las_r = np.array(las.red)
    las_g = np.array(las.green)
    las_b = np.array(las.blue)
    las_i = np.array(las.intensity)
    # 堆叠
    points = np.stack([las_x, las_y, las_z, las_i], axis=1)  # type(points)--->numpy.ndarray
    colors = np.stack([las_r, las_g, las_b], axis=1)  # type(colors)--->numpy.ndarray

    return points


def write_pcd(pcd_file, points):
    points = np.array(points, dtype=np.float64)

    with open(pcd_file, 'w', encoding='ascii') as pcd_file:
        point_num = points.shape[0]
        heads = [
            '# .PCD v0.7 - Point Cloud Data file format',
            'VERSION 0.7',
            'FIELDS x y z i',
            'SIZE 8 8 8 4',
            'TYPE F F F F',
            'COUNT 1 1 1 1',
            f'WIDTH {point_num}',
            'HEIGHT 1',
            'VIEWPOINT 0 0 0 1 0 0 0',
            f'POINTS {point_num}',
            'DATA ascii'
        ]

        pcd_file.write('\n'.join(heads))
        for i in range(point_num):
            string_point = '\n' + str(points[i, 0]) + ' ' + str(points[i, 1]) + ' ' + str(points[i, 2]) + ' ' + str(points[i, 3])
            pcd_file.write(string_point)


def save_pcd(in_path):
    for file in tqdm(list_files(in_path)):
        points = load_las_points(file)
        file_name = os.path.splitext(os.path.basename(file))[0]
        pcd_path = os.path.join(os.path.dirname(file), '3d_url')
        if not os.path.exists(pcd_path):
            os.mkdir(pcd_path)
        pcd_file = os.path.join(pcd_path, file_name + '.pcd')
        write_pcd(pcd_file, points)
        # point_all = []


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('in_path', type=str)
    args = parser.parse_args()
    in_path = args.in_path
    # in_path = r'D:\Desktop\Project file\张子千\M4143G1\las'
    # in_path = input("请输入las文件路径:\n")
    save_pcd(in_path)
    input("已完成，按任意键退出")
