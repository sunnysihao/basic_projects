# _*_ coding=: utf-8 _*_
import os
import json

# 根据路径列出当前路径下所有的文件名(不含后缀名)
def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list


# 读取json文件内容返回python类型的对象
def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


# 生成单独的每个视角个相机参数json文件
def write_single_config(config_file, x):
    file = os.path.basename(config_file)
    single_config = os.path.join(os.path.dirname(os.path.dirname(config_file)), "single_configs")
    if not os.path.exists(single_config):
        os.makedirs(single_config)
    json_content = load_json(config_file)
    data = json_content
    for i in range(x):

        single_data = {
            "3d_img0": data[f'3d_img{i}']
        }
        with open(os.path.join(single_config, file + f'-{i}' + '.json'), 'w', encoding='utf-8') as sf:
            sf.write(json.dumps(single_data))

config_file = r"C:\Users\EDY\Downloads\pilot_Data-20221108T101954Z-001\pilot_Data\sequence_frames_curve_1hz_new\camera_config\310.json"
write_single_config(config_file, 3)
