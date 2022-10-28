import os
import json
from tqdm import tqdm


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_list.append(os.path.join(root, file))
    return file_list


def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def fu(path):
    l = []
    for file in list_files(path):
        json_content = load_json(file)
        rs = json_content['markResult']['features']
        for r in rs:
            label = r['properties']['content']['label']
            l.append(label)
    print(set(l))


path = r"C:\Users\EDY\Downloads\json_44194_more_20221026173640"
fu(path)
