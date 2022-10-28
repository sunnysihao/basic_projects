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
                file_list.append(file_name)
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
            print(f"{file}.bin to {file}.pcd ===> failed : {file}.bin 文件无法解析或字段与数据类型输入错误")


# 读取bin文件点数据(未知字段信息)
def get_points2(bin_data, how_many_bytes: int):
    points = np.frombuffer(bin_data, dtype=f'float{how_many_bytes}')
    num = len(points)
# 根据数据个数判断bin文件字段个数
    if num % 3 == 0 or num % 6 == 0:
        if num % 6 == 0:
            p3 = points.reshape((-1, 3))[:, 2]
            p6 = points.reshape((-1, 6))[:, 5]
            if (max(p3) - min(p3)) > (max(p6) - min(p6)):
                if np.std(points.reshape((-1, 3))[:, 2]) > np.std(points.reshape((-1, 6))[:, 2]):
                    points = points.reshape((-1, 6))
                else:
                    points = points.reshape((-1, 3))
            elif (max(p3) - min(p3)) == (max(p6) - min(p6)):
                if np.std(points.reshape((-1, 3))[:, 2]) < np.std(points.reshape((-1, 6))[:, 2]):
                    points = points.reshape((-1, 6))
                else:
                    points = points.reshape((-1, 3))
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


# 将点数据写入pcd文件(encoding=ascii)
def bin2pcd(bin_file_dir):
    result_path = os.path.join(os.path.dirname(bin_file_dir), 'pcd_files')
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    for file in list_files(bin_file_dir):
        bin_url = os.path.join(bin_file_dir, file + '.bin')
        try:
            with open(bin_url, 'rb') as bf:
                bin_data = bf.read()
                points_32 = get_points2(bin_data, 32)
                points_64 = get_points2(bin_data, 64)
                point_all = [points_32, points_64]
                std_32 = np.std(points_32)
                std_64 = np.std(points_64)
                std_l = [std_32, std_64]
                points = point_all[std_l.index(min(std_l))]
                with open(os.path.join(result_path, file + '.pcd'), 'w', encoding='ascii') as pcd_file:
                    point_num = points.shape[0]
                    if points.shape[1] == 4:
                        #定义pcd文件头---有4个维度的情况
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
                        # 定义pcd文件头---有3个维度的情况
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
                    print(f"{file}.bin converted to {file}.pcd ===> successful")
        except Exception as e:
            print(f"{file}.bin to {file}.pcd ===> failed : {file}.bin 文件无法解析")


def main():
    options = int(input("是否已知字段名及数据类型:   (已知输入 1,未知输入 0)\n"))
    while options not in [0, 1]:
        print("输入不正确，请重新输入:")
        options = input()
    else:
        bin_file_dir = input("请输入bin文件路径:\n")
        while not os.path.exists(bin_file_dir):
            print(f"未找到路径：{bin_file_dir} ")
            bin_file_dir = input("请重新输入:\n")
        else:
            file_num = len(list_files(bin_file_dir))
            if options == 0:
                print(f"路径中共找到{file_num}个'.bin'后缀文件\nStart converting bin to pcd"
                      f"\n--------------------------------------------------")
                bin2pcd(bin_file_dir)
                save_path = os.path.join(os.path.dirname(bin_file_dir), 'pcd_files')
                print(f"pcd文件保存路径为：{save_path}")
            else:
                which_fields = input(f"请输入bin文件的字段名,以','号隔开: (如：x,y,z,i):\n")
                data_type = input(f"请输入每个字段(维度)的数据类型,以','号隔开: (如: float32,float32,float32,float32)\n"
                                  f"(支持的数据类型：float32,float64,uint8,uint16,uint32,uint64,int16,int32,int64):\n")
                print(f"路径中共找到{file_num}个'.bin'后缀文件\nStart converting bin to pcd"
                      f"\n--------------------------------------------------")
                bin_to_pcd(bin_file_dir, which_fields, data_type)
            save_path = os.path.join(os.path.dirname(bin_file_dir), 'pcd_files')
            print(f"--------------------------------------------------\npcd文件保存路径为：{save_path}")


if __name__ == "__main__":
    main()
