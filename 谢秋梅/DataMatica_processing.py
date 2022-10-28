# _*_ coding=: utf-8 _*_
import json
import os
import re
import numpy as np
from tqdm import tqdm
from PIL import Image
from numpy.linalg import inv
from scipy.spatial.transform import Rotation as R


def list_files(in_path: str, suffix_match: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == f'.{suffix_match}':
                file_list.append(os.path.join(root, file))
            else:
                continue
    return file_list


def create_imgdir(in_path: str, num: int):
    new_cam_path = os.path.join(os.path.dirname(in_path), 'upload data package', f'3d_img{num}')
    if not os.path.exists(new_cam_path):
        os.makedirs(new_cam_path)
    return new_cam_path


def rename_image(in_path: str):
    new_cam_path0 = create_imgdir(in_path, 0)
    new_cam_path1 = create_imgdir(in_path, 1)
    new_cam_path2 = create_imgdir(in_path, 2)
    new_cam_path3 = create_imgdir(in_path, 3)
    new_cam_path4 = create_imgdir(in_path, 4)
    original_camera_path = os.path.join(in_path, 'sensor_raw_data', 'camera')
    for original_img_file in tqdm(list_files(original_camera_path, 'jpg'), desc='rename image'):
        original_file_name = os.path.basename(original_img_file)
        if re.findall(re.compile('[_]front'), original_file_name):
            new_file_name = original_file_name.replace('front', 'lidar')
            new_file = os.path.join(new_cam_path0, new_file_name)
            os.rename(original_img_file, new_file)
        elif re.findall('leftfront', original_file_name):
            new_file_name = original_file_name.replace('leftfront', 'lidar')
            new_file = os.path.join(new_cam_path1, new_file_name)
            os.rename(original_img_file, new_file)
        elif re.findall('leftrear', original_file_name):
            new_file_name = original_file_name.replace('leftrear', 'lidar')
            new_file = os.path.join(new_cam_path2, new_file_name)
            iml = Image.open(original_img_file)
            outl = iml.transpose(Image.FLIP_LEFT_RIGHT)
            outl.save(new_file)
        elif re.findall('rightfront', original_file_name):
            new_file_name = original_file_name.replace('rightfront', 'lidar')
            new_file = os.path.join(new_cam_path3, new_file_name)
            os.rename(original_img_file, new_file)
        elif re.findall('rightrear', original_file_name):
            new_file_name = original_file_name.replace('rightrear', 'lidar')
            new_file = os.path.join(new_cam_path4, new_file_name)
            imr = Image.open(original_img_file)
            outr = imr.transpose(Image.FLIP_LEFT_RIGHT)
            outr.save(new_file)
        else:
            print(f"err file name {original_img_file}")


def load_json(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def get_cam_in(json_content: dict, obj: str):
    intrinsic = json_content[f'{obj}']['Intrinsic']
    fx = intrinsic['Fx']
    fy = intrinsic['Fy']
    cx = intrinsic['Cx']
    cy = intrinsic['Cy']
    cam_in = {
        "fx": fx,
        "cx": cx,
        "cy": cy,
        "fy": fy
    }
    return cam_in

def get_cam_ext(json_content: dict, obj: str):
    extric = json_content[f'{obj}']['Extrinsic']
    tx = extric['Tx']
    ty = extric['Ty']
    tz = extric['Tz']
    rx = extric['Rx']
    ry = extric['Ry']
    rz = extric['Rz']
    # rx = extric['Rx']*(math.pi/180)
    # ry = extric['Ry']*(math.pi/180)
    # rz = extric['Rz']*(math.pi/180)

    r = R.from_euler('xyz', [rx, rz, ry], degrees=True).as_matrix()
    vec = np.array([0, 0, 0, 1])
    t = np.array([-tx, -ty, -tz]).reshape((3, 1))
    d = np.array([[0, -1, 0, 0],
                  [0, 0, -1, 0],
                  [1, 0, 0, 0],
                  [0, 0, 0, 1]])
    ext = np.hstack((r, t))
    cam_ext = inv(np.vstack((ext, vec)) @ d)
    return cam_ext.flatten().tolist()



def create_config_file(in_path: str):
    # config_json = os.path.join(in_path, 'calibration.json')
    # json_content = load_json(config_json)['camera']
    # cam_in0 = get_cam_in(json_content, 'front')
    # cam_in1 = get_cam_in(json_content, 'left_front')
    # cam_in2 = get_cam_in(json_content, 'left_rear')
    # cam_in3 = get_cam_in(json_content, 'right_front')
    # cam_in4 = get_cam_in(json_content, 'right_rear')
    # cam_ext0 = get_cam_ext(json_content, 'front')
    # cam_ext1 = get_cam_ext(json_content, 'left_front')
    # cam_ext2 = get_cam_ext(json_content, 'left_rear')
    # cam_ext3 = get_cam_ext(json_content, 'right_front')
    # cam_ext4 = get_cam_ext(json_content, 'right_rear')
    data = {
        "3d_img0": {
            "camera_internal": {
                "fx": 500.3176269531,
                "fy": 498.1853027344,
                "cx": 320.4075927734,
                "cy": 180.5059814453
            },
            "camera_external": [
                -0.21941598253242761,
                0.0053147863405824695,
                0.97561692259589483,
                1.3500467114598333,
                -0.97549407287113687,
                0.01558237814953279,
                -0.21947324047474848,
                0.40526506027572695,
                -0.016368885197571185,
                -0.99986446208341673,
                0.0017655197619432799,
                1.4706177025607547,
                0,
                0,
                0,
                1
            ]
        },
        "3d_img1": {
            "camera_internal": {
                "fx": 150.6765136719,
                "fy": 149.7344970703,
                "cx": 160.0305786133,
                "cy": 90.5824584961
            },
            "camera_external": [
                0.981263365079543,
                -0.019729307183699446,
                0.19165845348124555,
                -1.63066721506825,
                -0.19098120829481086,
                0.03186646562731088,
                0.98107630001273494,
                1.3560728664279411,
                -0.025463433213642125,
                -0.9992973945760466,
                0.027501468369884208,
                0.985734172870582,
                0,
                0,
                0,
                1
            ]
        },
        "3d_img2": {
            "camera_internal": {
              "fx": 400.3176269531,
              "fy": 399.1853027344,
              "cx": 160.4075927734,
              "cy": 90.5059814453
            },
            "camera_external": [
                 0.38911576358613165,
                 -0.0016896440160204533,
                 -0.92118731408540411,
                 -1.6493253438958202,
                 0.92082699455317651,
                 -0.027313332981532164,
                 0.38901366035603963,
                 1.1971726496686779,
                 -0.025817990451348694,
                 -0.99962549334465223,
                 -0.0090721785980543146,
                 1.2874853117093406,
                 0,
                 0,
                 0,
                 1
            ]
        },
        "3d_img3": {
            "camera_internal": {
                "fx": 150.6765136719,
                "fy": 149.7344970703,
                "cx": 160.0305786133,
                "cy": 90.5824584961
            },
            "camera_external": [
                -0.96922141602791245,
                -0.033427849885115782,
                0.24391069178063496,
                -1.7079330079514672,
                -0.24608124216423383,
                0.10200634498971284,
                -0.96386655084443507,
                -1.2623519655673281,
                0.007339548198457212,
                -0.99422194928189866,
                -0.10709270095736945,
                1.6248548245462029,
                0,
                0,
                0,
                1
            ]
        },
        "3d_img4": {
            "camera_internal": {
                "fx": 300.3176269531,
                "fy": 299.1853027344,
                "cx": 160.4075927734,
                "cy": 90.5059814453
            },
            "camera_external": [
                -0.46052986604899926,
                0.00012844683235535559,
                -0.88764420010401823,
                -1.9148091853973153,
                0.88760165590396911,
                0.0098583342523266282,
                -0.46050636660343958,
                -0.76317344184571634,
                0.0086915426376946141,
                -0.99995139719247406,
                -0.0046540669737842313,
                1.1560703944341313,
                0,
                0,
                0,
                1
            ]
        }
    }
    pcd_path = os.path.join(os.path.dirname(in_path), 'upload data package', '3d_url')
    config_path = os.path.join(os.path.dirname(in_path), 'upload data package', 'camera_config')
    if not os.path.exists(config_path):
        os.makedirs(config_path)
    for original_pcd_file in tqdm(list_files(pcd_path, 'pcd'), desc='create config file'):
        json_file_name = os.path.basename(original_pcd_file).replace('.pcd', '.json')
        json_file = os.path.join(config_path, json_file_name)
        with open(json_file, 'w', encoding='utf-8') as jf:
            jf.write(json.dumps(data))


def rename_pcd(in_path: str):
    new_pcd_path = os.path.join(os.path.dirname(in_path), 'upload data package', '3d_url')
    if not os.path.exists(new_pcd_path):
        os.makedirs(new_pcd_path)
    for original_pcd_file in tqdm(list_files(in_path, 'pcd'), desc='pcd file'):
        file_name = os.path.basename(original_pcd_file)
        new_pcd_file = os.path.join(new_pcd_path, file_name)
        os.rename(original_pcd_file, new_pcd_file)


def main():
    in_path = input("Please enter the path of the data folder to be processed :\n")
    while not os.path.exists(in_path):
        in_path = input("The path was not found, please re-enter:\n")
    else:
        print("***************************************************************")
        print("Start refactoring the image directory structure ===>\n")
        rename_image(in_path)
        print("Start refactoring the .pcd directory structure ===>\n")
        rename_pcd(in_path)
        print("Start creating camera parameter profiles ===>\n")
        create_config_file(in_path)
        input("Done, press any key to exit")


if __name__ == "__main__":
    main()


