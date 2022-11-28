# -*- coding: utf-8 -*- 
# @Time : 2022/11/9
# @Author : zhangsihao@basicfinder.com
"""
"""
import json
import os
import numpy as np
import shutil
from tqdm import tqdm
from scipy.spatial.transform import Rotation as R
from numpy.linalg import inv


def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def list_files(in_path: str, match):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == match:
                file_list.append(os.path.join(root, file))
    return file_list


def save_pcd(pc: np.ndarray, file, binary=True):
    pc = pc.astype(np.float32)
    num_points = len(pc)

    with open(file, 'wb' if binary else 'w') as f:
        # heads
        headers = [
            '# .PCD v0.7 - Point Cloud Data file format',
            'VERSION 0.7',
            'FIELDS x y z i',
            'SIZE 4 4 4 4',
            'TYPE F F F F',
            'COUNT 1 1 1 1',
            f'WIDTH {num_points}',
            'HEIGHT 1',
            'VIEWPOINT 0 0 0 1 0 0 0',
            f'POINTS {num_points}',
            f'DATA {"binary" if binary else "ascii"}'
        ]
        header = '\n'.join(headers) + '\n'
        if binary:
            header = bytes(header, 'ascii')
        f.write(header)

        # points
        if binary:
            f.write(pc.tobytes())
        else:
            for i in range(num_points):
                x, y, z, i = pc[i]
                f.write(f"{x:.3f} {y:.3f} {z:.3f} {i:.3f}\n")


def save_pc(json_file, pcd_file):
    file_name = os.path.splitext(os.path.basename(json_file))[0]
    json_content = load_json(json_file)
    j_points = json_content['points']
    x = []
    y = []
    z = []
    i = []
    for p in j_points:
        x.append(p['x'])
        y.append(p['y'])
        z.append(p['z'])
        i.append(p['i'])
    points0 = np.stack([x, y, z, i], axis=1)
    points = np.array(points0, dtype=np.float32)
    save_pcd(points, pcd_file)


def rename_img(path, x1=True):
    if x1:
        img_path0 = os.path.join(path, 'image0')
        img_path1 = os.path.join(path, 'image1')
        img_path2 = os.path.join(path, 'image2')
    else:
        img_path0 = os.path.join(path, '3d_img0')
        img_path1 = os.path.join(path, '3d_img1')
        img_path2 = os.path.join(path, '3d_img2')
    if not os.path.exists(img_path0):
        os.mkdir(img_path0)
    if not os.path.exists(img_path1):
        os.mkdir(img_path1)
    if not os.path.exists(img_path2):
        os.mkdir(img_path2)
    for img_f in tqdm(list_files(path, '.jpeg')):
        file_name = os.path.basename(img_f)
        if file_name.startswith('c'):
            new_name = file_name.replace('c_', '')
            new_file = os.path.join(img_path0, new_name)
        elif file_name.startswith('l'):
            new_name = file_name.replace('l_', '')
            new_file = os.path.join(img_path1, new_name)
        else:
            new_name = file_name.replace('r_', '')
            new_file = os.path.join(img_path2, new_name)
        shutil.copyfile(img_f, new_file)


def set_config(json_file, config_file, x1=True):
    json_content = load_json(json_file)
    img_param = json_content['images']
    # lidar_param_t = np.array([0, 0, 0]).reshape(3, 1)
    # lidar_param_t = np.array([json_content['device_position']['x'], json_content['device_position']['y'], json_content['device_position']['z']]).reshape(3, 1)
    # lidar_param_quat = [json_content['device_heading']['x'], json_content['device_heading']['y'], json_content['device_heading']['z'], json_content['device_heading']['w']]
    # lidar_ext = parse_ext(lidar_param_t, lidar_param_quat)
    img0 = None
    img1 = None
    img2 = None
    for param in img_param:
        fx = param['fx']
        fy = param['fy']
        cx = param['cx']
        cy = param['cy']
        cam_in = {
            "fx": fx,
            "cx": cx,
            "cy": cy,
            "fy": fy
        }
        # cam_t = np.array([0, 0, 0]).reshape(3, 1)
        cam_t = np.array([param['position']['x'], param['position']['y'], param['position']['z']]).reshape(3, 1)
        cam_quat = [param['heading']['x'], param['heading']['y'], param['heading']['z'], param['heading']['w']]
        cam_ext0 = parse_ext(cam_t, cam_quat)
        cam_ext = cam_ext0
        image_url = param['image_url']
        if image_url.startswith('c'):
            img0 = {
            "camera_internal": cam_in,
            "camera_external": cam_ext.flatten().tolist()
        }
        elif image_url.startswith('l'):
            img1 = {
            "camera_internal": cam_in,
            "camera_external": cam_ext.flatten().tolist()
        }
        else:
            img2 = {
                "camera_internal": cam_in,
                "camera_external": cam_ext.flatten().tolist()
            }
    if not img0 or not img1 or not img2:
        print(f"{json_file} 缺少参数")
    else:
        if x1:
            config_data = [img0, img1, img2]
        else:
            config_data = {
                "3d_img0": img0,
                "3d_img1": img1,
                "3d_img2": img2
            }

        with open(config_file, 'w', encoding='utf-8') as cf:
            json.dump(config_data, cf)


def parse_ext(t, quat):
    ext_r = R.from_quat(quat).as_matrix()
    ext = np.hstack((ext_r, t))
    ext = np.vstack((ext, [0, 0, 0, 1]))
    return inv(ext)


def main(path, x1=True):
    rename_img(path, x1)
    if x1:
        pcd_path = os.path.join(path, 'point_cloud')
    else:
        pcd_path = os.path.join(path, '3d_url')
    if not os.path.exists(pcd_path):
        os.mkdir(pcd_path)
    config_path = os.path.join(path, 'camera_config')
    if not os.path.exists(config_path):
        os.mkdir(config_path)
    for jf in tqdm(list_files(path, '.json')):
        file_name = os.path.splitext(os.path.basename(jf))[0]
        pcd_file = os.path.join(pcd_path, file_name + '.pcd')
        config_file = os.path.join(config_path, file_name + '.json')
        set_config(jf, config_file, x1)
        save_pc(jf, pcd_file)


if __name__ == '__main__':
    total_dir = r"D:\Desktop\Project_file\谢秋梅\polit\新建文件夹"
    for dir in os.listdir(total_dir):
        path = os.path.join(total_dir, dir)
    # path = r"C:\Users\EDY\Downloads\pilot_Data-20221108T101954Z-001\pilot_Data\single"
        main(path, x1=True)
