import json
import os
from tqdm import tqdm


def list_files(in_path: str, match):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == match:
                file_list.append(os.path.join(root, file))
    return file_list


def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def main(pcd_path, json_file):
    json_content = load_json(json_file)
    json_data = []
    for obj in json_content.keys():
        json_data.append(json_content[obj])
    for file in list_files(pcd_path, '.pcd'):
        file_name = os.path.splitext(os.path.basename(file))[0]
        json_file = os.path.join(os.path.dirname(os.path.dirname(file)), 'camera_config', file_name + '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f)


if __name__ == '__main__':
    pcd_path = r"D:\result_file\result_file\point_cloud"
    json_file = r"D:\result_file\result_file\hxzn_camera_config_0929.json"
    main(pcd_path, json_file)
