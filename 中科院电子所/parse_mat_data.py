# _*_ coding=: utf-8 _*_
# @Time    : 2022/07/27
# @Author  : zhangsihao@basicfinder.com
"""
功能：
    中科院电子所mat文件解析为平台标注数据导入格式。
使用方法：
    运行程序，根据命令提示输入对应文件路径。
"""
import os
from PIL import Image
import scipy.io as io
from tqdm import tqdm


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.mat':
                file_name = os.path.splitext(file)[0]
                file_list.append(file_name)
    return file_list


def load_mat(mat_file: str):
    mat_data = io.loadmat(mat_file)
    return mat_data


def create_file(mat_file, result_dir):
    mat_path = os.path.dirname(mat_file)
    mat_file_name = os.path.splitext(os.path.basename(mat_file))[0]
    result_path = os.path.join(os.path.dirname(mat_path), result_dir)
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    result_file_name = os.path.join(result_path, mat_file_name)
    return result_file_name


def write_pcd(mat_file: str):
    pcd_file = create_file(mat_file, '3d_url') + '.pcd'
    mat_data = load_mat(mat_file)
    points = mat_data['lidar_points']
    with open(pcd_file, 'a') as pcd_file:
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
            string = '\n' + str(points[i, 0]) + ' ' + str(points[i, 1])\
                     + ' ' + str(points[i, 2]) + ' ' + str(points[i, 3])
            pcd_file.write(string)


def save_img(mat_file):
    mat_data = load_mat(mat_file)
    img0_file = create_file(mat_file, '3d_img0') + '.jpg'
    im0 = Image.fromarray(mat_data['camera_bleft'])
    im0.save(img0_file)

    img1_file = create_file(mat_file, '3d_img1') + '.jpg'
    im1 = Image.fromarray(mat_data['camera_bright'])
    im1.save(img1_file)

    img2_file = create_file(mat_file, '3d_img2') + '.jpg'
    im2 = Image.fromarray(mat_data['camera_fleft'])
    im2.save(img2_file)

    img3_file = create_file(mat_file, '3d_img3') + '.jpg'
    im3 = Image.fromarray(mat_data['camera_fright'])
    im3.save(img3_file)

    img4_file = create_file(mat_file, '3d_img4') + '.jpg'
    im4 = Image.fromarray(mat_data['camera_front'])
    im4.save(img4_file)

    img5_file = create_file(mat_file, '3d_img5') + '.jpg'
    im5 = Image.fromarray(mat_data['camera_lleft'])
    im5.save(img5_file)

    img6_file = create_file(mat_file, '3d_img6') + '.jpg'
    im6 = Image.fromarray(mat_data['camera_rright'])
    im6.save(img6_file)


def main(mat_dir):
    for file in tqdm(list_files(mat_dir), desc='进度', leave=True, unit='file', colour='blue'):
        mat_file = os.path.join(mat_dir, file + '.mat')
        write_pcd(mat_file)
        save_img(mat_file)


if __name__ == "__main__":
    mat_dir = input("请输入.mat文件所在目录路径：\n")
    print('-------------------------------------------------')
    main(mat_dir)
    input("解析完成\n按任意键退出")
