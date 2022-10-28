import os
import json
import numpy as np
from pathlib import Path
from numpy.lib.recfunctions import repack_fields
import re
import struct
import open3d as o3d
import lzf

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

    def parse_binary_compressed_pc_data(self, f, dtype, metadata):
        """ Parse lzf-compressed data.
        """
        fmt = 'II'
        compressed_size, uncompressed_size = struct.unpack(fmt, f.read(struct.calcsize(fmt)))
        compressed_data = f.read(compressed_size)

        buf = lzf.decompress(compressed_data, uncompressed_size)
        if len(buf) != uncompressed_size:
            raise IOError('Error decompressing data')
        # the data is stored field-by-field
        # pc_data = self._parse_points_from_buf(buf, dtype)
        num_points = uncompressed_size // dtype.itemsize
        pc_data = np.zeros(num_points, dtype=dtype)
        ix = 0
        for dti in range(len(dtype)):
            dt = dtype[dti]
            bytes = dt.itemsize * num_points
            column = np.fromstring(buf[ix:(ix + bytes)], dt)
            pc_data[dtype.names[dti]] = column
            ix += bytes
        return pc_data

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
    points = pc.numpy(dtype=np.float64)
    return points


class_mapping = {
    "other": 0,
    "driveable_surface": 1,
    "sidewalk": 2,
    "terrain": 3,
    "undefined_surface": 4,
    "moveable_object": 5,
    "unmoveable_object": 6,
    "suspend_object": 7,
    "curb": 8,
    "fence": 9,
    "separation": 10,
    "wall": 11,
    "vegetation": 12,
    "building": 13,
    "noise": 14,
    "reflection": 15
}


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_list.append(os.path.join(root, file))
            else:
                continue
    return file_list


def load_json(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def load_points(pcd_file):
    points = load_pc_data(pcd_file)
    filter_points = points[~np.isnan(points[:, :3]).any(axis=1)]
    return filter_points

    # pcd = o3d.io.read_point_cloud(pcd_file, remove_nan_points=True)
    # points = np.asarray(pcd.points)

    # return points


def add_label(json_path: str, save_pcd_dir: str):
    for file in list_files(json_path):
        points_c = []
        json_content = load_json(file)
        file_name = os.path.splitext(json_content['data']['3d_url'].split('/')[-1])[0]
        pcd_path = r"/basicfinder/www/saas.basicfinder.com/api/resource"
        pcd_url = json_content['data']['3d_url']
        pcd_file = os.path.join(pcd_path, pcd_url)

        # file_name = os.path.splitext(os.path.basename(file))[0] + '.pcd'
        # pcd_path = r"D:\Desktop\BasicProject\王满顺\理想\点云试标数据1019\点云试标\AT128_A4202203171225_1080_1647491210444606\pcd"
        # pcd_file = os.path.join(pcd_path, file_name)

        save_path = os.path.dirname(file).replace(json_path, save_pcd_dir)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        save_pcd_file = os.path.join(save_path, file_name + '.pcd')
        points = load_points(pcd_file)
        boxes = json_content['result']['data']
        for box in boxes:
            label = box['attr']['label'][0]
            class_num = class_mapping[label]
            point_index = box['indexs']
            pnum = points.shape[0]-1
            for dex in point_index:
                if dex > pnum:
                    continue
                else:
                    point = points[dex]
                    new_point = np.hstack((point, class_num))
                    points_c.append(new_point)

        points_c = np.array(points_c)
        with open(save_pcd_file, 'w', encoding='ascii') as pcd_file:
            point_num = points_c.shape[0]
            heads = [
                '# .PCD v0.7 - Point Cloud Data file format',
                'VERSION 0.7',
                'FIELDS x y z intensity timestamp ring label',
                'SIZE 4 4 4 1 8 2 2',
                'TYPE F F F U F U U',
                'COUNT 1 1 1 1 1 1 1',
                f'WIDTH {point_num}',
                'HEIGHT 1',
                'VIEWPOINT 0 0 0 1 0 0 0',
                f'POINTS {point_num}',
                'DATA ascii'
            ]

            pcd_file.write('\n'.join(heads))
            for i in range(point_num):
                # string_point = '\n' + str(points_c[i, 0]) + ' ' + str(points_c[i, 1]) + ' ' + str(
                #     points_c[i, 2]) + ' ' + str(
                #     points_c[i, 3])
                string_point = '\n' + str(points_c[i, 0]) + ' ' + str(points_c[i, 1]) + ' ' + str(points_c[i, 2]) + ' ' + str(
                    points_c[i, 3]) + ' ' + str(points_c[i, 4]) + ' ' + str(points_c[i, 5]) + ' ' + str(points_c[i, 6])
                pcd_file.write(string_point)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('result_json_path', type=str)
    parser.add_argument('save_pcd_path', type=str)
    args = parser.parse_args()

    result_json_path = args.result_json_path
    save_pcd_path = args.save_pcd_path
    # save_pcd_path = r"C:\Users\EDY\Downloads\下载结果_json_44265_110926_20221025153510\点云试标数据1019-lx.zip\点云试标数据1019-lx\点云试标\AT128_A4202203171035_620_1647484563636202\3d_url"
    # result_json_path = r"C:\Users\EDY\Downloads\下载结果_json_44265_110926_20221025153510\点云试标数据1019-lx.zip\点云试标数据1019-lx\点云试标\AT128_A4202203171225_1080_1647491210444606\3d_url"

    add_label(result_json_path, save_pcd_path)
