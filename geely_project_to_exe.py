# _*_ coding=: utf-8 _*_
# 安装：pip install numpy tqdm argparse
# 使用：geely_project_to_exe.py <json源文件目录路径> <结果输出目录路径>

import os
import json
import numpy as np
import math
import time
from tqdm import tqdm

def alpha_in_pi(a):
    pi = math.pi
    return a - math.floor((a + pi) / (2 * pi)) * 2 * pi


def convert_json_to_txt(json_dir_path: str, result_path: str):
    json_files = os.listdir(json_dir_path)
    print("=====>开始转换")
    for json_file in tqdm(json_files, unit='file', colour='white'):
        if os.path.splitext(json_file)[1] == ".json":
            with open(os.path.join(json_dir_path, json_file), "r", encoding="utf-8") as f:
                str_data = f.read()
                json_content = json.loads(str_data)
                result = json_content['result']['data']
                for i in range(len(result)):
                    result_data = result[i]

                    if "车辆类型" in result_data['attr']['category']:
                        label_name = result_data['attr']['label'][result_data['attr']['category'].index("车辆类型")]
                    else:
                        label_name = "null"

                    if "截断等级" in result_data['attr']['category']:
                        truncate = float(result_data['attr']['label'][result_data['attr']['category'].index("截断等级")])
                        truncate = ("%.2f" % truncate)
                    else:
                        truncate = float(0.00)
                        truncate = ("%.2f" % truncate)

                    if "遮挡等级" in result_data['attr']['category']:
                        occlud = int(result_data['attr']['label'][result_data['attr']['category'].index("遮挡等级")])
                    else:
                        occlud = int(0)

                location = [result_data['3Dcenter']['x'],result_data['3Dcenter']['y'],result_data['3Dcenter']['z']]
                location_np = np.asarray(location)
                location_np_2f = np.round(location_np, 2)
                location = list(location_np_2f)
                demension = [result_data['3Dsize']['height'], result_data['3Dsize']['width'], result_data['3Dsize']['deep']]  #3D维度
                demension_np = np.asarray(demension)
                demension_np_2f = np.round(demension_np, 2)
                demension = list(demension_np_2f)
                rotation_y = alpha_in_pi(result_data['3Dsize']['alpha'])
                data = f"{label_name} {truncate} {occlud} {location} {demension} {round(rotation_y, 2)}\n"
                data = data.replace(",", "").replace("[", "").replace("]", "")
                to_path = os.path.join(result_path, os.path.splitext(json_file)[0])
                with open(to_path + ".txt", "+a", encoding='utf-8') as f:
                    f.write(data)
        else:
            continue

if __name__ == "__main__":
    # import argparse
    #
    # parser = argparse.ArgumentParser()
    # parser.add_argument('json_dir_path', type=str)
    # parser.add_argument('result_path', type=str)
    # args = parser.parse_args()
    #
    # #json文件目录路径
    # json_dir_path = args.json_dir_path
    # #结果输出目录路径
    # result_path = args.result_path
    # convert_json_to_txt(json_dir_path, result_path)
    # print("=====>转换完成")
    #time.sleep(10)

    json_dir_path = input("请输入json文件目录路径:")
    result_path = input("请输入导出结果目标路径:")
    convert_json_to_txt(json_dir_path, result_path)
    print("=====> 转换完成")
    print("=====> 即将退出程序")
    time.sleep(3)

