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


def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


# cam_ext_n = np.array([[-0.9998804433808629, -0.009246969554653978, -0.012393244068625105, 0.14300159613520116],
#              [0.012186398365472181, 0.02209971325761133, -0.9996814964621532, -0.6750056039358172],
#              [0.009517911502384672, -0.9997130069314828, -0.021984383835943862, -0.9549963628302615],
#              [0.0, 0.0, 0.0, 1.0]]).T
#
# cam_ext_w = np.array([[-0.9972817079920098, -0.06623422502447494, -0.032283468524105734, -0.27999547619159015],
#              [0.031458761235835235, 0.013457060601827057, -0.9994144554995517, -0.7129974429695398],
#              [0.06662988253063652, -0.9977133531006618, -0.01133683371085651, -0.9750004274292101],
#              [0.0, 0.0, 0.0, 1.0]]).T

jc = load_json(r"D:\Data\we_chat_files\WeChat Files\wxid_pzn3n31pjyvc29\FileStorage\File\2022-11\lidar_2_camera_from_8th.json")
cam_ext_n = np.array(jc['image_n']['l2c_matrix'])
cam_ext_w = np.array(jc['image_w']['l2c_matrix'])

data = {
    "3d_img0": {
        "camera_internal": {
        "fx": 7389.27392578125,
        "fy": 7389.27392578125,
        "cx": 1976.8890380859375,
        "cy": 1107.0076904296875
        },
        "camera_external": cam_ext_n.flatten().tolist()
    },
    "3d_img1": {
        "camera_internal": {
            "fx": 1862.576904296875,
            "fy": 1862.576904296875,
            "cx": 1928.728271484375,
            "cy": 1094.4244384765625
        },
        "camera_external": cam_ext_w.flatten().tolist()
    }
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
