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

label_mapping = {
    "Pedestrian": 20,
    "Bicycle": 20,
    "Car": 18,
    "Bus": 25,
    "Truck": 25,
    "Tricycle": 20,
    "Motorcycle": 20
}
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
    result_dir = os.path.join(os.path.dirname(in_path), 'result')
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)
    all_err = {}
    for _dir in list_dir(in_path):

        batch_err = {}
        json_path = os.path.join(in_path, _dir, '3d_url')
        set_name = _dir
        result_path1 = os.path.join(result_dir, set_name)
        if not os.path.exists(result_path1):
            os.mkdir(result_path1)
        result_path = os.path.join(result_path1, '3d_url')
        if not os.path.exists(result_path):
            os.mkdir(result_path)

        # job_list = []
        frame_count = 0

        for file in list_files(json_path):

            json_file = os.path.join(json_path, file + '.json')
            json_content = load_json(json_file)
            batch_id = json_content['data_id']
            frame_number = json_content['data']['frameNumber'] + 1
            boxs = json_content['result']['data']
            annotations = []
            one_file_err = []
            for box in boxs:  # 读取每个3D框数据
                x, y, z = box['3Dcenter'].values()
                nx, ny, nz = box['3Dsize'].values()
                alpha = box['3Drotation']['z']
                int_id = box['intId']
                job_id = box['cBy']
                label = box['classType']
                point_num = box['pointN']
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
            new_json_file = os.path.join(result_path, file + '.json')
            if not one_file_err:  # 若此文件未检测出标注错误，则转换文件，否则记录错误文件
                with open(new_json_file, 'w', encoding='utf-8') as nf:
                    nf.write(json.dumps(annotations))
            else:

                # job_list.append(job_id)
                one_job_err = {}
                if f"第{frame_number}帧" not in one_job_err.keys():
                    one_job_err[f"第{frame_number}帧"] = [one_file_err]
                else:
                    one_job_err[f"第{frame_number}帧"].append(one_file_err)

                if f"{batch_id}" not in batch_err.keys():
                    batch_err[f"{batch_id}"] = [one_job_err]
                else:
                    batch_err[f"{batch_id}"].append(one_job_err)

                continue

            frame_count += 1
        print(f"{set_name}===>共{frame_count}帧数据转换完成\n文件保存路径为：{result_path}")

        if f"{set_name}" not in all_err.keys():
            all_err[f"{set_name}"] = [batch_err]
        else:
            all_err[f"{set_name}"].append(batch_err)

    error = {
            "errors": all_err
        }
    err_file = os.path.join(os.path.dirname(in_path), 'errors.json')

    with open(err_file, 'w', encoding='utf-8') as ef:
        ef.write(json.dumps(error))


if __name__ == "__main__":
    json_files_path = input("请输入平台'3D一帧一结果'脚本打包的原结果文件夹路径:\n")
    while not os.path.exists(json_files_path):
        print(f"未找到路径：{json_files_path} ")
        json_files_path = input("请重新输入:\n")
    else:
        write_json(json_files_path)
        input("程序执行完成，按任意键退出")
