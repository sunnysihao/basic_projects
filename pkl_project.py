# _*_ coding=: utf-8 _*_
import gzip
import pickle
import json
import os
import numpy as np
from scipy.spatial.transform import Rotation as R
from numpy.linalg import inv


label_class = {
  "1": "Smoke",
  "2": "Exhaust",
  "3": "Spray or rain",
  "4": "Reflection",
  "5": "Vegetation",
  "6": "Ground",
  "7": "Road",
  "8": "Lane Line Marking",
  "9": "Stop Line Marking",
  "10": "Other Road Marking",
  "11": "Sidewalk",
  "12": "Driveway",
  "13": "Car",
  "14": "Pickup Truck",
  "15": "Medium-sized Truck",
  "16": "Semi-truck",
  "17": "Towed Object",
  "18": "Motorcycle",
  "19": "Other Vehicle - Construction Vehicle",
  "20": "Other Vehicle - Uncommon",
  "21": "Other Vehicle - Pedicab",
  "22": "Emergency Vehicle",
  "23": "Bus",
  "24": "Personal Mobility Device",
  "25": "Motorized Scooter",
  "26": "Bicycle",
  "27": "Train",
  "28": "Trolley",
  "29": "Tram / Subway",
  "30": "Pedestrian",
  "31": "Pedestrian with Object",
  "32": "Animals - Bird",
  "33": "Animals - Other",
  "34": "Pylons",
  "35": "Road Barriers",
  "36": "Signs",
  "37": "Cones",
  "38": "Construction Signs",
  "39": "Temporary Construction Barriers",
  "40": "Rolling Containers",
  "41": "Building",
  "42": "Other Static Object"
}


# 根据路径列出当前路径下所有的文件名(不含后缀名)
def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list


def load_gz(gz_file):
    with gzip.open(gz_file, 'r') as f:
        gz_data = pickle.load(f)
    return gz_data


# 加载压缩的.gz格式的pkl数据
def load_pkl(pkl_file):
    with gzip.open(pkl_file, 'r') as f:
        data = pickle.load(f)
        points_array = data.values
    return points_array


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
        cam_external = np.vstack((cam_ext, t))
        params.append(cam_external)
    return params

# 将点云数据写入pcd文件
def write_points2pcd(pkl_path, pcd_path):
    lidar_ext_list = get_param(r"D:\Desktop\BasicProject\任从辉\pkl数据集\ideastoimpacts\002\json\poses.json")
    j = 0
    for file in list_files(pkl_path):
        points = load_pkl(os.path.join(pkl_path, file +'.gz'))
        itd = points[:, 3:]
        points = points[:, :3]
        num = points.shape[0]
        t = np.ones((num, 1))
        points = np.hstack((points, t))
        cam_ext = inv(lidar_ext_list[j])
        points = (points @ cam_ext.T)[:, :3]
        points = np.hstack((points, itd))
        pcd_file_name = os.path.splitext(file)[0]
        with open(os.path.join(pcd_path, pcd_file_name + '.pcd'), 'a') as pcd_file:
            # 得到点云点数
            point_num = points.shape[0]
            # 写pcd文件头部
            pcd_file.write(
                '# .PCD v0.7 - Point Cloud Data file format\nVERSION 0.7\nFIELDS x y z i t d\nSIZE 4 4 4 4 4 4\nTYPE F F F F F F\nCOUNT 1 1 1 1 1 1')
            string1 = '\nWIDTH ' + str(point_num)
            pcd_file.write(string1)
            pcd_file.write('\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0')
            string2 = '\nPOINTS ' + str(point_num)
            pcd_file.write(string2)
            # 依次写入点,以ascii格式存储点云数据集部分
            pcd_file.write('\nDATA ascii')
            for i in range(point_num):
                string_point = '\n' + str(points[i, 0]) + ' ' + str(points[i, 1]) + ' ' + str(points[i, 2]) + ' ' + str(points[i, 3]) + ' ' + str(points[i, 4]) + ' ' + str(points[i, 5])
                pcd_file.write(string_point)
            j += 1

