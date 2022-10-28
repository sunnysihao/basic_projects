# _*_ coding=: utf-8 _*_
# @Time    : 2022/07/21
# @Author  : zhangsihao@basicfinder.com
"""
功能：六安智梭点云标注结果导出，针对平台'Json(一作业一结果)'脚本打包的数据进行转换导出。
使用方法：pip install tqdm
    运行程序，根据命令提示输入对应文件路径。
"""
import os
import json
import math
from tqdm import tqdm

def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_name = os.path.splitext(file)[0]
                file_list.append(file_name)
            else:
                continue
    return file_list


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
    count = 0
    detection = []
    for dir1 in list_dir(in_path):
        count2 = 0
        result_path1 = os.path.join(in_path, 'data')
        if not os.path.exists(result_path1):
            os.mkdir(result_path1)
        result_path2 = os.path.join(result_path1, dir1)
        if not os.path.exists(result_path2):
            os.mkdir(result_path2)
        result_path = os.path.join(result_path2, 'label')
        if not os.path.exists(result_path):
            os.mkdir(result_path)

        for dir2 in list_dir(os.path.join(in_path, dir1)):
            json_dir = os.path.join(in_path, dir1, dir2, '3d_url')
            for file in tqdm(list_files(json_dir), desc=f'{dir1}/{dir2}', leave=True, unit='file', colour='blue'):
                data = []
                json_file = os.path.join(json_dir, file + '.json')
                json_content = load_json(json_file)
                job_id = json_content['data_id']
                boxs = json_content['result']['data']
                for box in boxs:  # 读取每个3D框数据
                    int_id= box['intId']
                    label_list = box['attr']['label']
                    if not label_list:
                        label = 'null'
                        err_str = f"{dir1}批次-{job_id}作业-{int_id}号框标签为空"
                        detection.append(err_str)
                    else:
                        label = label_list[0]
                    x, y, z = box['3Dcenter'].values()
                    l = box['3Dsize']['height']
                    w = box['3Dsize']['width']
                    h = box['3Dsize']['deep']
                    alpha = alpha_in_pi(box['3Dsize']['alpha'])


                    box_data = {
                        "label": label,
                        "xyz": [x, y, z],
                        "lwh": [l, w, h],
                        "yaw": alpha
                    }
                    data.append(box_data)

                new_json_file = os.path.join(result_path, file + '.json')
                with open(new_json_file, 'w', encoding='utf-8') as f:
                    f.write(json.dumps(data))
                count += 1
                count2 += 1
        print(f"* * * * * * * * * * * * * * * * * * * * \n{dir1}----共 {count2} 个结果"
              f"\n保存路径为：{result_path}\n* * * * * * * * * * * * * * * * * * * * * * * * * ")
    with open(os.path.join(in_path, 'detection_information' + '.txt'), 'w', encoding='utf-8') as ef:
        ef.writelines(detection)
    print(f"---------------------------------------------------------------------\n共完成{count}个文件")


if __name__ == "__main__":
    in_files_path = input("请输入平台'3D一帧一结果'脚本打包的原结果文件夹路径:\n")
    while not os.path.exists(in_files_path):
        print(f"未找到路径：{in_files_path} ")
        in_files_path = input("请重新输入:\n")
    else:
        print("===>开始转换\n---------------------------------------------------------------------")
        write_json(in_files_path)
        input("程序运行完成\n按任意键退出")



