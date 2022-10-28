import pandas as pd
import json
import os
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


def json2csv(json_dir):
    for file in tqdm(list_files(json_dir)):
        csv_path = os.path.join(json_dir, 'csv_result')
        if not os.path.exists(csv_path):
            os.mkdir(csv_path)
        file_name = os.path.splitext(os.path.basename(file))[0]
        csv_file = os.path.join(csv_path, file_name + '.csv')
        json_content = load_json(file)
        boxes = json_content['result']['data']
        x_l = []
        y_l = []
        w_l = []
        h_l = []
        for box in boxes:
            w = box['width']
            h = box['height']
            iw = box['iw']
            ih = box['ih']
            ax = []
            ay = []
            for point in box['points']:
                ax.append(point['x'])
                ay.append(point['y'])
            x = min(ax)*iw
            y = min(ay)*ih
            x_l.append(x)
            y_l.append(y)
            w_l.append(w)
            h_l.append(h)
        data = {
            "x": x_l,
            "y": y_l,
            "w": w_l,
            "h": h_l
        }
        df = pd.DataFrame(data)
        df.to_csv(csv_file, index=False, sep=',')


if __name__ == '__main__':
    # json_dir = r"C:\Users\EDY\Downloads\zzq

    json_dir = input("请输入json文件路径:\n")
    json2csv(json_dir)
    input("已完成，按任意键退出")
