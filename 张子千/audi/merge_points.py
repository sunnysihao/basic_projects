# -*- coding: utf-8 -*- 
# @Time : 2022/12/30
# @Author : zhangsihao@basicfinder.com
"""
"""
import json
import os
import numpy as np
import numpy.linalg as la

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
    return np.hstack((points[:, 0:3]), i.reshape((-1, 1)))


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


def main(o_dir):
    lidar_dir = os.path.join(o_dir, 'lidar')
    camera_dir = os.path.join(o_dir, 'camera')
    dirs = os.listdir(lidar_dir)
    files = list_files(os.path.join(lidar_dir, lidar_dirs[0]), '.npz')
    for file in files:
        file_name = os.path.splitext(os.path.basename(file))[0]
        ext_json_file = os.path.join()
    for d in range(6):
        files = list_files(os.path.join(lidar_dir, lidar_dirs[d]), '.npz')

        ext_json = files[]
        points = np.array([[0, 0, 0, 1]])
        for i in range(5):
            datas = np.load(files[i])
            lidar = config['lidars'][views[i]]['view']
            ext = get_transform_to_global(lidar)
            point = parse_points(datas, ext)
            points = np.around(np.vstack((points, point)), 3)
            write_pcd(points)

