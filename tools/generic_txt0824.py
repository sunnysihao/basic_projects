# _*_ coding=: utf-8 _*_
import json
import os
import math


# 列出json文件绝对路径列表
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


# 将alpha角度取值范围限制在-pi到pi
def alpha_in_pi(alpha):
    pi = math.pi
    return alpha - math.floor((alpha + pi) / (2 * pi)) * 2 * pi


# 读取json文件内容返回python类型的对象
def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


empty_l = []


def write_while_old(json_content):
    txt_data = []
    data_id = json_content['data_id']
    if 'frameNumber' in json_content['data'].keys():
        fram_number = json_content['data']['frameNumber'] + 1
    else:
        fram_number = 0
    boxes = json_content['result']['data']
    for box in boxes:
        x = box['3Dcenter'].get('x')
        y = box['3Dcenter'].get('y')
        z = box['3Dcenter'].get('z')
        length = box['3Dsize'].get('height')
        width = box['3Dsize'].get('width')
        height = box['3Dsize'].get('deep')
        alpha = alpha_in_pi(box['3Dsize'].get('alpha'))
        int_id = box['intId']
        cby = box['cBy']
        o_label = box['attr']['label']
        if not o_label:
            empty_str = f"作业id:{data_id}---第{fram_number}帧---{int_id}号框标签为空,创建人{cby}\n"
            empty_l.append(empty_str)
            label = 'null'
        else:
            label = o_label[0]
        line_data = f"{label} {x:.2f} {y:.2f} {z:.2f} {length:.2f} {width:.2f} {height:.2f} {alpha:.2f}\n"
        txt_data.append(line_data)
    return txt_data


def write_while_new(json_content):
    txt_data = []

    data_id = json_content['data_id']
    if 'frameNumber' in json_content['data'].keys():
        fram_number = json_content['data']['frameNumber'] + 1
    else:
        fram_number = 0
    boxes = json_content['result']['data']
    for box in boxes:
        x = box['3Dcenter'].get('x')
        y = box['3Dcenter'].get('y')
        z = box['3Dcenter'].get('z')
        length = box['3Dsize'].get('x')
        width = box['3Dsize'].get('y')
        height = box['3Dsize'].get('z')
        alpha = alpha_in_pi(box['3Drotation'].get('z'))
        int_id = box['intId']
        cby = box['cBy']
        o_label = box['classType']
        if not o_label:
            empty_str = f"作业id:{data_id}---第{fram_number}帧---{int_id}号框标签为空,创建人{cby}\n"
            empty_l.append(empty_str)
            label = 'null'
        else:
            label = o_label
        line_data = f"{label} {x:.2f} {y:.2f} {z:.2f} {length:.2f} {width:.2f} {height:.2f} {alpha:.2f}\n"
        txt_data.append(line_data)
    return txt_data


def write_while_beta(json_content):
    txt_data = []
    data_id = json_content['data_id']
    if 'frameNumber' in json_content['data'].keys():
        fram_number = json_content['data']['frameNumber'] + 1
    else:
        fram_number = 0
    boxes = json_content['result']['data']
    for box in boxes:
        x = box['center3D'].get('x')
        y = box['center3D'].get('y')
        z = box['center3D'].get('z')
        length = box['size3D'].get('x')
        width = box['size3D'].get('y')
        height = box['size3D'].get('z')
        alpha = alpha_in_pi(box['rotation3D'].get('z'))
        int_id = box['trackName']
        cby = box['cBy']
        o_label = box['classType']
        if not o_label:
            empty_str = f"作业id:{data_id}---第{fram_number}帧---{int_id}号框标签为空,创建人{cby}\n"
            empty_l.append(empty_str)
            label = 'null'
        else:
            label = o_label
        line_data = f"{label} {x:.2f} {y:.2f} {z:.2f} {length:.2f} {width:.2f} {height:.2f} {alpha:.2f}\n"
        txt_data.append(line_data)
    return txt_data


def write_kitti(json_result_dir: str, txt_result_dir: str):

    for json_file in list_files(json_result_dir):
        txt_file = json_file.replace(json_result_dir, txt_result_dir).replace('.json', '.txt')
        if not os.path.exists(os.path.dirname(txt_file)):
            os.makedirs(os.path.dirname(txt_file))
        json_content = load_json(json_file)
        if not json_content['result']['data'][0]:
            continue
        else:
            if '3Drotation' not in json_content['result']['data'][0].keys():
                if 'center3D' in json_content['result']['data'][0].keys():
                    txt_data = write_while_beta(json_content)
                else:
                    txt_data = write_while_old(json_content)
            else:
                txt_data = write_while_new(json_content)

            with open(txt_file, 'w', encoding='utf-8') as tf:
                tf.writelines(txt_data)
    empty_label_file = os.path.join(txt_result_dir, 'empty_labels.txt')
    with open(empty_label_file, 'w', encoding='utf-8') as ef:
        ef.writelines(empty_l)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('json_result_dir', type=str)
    parser.add_argument('txt_result_dir', type=str)
    args = parser.parse_args()

    json_result_dir = args.json_result_dir
    txt_result_dir = args.txt_result_dir
    # json_result_dir = r"D:\Desktop\ttttt"
    # txt_result_dir = r"D:\Desktop\ttttt\result"
    write_kitti(json_result_dir, txt_result_dir)
