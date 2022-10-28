import json
import os
from tqdm import tqdm


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_list.append(os.path.join(root, file))
            else:
                continue
    return file_list


def load_json(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def to_txt(json_path: str, txt_path: str):
    for file in tqdm(list_files(json_path)):
        file_name = os.path.splitext(os.path.basename(file))[0]
        txt_dirs = os.path.dirname(file).replace(json_path, txt_path)
        if not os.path.exists(txt_dirs):
            os.makedirs(txt_dirs, exist_ok=True)
        txt_file = os.path.join(txt_dirs, file_name + '.txt')
        txt_content = []
        json_content = load_json(file)
        boxes = json_content['result']['data']
        for box in boxes:
            label = box['label'][0]
            x_l = []
            y_l = []
            for point in box['coordinate']:
                x_l.append(point['x'])
                y_l.append(point['y'])
            txt_str = f"{label},{int(min(x_l)+0.5)} {int(min(y_l)+0.5)} {int(max(x_l)+0.5)} {int(max(y_l)+0.5)}\n"
            txt_content.append(txt_str)
        with open(txt_file, 'w', encoding='utf-8') as tf:
            tf.writelines(txt_content)



if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('json_path', type=str)
    parser.add_argument('output_path', type=str)
    args = parser.parse_args()

    json_path = args.json_path
    output_path = args.output_path

    # json_path = r"D:\Desktop\BasicProject\刘晓龙\下载结果_json_43611_more_20220930102721"
    to_txt(json_path, output_path)

