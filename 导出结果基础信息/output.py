# _*_ coding=: utf-8 _*_
'''
功能：点云标注项目，将平台导出结果转为只包含基础信息的json文件
基础信息有：3D框中心点坐标、3D框尺寸（长宽高）、方向、标签、截断值、遮挡值
'''
import os
import json


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list


def load_json(json_path:str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def write_data_to_json(json_path: str):
    result_path = os.path.join(os.path.dirname(json_path), 'json_result_output')
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    for file in list_files(json_path):
        old_json_file = os.path.join(json_path, file + '.json')
        json_content = load_json(old_json_file)
        result_data = []
        for box in json_content['result']['data']:
            x, y, z = box['3Dcenter']['x'], box['3Dcenter']['y'], box['3Dcenter']['z']
            length, width, height = box['3Dsize']['x'], box['3Dsize']['y'], box['3Dsize']['z']
            pitch, roll, yaw = box['3Drotation']['x'], box['3Drotation']['y'], box['3Drotation']['z']
            attrs, class_type = box['attrs'], box['classType']
            box_data = {
                "position": {  # 3D框中心点坐标
                    "x": x,
                    "y": y,
                    "z": z
                },
                "dimension": {  # 3D框尺寸，长宽高
                    "length": length,
                    "width": width,
                    "height": height
                },
                "rotation": {  # 3D框方向（欧拉角）
                    "pitch": pitch,
                    "roll": roll,
                    "yaw": yaw
                },
                "property": {  # 属性
                    "category": attrs,
                    "label": class_type
                }
            }
            result_data.append(box_data)
        o_data = json_content['data']
        new_json_data = {
            "data": o_data,
            "result": {
                "data": result_data
            }
        }
        result_file = os.path.join(result_path, file + ".json")
        with open(result_file, "w", encoding='utf-8') as f:
            f.write(json.dumps(new_json_data))


if __name__ == "__main__":
    json_path = r"C:\Users\EDY\Downloads\json_41462_88867_20220629121727\毫末测试 06.28\3d_url"  # bin文件夹路径
    write_data_to_json(json_path)
