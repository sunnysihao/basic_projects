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


def box2corners(center, half_size, angle):
    corners = np.stack([-half_size, half_size], axis=0)
    corners = np.stack([
        corners[[0, 1, 1, 0], 0],
        corners[[0, 0, 1, 1], 1]
    ], axis=1)

    corners = np.vstack([
        corners,
        [[0, 0]]
    ])

    rot_mat = np.asarray([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle), np.cos(angle)],
    ])
    return corners @ rot_mat.T + center


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
    ax, ay, _, adx, ady = box_a[:5]
    bx, by, _, bdx, bdy = box_b[:5]
    ax1, ax2 = ax - adx / 2, ax + adx / 2
    bx1, bx2 = bx - bdx / 2, bx + bdx / 2
    ay1, ay2 = ay - ady / 2, ay + ady / 2
    by1, by2 = by - bdy / 2, by + bdy / 2
    angle_diff = box_b[6] - box_a[6]
    if abs(angle_diff) < 1e-3:
        return (
                range_overlap([ax1, ax2], [bx1, bx2])
                and range_overlap([ay1, ay2], [by1, by2])
        )

    box_a_corners = box2corners(box_a[:2], box_a[3:5] / 2, angle_diff)
    box_b_corners = box2corners(box_b[:2], box_b[3:5] / 2, angle_diff)
    return (
            corners_overlap([ax1, ax2, ay1, ay2], box_b_corners) or
            corners_overlap([bx1, bx2, by1, by2], box_a_corners)
    )


def main():
    boxes = np.array([
        [0, 0, 0, 1, 2, 3, 0],
        [1.1, 0, 0, 1, 2, 3, 0],
        [1.2, 0, 0, 1, 2, 3, 0.5],
        [0.5, 1, 0, 1, 2, 3, 1.5],
        [-1.5, 1, 0, 1, 2, 3, 2.5],
    ], np.float32)

    N = len(boxes)

    result = np.zeros((N, N), dtype=int)
    for i, box1 in enumerate(boxes):
        for j in range(i, len(boxes)):
            flag = box_overlap(box1, boxes[j])
            v = int(flag)
            result[i, j] = v
            result[j, i] = v

    print(result)




