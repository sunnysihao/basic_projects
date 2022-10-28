# _*_ coding=: utf-8 _*_
# @Time    : 2022/10/08
# @Author  : zhangsihao@basicfinder.com
import json
import os
import math
import numpy as np


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_list.append(os.path.join(root, file))
    return sorted(file_list)


# 将alpha角度取值范围限制在-pi到pi
def alpha_in_pi(alpha):
    pi = math.pi
    return alpha - math.floor((alpha + pi) / (2 * pi)) * 2 * pi


# 读取json文件内容返回python类型的对象
def load_json(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


calib_content = [
            "Tr_velo_to_cam:[[0, -1, 0, 0],[0, 0, -1, 0],[1, 0, 0, 0],[0, 0, 0, 1]]\n",
            "Camera internal:[[292.1274058, 0, 292.1628842], [0, 238.4474201, 335.0661855], [0, 0, 1]]"
        ]


def write_result(json_dir: str, output_path: str, check_file: str):
    name_num = 1
    result_path = os.path.join(output_path, 'label')
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    calib_path = os.path.join(output_path, 'calib')
    if not os.path.exists(calib_path):
        os.mkdir(calib_path)
    empty_label = []
    marking_error = []
    for file in list_files(json_dir):
        # file_name = os.path.splitext(os.path.basename(file))[0]
        result_file = os.path.join(result_path, str(name_num) + '.txt')
        calib_file = os.path.join(calib_path, str(name_num) + '.txt')
        line_data = []
        json_content = load_json(file)
        data_id = json_content['data_id']
        boxs = json_content['result']['data']
        ext = np.array([[0, -1, 0, 0],
                        [0, 0, -1, 0],
                        [1, 0, 0, 0],
                        [0, 0, 0, 1]]).reshape((4, 4))
        cam_ext = ext.T
        id_mapping = {}
        truncated = 0
        occluded = 0
        score = 1
        for box in boxs:
            otype = box['objType']
            tid = box['trackId']
            intid = box['trackName']
            label = box['classType']
            if otype == '3d':
                if not label:
                    empty_label_str = f"作业id:{data_id}-{intid}号框未选择标签"
                    empty_label.append(empty_label_str)
                    continue
                else:
                    x = box['center3D']['x']
                    y = box['center3D']['y']
                    z = box['center3D']['z']
                    center = np.array([x, y, z, 1])
                    n_center = center @ cam_ext
                    nx, ny, nz = n_center[0:3]
                    length = box['size3D']['x']
                    width = box['size3D']['y']
                    height = box['size3D']['z']
                    b_alpha = alpha_in_pi(box['rotation3D']['z'])
                    theta = math.atan2(nx, nz)
                    r_y = -1 * alpha_in_pi(b_alpha + (math.pi / 2))
                    alpha = "%.2f" % alpha_in_pi(float(r_y - theta))
                    size = f"{height:.2f} {width:.2f} {length:.2f}"
                    bottom_center = f"{nx:.2f} {ny:.2f} {nz:.2f}"

                    box = {
                        "center": bottom_center,
                        "size": size,
                        "label": label,
                        "alpha": alpha,
                        "r_y": r_y
                    }
                    id_mapping[tid] = box
            else:
                continue

        for rect in boxs:
            otype = rect['objType']
            tid = rect['trackId']
            intid = rect['trackName']
            if otype == '3d':
                continue
            else:
                if tid in id_mapping.keys():
                    x_l = []
                    y_l = []
                    for point in rect['points']:
                        x_l.append(point['x'])
                        y_l.append(point['y'])
                    x_min = min(x_l)
                    x_max = max(x_l)
                    y_min = min(y_l)
                    y_max = max(y_l)
                    scale = f"{x_min:.2f} {y_min:.2f} {x_max:.2f} {y_max:.2f}"
                    id_mapping[tid]['scale'] = scale
                else:
                    only_rect_str = f"作业id:{data_id}-{intid}号框标注错误"
                    marking_error.append(only_rect_str)
                    continue
        for obj in id_mapping.values():
            label = obj['label']
            alpha = obj['alpha']
            if 'scale' in obj.keys():
                scale = obj['scale']
            else:
                scale = f"{0:.2f} {0:.2f} {0:.2f} {0:.2f}"
            size = obj['size']
            center = obj['center']
            r_y = obj['r_y']

            string = f"{label} {truncated:.2f} {occluded} {alpha} {scale} {size} {center} {r_y:.2f} {score:.2f}\n"
            line_data.append(string)


        with open(result_file, 'w', encoding='utf-8') as f:
            f.writelines(line_data)

        with open(calib_file, 'w', encoding='utf-8') as cf:
            cf.writelines(calib_content)
        name_num += 1

    detection_info = {
        "marking_detection": marking_error,
        "empty_label": empty_label
    }
    if not os.path.exists(check_file):
        with open(check_file, 'w', encoding='utf-8') as df:
            df.write(json.dumps(detection_info))
    else:
        with open(check_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            detection_content = json.loads(content)
            detection_content['detection_info'] = detection_info
            with open(check_file, 'w', encoding='utf-8') as df:
                df.write(json.dumps(detection_content))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('result_json_path', type=str)
    parser.add_argument('output_path', type=str)
    parser.add_argument('check_file', type=str)
    args = parser.parse_args()

    result_json_path = args.result_json_path
    output_path = args.output_path
    check_file = args.check_file

    # result_json_path = r"C:\Users\EDY\Downloads\jskxy一作业一结果"
    # output_path = r"C:\Users\EDY\Downloads\jskxy一作业一结果\txt_result"
    # check_file = r"C:\Users\EDY\Downloads\jskxy一作业一结果\check file.txt"
    write_result(result_json_path, output_path, check_file)

