# _*_ coding=: utf-8 _*_
'''
功能：bin格式点云文件转pcd格式点云文件。
使用方法：直接运行程序，在命令行输入bin文件所在文件夹路径，按enter即开始文件转换。输出文件在bin文件上级目录的“3d_url”路径下
备注：由于bin文件字段数量未知，此脚本仅针对大部分bin文件包含字段数量在 3-7 个的，每个字段32字节及64字节的文件。
bin文件若是4个字段，转换后的pcd点云文件 包含(x,y,z,i)坐标+强度4个维度，其他数据均仅保留(x,y,z)坐标。
'''
import os
import numpy as np

# 返回路径下目录包含的所有文件及所有子目录下文件名的列表
def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.bin':
                file_name = os.path.splitext(file)[0]
                file_list.append(file_name)
            else:
                continue
    return file_list

# 读取bin文件点数据
def get_points(bin_data, how_many_bytes: int):
    points = np.frombuffer(bin_data, dtype=f'float{how_many_bytes}')
    num = len(points)
    if num % 3 == 0 or num % 6 == 0:
        if num % 6 == 0:
            if np.std(points.reshape((-1, 3))[:, 2]) > np.std(points.reshape((-1, 6))[:, 2]):
                points = points.reshape((-1, 6))
            else:
                points = points.reshape((-1, 3))
        else:
            points = points.reshape((-1, 3))
    elif num % 4 == 0:
        points = points.reshape((-1, 4))
    elif num % 5 == 0:
        points = points.reshape((-1, 5))
    elif num % 7 == 0:
        points = points.reshape((-1, 7))
    else:
        print("此bin文件超出7个字段")
    return points

# 将点数据写入pcd文件
def bin2pcd(bin_path):
    result_path = os.path.join(os.path.dirname(bin_path), 'pcd_files')
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    for file in list_files(bin_path):
        bin_url = os.path.join(bin_path, file + '.bin')
        try:
            with open(bin_url, 'rb') as bf:
                bin_data = bf.read()
                points_32 = get_points(bin_data, 32)
                points_64 = get_points(bin_data, 64)
                point_all = [points_32, points_64]
                std_32 = np.std(points_32)
                std_64 = np.std(points_64)
                std_l = [std_32, std_64]
                points = point_all[std_l.index(min(std_l))]

                with open(os.path.join(result_path, file + '.pcd'), 'w') as pcd_file:
                    point_num = points.shape[0]
                    if points.shape[1] == 4:
                        #定义pcd文件头
                        heads = [
                            '# .PCD v0.7 - Point Cloud Data file format',
                            'VERSION 0.7',
                            'FIELDS x y z i',
                            'SIZE 4 4 4 4',
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
                        string_point = '\n' + str(points[i, 0]) + ' ' + str(points[i, 1]) + ' ' + str(points[i, 2]) + ' ' + str(
                            points[i, 3])
                        pcd_file.write(string_point)

                    else:
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
                    print(f"{file}.bin to {file}.pcd ===> successful")
        except Exception as e:
            print(f"{file}.bin to {file}.pcd ===> failed : 文件不符合bin格式规范或损坏")


if __name__ == "__main__":
    # bin_path = r"C:\Users\EDY\Downloads\kitti bin file" # bin文件夹路径
    bin_path = input("请输入bin文件路径(完成后按 enter):\n")
    bin2pcd(bin_path)
