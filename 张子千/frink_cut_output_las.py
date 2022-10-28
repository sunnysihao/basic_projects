import os
import json
import open3d as o3d
import numpy as np
import laspy
from tqdm import tqdm


class_mapping = {
    "ground": 1,
    "road": 2,
    "water": 3,
    "vegetation": 4,
    "building": 5,
    "house": 6,
    "vehicle": 7,
    "power line": 8,
    "other": 9
}


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_list.append(os.path.join(root, file))
            else:
                continue
    return file_list


def load_json(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def load_points(pcd_file):
    pcd = o3d.io.read_point_cloud(pcd_file)
    points = np.asarray(pcd.points)
    filter_points = points[~np.isnan(points).any(axis=1)]
    return filter_points


def add_label(json_path, pcd_path):
    for file in tqdm(list_files(json_path)):
        points_c = []
        json_content = load_json(file)
        file_name = os.path.splitext(json_content['data']['3d_url'].split('/')[-1])[0]
        pcd_file = os.path.join(pcd_path, file_name + '.pcd')
        out_path = os.path.join(os.path.dirname(pcd_path), 'las_with_class')
        if not os.path.exists(out_path):
            os.mkdir(out_path)
        out_file_las = os.path.join(out_path, file_name + '.las')
        points = load_points(pcd_file)
        boxes = json_content['result']['data']
        for box in boxes:
            label = box['attr']['label'][0]
            class_num = class_mapping[label]
            point_index = box['indexs']
            for dex in point_index:
                point = points[dex]
                new_point = np.hstack((point, class_num))
                points_c.append(new_point)
        points_c = np.array(points_c)

        header = laspy.LasHeader(point_format=3, version="1.2")
        header.offsets = np.min(points, axis=0)
        header.scales = np.array([0.001, 0.001, 0.001])
        out_file = laspy.LasData(header)

        classification = np.array(points_c[:, 3], dtype=np.uint8)
        out_file.x = points_c[:, 0]
        out_file.y = points_c[:, 1]
        out_file.z = points_c[:, 2]
        out_file['classification'] = classification
        out_file.write(out_file_las)


if __name__ == '__main__':
    # json_path = r"D:\Desktop\BasicProject\张子千\frinksyn\json_result"
    # pcd_path = r"D:\Desktop\BasicProject\张子千\frinksyn\point_cloud"

    json_path = input("请输入json文件路径:\n")
    pcd_path = input("请输入pcd文件路径:\n")
    add_label(json_path, pcd_path)
    input("已完成，按任意键退出")

