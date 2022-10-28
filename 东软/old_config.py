# _*_ coding=: utf-8 _*_
# _*_ coding=: utf-8 _*_
"""
功能：新老点云工具相机参数互转。
使用方法: pip install numpy
    运行程序，在命令行输入 old to new 选择老点云工具相机参数转新工具相机参数;
                       或  new to old 选择新点云工具相机参数转老工具相机参数,按enter确认。
备注：
    老点云工具相机参数转新工具相机参数文件保存文件夹为"new_camera_config"
    新点云工具相机参数转老工具相机参数文件保存文件夹为"old_camera_config"
"""
import os
import json
import numpy as np
from numpy.linalg import inv


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':  # 只读取.json后缀的文件
                file_list.append(file)
            else:
                continue
    return file_list


def load_json(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


# 老点云工具相机参数转新点云工具相机参数
def convert_parameters_old_to_new(camera_config_path: str):
    result_path = os.path.join(camera_config_path, '../new_camera_config')
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    for file in list_files(camera_config_path):
        json_file = os.path.join(camera_config_path, file)
        json_content = load_json(json_file)
        num = len(json_content)
        data = {}
        for i in range(num):
            cam_int = json_content[f"3d_img{i}"]['camera_internal']
            cam_ext = json_content[f"3d_img{i}"]['camera_external']
            cam_ext = np.asarray(cam_ext).reshape((4, 4))
            cam_ext = inv(cam_ext)
            one_data = {
                    "camera_internal": cam_int,
                    "camera_external": cam_ext.flatten().tolist()
            }
            data[f"3d_img{i}"] = one_data
        with open(os.path.join(result_path, file), 'w', encoding='utf-8') as f:
            f.write(json.dumps(data))


# 新点云工具相机参数转老点云工具相机参数
def convert_parameters_new_to_old(camera_config_path: str):
    result_path = os.path.join(camera_config_path, '../old_camera_config')
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    for file in list_files(camera_config_path):
        json_file = os.path.join(camera_config_path, file)
        json_content = load_json(json_file)
        num = len(json_content)
        data = {}
        for i in range(num):
            cam_int = json_content[f"3d_img{i}"]['camera_internal']
            cam_ext = json_content[f"3d_img{i}"]['camera_external']
            cam_ext = np.asarray(cam_ext).reshape((4, 4))
            cam_ext = inv(cam_ext.T)
            one_data = {
                    "camera_internal": cam_int,
                    "camera_external": cam_ext.flatten().tolist()
            }
            data[f"3d_img{i}"] = one_data
        with open(os.path.join(result_path, file), 'w', encoding='utf-8') as f:
            f.write(json.dumps(data))


def main():
    t = input("请选择老平台相机转新平台相机参数or新平台相机参数转老平台相机参数:\n(老平台转新平台请输入: old to new / 新平台转老平台请输入: new to old ---按enter结束）\n")
    while t not in ['old to new', 'new to old']:
        print("输入不正确，请重新输入:")
        t = input()
    else:
        if t == 'old to new':
            camera_config_path = input("请输入原'camera_config'文件夹路径:\n")
            print("-------------------------------------------------------------")
            convert_parameters_old_to_new(camera_config_path)
            save_path = os.path.join(os.path.dirname(camera_config_path), 'new_camera_config')
            print(f"===>老点云工具相机参数 转 新点云工具相机参数转换完成\n保存路径为 {save_path}")

        else:
            new_camera_config_path = input("请输入原'camera_config'文件夹路径:\n")
            print("-------------------------------------------------------------")
            convert_parameters_new_to_old(new_camera_config_path)
            save_path = os.path.join(os.path.dirname(new_camera_config_path), 'old_camera_config')
            print(f"===>新点云工具相机参数 转 老点云工具相机参数转换完成\n保存路径为 {save_path}")


if __name__ == "__main__":
    main()