label_mapping = {
    "Pedestrian": 20,
    "Bicycle": 20,
    "Car": 18,
    "Bus": 25,
    "Truck": 25,
    "Tricycle": 20,
    "Motorcycle": 20,
    "null": 0
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
    points = np.asarray(pcd.points)  # type(points)--->numpy.ndarray
    return points

def write_json(in_path: str):
    # result_dir = os.path.join(os.path.dirname(in_path), 'result')
    # if not os.path.exists(result_dir):
    #     os.mkdir(result_dir)
    # all_err = {}
    # for _dir in list_dir(in_path):
    batch_err = {}
    batch_lap = {}
    batch_label = {}
    batch_cut = {}
    one_job_label = {}
    one_job_cut = {}

    # json_path = os.path.join(in_path, _dir, '3d_url')
    # set_name = _dir
    # result_path1 = os.path.join(result_dir, set_name)
    # if not os.path.exists(result_path1):
    #     os.mkdir(result_path1)
    # result_path = os.path.join(result_path1, '3d_url')
    # if not os.path.exists(result_path):
    #     os.mkdir(result_path)

    # job_list = []
    # frame_count = 0

    for file in tqdm(list_files(in_path)):
        one_job_err = {}
        one_job_lap = {}
        file_name = os.path.splitext(os.path.basename(file))[0] + '.pcd'
        pcd_path = r"D:\Desktop\新建文件夹\pcd"
        pcd_file = os.path.join(pcd_path, file_name)
        points = get_points(pcd_file)
        # json_file = os.path.join(json_path, file + '.json')
        json_content = load_json(file)
        batch_id = json_content['data_id']
        frame_number = json_content['data']['frameNumber'] + 1
        boxs = json_content['result']['data']
        annotations = []
        one_file_err = []
        one_file_label = []
        one_file_cut = []

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
                one_box_label = f"创建人{job_id}, {int_id}号框无标签信息"
                one_file_label.append(one_box_label)


            else:
                if '断裂' in attr_label:
                    one_box_cut = f"创建人{job_id}, {int_id}存在断裂"
                    one_file_cut.append(one_box_cut)
                    if len(attr_label) == 1:
                        label = "null"
                    else:
                        label = attr_label[0]
                else:
                    label = attr_label[0]

            point_num = count_points_in_3dbox(box_border, points)
            wide = label_mapping[f'{label}']

            if point_num < wide:
                one_box_err = f"创建人{job_id}, {int_id}号框点数小于限制"
                one_file_err.append(one_box_err)
                continue
            else:
                box_data = {
                    "name": label,
                    "bbox_center": [x, y, z],
                    "bbox_size": [nx, ny, nz],
                    "heading": alpha
                }
                annotations.append(box_data)
        lap = 0
        if lap:  # 如果有框重叠
            one_file_lap = f"第{frame_number}帧有框重叠"
            if f"第{frame_number}帧" not in one_job_lap.keys():
                one_job_lap[f"第{frame_number}帧"] = [one_file_lap]
            else:
                one_job_lap[f"第{frame_number}帧"].append(one_file_lap)
            if f"{batch_id}" not in batch_lap.keys():
                batch_lap[f"{batch_id}"] = [one_job_lap]
            else:
                batch_lap[f"{batch_id}"].append(one_job_err)
        else:  # 如果没有框重叠
            if not one_file_err:  # 也没有框不符合点数要求， 则写入文件
                with open(file, 'w', encoding='utf-8') as nf:
                    nf.write(json.dumps(annotations))
            else:
                if f"第{frame_number}帧" not in one_job_err.keys():
                    one_job_err[f"第{frame_number}帧"] = one_file_err
                else:
                    one_job_err[f"第{frame_number}帧"].append(one_file_err)

                if f"{batch_id}" not in batch_err.keys():
                    batch_err[f"{batch_id}"] = [one_job_err]
                else:
                    batch_err[f"{batch_id}"].append(one_job_err)

        if f"第{frame_number}帧" not in one_job_label.keys():
            one_job_label[f"第{frame_number}帧"] = [one_file_label]
        else:
            one_job_label[f"第{frame_number}帧"].append(one_file_label)

        if lap:
            one_box_lap = f"创建人{job_id}, {int_id}号框有重叠"
            one_file_lap.append(one_box_lap)
            if f"{batch_id}" not in batch_label.keys():
                batch_label[f"{batch_id}"] = [one_job_label]
            else:
                batch_label[f"{batch_id}"].append(one_job_label)

            if f"{file_name}" not in one_job_cut.keys():
                one_job_cut[f"{file_name}"] = [one_file_cut]
            else:
                one_job_cut[f"{file_name}"].append(one_file_cut)

            if f"{batch_id}" not in batch_cut.keys():
                batch_cut[f"{batch_id}"] = [one_job_cut]
            else:
                batch_cut[f"{batch_id}"].append(one_job_cut)

        one_job_err = {}
        one_job_lap = {}


        if f"第{frame_number}帧" not in one_job_lap.keys():
            one_job_lap[f"第{frame_number}帧"] = [one_file_lap]
        else:
            one_job_lap[f"第{frame_number}帧"].append(one_file_lap)

        if f"{batch_id}" not in batch_err.keys():
            batch_err[f"{batch_id}"] = [one_job_err]
        else:
            batch_err[f"{batch_id}"].append(one_job_err)

        if f"{batch_id}" not in batch_lap.keys():
            batch_lap[f"{batch_id}"] = [one_job_lap]
        else:
            batch_lap[f"{batch_id}"].append(one_job_lap)

        continue

# frame_count += 1
# print(f"{set_name}===>共{frame_count}帧数据转换完成\n文件保存路径为：{result_path}")

        # if f"{set_name}" not in all_err.keys():
        #     all_err[f"{set_name}"] = [batch_err]
        # else:
        #     all_err[f"{set_name}"].append(batch_err)

    error = {
        "border_errors": batch_err,
        "overlapped_errors": batch_lap,
        "empty_label": batch_cut,
        "含断裂": batch_cut
        }
    err_file = os.path.join(os.path.dirname(in_path), 'errors.json')

    with open(err_file, 'w', encoding='utf-8') as ef:
        ef.write(json.dumps(error))


if __name__ == "__main__":
    # import argparse
    #
    # parser = argparse.ArgumentParser()
    # parser.add_argument('result_json_path', type=str)
    # parser.add_argument('output_path', type=str)
    # args = parser.parse_args()


    # json_files_path = input("请输入平台'3D一帧一结果'脚本打包的原结果文件夹路径:\n")
    # while not os.path.exists(json_files_path):
    #     print(f"未找到路径：{json_files_path} ")
    #     json_files_path = input("请重新输入:\n")
    # else:
    #     write_json(json_files_path)
    #     input("程序执行完成，按任意键退出")

    in_path = r"D:\Desktop\新建文件夹\json"
    write_json(in_path)
