# _*_ coding=: utf-8 _*_
import os
import json
from scipy.spatial.transform import Rotation as R
import numpy as np
from numpy.linalg import inv


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0].split('.')[0]
            file_list.append(file_name)
    return file_list

def load_json(json_path:str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content

def get_param(json_parameter_file):
    json_content = load_json(json_parameter_file)
    params = []
    for param in json_content:
        p = list(param['position'].values())
        #p = [0, 0, 0]
        pos = np.asarray(p).reshape((3, 1))
        w, x, y, z = param['heading'].values()
        r = R.from_quat([x, y, z, w]).as_matrix()
        cam_ext = np.hstack((r, pos))
        t = np.asarray([[0, 0, 0, 1]])
        cam_external =np.vstack((cam_ext, t))
        params.append(cam_external)
    return params


def write_param(name_path, config_path):
    cam_ext0_list = get_param(r"D:\Desktop\BasicProject\任从辉\pkl数据集\ideastoimpacts\002\camera\left_camera\poses.json")
    cam_ext1_list = get_param(r"D:\Desktop\BasicProject\任从辉\pkl数据集\ideastoimpacts\002\camera\front_right_camera\poses.json")
    cam_ext2_list = get_param(r"D:\Desktop\BasicProject\任从辉\pkl数据集\ideastoimpacts\002\camera\front_camera\poses.json")
    cam_ext3_list = get_param(r"D:\Desktop\BasicProject\任从辉\pkl数据集\ideastoimpacts\002\camera\front_right_camera\poses.json")
    cam_ext4_list = get_param(r"D:\Desktop\BasicProject\任从辉\pkl数据集\ideastoimpacts\002\camera\right_camera\poses.json")
    cam_ext5_list = get_param(r"D:\Desktop\BasicProject\任从辉\pkl数据集\ideastoimpacts\002\camera\back_camera\poses.json")

    lidar_ext_list = get_param(r"D:\Desktop\BasicProject\任从辉\pkl数据集\ideastoimpacts\002\json\poses.json")

    for i in range(len(cam_ext0_list)):
        cam_ext0 = inv(cam_ext0_list[i])
        cam_ext1 = inv(cam_ext1_list[i])
        cam_ext2 = inv(cam_ext2_list[i])
        cam_ext3 = inv(cam_ext3_list[i])
        cam_ext4 = inv(cam_ext4_list[i])
        cam_ext5 = inv(cam_ext5_list[i])
        lidar_ext = np.eye(4)#lidar_ext_list[i]
        camera_external0 = inv(cam_ext0 @ lidar_ext).flatten().tolist()
        camera_external1 = inv(cam_ext1 @ lidar_ext).flatten().tolist()
        camera_external2 = inv(cam_ext2 @ lidar_ext).flatten().tolist()
        camera_external3 = inv(cam_ext3 @ lidar_ext).flatten().tolist()
        camera_external4 = inv(cam_ext4 @ lidar_ext).flatten().tolist()
        camera_external5 = inv(cam_ext5 @ lidar_ext).flatten().tolist()

        data = {
            "3d_img0": {
                "camera_internal": {
                    "fx": 930.4514,
                    "cx": 991.6883,
                    "cy": 541.6057,
                    "fy": 930.0891
                },
                "camera_external": camera_external0
            },
            "3d_img1": {
                "camera_internal": {
                    "fx": 929.8429,
                    "cx": 972.1794,
                    "cy": 508.0057,
                    "fy":  930.0592
                },
                "camera_external": camera_external1
            },
            "3d_img2": {
                "camera_internal": {
                    "fx": 1970.0131,
                    "cx": 970.0002,
                    "cy": 483.2988,
                    "fy": 1970.0091
                },
                "camera_external": camera_external2
            },
            "3d_img3": {
                "camera_internal": {
                    "fx": 930.0407,
                    "cx": 965.0525,
                    "cy": 463.4161,
                    "fy": 930.0324
                },
                "camera_external": camera_external3
            },
            "3d_img4": {
                "camera_internal": {
                    "fx": 922.5465,
                    "cx": 945.057,
                    "cy": 517.575,
                    "fy": 922.4229
                },
                "camera_external": camera_external4
            },
            "3d_img5": {
                "camera_internal": {
                    "fx": 933.4667,
                    "cx": 896.4692,
                    "cy": 507.3557,
                    "fy": 934.6754
                },
                "camera_external": camera_external5
            }
        }
        file = list_files(name_path)[i]
        with open(os.path.join(config_path, file + '.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps(data))

if __name__ == "__main__":
    pkl_path = r"D:\Desktop\BasicProject\任从辉\pkl数据集\ideastoimpacts\002\annotations\cuboids"  #.pkl.gz文件路径
    config_path = r"D:\Desktop\BasicProject\任从辉\pkl数据集\config"  #camera_config路径
    write_param(pkl_path, config_path)

