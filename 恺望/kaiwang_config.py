# _*_ coding=: utf-8 _*_
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
    t = np.array([x, y, z]).reshape((3, 1))
    r = R.from_quat([rx, ry, rz, w]).as_matrix()
    cam_ext = np.hstack((r, t))
    cam_ext = np.vstack((cam_ext, row))
    cam_ext = cam_ext

    img = {
        "camera_internal": camera_internal,
        "camera_external": cam_ext.flatten().tolist()
    }
    return img


in_list0 = [1965.8002929, 934.8499755, 1968.1374511, 533.8405151]
ext_list0 = [0.0115900288253539, -1.16320525032802, -0.102850359844642,
             -0.010862912275385597, 0.7121132102372025, -0.7018351451097646, 0.014289927617682793]
img0 = get_cam_config(in_list0, ext_list0)

in_list1 = [962.596130371094, 967.387268066406, 960.4140625, 561.550354003906]
ext_list1 = [0.0307674525980687, 0.705856192907587, -0.412476297892775,
             0.7266562079396163, 0.006482653399297765, -0.0017229835991964607, -0.6869685305712617]
img1 = get_cam_config(in_list1, ext_list1)

in_list2 = [5240.956, 982.21576, 5248.1108, 474.3055]
ext_list2 = [-0.0186139321610589, 0.691479555969436, -0.344990173135634,
             0.71663853226928, 0.0073808258712575485, -0.0036631633331418224, -0.6973960988640424]
img2 = get_cam_config(in_list2, ext_list2)

in_list3 = [959.021606445312, 966.002258300781, 956.644897460938, 565.31298828125]
ext_list3 = [-0.929882992462762, 0.831947148359441, -0.725745174983317,
             0.6821828922293315, 0.2409070793960913, -0.2774618759065646, -0.6321433287355644]
img3 = get_cam_config(in_list3, ext_list3)

in_list4 = [960.546752929688, 970.816772460938, 958.115600585938, 551.124633789062]
ext_list4 = [-0.906111044556051, 1.14912078655794, -0.971412683330519,
             0.3061743584888434, 0.6503978492194252, -0.6277999402776966, -0.29850818233678555]
img4 = get_cam_config(in_list4, ext_list4)

in_list5 = [965.971496582031, 981.216247558594, 963.780822753906, 570.459899902344]
ext_list5 = [0.77425580124057, 1.24638576919953, -1.04062158761967,
             -0.30399206875981455, 0.6510639522727106, -0.6275765421528995, 0.2997536253685277]
img5 = get_cam_config(in_list5, ext_list5)

in_list6 = [955.094909667969, 985.855712890625, 953.324340820312, 554.322998046875]
ext_list6 = [0.836089070080024, 0.867663494840816, -0.521764412672669,
             0.6500303264784554, -0.3208493157548192, 0.3271042562674439, -0.6062335331946753]
img6 = get_cam_config(in_list6, ext_list6)

data = {
            "3d_img0": img0,
            "3d_img1": img1,
            "3d_img2": img2,
            "3d_img3": img3,
            "3d_img4": img4,
            "3d_img5": img5,
            "3d_img6": img6
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


pcd_path = r"D:\Desktop\BasicProject\毛岩\恺望\恺望试标数据\3d_url"
config_path = r"D:\Desktop\BasicProject\毛岩\恺望\恺望试标数据\camera_config"
set_config(pcd_path, config_path)
