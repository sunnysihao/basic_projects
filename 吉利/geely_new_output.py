# _*_ coding=: utf-8 _*_
# _*_ coding=: utf-8 _*_
# 安装：pip install numpy tqdm argparse
# 使用：geely_project.py <json源文件目录路径> <结果输出目录路径>

import os
import json
import math
from tqdm import tqdm


def alpha_in_pi(a):
    pi = math.pi
    return a - math.floor((a + pi) / (2 * pi)) * 2 * pi


def convert_json_to_txt(json_dir_path: str):
    result_path = os.path.join(os.path.dirname(json_dir_path), 'results')
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    json_files = os.listdir(json_dir_path)
    print("=====>开始转换")
    for json_file in tqdm(json_files, desc='进度', leave=True, unit='file', colour='red'):
        if os.path.splitext(json_file)[1] == ".json":
            with open(os.path.join(json_dir_path, json_file), "r", encoding="utf-8") as f:
                str_data = f.read()
                json_content = json.loads(str_data)
                result = json_content['result']['data']
                for i in range(len(result)):
                    result_data = result[i]
                    if result_data['classType'] == None:
                        label_name = "null"
                    else:
                        if result_data['classType'] == '摩托车和骑摩托车的人':
                            label_name = 'Motorcycle'
                        else:
                            label_name = result_data['classType']

                    if result_data['attrs'] == None:
                        truncate = ("%.2f" % float(0.00))
                        occlud = int(0)
                    else:

                        if "截断等级" in result_data['attrs']:
                            truncate = float(result_data['attrs']['截断等级'])
                            truncate = ("%.2f" % truncate)
                        else:
                            truncate = float(0.00)
                            truncate = ("%.2f" % truncate)

                        if "遮挡等级" in result_data['attrs']:
                            occlud = int(result_data['attrs']['遮挡等级'])
                        else:
                            occlud = int(0)

                    x, y, z = [result_data['3Dcenter']['x'], result_data['3Dcenter']['y'], result_data['3Dcenter']['z']]
                    location = f"{x:.2f} {y:.2f} {z:.2f}"
                    nx, ny, nz = result_data['3Dsize'].values()  # 3D维度
                    demension = f"{nx:.2f} {ny:.2f} {nz:.2f}"
                    rotation_y = alpha_in_pi(result_data['3Drotation']['z'])
                    data = f"{label_name} {truncate} {occlud} {location} {demension} {round(rotation_y, 2)}\n"
                    data = data.replace(",", "").replace("[", "").replace("]", "")
                    to_path = os.path.join(result_path, os.path.splitext(json_file)[0])
                    with open(to_path + ".txt", "+a", encoding='utf-8') as f:
                        f.write(data)
        else:
            continue


if __name__ == "__main__":

    json_dir_path = input("请输入json文件目录路径:\n")
    while not os.path.exists(json_dir_path):
        json_dir_path = input(f"未找到路径：{json_dir_path}\n请重新输入:\n")
    else:
        output_path = os.path.join(os.path.dirname(json_dir_path), 'results')
        convert_json_to_txt(json_dir_path)
        print(f"=====>转换完成  文件保存路径为{output_path}\n=====>即将退出程序")


