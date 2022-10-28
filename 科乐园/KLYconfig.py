# _*_ coding=: utf-8 _*_
import os
import json
import numpy as np
from numpy.linalg import inv
from scipy.spatial.transform import Rotation as R


def get_cam_config(in_list, ext_list):
    fx, cx, fy, cy = in_list
    camera_internal = {
        "fx": fx,
        "cx": cx,
        "cy": cy,
        "fy": fy
    }
    x, y, z, rx, ry, rz, w = ext_list
    row = [[0, 0, 0, 1]]
    t = np.array([-x, -y, -z]).reshape((3, 1))
    r = R.from_quat([rx, ry, rz, w]).as_matrix()
    cam_ext = np.hstack((r, t))
    cam_ext = np.vstack((cam_ext, row))
    # cam_ext = inv(cam_ext.T)

    img = {
        "camera_internal": camera_internal,
        "camera_external": cam_ext.flatten().tolist()
    }
    return img


def get_cam_config4(in_list, ext_list):
    fx, cx, fy, cy = in_list
    camera_internal = {
        "fx": fx,
        "cx": cx,
        "cy": cy,
        "fy": fy
    }
    x, y, z, rx, ry, rz, w = ext_list
    row = [[0, 0, 0, 1]]
    t = np.array([-x, -y, -z]).reshape((3, 1))
    r = R.from_quat([rx, ry, rz, w]).as_matrix()
    cam_ext = np.hstack((r, t))
    cam_ext = np.vstack((cam_ext, row))
    cam_ext = inv(cam_ext)

    img = {
        "camera_internal": camera_internal,
        "camera_external": cam_ext.flatten().tolist()
    }
    return img


def get_cam_config5(in_list, ext_list):
    fx, cx, fy, cy = in_list
    camera_internal = {
        "fx": fx,
        "cx": cx,
        "cy": cy,
        "fy": fy
    }
    x, y, z, rx, ry, rz, w = ext_list
    row = [[0, 0, 0, 1]]
    t = np.array([-x, -y, -z]).reshape((3, 1))
    r = R.from_quat([rx, ry, rz, w]).as_matrix()
    cam_ext = np.hstack((r, t))
    cam_ext = np.vstack((cam_ext, row))
    # cam_ext = inv(cam_ext)

    img = {
        "camera_internal": camera_internal,
        "camera_external": cam_ext.flatten().tolist()
    }
    return img

in_list0 = [1004.998550, 941.932659, 1006.636683, 489.066076]
ext_list0 = [-0.324091958, 1.142937350, -1.892258221, -0.479355, 0.413391, -0.504741, 0.586995]
img0 = get_cam_config(in_list0, ext_list0)

in_list1 = [1015.572966, 967.256768, 1018.109118, 526.733231]
ext_list1 = [-0.792697852, 1.062722957, -1.444306570, -0.6644, 0.252999, -0.280623, 0.644837]
img1 = get_cam_config(in_list1, ext_list1)

in_list2 = [1019.273400, 953.415737, 1022.102958, 488.271551]
ext_list2 = [-2.095355681, 0.968610217, -1.328715374, -0.691689, -0.295168, 0.305431, 0.584084]
img2 = get_cam_config(in_list2, ext_list2)

# in_list3 = [1015.484077, 948.357658, 1018.473587, 495.930854]
# ext_list3 = [-1.064925781, 0.00643384, 1.079256836, 0.584448, 0.597907, -0.391746, 0.384009]
# img3 = get_cam_config(in_list3, ext_list3)

in_list4 = [1009.285256, 993.082226, 1011.111006, 498.692282]
ext_list4 = [2.047400266, 1.026643841, 0.111049355, 0.243929, 0.685425, -0.635714, -0.257991]
img4 = get_cam_config5(in_list4, ext_list4)

in_list5 = [1006.697620, 933.560809, 1009.198074, 507.401347]
ext_list5 = [2.106157227, -0.803435852, 0.824464294, -0.271829, 0.685407, -0.629719, -0.244502]
img5 = get_cam_config4(in_list5, ext_list5)


img3 = {
    "camera_internal": {
      "fx": 1015.484077,
      "fy": 1018.473587,
      "cx": 948.357658,
      "cy": 495.930854
    },
    "camera_external": [
      -0.02189125334656028,
      0.38296771088492459,
      -0.92350230397464561,
      -0.96390209616094114,
      0.99975899417071479,
      0.0099112986581244584,
      -0.019588765496345865,
      -1.0857466690399959,
      0.0016512424649612889,
      -0.923708557164256,
      -0.38309238418409131,
      0.89401380989845114,
      0,
      0,
      0,
      1
    ]
}

data = {
            "3d_img0": img0,
            "3d_img1": img1,
            "3d_img2": img2,
            "3d_img3": img3,
            "3d_img4": img5,
            "3d_img5": img4
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


pcd_path = r"D:\Desktop\BasicProject\柴碧波\baidu\KLY_baidu试标数据\3d_url"
config_path = r"D:\Desktop\BasicProject\柴碧波\baidu\KLY_baidu试标数据\camera_config"
set_config(pcd_path, config_path)
