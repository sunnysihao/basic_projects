# _*_ coding=: utf-8 _*_
# @Time    : 2022/07/19
# @Author  : zhangsihao@basicfinder.com
"""
功能：东软睿驰新点云连续帧结果结果导出，针对平台'3D一帧一结果'脚本打包的数据进行转换导出。
使用方法：
    运行程序，根据命令提示输入对应信息，输出文件在原路径上一级的“results”目录下。
"""
import json
import os
import math
from tqdm import tqdm

def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_name = os.path.splitext(file)[0]
                file = os.path.join(root, file)
                file_list.append(file)
            else:
                continue
    return file_list


def list_files_name(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_name = os.path.splitext(file)[0]
                file_list.append(file_name)
            else:
                continue
    return file_list


# 将alpha角度取值范围限制在-pi到pi
def alpha_in_pi(alpha):
    pi = math.pi
    return alpha - math.floor((alpha + pi) / (2 * pi)) * 2 * pi


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


def write_json(in_path: str):
    err_list = []
    for file in tqdm(list_files(in_path), desc='进度', leave=True, unit='file', colour='blue'):
        json_content = load_json(file)
        boxs = json_content['result']['data']
        annotations = []
        for box in boxs:  # 读取每个3D框数据
            x, y, z = box['3Dcenter'].values()
            nx, ny, nz = box['3Dsize'].values()
            alpha = box['3Drotation']['z']
            int_id = box['intId']
            label = box['classType']
            if not box['cubeMap']:
                bbox = None
                err_list.append(f"{file}---含空2D框结果\n")
            else:
                cube_points = box['cubeMap'][0]['cubePoints']
                xl = []
                yl = []
                for coordinate in cube_points:
                    xl.append(coordinate['x'])
                    yl.append(coordinate['y'])
                x_min = min(xl)
                y_min = min(yl)
                x_max = max(xl)
                y_max = max(yl)
                bbox = {
                      "x": x_min,
                      "y": y_min,
                      "rw": x_max-x_min,
                      "rh": y_max-y_min
                    }
            box_data = {
                "id": int_id,
                "type": label,
                "x": x,
                "y": y,
                "z": z,
                "long": nx,
                "width": ny,
                "height": nz,
                "alpha": alpha_in_pi(alpha),
                "points_3d": [
                    {
                      "x": x-nx/2,
                      "y": y+ny/2,
                      "z": z+nz/2
                    },
                    {
                      "x": x-nx/2,
                      "y": y-ny/2,
                      "z": z+nz/2
                    },
                    {
                      "x": x-nx/2,
                      "y": y-ny/2,
                      "z": z-nz/2
                    },
                    {
                      "x": x-nx/2,
                      "y": y+ny/2,
                      "z": z-nz/2
                    },
                    {
                      "x": x+nx/2,
                      "y": y+ny/2,
                      "z": z+nz/2
                    },
                    {
                      "x": x+nx/2,
                      "y": y-ny/2,
                      "z": z+nz/2
                    },
                    {
                      "x": x+nx/2,
                      "y": y-ny/2,
                      "z": z-nz/2
                    },
                    {
                      "x": x+nx/2,
                      "y": y+ny/2,
                      "z": z-nz/2
                    }
                ],
                "bbox": bbox
            }
            annotations.append(box_data)
        with open(file, 'w', encoding='utf-8') as nf:
            nf.write(json.dumps(annotations))
    with open(in_path + r'\errors.txt', 'w', encoding='utf-8') as tf:
        tf.writelines(err_list)


if __name__ == "__main__":
    json_files_path = input("请输入平台'3D一帧一结果'脚本打包的原结果文件夹路径:\n")
    while not os.path.exists(json_files_path):
        print(f"未找到路径：{json_files_path} ")
        json_files_path = input("请重新输入:\n")
    else:
        write_json(json_files_path)
        input("程序执行完成，按任意键退出")
