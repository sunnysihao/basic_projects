# _*_ coding=: utf-8 _*_
import json
import os
import re
import shutil
from functools import partial
from os.path import join, splitext, dirname, basename, exists, getsize
from typing import Callable

import laspy
import numpy as np
import pcl
from sklearn.neighbors import BallTree
from tqdm import tqdm


def list_files(dir_path: str, name_regex: str = None):
    if name_regex:
        name_regex = re.compile(name_regex)

    for root, _, file_names in os.walk(dir_path):
        for file_name in file_names:
            if name_regex is None or name_regex.match(file_name):
                yield join(root, file_name)


class PCDataProcessor:
    def __init__(self, src_dir: str = None, output_dir: str = None):
        self.src_dir = src_dir
        self.output_dir = output_dir

        # pre process
        self.pcd_dir = join(self.output_dir, "pcd")
        self.downsampled_pcd_dir = join(self.output_dir, "pcd_downsampled")

        # post process
        self.segmented_pcd_dir = join(self.output_dir, "pcd_segmented")

    @staticmethod
    def laz2las(laz_file: str, las_file: str):
        las = laspy.read(laz_file)
        las.write(las_file)

    def laz2las_files(self, laz_dir: str = None, las_dir: str = None):
        self._convert_files(laz_dir,
                            las_dir,
                            from_ext='laz', to_ext='las',
                            converter=PCDataProcessor.laz2las)

    @staticmethod
    def las2pcd(las_file: str, pcd_file: str):
        print(f"\n{las_file} ==> {pcd_file}")
        f = laspy.read(las_file)

        data = np.stack((f.x, f.y, f.z), axis=1)
        data = data.astype(np.float64)
        # data = (data - data.mean(axis=0)).astype(np.float32)
        pc = pcl.PointCloud(data)
        pcl.save(pc, pcd_file)

    def las2pcd_files(self, las_dir: str, pcd_dir: str):
        print("==> convert files from las to pcd...")
        self._convert_files(las_dir,
                            pcd_dir,
                            from_ext='las', to_ext='pcd',
                            converter=PCDataProcessor.las2pcd)
        print(f"\tpcd files ==> {pcd_dir}")

    @staticmethod
    def _convert_file_name(from_dir: str, from_file: str, to_dir: str, to_ext: str):
        from_file_relative = from_file[len(from_dir) + 1:]
        file_name = splitext(basename(from_file_relative))[0]

        to_dir2 = join(to_dir, dirname(from_file_relative))
        os.makedirs(to_dir2, exist_ok=True)
        to_file = join(to_dir2, f"{file_name}.{to_ext}")
        return to_file

    @staticmethod
    def _convert_files(from_dir: str, to_dir: str, from_ext: str, to_ext: str, converter: Callable):
        from_files = list(list_files(from_dir, name_regex=f".+\\.{from_ext}"))
        bar = tqdm(from_files, ascii=True)
        for from_file in bar:
            bar.set_description(basename(from_file))

            # convert pcd
            to_file = PCDataProcessor._convert_file_name(from_dir, from_file, to_dir, to_ext)
            converter(from_file, to_file)

    @classmethod
    def do_voxel_grid_filter(cls, point_cloud, leaf_size=0.01):
        # Returns Downsampled version of a point cloud
        # The bigger the leaf size the less information retained
        voxel_filter = point_cloud.make_voxel_grid_filter()
        voxel_filter.set_leaf_size(leaf_size, leaf_size, leaf_size)
        return voxel_filter.filter()

    # leaf_size_list = [50, 100, 200, 300, 400, 500, 550, 600, 650, 700, 750, 800]
    max_file_size = 20 * 1024 * 1024
    max_num_points = 60 * 10000
    threshold = 1.3

    @classmethod
    def down_sample_pcd_file(cls, in_pcd_file: str, out_pcd_file: str):
        file_size = getsize(in_pcd_file)
        if file_size > cls.max_file_size * cls.threshold:
            cloud = pcl.load(in_pcd_file)
            max_count = 15
            last_idx = max_count - 1
            for i in range(max_count):
                leaf_size = 0.005 * (1.5 ** i)
                downsampled_cloud = cls.do_voxel_grid_filter(point_cloud=cloud, leaf_size=leaf_size)
                point_count = downsampled_cloud.size
                is_last = i == last_idx
                if point_count <= cls.max_num_points * cls.threshold or is_last:
                    pcl.save(downsampled_cloud, out_pcd_file, binary=False)
                    if is_last:
                        print("***too big point cloud, using final leaf")
                    # print(f"\tusing leaf_size: {leaf_size}, point count: {point_count}")
                    break
        else:
            shutil.copyfile(in_pcd_file, out_pcd_file)
        print(f"\tdown sampled pcd file ==> {out_pcd_file}")

    @classmethod
    def down_sample_pcd_files(cls, in_pcd_dir: str, out_pcd_dir: str):
        print("==> down sample pcd file...")
        cls._convert_files(in_pcd_dir,
                           out_pcd_dir,
                           from_ext='pcd',
                           to_ext='pcd',
                           converter=cls.down_sample_pcd_file)

    def pre_process(self):
        self.las2pcd_files(self.src_dir, self.pcd_dir)
        self.down_sample_pcd_files(self.pcd_dir, self.downsampled_pcd_dir)

    def post_process(self, json_dir: str, to_ext):
        """
        :param json_dir:
        :param to_ext: 'txt', 'las', 'laz', default to 'txt'
        :return:
        """
        if not exists(self.segmented_pcd_dir):
            self.post_build_segmented_pcd_files(self.pcd_dir, self.segmented_pcd_dir, json_dir)
        self.post_build_files(self.segmented_pcd_dir, to_ext=to_ext)

    def build_segmented_pcd(self, las_file: str, segmented_pcd_file: str, json_dir: str):
        json_file = self._convert_file_name(self.pcd_dir, pcd_file, json_dir, "json")

        if not exists(json_file):
            print(f"json({json_file}) file does not exist")
            return

        point_labels = []
        with open(json_file) as js:
            json_obj = json.load(js)
            segments = json_obj['result']['data']
            point_list = []
            for pcd_seg in segments:
                indexs_list = pcd_seg['indexs']
                for indexs in indexs_list:
                    pcd_point = indexs.strip().split(' ')
                    pcd_label_no = int(pcd_point[-1]) if len(pcd_point) == 4 else 1

                    point_list.append(pcd_point[:3])
                    point_labels.append(pcd_label_no)
            tree = BallTree(np.asarray(point_list))

        # 读取las文件
        las = laspy.read(las_file)
        # 获取文件头
        # header = las.header
        # # 点类型
        # point_format = las.point_format
        # # 属性字段名
        # dimension_name = point_format.dimension_names
        # # 点集外边框
        # mins = header.mins
        # maxs = header.maxs
        # # 点个数
        # point_num = header.point_count
        # # 获取坐标和颜色
        las_x = np.array(las.x)
        las_y = np.array(las.y)
        las_z = np.array(las.z)

        las_X = np.array(las.X)
        las_Y = np.array(las.Y)
        las_Z = np.array(las.Z)
        # cloud = pcl.load(pcd_file)
        # num_points = cloud.size
        pcd_src_array = np.stack([las_X,las_Y,las_Z],axis=1)
        with open(segmented_pcd_file, "w", encoding='utf-8') as f:
            headers = [
                '# .PCD v0.7 - Point Cloud Data file format\n',
                'VERSION .7\n',
                'FIELDS x y z c\n',
                'SIZE 4 4 4 4\n',
                'TYPE F F F F\n',
                'COUNT 1 1 1 1\n'
            ]
            f.writelines(headers)
            f.write('WIDTH {}\n'.format(num_points))
            f.write('HEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0 0\n')
            f.write('POINTS {}\n'.format(num_points))
            f.write('DATA ascii')

            _, indices = tree.query(pcd_src_array[:, :3])
            for p, ind in zip(pcd_src_array, indices):
                f.write(f'\n{p[0]} {p[1]} {p[2]} {point_labels[ind[0]]}')

    def post_build_segmented_pcd_files(self, src_pcd_dir, out_pcd_dir, json_dir):
        print("==> build segmented pcd files...")
        self._convert_files(src_pcd_dir,
                            out_pcd_dir,
                            from_ext='pcd',
                            to_ext='pcd',
                            converter=partial(self.build_segmented_pcd, json_dir=json_dir))

        print(f"\tannotated pcd files ==> {out_pcd_dir}")

    @staticmethod
    def check_pcd_matches_for_file(pcd_file, las_file):
        in_file = laspy.read(las_file)
        pcd_load = pcl.load(pcd_file)
        pcd_arr = np.asarray(pcd_load)

        # count
        if in_file.header.point_count != pcd_arr.shape[0]:
            print("point count are not equal")
            return False

        # fast
        bin_mask = np.equal(pcd_arr[:, 0], in_file.X)
        bin_mask = np.bitwise_and(bin_mask, np.equal(pcd_arr[:, 1], in_file.Y))
        bin_mask = np.bitwise_and(bin_mask, np.equal(pcd_arr[:, 2], in_file.Z))
        if sum(bin_mask) == len(bin_mask):
            return True
        else:
            print('two arrays are not in same order, will start more accurate test')

            # check if on same area:
            pcd_min_x, pcd_min_y, pcd_min_z = np.min(pcd_arr, 0)
            pcd_max_x, pcd_max_y, pcd_max_z = np.max(pcd_arr, 0)
            las_min_x, las_min_y, las_min_z = in_file.X.min(), in_file.Y.min(), in_file.Z.min()
            las_max_x, las_max_y, las_max_z = in_file.X.max(), in_file.Y.max(), in_file.Z.max()
            template = '\tX- No ovelap on {} axis las[{:<10.2f} {:<10.2f}] vs pcd [{:<10.2f} {:<10.2f}]'
            no_overlap = False
            if las_max_x < pcd_min_x or pcd_max_x < las_min_x:
                no_overlap = True
                print(template.format('x', las_min_x, las_max_x, pcd_min_x, pcd_max_x))
            if las_max_y < pcd_min_y or pcd_max_y < las_min_y:
                no_overlap = True
                print(template.format('y', las_min_y, las_max_y, pcd_min_y, pcd_max_y))
            if las_max_z < pcd_min_z or pcd_max_z < las_min_z:
                no_overlap = True
                print(template.format('z', las_min_z, las_max_z, pcd_min_z, pcd_max_z))
            if no_overlap:
                return False

        return True

    # build segmented txt files
    def pcd2txt(self, segmented_pcd_file, segmented_txt_file):
        src_las_file = self._convert_file_name(from_dir=self.segmented_pcd_dir,
                                               from_file=segmented_pcd_file,
                                               to_dir=self.src_dir,
                                               to_ext="las")
        if not self.check_pcd_matches_for_file(segmented_pcd_file, src_las_file):
            print(f"pcd file({segmented_pcd_file}) does not match the las file")
            return

        in_file = laspy.read(src_las_file)

        # pcd labels
        pcd_labels = np.genfromtxt(segmented_pcd_file,
                                   delimiter=' ',
                                   skip_header=11,
                                   usecols=(-1,),
                                   dtype=np.uint8)

        data = np.stack((in_file.X, in_file.Y, in_file.Z, pcd_labels), axis=1)
        np.savetxt(segmented_txt_file, data, delimiter=',', fmt="%d")

    def post_build_files(self, segmented_pcd_dir: str, to_ext: str):
        segmented_dst_dir = join(self.output_dir, f"{to_ext}_segmented")
        print(f'==> build segmented {to_ext} files to "{segmented_dst_dir}"...')
        if to_ext == 'txt':
            fn = self.pcd2txt
        elif to_ext == 'las':
            fn = self.pcd2laz
        elif to_ext == 'laz':
            fn = self.pcd2laz
        else:
            raise ValueError(f'invalid target file type: "{to_ext}"')

        self._convert_files(segmented_pcd_dir,
                            segmented_dst_dir,
                            from_ext='pcd',
                            to_ext=to_ext,
                            converter=fn)
        print(f"\tannotated {to_ext} files ==> {segmented_dst_dir}")

    def pcd2laz(self, segmented_pcd_file, segmented_laz_file):
        src_las_file = self._convert_file_name(from_dir=self.segmented_pcd_dir,
                                               from_file=segmented_pcd_file,
                                               to_dir=self.src_dir,
                                               to_ext="las")
        if not self.check_pcd_matches_for_file(segmented_pcd_file, src_las_file):
            print(f"pcd file({segmented_pcd_file}) does not match the las file")
            return

        in_file = laspy.read(src_las_file)
        out_file = laspy.LasData(in_file.header)
        for dim in in_file.point_format.dimension_names:
            out_file[dim] = in_file[dim]

        # pcd labels
        pcd_labels = np.genfromtxt(segmented_pcd_file,
                                   delimiter=' ',
                                   skip_header=11,
                                   usecols=(-1,),
                                   dtype=np.uint8)

        # Write new_classification
        out_file['raw_classification'] = pcd_labels

        out_file.write(segmented_laz_file)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='arg parser')
    parser.add_argument('src_dir', type=str, help='src files directory')
    parser.add_argument('dst_dir', type=str, default=None, nargs='?', help='result files directory')
    parser.add_argument('--json_dir', type=str, default=None, nargs='?', help="annotated json files directory")
    parser.add_argument('--output_type', type=str, default='laz', help='the output file type')
    args = parser.parse_args()

    dst_dir = args.dst_dir
    if dst_dir is None:
        dst_dir = args.src_dir + '_output'
    processor = PCDataProcessor(args.src_dir, dst_dir)
    if args.json_dir is None:
        processor.pre_process()
    else:
        processor.post_process(args.json_dir, to_ext=args.output_type)


if __name__ == '__main__':
    main()
