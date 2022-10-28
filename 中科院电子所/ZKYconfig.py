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
    cam_in = y_data['CameraMat']['data']
    fx = cam_in[0]
    cx = cam_in[2]
    fy = cam_in[4]
    cy = cam_in[5]
    camera_internal = {
        "fx": fx,
        "cx": cx,
        "cy": cy,
        "fy": fy
    }
    return camera_internal

def get_cam_ext(yaml_file):
    cam_ext = load_yaml(yaml_file)['CameraExtrinsicMat']['data']
    cam_ext = np.array(cam_ext).reshape((4, 4))
    cam_ext = cam_ext.flatten().tolist()
    return cam_ext

cam_in0 = get_cam_in(r"D:\Desktop\BasicProject\魏宏锐\中科院电子所\2bc051f834ecd7a1dabb9376ad85d9df_198eaa0cad7cc28aa9f569c1261b8358_8\bleft_camera_lidar_pro.yml")
cam_ext0 = get_cam_ext(r"D:\Desktop\BasicProject\魏宏锐\中科院电子所\2bc051f834ecd7a1dabb9376ad85d9df_198eaa0cad7cc28aa9f569c1261b8358_8\bleft_camera_lidar_pro.yml")

cam_in1 = get_cam_in(r"D:\Desktop\BasicProject\魏宏锐\中科院电子所\2bc051f834ecd7a1dabb9376ad85d9df_198eaa0cad7cc28aa9f569c1261b8358_8\bright_camera_lidar_pro.yml")
cam_ext1 = get_cam_ext(r"D:\Desktop\BasicProject\魏宏锐\中科院电子所\2bc051f834ecd7a1dabb9376ad85d9df_198eaa0cad7cc28aa9f569c1261b8358_8\bright_camera_lidar_pro.yml")

cam_in2 = get_cam_in(r"D:\Desktop\BasicProject\魏宏锐\中科院电子所\2bc051f834ecd7a1dabb9376ad85d9df_198eaa0cad7cc28aa9f569c1261b8358_8\fleft_camera_lidar_pro.yml")
cam_ext2 = get_cam_ext(r"D:\Desktop\BasicProject\魏宏锐\中科院电子所\2bc051f834ecd7a1dabb9376ad85d9df_198eaa0cad7cc28aa9f569c1261b8358_8\fleft_camera_lidar_pro.yml")

cam_in3 = get_cam_in(r"D:\Desktop\BasicProject\魏宏锐\中科院电子所\2bc051f834ecd7a1dabb9376ad85d9df_198eaa0cad7cc28aa9f569c1261b8358_8\fright_camera_lidar_pro.yml")
cam_ext3 = get_cam_ext(r"D:\Desktop\BasicProject\魏宏锐\中科院电子所\2bc051f834ecd7a1dabb9376ad85d9df_198eaa0cad7cc28aa9f569c1261b8358_8\fright_camera_lidar_pro.yml")

cam_in4 = get_cam_in(r"D:\Desktop\BasicProject\魏宏锐\中科院电子所\2bc051f834ecd7a1dabb9376ad85d9df_198eaa0cad7cc28aa9f569c1261b8358_8\front_camera_lidar_pro.yml")
cam_ext4 = get_cam_ext(r"D:\Desktop\BasicProject\魏宏锐\中科院电子所\2bc051f834ecd7a1dabb9376ad85d9df_198eaa0cad7cc28aa9f569c1261b8358_8\front_camera_lidar_pro.yml")

cam_in5 = get_cam_in(r"D:\Desktop\BasicProject\魏宏锐\中科院电子所\2bc051f834ecd7a1dabb9376ad85d9df_198eaa0cad7cc28aa9f569c1261b8358_8\lleft_camera_lidar_pro.yml")
cam_ext5 = get_cam_ext(r"D:\Desktop\BasicProject\魏宏锐\中科院电子所\2bc051f834ecd7a1dabb9376ad85d9df_198eaa0cad7cc28aa9f569c1261b8358_8\lleft_camera_lidar_pro.yml")

cam_in6 = get_cam_in(r"D:\Desktop\BasicProject\魏宏锐\中科院电子所\2bc051f834ecd7a1dabb9376ad85d9df_198eaa0cad7cc28aa9f569c1261b8358_8\rright_camera_lidar_pro.yml")
cam_ext6 = get_cam_ext(r"D:\Desktop\BasicProject\魏宏锐\中科院电子所\2bc051f834ecd7a1dabb9376ad85d9df_198eaa0cad7cc28aa9f569c1261b8358_8\rright_camera_lidar_pro.yml")

data = {
            "3d_img0": {
                "camera_internal": cam_in0,
                "camera_external": cam_ext0
            },
            "3d_img1": {
                "camera_internal": cam_in1,
                "camera_external": cam_ext1
            },
            "3d_img2": {
                "camera_internal": cam_in2,
                "camera_external": cam_ext2
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
    pcd_path = r"D:\Desktop\BasicProject\魏宏锐\中科院电子所\中科院电子所\3d_url"
    config_path = r"D:\Desktop\BasicProject\魏宏锐\中科院电子所\中科院电子所\camera_config"
    set_config(pcd_path, config_path)
