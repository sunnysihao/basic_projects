# _*_ coding=: utf-8 _*_
import os
import json
import re
import numpy as np
from scipy.spatial.transform import Rotation as R
from numpy.linalg import inv


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list



def rename_image(pcd_path, image_dir):
    for file in list_files(pcd_path):
        image_path = os.path.join(image_dir, file)
        for img_file in list_files(image_path):
            if re.findall('lf', img_file):
                os.rename(os.path.join(image_path, img_file + '.jpg'),
                          os.path.join(os.path.dirname(pcd_path), '3d_img0', file + '.jpg'))
            elif re.findall('front', img_file):
                os.rename(os.path.join(image_path, img_file + '.jpg'),
                          os.path.join(os.path.dirname(pcd_path), '3d_img1', file + '.jpg'))
            elif re.findall('rf', img_file):
                os.rename(os.path.join(image_path, img_file + '.jpg'),
                          os.path.join(os.path.dirname(pcd_path), '3d_img2', file + '.jpg'))
            elif re.findall('rr', img_file):
                os.rename(os.path.join(image_path, img_file + '.jpg'),
                          os.path.join(os.path.dirname(pcd_path), '3d_img3',file + '.jpg'))
            elif re.findall('rear', img_file):
                os.rename(os.path.join(image_path, img_file + '.jpg'),
                          os.path.join(os.path.dirname(pcd_path), '3d_img4', file + '.jpg'))
            else:
                os.rename(os.path.join(image_path, img_file + '.jpg'),
                          os.path.join(os.path.dirname(pcd_path), '3d_img5', file + '.jpg'))

# rps = requests.get("https://bucket-dataengine.oss-cn-beijing.aliyuncs.com/release%2Fbundle%2Fcenter_128_lidar-8_camera%2Fhardwire_config%2Ficu30%2FHP-30-V71-AC-021%2F1649928594353822.json?Expires=1661070754&OSSAccessKeyId=LTAI4G1SJVrLv4JXiJTShuLq&Signature=TWW7LJFRl1B1HcD84SyIDJLzv1A%3D")
# json_data = rps.json()
# cam_param = json_data['sensor_config']['cam_param']
# lidar_param = json_data['sensor_config']['lidar_param']
# cam_r0 = cam_param[4]['pose']['attitude']

def create_external(translation_list: list, rotation_list: list):
    row = [[0, 0, 0, 1]]
    cam_r = R.from_quat(rotation_list).as_matrix()
    cam_t = np.array(translation_list).reshape((3, 1))
    cam_ext = np.hstack((cam_r, cam_t))
    cam_ext = np.vstack((cam_ext, row))
    return cam_ext

row = [[0, 0, 0, 1]]

lidar_r = [-0.001658200053498149, -0.00693550007417798, 0.7055191993713379, 0.7086549401283264]
lidar_t = [1.1799999475479126, 0, 1.7312175035476685]
lidar_ext = create_external(lidar_t, lidar_r)

cam_r0 = [-0.6488929986953735, 0.26866060495376587, -0.2716994285583496, 0.6579808592796326]
cam_t0 = [2.666929244995117, 1.034934639930725, 0.6732346415519714]
cam_ext0 = inv(create_external(cam_t0, cam_r0)) @ lidar_ext


cam_r1 = [-0.48309552669525146, 0.485343337059021, -0.5161051750183105, 0.5144861936569214]
cam_t1 = [2.1321001052856445, 0.02004058286547661, 1.2012841701507568]
# cam_t1 = np.array([[0], [0], [0]])
cam_ext1 = inv(create_external(cam_t1, cam_r1)) @ lidar_ext

cam_r2 = [0.2719002664089203, -0.6466688513755798, 0.6553577184677124, -0.2799926698207855]
cam_t2 = [2.6686551570892334, -0.9747444987297058, 0.660169780254364]
# cam_t2 = np.array([[0], [0], [0]])
cam_ext2 = inv(create_external(cam_t2, cam_r2)) @ lidar_ext
# cam_ext2 = inv(arr @ cam_ext2 @ lidar_ext).flatten().tolist()

