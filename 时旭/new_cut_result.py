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


def list_files_all(in_path):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            # if os.path.splitext(file)[-1] == '.json':
            file_list.append(os.path.join(root, file))
            # else:
            #     continue
    return file_list


def load_json(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def list_files(dir_path: str, name_regex: str = None):
    if name_regex:
        name_regex = re.compile(name_regex)

    for root, _, file_names in os.walk(dir_path):
        for file_name in file_names:
            if name_regex is None or name_regex.match(file_name):
                yield join(root, file_name)


def build_segmented_pcd(las_file: str, segmented_pcd_file: str, json_file: str):

    if not exists(json_file):
        print(f"json({json_file}) file does not exist")
        return

    point_labels = []
    with open(json_file, 'r', encoding='utf-8') as js:
        content = js.read()
        json_obj = json.loads(content)
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


    las = laspy.read(las_file)

    las_x = np.array(las.x)
    las_y = np.array(las.y)
    las_z = np.array(las.z)

    las_X = np.array(las.X)
    las_Y = np.array(las.Y)
    las_Z = np.array(las.Z)

    las_r = np.array(las.red)
    las_g = np.array(las.green)
    las_b = np.array(las.blue)
    # cloud = pcl.load(pcd_file)
    # num_points = cloud.size
    pcd_src_array = np.stack([las_X, las_Y, las_Z], axis=1)
    # rgb_src_array = np.stack([las_r, las_g, las_b], axis=1)
    num_points = pcd_src_array.shape[0]
    with open(segmented_pcd_file, "w", encoding='utf-8') as f:
        headers = [
            '# .PCD v0.7 - Point Cloud Data file format\n',
            'VERSION .7\n',
            'FIELDS x y z r g b c\n',
            'SIZE 4 4 4 4 4 4 4\n',
            'TYPE F F F U U U U\n',
            'COUNT 1 1 1 1 1 1 1\n'
        ]
        f.writelines(headers)
        f.write('WIDTH {}\n'.format(num_points))
        f.write('HEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0 0\n')
        f.write('POINTS {}\n'.format(num_points))
        f.write('DATA ascii')

        _, indices = tree.query(pcd_src_array[:, :3])
        i = 0
        for p, ind in zip(pcd_src_array, indices):
            f.write(f'\n{las_x[i]} {las_y[i]} {las_z[i]} {int(las_r[i]/2**8)} {int(las_g[i]/2**8)} {int(las_b[i]/2**8)} {point_labels[ind[0]]}')
            i += 1

def pcd2laz(las_file, segmented_pcd_file, segmented_laz_file):
    # src_las_file = self._convert_file_name(from_dir=self.segmented_pcd_dir,
    #                                        from_file=segmented_pcd_file,
    #                                        to_dir=self.src_dir,
    #                                        to_ext="las")
    # if not self.check_pcd_matches_for_file(segmented_pcd_file, src_las_file):
    #     print(f"pcd file({segmented_pcd_file}) does not match the las file")
    #     return

    in_file = laspy.read(las_file)
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


def main(in_path):
    las_path = os.path.join(in_path, 'las_files')
    for las_file in tqdm(list_files_all(las_path)):
        pcd_file = las_file.replace('las_files', 'pcd_files').replace('.las', '.pcd')
        json_file = las_file.replace('las_files', 'result_json').replace('.las', '.json')
        # laz_file = las_file.replace('las_files', 'laz_files').replace('.las', '.laz')
        # if not os.path.exists(dirname(laz_file)):
        #     os.mkdir(dirname(laz_file))
        build_segmented_pcd(las_file, pcd_file, json_file)
        # pcd2laz(las_file, pcd_file, laz_file)

if __name__ == "__main__":
    in_path = r"D:\Desktop\BasicProject\王满顺\时旭\时旭科技数据\时旭科技数据\sx_data"
    main(in_path)


