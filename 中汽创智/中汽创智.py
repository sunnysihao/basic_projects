# _*_ coding=: utf-8 _*_
import os
import json
import numpy as np
from numpy.linalg import inv


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list


def create_external(cam_ext):
    cam_ext = inv(inv(cam_ext)).T
    # cam_ext = inv(cam_ext)
    return cam_ext


cam0 = np.array([[0.62664706, -0.7792481, -0.00927216, -0.7004834],
                 [0.01732562, 0.02582582, -0.9995163, 1.3687056],
                 [0.77911067, 0.6261832, 0.02968462, -1.7834119],
                 [0,          0,           0,           1     ]])
cam_ext0 = create_external(cam0)

cam1 = np.array([[3.5275958e-02, -9.9935186e-01, -7.1838102e-03, -1.8662055e-01],
                 [1.8876614e-03, 7.2548999e-03, -9.9997193e-01, 1.5947640e+00],
                 [9.9937582e-01, 3.5261404e-02,  2.1423604e-03, -2.2961266e+00],
                 [0.0000000e+00, 0.0000000e+00,  0.0000000e+00, 1.0000000e+00]])
cam_ext1 = create_external(cam1)

cam2 = np.array([[-0.6377395, -0.77003396, 0.01833395, 0.7158891 ],
                 [0.02324471, -0.04303197, -0.99880326, 1.3636765 ],
                 [0.7699014, -0.6365501, 0.0453424, -1.7965411 ],
                 [0,          0,          0,          1         ]])
cam_ext2 = create_external(cam2)

cam3 = np.array([[0.01882715, -0.99939436, -0.02926579, 0.09263456],
                 [0.02517312, 0.02973552, -0.9992408,  1.4351026 ],
                 [0.9995058, 0.01807615, 0.02571771, -1.9826291 ],
                 [0,          0,         0,          1        ]])
cam_ext3 = create_external(cam3)

cam4 = np.array([[0.7514312, 0.6497577, -0.11474427, 0.16818228],
                 [-0.052101, -0.11493013, -0.99200636, 1.313457],
                 [-0.65775126, 0.7514028, -0.05250905, -0.70640373],
                 [0,         0,          0,          1        ]])
cam_ext4 = create_external(cam4)

cam5 = np.array([[-0.78065246, 0.6119089, 0.12707958, -0.15781535],
                 [-0.06207412, 0.12641537, -0.99003327, 1.2983483],
                 [-0.62187505, -0.7807603, -0.06070276, -0.7363976],
                 [0,           0,          0,           1       ]])
cam_ext5 = create_external(cam5)


data = {
            "3d_img0": {
                "camera_internal": {
                    "fx": 961.77594733070407,
                    "cx": 974.61840251373656,
                    "cy": 552.96591030571460,
                    "fy": 960.99392883769042
                },
                "camera_external": cam_ext0.flatten().tolist()
            },
            "3d_img1": {
                "camera_internal": {
                    "fx": 3844.404756,
                    "cx": 974.434366,
                    "cy": 574.655941,
                    "fy": 3837.868761
                },
                "camera_external": cam_ext1.flatten().tolist()
            },
            "3d_img2": {
                "camera_internal": {
                    "fx": 957.37211215005243,
                    "cx": 970.54266294365800,
                    "cy": 495.45835769900037,
                    "fy": 957.67352223614478
                },
                "camera_external": cam_ext2.flatten().tolist()
            },
            "3d_img3": {
                "camera_internal": {
                    "fx": 959.788106,
                    "cx": 1027.95138,
                    "cy": 512.57296788,
                    "fy": 960.26769
                },
                "camera_external": cam_ext3.flatten().tolist()
            },
            "3d_img4": {
                "camera_internal": {
                    "fx": 948.15778248884362,
                    "cx": 976.65931835371475,
                    "cy": 473.01344232244276,
                    "fy": 949.02380470323703
                },
                "camera_external": cam_ext4.flatten().tolist()
            },
            "3d_img5": {
                "camera_internal": {
                    "fx": 955.49811291895389,
                    "cx": 950.21978716305557,
                    "cy": 540.42829047797034,
                    "fy": 956.66659049535383
                },
                "camera_external": cam_ext5.flatten().tolist()
            }
        }


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


def write_json(pcd_path, config_path):
    for file in list_files(pcd_path):
        with open(os.path.join(config_path, file + '.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps(data))


if __name__ == "__main__":
    pcd_path = r"D:\Desktop\BasicProject\王满顺\中汽创智\3d_url"
    config_path = r"D:\Desktop\BasicProject\王满顺\中汽创智\camera_config"
    # write_json(pcd_path, config_path)
    write_single_config(pcd_path, config_path, 6)

