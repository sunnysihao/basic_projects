import os
import json
import numpy as np
from tqdm import tqdm


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.pcd':
                file_list.append(os.path.join(root, file))
    return file_list


cam_ext_n = np.array([[-0.9998804433808629, -0.009246969554653978, -0.012393244068625105, 0.14300159613520116],
             [0.012186398365472181, 0.02209971325761133, -0.9996814964621532, -0.6750056039358172],
             [0.009517911502384672, -0.9997130069314828, -0.021984383835943862, -0.9549963628302615],
             [0.0, 0.0, 0.0, 1.0]]).T

cam_ext_w = np.array([[-0.9972817079920098, -0.06623422502447494, -0.032283468524105734, -0.27999547619159015],
             [0.031458761235835235, 0.013457060601827057, -0.9994144554995517, -0.7129974429695398],
             [0.06662988253063652, -0.9977133531006618, -0.01133683371085651, -0.9750004274292101],
             [0.0, 0.0, 0.0, 1.0]]).T
data = {
    "3d_img0": {
        "camera_internal": {
        "fx": 7384.70361328125,
        "fy": 7384.70361328125,
        "cx": 2013.9853515625,
        "cy": 1211.111083984375
    },
        "camera_external": cam_ext_n.flatten().tolist()
  },
    "3d_img1": {
        "camera_internal": {
            "fx": 1855.5054931640625,
            "fy": 1866.17431640625,
            "cx": 1922.6373291015625,
            "cy": 1110.877685546875
        },
        "camera_external": cam_ext_w.flatten().tolist()
  }
}


def set_config(pcd_path: str):
    for file in tqdm(list_files(pcd_path)):
        json_file = file.replace('.pcd', '.json').replace('pcd', 'camera_config')
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
