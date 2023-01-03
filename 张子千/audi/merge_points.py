# -*- coding: utf-8 -*- 
# @Time : 2022/12/30
# @Author : zhangsihao@basicfinder.com
"""
"""
import json
import os
import numpy as np
import numpy.linalg as la
from tqdm import tqdm
import shutil

with open(r'D:\Desktop\Project_file\张子千\audi\a2d2-preview\cams_lidars.json', 'r') as f:
    config = json.load(f)


def list_files(in_path: str, match):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == match:
                file_list.append(os.path.join(root, file))
    return file_list


EPSILON = 1.0e-10 # norm should not be small
def get_axes_of_a_view(view):
    x_axis = view['x-axis']
    y_axis = view['y-axis']

    x_axis_norm = la.norm(x_axis)
    y_axis_norm = la.norm(y_axis)

    if (x_axis_norm < EPSILON or y_axis_norm < EPSILON):
        raise ValueError("Norm of input vector(s) too small.")

    # normalize the axes
    x_axis = x_axis / x_axis_norm
    y_axis = y_axis / y_axis_norm

    # make a new y-axis which lies in the original x-y plane, but is orthogonal to x-axis
    y_axis = y_axis - x_axis * np.dot(y_axis, x_axis)

    # create orthogonal z-axis
    z_axis = np.cross(x_axis, y_axis)

    # calculate and check y-axis and z-axis norms
    y_axis_norm = la.norm(y_axis)
    z_axis_norm = la.norm(z_axis)

    if (y_axis_norm < EPSILON) or (z_axis_norm < EPSILON):
        raise ValueError("Norm of view axis vector(s) too small.")

    # make x/y/z-axes orthonormal
    y_axis = y_axis / y_axis_norm
    z_axis = z_axis / z_axis_norm

    return x_axis, y_axis, z_axis


def get_origin_of_a_view(view):
    return view['origin']


def get_transform_to_global(view):
    # get axes
    x_axis, y_axis, z_axis = get_axes_of_a_view(view)

    # get origin
    origin = get_origin_of_a_view(view)
    transform_to_global = np.eye(4)

    # rotation
    transform_to_global[0:3, 0] = x_axis
    transform_to_global[0:3, 1] = y_axis
    transform_to_global[0:3, 2] = z_axis

    # origin
    transform_to_global[0:3, 3] = origin

    return transform_to_global


def parse_points(file, ext):
    datas = np.load(file)
    i = datas['pcloud_attr.reflectance']
    point = datas['pcloud_points']
    one = np.ones(len(point))
    points = np.hstack((point, one.reshape((-1, 1)))) @ ext.T
    return np.hstack(((points[:, 0:3]), i.reshape(-1, 1)))


def parse_ext(file):
    with open(file, 'r') as tf:
        cfg = json.load(tf)
        ext_t = get_transform_to_global(cfg['pcld_view'])
        return ext_t


def write_pcd(points, file):
    with open(file, 'w', encoding='ascii') as pcd_file:
        point_num = points.shape[0]
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
            string_point = '\n' + str(points[i, 0]) + ' ' + str(points[i, 1]) + ' ' + str(points[i, 2]) + ' ' + str(points[i, 3])
            pcd_file.write(string_point)


def main(o_dir, save_dir):
    merge_pc_dir = os.path.join(save_dir, 'point_cloud')
    if not os.path.exists(merge_pc_dir):
        os.mkdir(merge_pc_dir)
    lidar_dir = os.path.join(o_dir, 'lidar')
    camera_dir = os.path.join(o_dir, 'camera')
    dirs = os.listdir(lidar_dir)

    file_nums = list_files(os.path.join(lidar_dir, dirs[0]), '.npz')
    for i in tqdm(range(len(file_nums))):
        name = os.path.splitext(os.path.basename(file_nums[i]))[0].split('_')
        save_name = '_'.join([name[0], name[-1]])
        pcd_file = os.path.join(merge_pc_dir, save_name + '.pcd')
        points = np.array([[0, 0, 0, 1]])
        for _dir in dirs:
            files = list_files(os.path.join(lidar_dir, _dir), '.npz')

            file_name = os.path.splitext(os.path.basename(files[i]))[0]
            lidar_file = os.path.join(lidar_dir, _dir, file_name + '.npz')
            ext_file = os.path.join(camera_dir, _dir, file_name.replace('lidar', 'camera') + '.json')
            o_img_file = os.path.join(camera_dir, _dir, file_name.replace('lidar', 'camera') + '.png')
            new_img_dir = os.path.join(save_dir, f"image{dirs.index(_dir)}")
            if not os.path.exists(new_img_dir):
                os.mkdir(new_img_dir)
            new_img_file = os.path.join(new_img_dir, save_name + '.png')
            shutil.copyfile(o_img_file, new_img_file)
            ext = parse_ext(ext_file)
            pc = parse_points(lidar_file, ext)
            points = np.around(np.vstack((points, pc)), 3)
        write_pcd(points, pcd_file)


if __name__ == '__main__':
   o_dir = r"D:\Desktop\Project_file\张子千\audi\a2d2-preview\camera_lidar\20180810_150607"
   save_dir = r"D:\Desktop\Project_file\张子千\audi\a2d2-preview\camera_lidar\20180810_150607\upload_files"
   main(o_dir, save_dir)
