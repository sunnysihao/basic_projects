# -*- coding: utf-8 -*- 
# @Time : 2023/1/9
# @Author : zhangsihao@basicfinder.com
"""
"""
import os
from tqdm import tqdm
import numpy as np
from pathlib import Path
from numpy.lib.recfunctions import repack_fields
import re
from os.path import *
import shutil


numpy_pcd_type_mappings = [
    (np.dtype('float32'), ('F', 4)),
    (np.dtype('float64'), ('F', 8)),
    (np.dtype('uint8'), ('U', 1)),
    (np.dtype('uint16'), ('U', 2)),
    (np.dtype('uint32'), ('U', 4)),
    (np.dtype('uint64'), ('U', 8)),
    (np.dtype('int16'), ('I', 2)),
    (np.dtype('int32'), ('I', 4)),
    (np.dtype('int64'), ('I', 8))]
numpy_type_to_pcd_type = dict(numpy_pcd_type_mappings)
pcd_type_to_numpy_type = dict((q, p) for (p, q) in numpy_pcd_type_mappings)


class PointCloud:
    def __init__(self, pcd_file):
        self.metadata = None
        self.code = None

        if pcd_file is not None:
            if isinstance(pcd_file, (str, Path)):
                with open(pcd_file, 'rb') as f:
                    self.data = self._load_from_file(f)
            else:
                self.data = self._load_from_file(pcd_file)

    @property
    def fields(self):
        return self.data.dtype.names

    def valid_fields(self, fields=None):
        if fields is None:
            fields = self.data.dtype.names
        else:
            fields = [
                f
                for f in fields
                if f in self.data.dtype.names
            ]
        return fields

    def numpy(self, fields=None, dtype=np.float32):
        fields = self.valid_fields(fields)
        return np.stack([
            self.data[name].astype(dtype)
            for name in fields
        ], axis=1)

    def normalized_fields(self, extra_fields: list = None):
        all_fields = set(self.fields)

        fields = ['x', 'y', 'z']
        for f in fields:
            if f not in all_fields:
                raise ValueError(f'can not find "{f}" field in pcd file')

        if 'intensity' in all_fields:
            fields.append('intensity')
        elif 'i' in all_fields:
            fields.append('i')

        if extra_fields:
            for f in extra_fields:
                if f in all_fields:
                    fields.append(f)
        return fields

    def normalized_numpy(self, extra_fields: list = None, dtype=np.float32):
        fields = self.normalized_fields(extra_fields)
        return self.numpy(fields, dtype)

    def normalized_pc(self, extra_fields: list = None):
        fields = self.normalized_fields(extra_fields)
        return repack_fields(self.data[fields])

    @staticmethod
    def _build_dtype(metadata):
        fieldnames = []
        typenames = []

        # process dulipcated names
        fields = metadata['fields']
        fields_dict = set()
        for i in range(len(fields)):
            name = fields[i]
            if name in fields_dict:
                while name in fields_dict:
                    name += '1'
                fields[i] = name
            fields_dict.add(name)

        for f, c, t, s in zip(fields,
                              metadata['count'],
                              metadata.get('type', 'F'),
                              metadata['size']):
            np_type = pcd_type_to_numpy_type[(t, s)]
            if c == 1:
                fieldnames.append(f)
                typenames.append(np_type)
            elif c == 0:  # zero count
                continue
            elif c < 0:  # negative count
                left_count = -c
                while left_count > 0:
                    left_count -= typenames[-1].itemsize
                    fieldnames.pop()
                    typenames.pop()
            else:
                fieldnames.extend(['%s_%04d' % (f, i) for i in range(c)])
                typenames.extend([np_type] * c)
        dtype = np.dtype(list(zip(fieldnames, typenames)))
        return dtype

    def parse_header(self, lines):
        """ Parse header of PCD files.
        """
        metadata = {}
        for ln in lines:
            if ln.startswith('#') or len(ln) < 2:
                continue
            match = re.match('(\w+)\s+([\w\s\.\-]+)', ln)
            if not match:
                print("warning: can't understand line: %s" % ln)
                continue
            key, value = match.group(1).lower(), match.group(2)
            if key == 'version':
                metadata[key] = value
            elif key in ('fields', 'type'):
                metadata[key] = value.split()
            elif key in ('size', 'count'):
                metadata[key] = list(map(int, value.split()))
            elif key in ('width', 'height', 'points'):
                metadata[key] = int(value)
            elif key == 'viewpoint':
                metadata[key] = map(float, value.split())
            elif key == 'data':
                metadata[key] = value.strip().lower()
            # TODO apparently count is not required?
        # add some reasonable defaults
        if 'count' not in metadata:
            metadata['count'] = [1] * len(metadata['fields'])
        if 'viewpoint' not in metadata:
            metadata['viewpoint'] = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]
        if 'version' not in metadata:
            metadata['version'] = '.7'
        return metadata

    @staticmethod
    def _parse_points_from_buf(buf, dtype):
        return np.frombuffer(buf, dtype=dtype)

    # def parse_binary_compressed_pc_data(self, f, dtype, metadata):
    #     """ Parse lzf-compressed data.
    #     """
    #     fmt = 'II'
    #     compressed_size, uncompressed_size = struct.unpack(fmt, f.read(struct.calcsize(fmt)))
    #     compressed_data = f.read(compressed_size)
    #
    #     buf = lzf.decompress(compressed_data, uncompressed_size)
    #     if len(buf) != uncompressed_size:
    #         raise IOError('Error decompressing data')
    #     # the data is stored field-by-field
    #     pc_data = self._parse_points_from_buf(buf, dtype)
    #     return pc_data

    def _load_from_file(self, f):
        header = []
        for _ in range(11):
            ln = f.readline().decode("ascii").strip()
            header.append(ln)
            if ln.startswith('DATA'):
                metadata = self.parse_header(header)
                self.code = code = metadata['data']
                dtype = self._build_dtype(metadata)
                break
        else:
            raise ValueError("invalid file header")

        if code == 'ascii':
            pc = np.genfromtxt(f, dtype=dtype, delimiter=' ')  # np.loadtxt is too slow
            # pc = np.fromfile(f, dtype=dtype, sep=' ') # error
        elif code == 'binary':
            rowstep = metadata['points'] * dtype.itemsize
            buf = f.read(rowstep)
            pc = self._parse_points_from_buf(buf, dtype)
        elif code == 'binary_compressed':
            pc = self.parse_binary_compressed_pc_data(f, dtype, metadata)
        else:
            raise ValueError(f'invalid pcd DATA: "{code}"')

        return pc

    @staticmethod
    def save_pcd(pc: np.ndarray, file):
        """
        :param structured ndarray
        :param file: str for file object
        """
        fields = pc.dtype.names
        if isinstance(file, str):
            f = open(file, 'wb')

        num_points = len(pc)
        num_fields = len(fields)
        dtypes = [pc.dtype[f] for f in fields]
        headers = [
            '# .PCD v0.7 - Point Cloud Data file format',
            'VERSION 0.7',
            f'FIELDS {" ".join(fields)}',
            f'SIZE {" ".join([str(d.itemsize) for d in dtypes])}',
            f'TYPE {" ".join([d.kind.upper() for d in dtypes])}',
            f'COUNT {" ".join(["1"] * num_fields)}',
            f'WIDTH {num_points}',
            'HEIGHT 1',
            'VIEWPOINT 0 0 0 1 0 0 0',
            f'POINTS {num_points}',
            'DATA binary'
        ]
        header = bytes('\n'.join(headers) + '\n', 'ascii')
        f.write(header)
        f.write(pc.tobytes())

        if isinstance(file, str):
            f.close()


