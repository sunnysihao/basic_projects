# _*_ coding=: utf-8 _*_
import os
import yaml
import json
import numpy as np
from numpy.linalg import inv


def load_yaml(yaml_path):
    with open(yaml_path, 'r', encoding='utf-8') as f:
        yaml_data = yaml.load(f, Loader=yaml.FullLoader)
    return yaml_data

def get_cam_in(yaml_file):
    y_data = load_yaml(yaml_file)
    fx, fy, cx, cy = y_data['K']
    camera_internal = {
        "fx": fx,
        "cx": cx,
        "cy": cy,
        "fy": fy
    }
    return camera_internal

def get_cam_ext(yaml_file):
    cam_ext = load_yaml(yaml_file)['transform']
    cam_ext = inv(np.array(cam_ext))
    cam_ext = cam_ext.flatten().tolist()
    return cam_ext

cam_in0 = get_cam_in(r"D:\Desktop\BasicProject\任从辉\科乐园\test(2)\test\sample000001\calibration\intrinics\left_front_camera.yaml")
cam_ext0 = get_cam_ext(r"D:\Desktop\BasicProject\任从辉\科乐园\test(2)\test\sample000001\calibration\extrinics\lidar2leftfront.yaml")

cam_in1 = get_cam_in(r"D:\Desktop\BasicProject\任从辉\科乐园\test(2)\test\sample000001\calibration\intrinics\front_main_camera.yaml")
cam_ext1 = get_cam_ext(r"D:\Desktop\BasicProject\任从辉\科乐园\test(2)\test\sample000001\calibration\extrinics\lidar2frontmain.yaml")

cam_in2 = get_cam_in(r"D:\Desktop\BasicProject\任从辉\科乐园\test(2)\test\sample000001\calibration\intrinics\front_wide_camera.yaml")
cam_ext2 = get_cam_ext(r"D:\Desktop\BasicProject\任从辉\科乐园\test(2)\test\sample000001\calibration\extrinics\lidar2frontwide.yaml")

cam_in3 = get_cam_in(r"D:\Desktop\BasicProject\任从辉\科乐园\test(2)\test\sample000001\calibration\intrinics\right_front_camera.yaml")
cam_ext3 = get_cam_ext(r"D:\Desktop\BasicProject\任从辉\科乐园\test(2)\test\sample000001\calibration\extrinics\lidar2rightfront.yaml")

cam_in4 = get_cam_in(r"D:\Desktop\BasicProject\任从辉\科乐园\test(2)\test\sample000001\calibration\intrinics\right_rear_camera.yaml")
cam_ext4 = get_cam_ext(r"D:\Desktop\BasicProject\任从辉\科乐园\test(2)\test\sample000001\calibration\extrinics\lidar2rightrear.yaml")

cam_in5 = get_cam_in(r"D:\Desktop\BasicProject\任从辉\科乐园\test(2)\test\sample000001\calibration\intrinics\rear_main_camera.yaml")
cam_ext5 = get_cam_ext(r"D:\Desktop\BasicProject\任从辉\科乐园\test(2)\test\sample000001\calibration\extrinics\lidar2rearmain.yaml")

cam_in6 = get_cam_in(r"D:\Desktop\BasicProject\任从辉\科乐园\test(2)\test\sample000001\calibration\intrinics\left_rear_camera.yaml")
cam_ext6 = get_cam_ext(r"D:\Desktop\BasicProject\任从辉\科乐园\test(2)\test\sample000001\calibration\extrinics\lidar2leftrear.yaml")

data = {
            "3d_img0": {
                "camera_internal": cam_in0,
                "camera_external": cam_ext0
            },
            "3d_img1": {
                "camera_internal": cam_in2,
                "camera_external": cam_ext2
            },
            "3d_img2": {
                "camera_internal": cam_in1,
                "camera_external": cam_ext1
            },
            "3d_img3": {
                "camera_internal": cam_in3,
                "camera_external": cam_ext3
            },
            "3d_img4": {
                "camera_internal": cam_in4,
                "camera_external": cam_ext4
            },
            "3d_img5": {
                "camera_internal": cam_in5,
                "camera_external": cam_ext5
            },
            "3d_img6": {
                "camera_internal": cam_in6,
                "camera_external": cam_ext6
            }
        }

def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0].split('.')[0]
            file_list.append(file_name)
    return file_list


def set_config(pcd_path, config_path):
    for file in list_files(pcd_path):
        with open(os.path.join(config_path, file + '.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps(data))


if __name__ == "__main__":
    pcd_path = r"D:\Desktop\BasicProject\任从辉\科乐园\科乐园数据集\3d_url"
    config_path = r"D:\Desktop\BasicProject\任从辉\科乐园\科乐园数据集\camera_config"
    set_config(pcd_path, config_path)