# 将3D框结果写入json文件
def write_3Dbox_to_json(gz_path, result_path):
    for file in list_files(gz_path):
        gz_data = load_gz(os.path.join(gz_path, file + '.gz'))
        json_file_name = os.path.splitext(file)[0]
        result_data = []
        for i in range(len(gz_data)):
            line_data = gz_data.iloc[i]
            x, y, z = line_data['position.x'], line_data['position.y'], line_data['position.z']
            height, width, deep = line_data['dimensions.x'], line_data['dimensions.y'], line_data['dimensions.z']
            label, alpha = line_data['label'], line_data['yaw']
            box_data = {
                "3Dcenter": {
                    "x": x,
                    "y": y,
                    "z": z
                },
                "3Dsize": {
                    "width": width,
                    "height": height,
                    "deep": deep,
                    "alpha": alpha
                },
                "attr": {
                    "category": [
                        label
                    ],
                    "label": [
                        label
                    ],
                    "code": [
                        label
                    ]
                }
            }
            result_data.append(box_data)
        new_json_data = {
            "data": {
                "3d_url": json_file_name + '.pcd',
                "3d_img0": json_file_name + '.jpg',
                "3d_img1": json_file_name + '.jpg',
                "3d_img2": json_file_name + '.jpg',
                "3d_img3": json_file_name + '.jpg',
                "3d_img4": json_file_name + '.jpg',
                "3d_img5": json_file_name + '.jpg'
            },
            "result": {
                "data": result_data
            }
        }
        with open(os.path.join(result_path, json_file_name + ".json"), 'w', encoding='utf-8') as f:
            f.write(json.dumps(new_json_data))


# 将点云分割结果写入json文件
def write_point_lable_to_json(gz_path, semresult_path):
    for file in list_files(gz_path):
        gz_data = load_gz(os.path.join(gz_path, file + '.gz'))
        json_file_name = os.path.splitext(file)[0]


def pcd2(pkl_path, pcd_path):
    for file in list_files(pkl_path):
        points = load_pkl(os.path.join(pkl_path, file + '.gz'))
        pcd_file_name = os.path.splitext(file)[0]
        with open(os.path.join(pcd_path, pcd_file_name + '.pcd'), 'a') as pcd_file:
            # 得到点云点数
            point_num = points.shape[0]
            # 写pcd文件头部
            pcd_file.write(
                '# .PCD v0.7 - Point Cloud Data file format\nVERSION 0.7\nFIELDS x y z i t d\nSIZE 4 4 4 4 4 4\nTYPE F F F F F F\nCOUNT 1 1 1 1 1 1')
            string1 = '\nWIDTH ' + str(point_num)
            pcd_file.write(string1)
            pcd_file.write('\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0')
            string2 = '\nPOINTS ' + str(point_num)
            pcd_file.write(string2)
            # 依次写入点,以ascii格式存储点云数据集部分
            pcd_file.write('\nDATA ascii')
            for i in range(point_num):
                string_point = '\n' + str(points[i, 0]) + ' ' + str(points[i, 1]) + ' ' + str(points[i, 2]) + ' ' + str(
                    points[i, 3]) + ' ' + str(points[i, 4]) + ' ' + str(points[i, 5])
                pcd_file.write(string_point)


if __name__ == "__main__":
    pkl_path = r"D:\Desktop\BasicProject\张子千\lidar"  #.pkl.gz点云文件路径
    pcd_path = r"D:\Desktop\BasicProject\张子千\pcd"  #3d_url存放pcd文件路径
    # write_points2pcd(pkl_path, pcd_path)

    # gz_path = r"D:\Desktop\BasicProject\任从辉\pkl数据集\ideastoimpacts\002\annotations\cuboids"
    # result_path = r"D:\Desktop\BasicProject\任从辉\pkl数据集\ai_result"
    # write_3Dbox_to_json(gz_path, result_path)
    #
    # pcd2_path = r"D:\Desktop\BasicProject\任从辉\pkl数据集\old_pcd"
    pcd2(pkl_path, pcd_path)