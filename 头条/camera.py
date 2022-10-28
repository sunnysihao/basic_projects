# _*_ coding=: utf-8 _*_
import os
import json
import re
import numpy as np
from scipy.spatial.transform import Rotation as R
from numpy.linalg import inv
import requests
from PIL import Image
import cv2

def get_param(url):
    rps = requests.get(url)
    json_content = rps.json()
    fx = json_content['cameraIntrinsicMatrix'][0]
    cx = json_content['cameraIntrinsicMatrix'][2]
    fy = json_content['cameraIntrinsicMatrix'][5]
    cy = json_content['cameraIntrinsicMatrix'][6]
    row = np.array([0, 0, 0, 1]).reshape((1, 4))
    ext = np.array(json_content['cameraExtrinsicMatrix']).reshape((3, 4))
    # t = np.array([0, 0, 0]).reshape((3, 1))
    # cam_ext = np.hstack((ext, t))
    # cam_ext = np.vstack((cam_ext, row))
    cam_ext = np.vstack((ext, row))
    cam_ext = inv(cam_ext)
    img = {
        "camera_internal": {
            "fx": fx,
            "cx": cx,
            "cy": cy,
            "fy": fy
        },
        "camera_external": cam_ext.flatten().tolist()
    }
    return img


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list


fc = "https://lf3-static.bytednsdoc.com/obj/crowdsourcing/point-cloud-box/pcd/mg/fc.json"
fl = "https://lf3-static.bytednsdoc.com/obj/crowdsourcing/point-cloud-box/pcd/mg/fl.json"
fr = "https://lf3-static.bytednsdoc.com/obj/crowdsourcing/point-cloud-box/pcd/mg/fr.json"
rc = "https://lf3-static.bytednsdoc.com/obj/crowdsourcing/point-cloud-box/pcd/mg/rc.json"
rl = "https://lf3-static.bytednsdoc.com/obj/crowdsourcing/point-cloud-box/pcd/mg/rl.json"
rr = "https://lf3-static.bytednsdoc.com/obj/crowdsourcing/point-cloud-box/pcd/mg/rr.json"

img0 = get_param(fc)
img1 = get_param(fl)
img2 = get_param(fr)
img3 = get_param(rc)
img4 = get_param(rl)
img5 = get_param(rr)

data = {
            "3d_img0": img0,
            "3d_img1": img1,
            "3d_img2": img2,
            "3d_img3": img3,
            "3d_img4": img4,
            "3d_img5": img5
        }

def write_json(pcd_path, config_path):
    for file in list_files(pcd_path):
        with open(os.path.join(config_path, file + '.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps(data))


# 生成单独的每个视角个相机参数json文件
def write_single_config(pcd_path, config_path, x):
    file = list_files(pcd_path)[0]
    single_config = os.path.join(os.path.dirname(config_path), "single_configs")
    if not os.path.exists(single_config):
        os.mkdir(single_config)
    for i in range(x):

        single_data = {
            "3d_img0": data[f'3d_img{i}']
        }
        with open(os.path.join(single_config, file + f'-{i}' + '.json'), 'w', encoding='utf-8') as sf:
            sf.write(json.dumps(single_data))

def fish_eye_to_normal_image(camera_internal:list, camera_D:list, fish_image_path:str, save_file_path:str):
    K = np.array(camera_internal)   #相机内参
    D = np.array(camera_D)   #相机畸变参数
    image = Image.open(fish_image_path)
    img = np.asarray(image)
    im = Image.fromarray(cv2.undistort(img, K, D, None, K))
    im.save(save_file_path)


# pcd,json,jpg文件按pcd文件名重命名
def rename_files(pcd_path, other_path):
    pcd_name_list = list_files(pcd_path)
    img_name_list = list_files(other_path)
    for i in range(len(pcd_name_list)):
        old_img_name = os.path.join(other_path, img_name_list[i] + '.jpg')
        new_name = os.path.join(other_path, pcd_name_list[i] + '.jpg')
        os.rename(old_img_name, new_name)

for num in range(1,6):
    other_path = rf"D:\Desktop\BasicProject\毛岩\头条\20220620164301-0\头条0712\3d_img{num}"

    pcd_path = r"D:\Desktop\BasicProject\毛岩\头条\20220620164301-0\头条0712\3d_url"
# config_path = r"D:\Desktop\BasicProject\毛岩\头条\20220620164301\20220620164301\camera_config"
# # write_json(pcd_path, config_path)
# con_p = r"D:\Desktop\BasicProject\毛岩\头条\20220620164301\cam"
# write_single_config(pcd_path, con_p, 6)
    rename_files(pcd_path, other_path)

# camera_internal = [[1960.94957, 0, 1892.89331],
#                     [0, 1133.92507, 1971.4898],
#                    [0, 0, 1]]
# camera_D = [-0.0550647437927507, 0.006864995718212008, -0.005955396965794746, 0.001171527394955791]
# fish_image_path = r"D:\Desktop\BasicProject\毛岩\头条\20220620164301\20220620164301\3d_img0\LNWM000001_20220620164301_image_00000.jpg"
# save_image_path = r"D:\Desktop\BasicProject\毛岩\头条\20220620164301\new-LNWM000001_20220620164301_image_00000.jpg"
# fish_eye_to_normal_image(camera_internal, camera_D, fish_image_path, save_image_path)