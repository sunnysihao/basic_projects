# _*_ coding=: utf-8 _*_

"""
功能：bin格式点云文件转pcd格式点云文件(已知bin点云文件字段及数据类型)。
使用方法：pip install numpy
    运行程序，在命令行依次输入bin文件所在文件夹路径、字段名、每个字段对应的数据类型，按enter确认，即开始文件转换。
    输出文件在bin文件上级目录的“pcd_files”路径下。
"""

import os
import numpy as np


# 建立numpy数据类型和pcd数据类型对应关系
numpy_pcd_type_mappings = [('float32', ('F', 4)),
                           ('float64', ('F', 8)),
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
                file_list.append(file_name)
            else:
                continue
    return file_list


# 读取bin文件点数据
def get_points(bin_file: str, which_fields: str, data_type: str):
    fields_list = which_fields.split(',')
    fieldnames = which_fields.split(',')
    typenames = data_type.split(',')
    dtype = np.dtype(list(zip(fieldnames, typenames)))
    k = len(fields_list)
    with open(bin_file, 'rb') as bf:
        bin_data = bf.read()
        points = np.frombuffer(bin_data, dtype=dtype)
        points = [list(o) for o in points]
        points = np.array(points)
        return points


# 将点数据写入pcd文件(encoding=ascii)
def bin_to_pcd(bin_file_dir: str, which_fields: str, data_type: str):
    result_path = os.path.join(os.path.dirname(bin_file_dir), 'pcd_files')
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    for file in list_files(bin_file_dir):
        bin_file = os.path.join(bin_file_dir, file + '.bin')
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
            with open(os.path.join(result_path, file + '.pcd'), 'w', encoding='ascii') as pcd_file:
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
                print(f"{file}.bin converted to {file}.pcd ===> successful")
        except Exception as e:
            print(f"{file}.bin to {file}.pcd ===> failed : The {file}.bin file is invalid")


def main():
    bin_file_dir = input("请输入bin文件路径(完成后按 enter):\n")
    which_fields = input(f"请输入bin文件的字段名,以','号隔开:\n(如：x,y,z,i  完成后按 enter):\n")
    data_type = input(f"请输入每个字段(维度)的数据类型,以','号隔开:\n(如: float32,float32,float32,float32)\n"
                      f"(支持的数据类型：float32,float64,uint8,uint16,uint32,uint64,int16,int32,int64 完成后按 enter):\n")
    file_num = len(list_files(bin_file_dir))
    print(f"路径中共找到{file_num}个'.bin'后缀文件")
    print("Start converting bin to pcd\n--------------------------------------------------")
    bin_to_pcd(bin_file_dir, which_fields, data_type)
    save_path = os.path.join(os.path.dirname(bin_file_dir), 'pcd_files')
    print(f"--------------------------------------------------\npcd文件保存路径为：{save_path}")


if __name__ == "__main__":
    main()
