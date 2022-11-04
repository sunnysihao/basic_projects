# -*- coding: utf-8 -*- 
# @Time : 2022/11/2
# @Author : zhangsihao@basicfinder.com
"""
功能:las转pcd工具，可选需要的字段，如颜色值(rgb)、强度(i)，默认只包含坐标(x,y,z)
使用方法:
    python las-pcd.py <las_files_dir> --pcd_dir <save_pcd_dir> --fields x y z rgb i --huge_coordinate_value True
可选参数:
    --pcd_dir # 保存pcd文件的路径，默认为 "las_file_dir" 同级的 "pcd_files" 路径下
    --fields # 字段名 rgb 和 i 为可选项，默认为 x y z
    --huge_coordinate_value # 坐标值是否达到百万级，默认为False, 若为True，则x,y坐标均减去各自均值进行处理
"""
import os
import laspy
import numpy as np
from tqdm import tqdm


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


class LasToPcd:
    def __init__(self, las_dir: str, pcd_dir=None, fields=['x', 'y', 'z'], huge_coordinate_values=False):
        self.las_dir = las_dir
        if pcd_dir is None:
            self.pcd_dir = os.path.join(os.path.dirname(self.las_dir), 'pcd_files')
            if not os.path.exists(self.pcd_dir):
                os.mkdir(self.pcd_dir)
        else:
            self.pcd_dir = pcd_dir
        self.fields = fields
        self.huge_coordinate_values = huge_coordinate_values
        self.data_type = ['float32', 'float32', 'float32']

    def list_files(self, path: str, suffix_match: str):
        file_list = []
        for root, _, files in os.walk(path):
            for file in files:
                if os.path.splitext(file)[-1] == suffix_match:
                    file_list.append(os.path.join(root, file))
                else:
                    continue
        return file_list

    def load_las_points(self, las_file: str):
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
        las_x = np.array(las.x, dtype=np.float32)
        x = las_x - np.average(las_x)
        las_y = np.array(las.y, dtype=np.float32)
        y = las_y - np.average(las_y)
        las_z = np.array(las.z, dtype=np.float32)
        z = las_z
        las_r = np.array(las.red)
        las_g = np.array(las.green)
        las_b = np.array(las.blue)
        las_rgb = []
        for num in range(len(las_r)):
            rgb = int((int(las_r[num]/256) << 16) + (int(las_g[num]/256) << 8) + int(las_b[num]/256))
            las_rgb.append(rgb)
        las_rgb = np.array(las_rgb, dtype=np.uint32)
        las_i = np.array(las.intensity, dtype=np.float32)
        # 堆叠
        if not self.huge_coordinate_values:
              # type(points)--->numpy.ndarray
            if self.fields == ['x', 'y', 'z', 'rgb']:
                points = np.stack([las_x, las_y, las_z, las_rgb], axis=1)
                self.data_type = ['float32', 'float32', 'float32', 'uint32']
            elif self.fields == ['x', 'y', 'z', 'i']:
                points = np.stack([las_x, las_y, las_z, las_i], axis=1)
                self.data_type = ['float32', 'float32', 'float32', 'float32']
            elif self.fields == ['x', 'y', 'z', 'rgb', 'i']:
                points = np.stack([las_x, las_y, las_z, las_rgb, las_i], axis=1)
                self.data_type = ['float32', 'float32', 'float32', 'uint32', 'float32']
            else:
                points = np.stack([las_x, las_y, las_z], axis=1)
        else:
            if self.fields == ['x', 'y', 'z', 'rgb']:
                points = np.stack([x, y, z, las_rgb], axis=1)
                self.data_type = ['float32', 'float32', 'float32', 'uint32']
            elif self.fields == ['x', 'y', 'z', 'i']:
                points = np.stack([x, y, z, las_i], axis=1)
                self.data_type = ['float32', 'float32', 'float32', 'float32']
            elif self.fields == ['x', 'y', 'z', 'rgb', 'i']:
                points = np.stack([x, y, z, las_rgb, las_i], axis=1)
                self.data_type = ['float32', 'float32', 'float32', 'uint32', 'float32']
            else:
                points = np.stack([x, y, z], axis=1)

        return points

    def write_pcd(self, pcd_file, points):
        fields = ' '.join(self.fields)
        t_type = []
        s_size = []
        for t, s in (numpy_type_to_pcd_type[k] for k in self.data_type):
            t_type.append(t)
            s_size.append(str(s))
        _type = ' '.join(t_type)
        _size = ' '.join(s_size)
        _count = '1 ' * len(t_type)
        with open(pcd_file, 'w', encoding='ascii') as f:
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
            f.write('\n'.join(heads))
            for j in range(point_num):
                string_point = []
                for k in range(len(t_type)):
                    string_point.append(str(points[j, k]))
                f.write("\n" + ' '.join(string_point))
            print(f"{os.path.splitext(os.path.basename(pcd_file))[0]}.las converted to {os.path.splitext(os.path.basename(pcd_file))} ===> successful")

    def save_pcd(self):
        for file in tqdm(self.list_files(self.las_dir, '.las')):
            points = self.load_las_points(file)
            file_name = os.path.splitext(os.path.basename(file))[0]
            pcd_file = os.path.join(self.pcd_dir, file_name + '.pcd')
            self.write_pcd(pcd_file, points)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='arg parser')
    parser.add_argument('las_dir', type=str, help='las files directory')
    parser.add_argument('--pcd_dir', type=str, default=None, nargs='?', help='The pcd files save_path')
    parser.add_argument('--fields', type=str, default=['x', 'y', 'z'], nargs='*', help='The fields of point')
    parser.add_argument('--huge_coordinate_value', type=str, default=False, nargs='?', help='Whether the coordinate value reaches millions')
    args = parser.parse_args()
    las_dir = args.las_dir
    pcd_dir = args.pcd_dir
    fields = args.fields
    huge_coordinate_value = args.huge_coordinate_value
    las_transer = LasToPcd(las_dir=las_dir, pcd_dir=pcd_dir, fields=fields, huge_coordinate_values=huge_coordinate_value)

    # las_dir = r"D:\Desktop\Project file\胡婷\Lone_Drone\新建文件夹"
    # fields = ['x', 'y', 'z', 'rgb', 'i']
    # las_transer = LasToPcd(las_dir=las_dir, fields=fields)

    las_transer.save_pcd()


if __name__ == '__main__':
    main()

