# _*_ coding=: utf-8 _*_
import os
import json
import numpy as np
from tqdm import tqdm
from numpy.linalg import inv
from scipy.spatial.transform import Rotation as R


def list_files(in_path: str, suffix_match):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == suffix_match:
                file_list.append(os.path.join(root, file))
    return file_list


def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content

def parse_param(jd):
    cam_parame = load_json(r"D:\Desktop\Project_file\郭章程\纽劢\4D-sample\4D-sample\intrin_extrin_params.json")
    param = cam_parame[jd]
    internal = param['camera_internal']
    cam_in = {
        "fx": internal['fx'],
        "fy": internal['fy'],
        "cx": internal['cx'],
        "cy": internal['cy']
    }
    cam_ext = np.array(param['camera_external']).flatten().tolist()

    data = {
        "camera_internal": cam_in,
        "camera_external": cam_ext
    }
    return data




def set_config(pcd_path: str):
    img0 = parse_param('FrontMiddle_120')
    img1 = parse_param('RearMiddle_60')
    img2 = parse_param('SideFrontLeft')
    img3 = parse_param('SideFrontRight')
    img4 = parse_param('SideRearLeft')
    img5 = parse_param('SideRearRight')

    data = {
        "3d_img0": img0,
        "3d_img1": img1,
        "3d_img2": img2,
        "3d_img3": img3,
        "3d_img4": img4,
        "3d_img5": img5
    }
    for file in tqdm(list_files(pcd_path, '.pcd')):
        json_file = file.replace('.pcd', '.json').replace('3d_url', 'camera_config')
        if not os.path.exists(os.path.dirname(json_file)):
            os.makedirs(os.path.dirname(json_file))
        with open(json_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(data))
    # print(f"----------------------------------\n输出文件在{config_path}")


def main():
    pcd_path = input("请输入pcd点云文件路径:\n")
    while not os.path.exists(pcd_path):
        print(f"=====>路径错误,请重新输入:")
        pcd_path = input()
    else:
        set_config(pcd_path)
        input("已完成， 按任意键退出")

def rename_file(total_path, img_dir):
    pcd_path = os.path.join(total_path, '3d_url')
    img_path = os.path.join(total_path, img_dir)
    pcds = list_files(pcd_path, '.pcd')
    imgs = list_files(img_path, '.json')
    for i in tqdm(range(len(pcds))):
        pcd_file = pcds[i]
        img_file = imgs[i]
        file_name = os.path.splitext(os.path.basename(pcd_file))[0]
        new_img = os.path.join(img_path, file_name + '.json')
        os.rename(img_file, new_img)




if __name__ == "__main__":

    # main()
    total_path = r"D:\Desktop\Project_file\郭章程\纽劢\4D-sample\4D-sample"
    # img_dirs = ['3d_img0', '3d_img1', '3d_img2', '3d_img3', '3d_img4', '3d_img5']
    # for img_dir in img_dirs:
    #     rename_file(total_path, img_dir)
    rename_file(total_path, 'label')
