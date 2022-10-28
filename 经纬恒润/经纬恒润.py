# _*_ coding=: utf-8 _*_
import os
import json
import re
import math
import pandas as pd


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list


# pcd,json,jpg文件按pcd文件名重命名
def rename_files(pcd_path, other_path):
    file_name_list = list_files(pcd_path)
    for file in list_files(other_path):
        for new_name in file_name_list:
            regex = re.compile(file)
            if re.findall(regex, new_name):
                os.rename(os.path.join(other_path, file + '.jpg'), os.path.join(other_path, new_name + '.jpg'))
            else:
                continue


def load_json(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


# 带结果的json转为平台反显示json格式
def write_data_to_json(old_json_path: str, save_path: str):
    for file in list_files(old_json_path):
        json_data = load_json(os.path.join(old_json_path, file + '.json'))
        result_data = []
        for box in json_data:
            x, y, z = box['bbox_center']
            height, width, deep = box['bbox_size']
            alpha = box['heading']
            label = box['name']
            box_data = {
                        "3Dcenter": {
                            "x": x,
                            "y": y,
                            "z": z
                        },
                        "3Dsize": {
                            "width": width,
                            "height": height,
                            "deep": deep,
                            "alpha": alpha
                        },
                        "attr": {
                            "category": [
                                label
                            ],
                            "label": [
                                label
                            ],
                            "code": [
                                label
                            ]
                        }
            }
            result_data.append(box_data)
        new_json_data = {
            "data": {
                "3d_url": file + '.pcd',
                "3d_img0": file + '.jpg'
            },
            "result": {
                "data": result_data
            }
        }

        with open(os.path.join(save_path, file + ".json"), 'w', encoding='utf-8') as f:
            f.write(json.dumps(new_json_data))

# 生成统计结果各类标签的3D框数量的txt文件
def statistical_results(json_dir: str, txt_path: str):
    with open(txt_path, 'a+', encoding='utf-8') as txt_f:
        for file in list_files(json_dir):
            json_content = load_json(os.path.join(json_dir, file + '.json'))
            label = ['Headstock', 'EmptyTrailer', 'Car', 'Pole', 'FullTrailer', 'IndicatorBoard',
                     'BlockOfStone', 'Other_Vehicle_Car', 'Other_Vehicle_Trailer', 'Pedestrian']
            label_list = []
            list_count_label = []
            for box in json_content['result']['data']:
                label_list.append(box['attr']['label'][0])
            for label_name in label:
                if label_name not in label_list:
                    label_name_count = 0
                else:
                    label_name_count = label_list.count(label_name)

                list_count_label.append(label_name + ' ' + str(label_name_count))
            total_count = len(json_content['result']['data'])
            string = f"\n{file} 3d_cube {total_count} {' '.join(list_count_label)}"
            txt_f.write(string)
# 结构化的txt数据转为excel表格
def txt2excel(txt_path, excel_path):
    df = pd.read_table(txt_path, header=None, sep=' ')
    df.to_excel(excel_path)

if __name__ == "__main__":
    # old_json_path = r"D:\Desktop\BasicProject\任从辉\经纬恒润\right_lidar\old"
    # save_path = r"D:\Desktop\BasicProject\任从辉\经纬恒润\right_lidar\ai_result"
    # write_data_to_json(old_json_path, save_path)

    # old_path = r"D:\Desktop\BasicProject\任从辉\经纬恒润 0613\经纬恒润 0613\right_lidar"
    # new_path = r"D:\Desktop\BasicProject\任从辉\经纬恒润\right_lidar\3d_img0"
    #
    # rename_files(old_path, new_path)
    for lidar in ['left_lidar', 'right_lidar', 'innoviz_lidar']:

        json_dir = rf"D:\Desktop\BasicProject\任从辉\经纬恒润\{lidar}\ai_result"
        txt_path = r"D:\Desktop\BasicProject\任从辉\经纬恒润\经纬恒润数据统计模板 V2.0.txt"
        statistical_results(json_dir, txt_path)