def load_pc_data(pcd_file):
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument('pcd_file', type=str)
    # args = parser.parse_args()

    # from time import time
    # start = time()
    pc = PointCloud(pcd_file)
    points = pc.numpy(dtype=np.float32)
    return points


def list_files(in_path: str, match):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == match:
                file_list.append(os.path.join(root, file))
    return file_list


def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
    return folder_path


def write_pcd(file, points):
    with open(file, 'w', encoding='ascii') as pcd_file:
        point_num = points.shape[0]
        heads = [
            '# .PCD v0.7 - Point Cloud Data file format',
            'VERSION 0.7',
            'FIELDS x y z rgb',
            'SIZE 4 4 4 4',
            'TYPE F F F U',
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


def trans_pcd(src_pcd, dst_pcd):
        data = load_pc_data(src_pcd)
        xyz = data[:, 0:3]
        channel = data[:, 8:9]
        rgb = []
        for c in channel:
            if 1 <= c <= 16 or 65 <= c <= 80:
                rgb.append(16711680)
            else:
                rgb.append(65280)
        points = np.hstack((xyz, np.array(rgb, dtype=np.uint32).reshape((-1, 1))))
        write_pcd(dst_pcd, points)


def main(input_path, save_path):
    for pcd_file in tqdm(list_files(input_path, '.pcd')):
        file_name = splitext(basename(pcd_file))[0]
        data_folder = dirname(dirname(pcd_file))
        img0 = join(data_folder, 'camera', 'camera_front', file_name + '.jpg')
        img1 = join(data_folder, 'camera', 'camera_front_far', file_name + '.jpg')

        new_folder = create_folder(data_folder.replace(input_path, save_path))
        pcd_folder = create_folder(join(new_folder, '3d_url'))
        img0_folder = create_folder(join(new_folder, '3d_img0'))
        img1_folder = create_folder(join(new_folder, '3d_img1'))
        n_pcd = join(pcd_folder, file_name + '.pcd')
        trans_pcd(pcd_file, n_pcd)
        n_img0 = join(img0_folder, file_name + '.jpg')
        n_img1 = join(img1_folder, file_name + '.jpg')
        shutil.copyfile(img0, n_img0)
        shutil.copyfile(img1, n_img1)


if __name__ == '__main__':
    # pcd_dir = r"D:\Data\we_chat_files\WeChat Files\wxid_pzn3n31pjyvc29\FileStorage\File\2023-01\2022-11-19_08-17-14_517_8_seg_0_clip_0_sample_sensor_aligned\2022-11-19_08-17-14_517_8_seg_0_clip_0_sample_sensor_aligned\lidar_top"
    # new_dir = r"D:\Data\we_chat_files\WeChat Files\wxid_pzn3n31pjyvc29\FileStorage\File\2023-01\2022-11-19_08-17-14_517_8_seg_0_clip_0_sample_sensor_aligned\2022-11-19_08-17-14_517_8_seg_0_clip_0_sample_sensor_aligned\new"
    pcd_dir = input("请输入原始文件路径:\n")
    new_dir = input("请输入结果保存路径:\n")
    main(pcd_dir, new_dir)
    input("已完成，按任意键退出")
