import os
import json
import math
from tqdm import tqdm


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_list.append(os.path.join(root, file))
    return file_list


def alpha_in_pi(alpha):
    pi = math.pi
    return alpha - math.floor((alpha + pi) / (2 * pi)) * 2 * pi


def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


image_index_mapping = {
    "0": 'img_n',
    "1": 'img_w'
}


def update_json(json_dir: str, check_file: str):
    num = 1
    detection = []
    for file in tqdm(list_files(json_dir)):
        json_content = load_json(file)
        data = json_content['data']
        create_data = data['3d_url']
        data_id = json_content['data_id']
        pcd_name = create_data.split('/')[-1]
        img_n = data['3d_img0'].split('/')[-1]
        img_w = data['3d_img1'].split('/')[-1]
        boxes = json_content['result']['data']
        traffic_light = []

        id_mapping = {}

        for box in boxes:
            uuid = box['id']
            track_id = box['trackId']
            objtype = box['objType']
            intid = int(box['trackName'])
            if objtype == '3d':
                center3d = box['center3D']
                rx = box['rotation3D']['x']
                ry = box['rotation3D']['y']
                rz = box['rotation3D']['z']
                length = box['size3D']['x']
                width = box['size3D']['y']
                height = box['size3D']['z']
                alpha = alpha_in_pi(box['rotation3D']['z'])
                label = box['classType']
                attrs = box['attrs']

                if -0.1 < rx < 0.1 and -0.1 < ry < 0.1:
                    if not attrs:
                        little_class = "un"
                        relevance = 'un'
                        occupied = 'un'
                        group = 'un'
                    else:
                        if '??????' in attrs.keys():
                            little_class = attrs['??????']
                        elif 'invisible' in attrs.keys():
                            little_class = attrs['invisible']
                        else:
                            little_class = "un"
                        if 'Relevance' in attrs.keys():
                            relevance = attrs['Relevance']
                        else:
                            relevance = 'un'
                        if 'Occupied' in attrs.keys():
                            occupied = attrs['Occupied']
                        else:
                            occupied = 'un'
                        if 'Group' in attrs.keys():
                            group = attrs['Group']
                        else:
                            group = 'un'

                    one_light = {
                        "object_id": intid,
                        "3Dcenter": center3d,
                        "3Dsize": {
                            "width": width,
                            "length": length,
                            "height": height,
                            "alpha": alpha,
                            "rx": 0,
                            "ry": 0,
                            "rz": rz
                        },
                        "super_class": label,
                        "class": little_class,
                        "relevance": relevance,
                        "occupied": occupied,
                        "group": group,
                        "uuid": uuid,
                        "track_id": track_id,
                        "data_id": data_id,
                        "2Dbbox": []
                    }

                    id_mapping[track_id] = one_light
                else:
                    mark_err_str = f"??????id:{data_id}-{intid}????????????????????????"
                    detection.append(mark_err_str)
                    continue
            else:
                continue

        for rect in boxes:
            track_id = rect['trackId']
            objtype = rect['objType']
            viewIndex = rect['viewIndex']
            intid = int(rect['trackName'])
            if objtype == '3d':
                continue
            else:
                if track_id in id_mapping.keys():
                    x_l = []
                    y_l = []
                    for point in rect['points']:
                        x_l.append(point['x'])
                        y_l.append(point['y'])
                    rl = min(x_l)
                    rt = min(y_l)
                    rw = max(x_l) - min(x_l)
                    rh = max(y_l) - min(y_l)

                    box_2d = {
                        "l": rl / 3840,
                        "t": rt / 2140,
                        "w": rw / 3840,
                        "h": rh / 2140,
                        "rl": rl,
                        "rt": rt,
                        "rw": rw,
                        "rh": rh,
                        "isBbox": True,
                        "image_index": image_index_mapping[f"{viewIndex}"]
                    }
                    id_mapping[track_id]['2Dbbox'].append(box_2d)

                else:
                    only_rect_str = f"??????id:{data_id}-{intid}??????????????????"
                    detection.append(only_rect_str)
                    continue

        for va in id_mapping.values():
            traffic_light.append(va)


        info = {
            "object_number": num,
            "3d_url": pcd_name,
            "2d_img_n": img_n,
            "2d_img_w": img_w
        }

        final_content = {
            "head": {
                "descriptioin": "default",
                "created_data": create_data,
                "supplier": "BeiSai"
            },
            "info": info,
            "traffic_light": traffic_light
        }
        num += 1
        with open(file, 'w', encoding='utf-8') as nf:
            nf.write(json.dumps(final_content))

    detection_info = {
        "marking_detection": detection
    }
    if not os.path.exists(check_file):
        with open(check_file, 'w', encoding='utf-8') as df:
            df.write(json.dumps(detection_info, ensure_ascii=False))
    else:
        with open(check_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            detection_content = json.loads(content)
            detection_content['detection_info'] = detection_info
            with open(check_file, 'w', encoding='utf-8') as df:
                df.write(json.dumps(detection_content, ensure_ascii=False))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('json_dir', type=str)
    parser.add_argument('check_file', type=str)
    args = parser.parse_args()

    json_dir = args.json_dir
    check_file = args.check_file
    # json_dir = r"C:\Users\EDY\Downloads\????????????_json_43957_109376_20221017110119\third_20220927.zip\third_20220927 - ??????"
    # check_file = r"C:\Users\EDY\Downloads\????????????_json_43957_109376_20221017110119\third_20220927.zip\third_20220927 - ??????\check file.json"
    update_json(json_dir, check_file)
