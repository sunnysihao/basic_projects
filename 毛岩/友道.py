# _*_ coding=: utf-8 _*_
import os
from scipy.spatial.transform import Rotation as R
import numpy as np
from numpy.linalg import inv
import json


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list

def rename_image(image_dir):
    for file in list_files(image_dir):
        old_file_name = os.path.join(image_dir, file + '.jpg')
        new_file = file.split('_')[2]
        new_file_name = os.path.join(image_dir, new_file + '.jpg')
        os.rename(old_file_name, new_file_name)

def create_external(translation_list: list, rotation_list: list):
    row = [[0, 0, 0, 1]]
    cam_r = R.from_quat(rotation_list).as_matrix()
    cam_t = np.array(translation_list).reshape((3, 1))
    cam_ext = np.hstack((cam_r, cam_t))
    cam_ext = np.vstack((cam_ext, row)).flatten().tolist()
    return cam_ext

# t0 = [5.094871883961432, 1.390502186799266, 1.691106456307773]
# r0 = [-0.666309, 0.246776, -0.280709, 0.645242]
# cam_ext0 = create_external(t0, r0)
#
# t1 = [4.904584364245445, 0.02716057841129192, 2.389377031158598]
# r1 = [0.507968, -0.49511, 0.50074, -0.496079]
# cam_ext1 = create_external(t1, r1)
#
# t2 = [5.137912388128064, -1.405874805575044, 1.752523925345209]
# r2 = [0.276809, -0.643116, 0.659593, -0.27334]
# cam_ext2 = create_external(t2, r2)
#
# t3 = [4.986381000144587, -1.395500380037224, 1.736904717142705]
# r3 = [-0.276263, -0.650612, 0.663092, 0.246356]
# cam_ext3 = create_external(t3, r3)
#
# t4 = [4.928515061552922, 1.423082599937332, 1.683499599298034]
# r4 = [-0.652754, -0.29322, 0.277227, 0.641154]
# cam_ext4 = create_external(t4, r4)

def set_config(json_file, config_path, pcd_dir):
    with open(json_file, "r", encoding='utf-8') as f:
        json_content = json.load(f)
        cam_in0 = json_content['left-forward']['camera_internal']
        cam_ext0 = list(map(float, json_content['left-forward']['camera_external']))
        cam_ext0 = np.asarray(cam_ext0).reshape((4, 4))
        cam_ext0 = inv(cam_ext0).T
        cam_in1 = json_content['forward']['camera_internal']
        cam_ext1 = list(map(float, json_content['forward']['camera_external']))
        cam_ext1 = np.asarray(cam_ext1).reshape((4, 4))
        cam_ext1 = inv(cam_ext1).T
        cam_in2 = json_content['right-forward']['camera_internal']
        cam_ext2 = list(map(float, json_content['right-forward']['camera_external']))
        cam_ext2 = np.asarray(cam_ext2).reshape((4, 4))
        cam_ext2 = inv(cam_ext2).T
        cam_in3 = json_content['right-backward']['camera_internal']
        cam_ext3 = list(map(float, json_content['right-backward']['camera_external']))
        cam_ext3 = np.asarray(cam_ext3).reshape((4, 4))
        cam_ext3 = inv(cam_ext3).T
        cam_in4 = json_content['left-backward']['camera_internal']
        cam_ext4 = list(map(float, json_content['left-backward']['camera_external']))
        cam_ext4 = np.asarray(cam_ext4).reshape((4, 4))
        cam_ext4 = inv(cam_ext4).T

        data = {
            "3d_img0": {
                "camera_internal": cam_in0,
                "camera_external": cam_ext0.flatten().tolist()
            },
            "3d_img1": {
                "camera_internal": cam_in1,
                "camera_external": cam_ext1.flatten().tolist()
            },
            "3d_img2": {
                "camera_internal": cam_in2,
                "camera_external": cam_ext2.flatten().tolist()
            },
            "3d_img3": {
                "camera_internal": cam_in3,
                "camera_external": cam_ext3.flatten().tolist()
            },
            "3d_img4": {
                "camera_internal": cam_in4,
                "camera_external": cam_ext4.flatten().tolist()
            }
        }

        for file in list_files(pcd_dir):
            with open(os.path.join(config_path, file + '.json'), 'w', encoding='utf-8') as f:
                f.write(json.dumps(data))

# def write_json(pcd_path, config_path):
#     for file in list_files(pcd_path):
#         with open(os.path.join(config_path, file + '.json'), 'w', encoding='utf-8') as f:
#             f.write(json.dumps(data))

if __name__ == "__main__":
    json_file = r"D:\Desktop\BasicProject\任从辉\有道原数据 06.24\params.json"
    pcd_dir = r"D:\Desktop\BasicProject\任从辉\有道原数据 06.24\3d_url"
    config_path =r"D:\Desktop\BasicProject\任从辉\有道原数据 06.24\new_config"
    set_config(json_file,  config_path, pcd_dir)
# image_dir = r"D:\Desktop\BasicProject\任从辉\有道原数据 06.24\images\3d_img4"
# rename_image(image_dir)

