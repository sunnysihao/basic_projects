# _*_ coding=: utf-8 _*_
import os
from plyfile import PlyData
import numpy as np
import pandas as pd


type = {
    'int8': 1,
    'char': 1,
    'uint8': 1,
    'uchar': 1,
    'int16': 2,
    'uint16': 2,
    'short': 2,
    'ushort': 2,
    'int32': 4,
    'int': 4,
    'uint32': 4,
    'uint': 4,
    'float32': 4,
    'float': 4,
    'float64': 8,
    'double': 8,
}


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.ply':
                file_list.append(os.path.join(root, file))
    return file_list


def ply2pcd(plyfile, savefile):
    with open(savefile, 'a+', encoding="ascii") as f:
        plydata = PlyData.read(plyfile)
        data = plydata.elements[0].data  # 读取数据
        data_pd = pd.DataFrame(data)  # 转换成DataFrame, 因为DataFrame可以解析结构化的数据
        data_np = np.zeros(data_pd.shape)  # 初始化储存数据的array
        property_names = data[0].dtype.names  # 读取property的名字
        for i, name in enumerate(property_names):  # 按property读取数据，这样可以保证读出的数据是同样的数据类型。
            data_np[:, i] = data_pd[name]
        points = data_np
        n = len(points)

        list = [
            '# .PCD v0.7 - Point Cloud Data file format\n',
            'VERSION 0.7\n',
            'FIELDS x y z rgb\n',
            'SIZE 4 4 4 4\n',
            'TYPE F F F U\n',
            'COUNT 1 1 1 1\n']
        f.writelines(list)
        f.write(f'WIDTH {n}\n')
        f.write('HEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\n')
        f.write(f'POINTS {n}\n')
        f.write('DATA ascii')

        for j in range(len(points)):
            x, y, z = points[j, 0:3]
            r, g, b, a = map(int, points[j, 3:])
            rgba = int((a << 24) + (r << 16) + (g << 8) + b)
            rgb = int((r << 16) + (g << 8) + b)
            f.write(f"\n{x} {y} {z} {rgb}")


def get_ply_files(path, save_path):
    for file in list_files(path):
        file_name = os.path.splitext(os.path.basename(file))[0]
        save_file = os.path.join(save_path, file_name + '.pcd')
        ply2pcd(file, save_file)


if __name__ == "__main__":
    ply_path = r"D:\Desktop\BasicProject\任从辉\大连理工\72869.629054"
    pcdPath = r"D:\Desktop\BasicProject\任从辉\大连理工\72869.629054\新建文件夹"
    get_ply_files(ply_path, pcdPath)
