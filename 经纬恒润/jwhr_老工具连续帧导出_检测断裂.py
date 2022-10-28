# _*_ coding=: utf-8 _*_
# @Time    : 2022/07/19
# @Author  : zhangsihao@basicfinder.com
"""
功能：经纬恒润老点云连续帧结果结果导出，检测含‘断裂’标签的pcd文件，针对平台'3D一帧一结果'脚本打包的数据进行转换导出。
使用方法：
    运行程序，根据命令提示输入对应信息，输出文件在原路径下。
"""
import json
import os
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
    errors = ["含'断裂'标签的pcd文件:\n"]
    for file in tqdm(list_files(in_path), desc='进度', leave=True, unit='file', colour='red'):
        json_content = load_json(file)
        pcd_name = json_content['data']['3d_url'].split('/')[-1]
        boxs = json_content['result']['data']
        annotations = []
        for box in boxs:  # 读取每个3D框数据
            x, y, z = box['3Dcenter'].values()
            nx = box['3Dsize']['height']
            ny = box['3Dsize']['width']
            nz = box['3Dsize']['deep']
            alpha = box['3Dsize']['alpha']
            label = box['attr']['label']
            if not label:
                label = 'null'
            else:
                if '断裂' in label:
                    error = f"{pcd_name}\n"
                    errors.append(error)
                    label = label[0]
                else:
                    label = label[0]
            box_data = {
                "name": label,
                "bbox_center": [x, y, z],
                "bbox_size": [nx, ny, nz],
                "heading": alpha
            }
            annotations.append(box_data)
        with open(file, 'w', encoding='utf-8') as nf:
            nf.write(json.dumps(annotations))
    detection_info_file = os.path.join(in_path, 'detection_info.txt')
    with open(detection_info_file, 'w', encoding='utf-8') as df:
        df.writelines(errors)

if __name__ == "__main__":
    json_files_path = input("请输入平台'3D一帧一结果'脚本打包的原结果文件夹路径:\n")
    while not os.path.exists(json_files_path):
        print(f"未找到路径：{json_files_path} ")
        json_files_path = input("请重新输入:\n")
    else:
        write_json(json_files_path)
    input("程序执行完成，按任意键退出")