cam_r3 = [0.2617827355861664, 0.6562781929969788, -0.6552519798278809, -0.2672331929206848]
cam_t3 = [2.4667441844940186, -0.9693453907966614, 0.5781583786010742]
# cam_t3 = np.array([[0], [0], [0]])
cam_ext3 = inv(create_external(cam_t3, cam_r3)) @ lidar_ext
# cam_ext3 = inv(arr @ cam_ext3 @ lidar_ext).flatten().tolist()

cam_r4 = [-0.5044846534729004, -0.5063685178756714, 0.48851117491722107, 0.5004427433013916]
cam_t4 = [ -0.46634215116500854, 0.08111245185136795, 1.3251941204071045]
# cam_t4 = np.array([[0], [0], [0]])
cam_ext4 = inv(create_external(cam_t4, cam_r4)) @ lidar_ext
# # cam_ext4 = inv(cam_ext4 @ lidar_ext).flatten().tolist()

cam_r5 = [-0.6526867151260376, -0.27093011140823364, 0.2644702196121216, 0.6562411189079285]
cam_t5 = [2.5473127365112305, 1.0652567148208618, 0.6394416093826294]
# cam_t5 = np.array([[0], [0], [0]])
cam_ext5 = inv(create_external(cam_t5, cam_r5)) @ lidar_ext
# # cam_ext5 = inv(arr @ cam_ext5 @ lidar_ext).flatten().tolist()



data = {
            "3d_img0": {
                "camera_internal": {
                    "fx": 1295.38720703125,
                    "cx": 973.1076049804688,
                    "cy": 570.2665405273438,
                    "fy": 1296.8865966796875
                },
                "camera_external": cam_ext0.T.flatten().tolist()
            },
            "3d_img1": {
                "camera_internal": {
                    "fx": 1977.1912841796875,
                    "cx": 987.43408203125,
                    "cy": 516.2479248046875,
                    "fy": 1977.8699951171875
                },
                "camera_external": cam_ext1.T.flatten().tolist()
            },
            "3d_img2": {
                "camera_internal": {
                    "fx": 1297.7847900390625,
                    "cx": 977.130615234375,
                    "cy": 523.7313842773438,
                    "fy": 1297.802490234375,
                },
                "camera_external": cam_ext2.T.flatten().tolist()
            },
            "3d_img3": {
                "camera_internal": {
                    "fx": 1292.692138671875,
                    "cx": 941.2689208984375,
                    "cy": 585.5317993164062,
                    "fy": 1293.5633544921875
                },
                "camera_external": cam_ext3.T.flatten().tolist()
            },
            "3d_img4": {
                "camera_internal": {
                    "fx": 1970.1702880859375,
                    "cx": 981.0914306640625,
                    "cy": 508.4887390136719,
                    "fy": 1971.5650634765625
                },
                "camera_external": cam_ext4.T.flatten().tolist()
            },
            "3d_img5": {
                "camera_internal": {
                    "fx": 1303.0411376953125,
                    "cx": 960.9192504882812,
                    "cy": 574.3096923828125,
                    "fy": 1302.9664306640625,
                },
                "camera_external": cam_ext5.T.flatten().tolist()
            }
        }

def write_json(pcd_path, config_path):
    for file in list_files(pcd_path):
        with open(os.path.join(config_path, file + '.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps(data))

if __name__ == "__main__":
    pcd_path = r"D:\Desktop\BasicProject\任从辉\毫末\毫末\3d_url"
    image_dir = r"D:\Desktop\BasicProject\任从辉\毫末\3.0原图\3.0原图"
    config_path = r"D:\Desktop\BasicProject\任从辉\毫末\毫末\new_config"
    # rename_image(pcd_path, image_dir)
    write_json(pcd_path, config_path)
