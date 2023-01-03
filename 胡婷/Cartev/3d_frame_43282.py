import json
import os
from tqdm import tqdm


def load_json(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_list.append(os.path.join(root, file))
    return file_list


color_mapping = {
    "vehicle": "#9370db",
    "pedestrian_sitting": "#48d1cc",
    "pedestrian_standing": "#0000cd",
    "cyclist": "#ba55d3",
    "baby_carriage": "#c71585",
    "vehicle_occluded": '#EA1A1A',
    "pedestrian_wheelchair": '#5D4037',
    "pedestrian_scooter": '#0D94AA'
}

def json_format(json_dir):
    err_empty = []
    for file in tqdm(list_files(json_dir)):
        json_content = load_json(file)
        data = json_content['data']
        boxes = json_content['result']['data']
        data_id = json_content['data_id']
        new_box = []
        for box in boxes:
            center3d = box['center3D']
            height = box['size3D']['x']
            width = box['size3D']['y']
            deep = box['size3D']['z']
            rx = box['rotation3D']['x']
            ry = box['rotation3D']['y']
            rz = box['rotation3D']['z']
            index = box['id']
            cby = box['cBy']
            cTime = box['cTime']
            cStep = box['cStep']
            mBy = box['mBy']
            mTime = box['mTime']
            mStep = box['mStep']
            eBy = box['eBy']
            eTime = box['eTime']
            eStep = box['eStep']
            vBy = box['vBy']
            vTime = box['vTime']
            vStep = box['vStep']
            label = box['classType']
            intid = int(box['trackName'])
            type_b = box['type']
            frame = box['frame']
            if not label:
                empty_str = f"作业id:{data_id}-第{frame + 1}帧-{intid}框标签为空\n"
                err_empty.append(empty_str)
                continue
            else:
                color = color_mapping[label]

            box_data = {
                "3Dcenter": center3d,
                "3Dsize": {
                    "width": width,
                    "height": height,
                    "deep": deep,
                    "alpha": rz,
                    "rx": rx,
                    "ry": ry,
                    "rz": rz
                },
                "index": index,
                "cBy": cby,
                "cTime": cTime,
                "cStep": cStep,
                "mBy": mBy,
                "mTime": mTime,
                "mStep": mStep,
                "eBy": eBy,
                "eTime": eTime,
                "eStep": eStep,
                "vBy": vBy,
                "vTime": vTime,
                "vStep": vStep,
                "attr": {
                    "category": [
                        label
                    ],
                    "color": color,
                    "label": [
                        label
                    ],
                    "code": [
                        label
                    ]
                },
                "intId": intid,
                "points": [],
                "cubeMap": [],
                "imageMap": [],
                "type": type_b,
                "id": index,
                "frame": frame
            }
            new_box.append(box_data)
        new_json_content = {
            "data": data,
            "result": {
                "data": new_box
            }
        }
        with open(file, 'w', encoding='utf-8') as nf:
            nf.write(json.dumps(new_json_content))
    err_empty_file = os.path.join(json_dir, 'empty_labels.txt')
    with open(err_empty_file, 'w', encoding='utf-8') as ef:
        ef.writelines(err_empty)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('result_json_path', type=str)
    args = parser.parse_args()

    json_dir = args.result_json_path

    # json_dir = r"C:\Users\Administrator\Downloads\cartev"
    json_format(json_dir)
