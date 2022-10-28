# _*_ coding=: utf-8 _*_
# @Time    : 2022/07/19
# @Author  : zhangsihao@basicfinder.com
"""
功能：经纬恒润新点云连续帧结果结果导出，针对平台'3D一帧一结果'脚本打包的数据进行转换导出。
使用方法：
    运行程序，根据命令提示输入对应信息，输出文件在原路径上一级的“results”目录下。
"""
import json
import os
import numpy as np
import open3d as o3d
from tqdm import tqdm
# from load_pcd_points import main



def rot_mat(angle):
    return np.asarray([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle), np.cos(angle)],
    ])


def box2corners(center, half_size, angle, angle2, center2):
    corners = np.stack([-half_size, half_size], axis=0)
    corners = np.stack([
        corners[[0, 1, 1, 0], 0],
        corners[[0, 0, 1, 1], 1]
    ], axis=1)

    corners = np.vstack([
        corners,
        [[0, 0]]
    ])

    corners = corners @ rot_mat(angle).T + center

    corners = (corners - center2) @ rot_mat(-angle2).T + center2

    return corners


def range_overlap(range1, range2):
    """
    :param range1: (start, end)
    :param range2: (start, end)
    """
    return range1[0] <= range2[1] and range1[1] >= range2[0]


def corners_overlap(rect, corners: np.ndarray):
    """
    :param rect: [x1, x2, y1, y2]
    :param corners: [(x, y), ...]
    """
    x1, x2, y1, y2 = rect
    _x1, _y1 = corners.min(axis=0)
    _x2, _y2 = corners.max(axis=0)
    if not range_overlap([x1, x2], [_x1, _x2]) and not range_overlap([y1, y2], [_y1, _y2]):
        return False

    for x, y in corners:
        if x1 <= x <= x2 and y1 <= y <= y2:
            return True

    return False


def box_overlap(box_a: np.ndarray, box_b: np.ndarray):
    """
    :params box_a: [x, y, z, dx, dy, dz, heading]
    :params box_b: [x, y, z, dx, dy, dz, heading]
    """
    ax, ay, _, adx, ady, _, a_angle = box_a
    bx, by, _, bdx, bdy, _, b_angle = box_b
    ax1, ax2 = ax - adx / 2, ax + adx / 2
    bx1, bx2 = bx - bdx / 2, bx + bdx / 2
    ay1, ay2 = ay - ady / 2, ay + ady / 2
    by1, by2 = by - bdy / 2, by + bdy / 2
    # angle_diff = box_b[6] - box_a[6]
    # if abs(angle_diff) < 1e-3:
    #     return (
    #         range_overlap([ax1, ax2], [bx1, bx2])
    #         and range_overlap([ay1, ay2], [by1, by2])
    #     )

    box_a_corners = box2corners(box_a[:2], box_a[3:5] / 2, a_angle, b_angle, box_b[:2])
    box_b_corners = box2corners(box_b[:2], box_b[3:5] / 2, b_angle, a_angle, box_a[:2])
    return (
            corners_overlap([ax1, ax2, ay1, ay2], box_b_corners) or
            corners_overlap([bx1, bx2, by1, by2], box_a_corners)
    )

    # box_a_corners = np.vstack([box_a_corners, box_a_corners[:1]])
    # box_b_corners = np.vstack([box_b_corners, box_b_corners[:1]])

    # for i in range(4):
    #     for j in range(4):
    #         if intersection(box_a_corners[i: i+2], box_b_corners[j: j+2]):
    #             return True
    # return False


def whether_overlap(boxes):
    # boxes = np.array([
    #     [0, 0, 0, 1, 2, 3, 0],
    #     [1.1, 0, 0, 1, 2, 3, 0],
    #     [1.2, 0, 0, 1, 2, 3, 0.5],
    #     [0.5, 1, 0, 1, 2, 3, 1.5],
    #     [-1.5, 1, 0, 1, 2, 3, 2.5],
    #
    #     # [-4.738579,   13.21626,    -1.1789553,   2.0536785,   0.81731683,  1.4574084, -2.2514746 ],
    #     # [-3.1748693, 13.156894,  -1.1951844,  1.9391056,  0.8340628,  1.5417628, -2.1293018]
    # ], np.float32)

    N = len(boxes)

    result = np.zeros((N, N), dtype=int)
    for i, box1 in enumerate(boxes):
        for j in range(i, len(boxes)):
            flag = box_overlap(box1, boxes[j])
            v = int(flag)
            result[i, j] = v
            result[j, i] = v
    sum_r = np.sum(result)
    if sum_r <= N:
        lap = 0
    else:
        lap = 1
        # print(result)
    return lap


label_mapping = {
    "Pedestrian": 20,
    "Bicycle": 20,
    "Car": 18,
    "Bus": 25,
    "Truck": 25,
    "Tricycle": 20,
    "Motorcycle": 20,
    "null": 0,
    "only_has_broken": 0
}


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_name = os.path.splitext(file)[0]
                file_list.append(os.path.join(root, file))
            else:
                continue
    return file_list


def list_dir(in_path: str):
    dir_list = []
    for _dir in os.listdir(in_path):
        if os.path.isdir(os.path.join(in_path, _dir)):
            dir_list.append(_dir)
        else:
            continue
    return dir_list


