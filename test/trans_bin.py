# _*_ coding=: utf-8 _*_
"""
功能：bin格式点云文件转pcd格式点云文件。
使用方法：pip install numpy
    运行程序，根据命令提示输入对应信息，输出文件在bin文件上级目录的“pcd_files”路径下。
注意：输入中的符号均为英文输入法下的符号,输入字段名及数据类型时请注意顺序。
备注：
    若未知bin点云文件字段等相关信息，此脚本仅针对大部分bin文件，包含字段数量在 3-7 个且前三个字段是x,y,z坐标的，
    每个字段32字节及64字节的文件。bin文件若是4个字段，转换后的pcd点云文件 包含(x,y,z,i)坐标+强度4个维度，其他数据均仅保留(x,y,z)坐标。
"""
import os
import numpy as np
import threading
import time
from tqdm import tqdm


# 建立numpy数据类型和pcd数据类型对应关系
numpy_pcd_type_mappings = [('float32', ('F', 4)),
                           ('float64', ('F', 4)),
                           ('uint8', ('U', 1)),
                           ('uint16', ('U', 2)),
                           ('uint32', ('U', 4)),
                           ('uint64', ('U', 8)),
                           ('int16', ('I', 2)),
                           ('int32', ('I', 4)),
                           ('int64', ('I', 8))]
numpy_type_to_pcd_type = dict(numpy_pcd_type_mappings)
pcd_type_to_numpy_type = dict((q, p) for (p, q) in numpy_pcd_type_mappings)


# 返回路径下目录包含的所有文件及所有子目录下文件名的列表
def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.bin':  # 只读取.bin后缀的文件
                file_name = os.path.splitext(file)[0]
                file_list.append(os.path.join(root, file))
            else:
                continue
    return file_list


# 读取bin文件点数据(已知字段信息及数据类型)
def get_points(bin_file: str, which_fields: str, data_type: str):
    fieldnames = which_fields.split(',')
    typenames = data_type.split(',')
    dtype = np.dtype(list(zip(fieldnames, typenames)))
    with open(bin_file, 'rb') as bf:
        bin_data = bf.read()
        points = np.frombuffer(bin_data, dtype=dtype)
        points = [list(o) for o in points]
        points = np.array(points)
        return points


# 将点数据写入pcd文件(encoding=ascii)
def bin_to_pcd(bin_file: str):
    which_fields = "x,y,z,i"
    data_type = "float32,float32,float32,float32"
    file = os.path.basename(bin_file)
    result_path = os.path.join(os.path.dirname(os.path.dirname(bin_file)), 'pcd_files')
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    try:
        points = get_points(bin_file, which_fields, data_type)
        fields = which_fields.replace(',', ' ')
        t_type = []
        s_size = []
        for t, s in (numpy_type_to_pcd_type[k] for k in data_type.split(',')):
            t_type.append(t)
            s_size.append(str(s))
        _type = ' '.join(t_type)
        _size = ' '.join(s_size)
        _count = '1 '*len(t_type)
        with open(os.path.join(result_path, file.replace('.bin', '.pcd')), 'w', encoding='ascii') as pcd_file:
            point_num = points.shape[0]
            heads = [
                '# .PCD v0.7 - Point Cloud Data file format',
                'VERSION 0.7',
                f'FIELDS {fields}',
                f'SIZE {_size}',
                f'TYPE {_type}',
                f'COUNT {_count}',
                f'WIDTH {point_num}',
                'HEIGHT 1',
                'VIEWPOINT 0 0 0 1 0 0 0',
                f'POINTS {point_num}',
                'DATA ascii'
            ]
            pcd_file.write('\n'.join(heads))
            for j in range(point_num):
                string_point = []
                for k in range(len(t_type)):
                    string_point.append(str(points[j, k]))
                pcd_file.write("\n" + ' '.join(string_point))
            # print(f"{file}.bin converted to {file}.pcd ===> successful")
    except Exception as e:
        print(f"{file}.bin to {file}.pcd ===> failed : {file}.bin 文件无法解析或字段与数据类型输入错误")


def multi_thread(bin_dir):
    threads = []
    for file in list_files(bin_dir):
        threads.append(
            threading.Thread(target=bin_to_pcd, args=(file,))
        )
    for thread in tqdm(threads):
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    t1 = time.time()
    bin_dir = r"D:\Desktop\BasicProject\胡婷\Cartev\Cartev"
    multi_thread(bin_dir)
    print(time.time() - t1)
