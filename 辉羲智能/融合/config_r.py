# _*_ coding=: utf-8 _*_
import os
import json
import numpy as np
from tqdm import tqdm
from numpy.linalg import inv
from scipy.spatial.transform import Rotation as R


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.pcd':
                file_list.append(os.path.join(root, file))
    return file_list


def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


cam_parame = load_json(r"D:\Desktop\BasicProject\季鑫窈\辉曦智能\calibration_beisai_8171_0929.json")
img0 = cam_parame['3d_img0']
img1 = cam_parame['3d_img1']
img2 = cam_parame['3d_img2']
img4 = cam_parame['3d_img4']
img6 = cam_parame['3d_img6']

img3 = cam_parame['3d_img3']
cx_3 = 3840 - img3['camera_internal']['cx']
cy_3 = 2160 - img3['camera_internal']['cy']
img3_ext = np.array(img3['camera_external']).reshape(4, 4)
rot = R.from_euler('z', np.pi).as_matrix()
t1 = np.array([0, 0, 0]).reshape(3, 1)
t2 = np.array([0, 0, 0, 1]).reshape(1, 4)
rot = np.hstack((rot, t1))
rot = np.vstack((rot, t2))
img3_ext = rot @ img3_ext
img3['camera_internal']['cx'] = cx_3
img3['camera_internal']['cy'] = cy_3
img3['camera_external'] = img3_ext.flatten().tolist()

img5 = cam_parame['3d_img5']
cx_5 = 3840 - img5['camera_internal']['cx']
cy_5 = 2160 - img5['camera_internal']['cy']
img5_ext = np.array(img5['camera_external']).reshape(4, 4)
img5_ext = rot @ img5_ext
img5['camera_internal']['cx'] = cx_5
img5['camera_internal']['cy'] = cy_5
img5['camera_external'] = img5_ext.flatten().tolist()

data = {
    "3d_img0": img0,
    "3d_img1": img1,
    "3d_img2": img2,
    "3d_img3": img3,
    "3d_img4": img4,
    "3d_img5": img5,
    "3d_img6": img6
}


def set_config(pcd_path: str):
    for file in tqdm(list_files(pcd_path)):
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

if __name__ == "__main__":

    main()