# 读取json文件内容返回python类型的对象
def load_json(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def count_points_in_3dbox(box: np.ndarray, pc: np.ndarray) -> int:
    """

    :param box: [x, y, z, dx, dy, dz, angle]

    :param pc: point cloud

    """
    angle = -box[-1]
    rot_mat = np.asarray([
        [np.cos(angle), -np.sin(angle), 0],
        [np.sin(angle), np.cos(angle), 0],
        [0, 0, 1]
    ])
    pc = (pc[:, :3] - box[:3]) @ rot_mat.T
    mask = (
            (-box[3] / 2 < pc[:, 0]) & (pc[:, 0] < box[3] / 2) &  # x
            (-box[4] / 2 < pc[:, 1]) & (pc[:, 1] < box[4] / 2) &  # y
            (-box[5] / 2 < pc[:, 2]) & (pc[:, 2] < box[5] / 2)  # z
    )
    pc = pc[mask]
    return len(pc)


def get_points(pcd_file):
    pcd = o3d.io.read_point_cloud(pcd_file)  # type(pcd)--->open3d.cpu.pybind.geometry.PointCloud
    points = np.asarray(pcd.points)
    # points = main(pcd_file)  # type(points)--->numpy.ndarray
    return points


def write_json(json_path: str, pcd_path: str):

    border_l = []
    overlap_l = []
    empty_label_l = []
    broken_l = []
    only_broken_l = []
    count_box = 0

    for file in tqdm(list_files(json_path)):
        file_name = os.path.splitext(os.path.basename(file))[0] + '.pcd'

        json_content = load_json(file)
        pcd_file = os.path.join(pcd_path, file_name)
        points = get_points(pcd_file)
        batch_id = json_content['data_id']
        boxs = json_content['result']['data']
        annotations = []
        boxes_l = []
        for box in boxs:  # 读取每个3D框数据
            x, y, z = box['3Dcenter'].values()
            nx = box['3Dsize']['height']
            ny = box['3Dsize']['width']
            nz = box['3Dsize']['deep']
            alpha = box['3Dsize']['alpha']

            int_id = box['intId']
            job_id = box['cBy']
            box_border = np.array([x, y, z, nx, ny, nz, alpha])

            attr_label = box['attr']['label']
            if not attr_label:
                label = "null"
                empty_err = f"作业ID:{batch_id} - 创建人{job_id} - {int_id}号框无标签信息\n"
                empty_label_l.append(empty_err)

            else:
                if '断裂' in attr_label:
                    broken_err = f"作业ID:{batch_id} - 创建人{job_id} - {int_id}号框存在断裂，pcd文件名为：{file_name}\n"
                    broken_l.append(broken_err)
                    if len(attr_label) == 1:
                        label = "only_has_broken"
                        only_broken_err = f"作业ID:{batch_id} - 创建人{job_id} - {int_id}号框只有断裂标签\n"
                        only_broken_l.append(only_broken_err)
                    else:
                        label = attr_label[0]
                else:
                    label = attr_label[0]

            point_num = count_points_in_3dbox(box_border, points)
            wide = label_mapping[f'{label}']

            if point_num < wide:
                border_err = f"作业ID:{batch_id} - 创建人{job_id} - {int_id}号框点数不符合标注规范\n"
                border_l.append(border_err)
                continue
            else:
                count_box += 1
                box_data = {
                    "name": label,
                    "bbox_center": [x, y, z],
                    "bbox_size": [nx, ny, nz],
                    "heading": alpha
                }
                annotations.append(box_data)
            box_7 = [x, y, z, nx, ny, nz, alpha]
            boxes_l.append(box_7)
        boxes = np.array(boxes_l, np.float32)
        lap = whether_overlap(boxes)
        if lap:  # 如果有框重叠
            overlap_err = f"作业ID:{batch_id} 有框重叠\n"
            overlap_l.append(overlap_err)
        with open(file, 'w', encoding='utf-8') as nf:
            nf.write(json.dumps(annotations))
    border_l.append(f"总计{len(border_l)}个框")
    overlap_l.append(f"总计{len(overlap_l)}个框")
    empty_label_l.append(f"总计{len(empty_label_l)}个框")
    broken_l.append(f"总计{len(broken_l)}个框")
    only_broken_l.append(f"总计{len(only_broken_l)}个框")
    # for err in ['border_errors', 'overlap_errors', 'empty_label_errors', 'broken_errors']:
    border_file = os.path.join(json_path, 'border_errors.txt')
    with open(border_file, 'w', encoding='utf-8') as bf:
        bf.writelines(border_l)
    overlap_file = os.path.join(json_path, 'overlap_errors.txt')
    with open(overlap_file, 'w', encoding='utf-8') as of:
        of.writelines(overlap_l)
    empty_file = os.path.join(json_path, 'empty_label_errors.txt')
    with open(empty_file, 'w', encoding='utf-8') as ef:
        ef.writelines(empty_label_l)
    broken_file = os.path.join(json_path, 'broken_errors.txt')
    with open(broken_file, 'w', encoding='utf-8') as kf:
        kf.writelines(broken_l)
    only_broken_file = os.path.join(json_path, 'only_has_broken_errors.txt')
    with open(only_broken_file, 'w', encoding='utf-8') as olf:
        olf.writelines(only_broken_l)
    count_box_file = os.path.join(json_path, 'count_box.txt')
    with open(count_box_file, 'w', encoding='utf-8') as olf:
        olf.writelines(f"总计{count_box} 个框")



def main():
    result_json_path = input("请输入平台'json一作业一结果'打包的结果文件路径:\n")
    while not os.path.exists(result_json_path):
        print(f"=====>路径错误,请重新输入:")
        result_json_path = input()
    else:
        pcd_path = input("请输入pcd点云文件路径:\n")
        while not os.path.exists(pcd_path):
            print(f"=====>路径错误,请重新输入")
            result_json_path = input()
        else:
            write_json(result_json_path, pcd_path)
            input("已完成， 按任意键退出")

if __name__ == "__main__":

    main()
