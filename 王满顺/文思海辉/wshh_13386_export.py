
"""
文思海辉,模板13386,点云连续帧(beta)标注，一帧一结果导出脚本
"""
import os
import json
import math
from tqdm import tqdm


def list_files(in_path: str, suffix_match: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == suffix_match:
                file_list.append(os.path.join(root, file))
            else:
                continue
    return file_list


def load_json(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        json_content = json.load(f)
    return json_content


attr_mapping = {
    "Occlusion": 'Occlusion', "Does the vehicle or animal have a rider": 'Rider',
    "Is the vehicle towing or being towed": 'Vehicle Towing', "Are any lights on? (in at least 1 frame)": 'Any Lights',
    "Are the object's reverse lights on? (in at least 1 frame)": 'Reverse Lights',
    "Are the object's brake lights on": 'Brake Lights',
    "Which turn signal indicator light is on": 'Indicator Status',
    "Does the vehicle have any door, trunk, or side panel open in any frame of the sequence": 'Door/Trunk/Panel Open',
    "Is the object parked in every frame": 'Parked',
    "Is the pedestrian a construction worker": 'Construction Worker'
}


def is_stationary(in_path):
    center_map = {}
    stationary_map = {}
    cl = []
    for file in tqdm(list_files(in_path, '.json')):
        jc = load_json(file)
        data_id = jc['data_id']
        boxes = jc['result']['data']
        for box in boxes:
            class_type = box['classType']
            if class_type == '标注类型':
                frame = box['frame']
                track_id = box['trackId']
                box_name = box['trackName']
                # if track_id in ['YP6FSWzXgnO69QWf', 'HOaVlXKjTsRlt_97']:
                #     print(f"{frame} {box_name}")

                center = box['center3D']
                point = center.values()
                if point in cl:
                    print(f"{frame} {box_name}")
                    continue
                else:
                    cl.append(point)
                if track_id not in center_map.keys():
                    center_map[track_id] = [center.values()]
                else:
                    center_map[track_id].append(center.values())
            else:
                continue
    for k, v in center_map.items():
        if len(set(v)) < 2:
            stationary_map[k] = True
        else:
            stationary_map[k] = False
    for i, j in stationary_map.items():
        if j:
            print(i)

def trans_json(in_path, point_json_path):
    mark_err = []
    for file in tqdm(list_files(in_path, '.json')):
        file_name = os.path.splitext(os.path.basename(file))[0]
        point_json_file = os.path.join(point_json_path, file_name + '.json')
        param = load_json(point_json_file)
        device_x = param['device_position']['x']
        device_y = param['device_position']['y']
        annotation = []
        jc = load_json(file)
        data_id = jc['data_id']
        boxes = jc['result']['data']
        for box in boxes:
            attributes = {}
            class_type = box['classType']
            if class_type == '标注类型':
                frame = box['frame']
                track_id = box['trackId']
                box_name = box['trackName']
                center = box['center3D']
                x = center['x']
                y = center['y']
                distance = math.sqrt((x-device_x)**2+(y-device_y)**2)
                size = box['size3D']
                heading = box['rotation3D']['z']
                point_n = box['pointN']
                attrs = box['attrs']
                if not attrs:
                    attrs_err = f"data_id:{data_id} | 第{frame}帧 | {box_name} 框缺少属性"
                    mark_err.append(attrs_err)
                    continue
                else:
                    if '动态物体' in attrs.keys():
                        label = attrs['动态物体']
                    elif '静态物体' in attrs.keys():
                        label = attrs['静态物体']
                    elif '鬼点噪点' in attrs.keys():
                        label = attrs['鬼点噪点']
                    else:
                        label_err = f"data_id:{data_id} | 第{frame}帧 | {box_name} 框缺少主标签"
                        mark_err.append(label_err)
                        continue
                    for ex in attrs.keys():
                        if ex in attr_mapping.keys():
                            if attrs[ex] == '不导出标签结果':
                                continue
                            else:
                                attributes[attr_mapping[ex]] = attrs[ex]
                        else:
                            continue

                    box = {
                        'uuid': track_id,
                        'label': label,
                        'position': center,
                        'dimensions': size,
                        'yaw': heading,
                        'stationary': False,
                        'camera_used': 3,
                        'numberOfPoints': point_n,
                        'distance_to_device': distance,
                        'attributes': attributes
                    }
                    annotation.append(box)
            else:
                continue
        final_json = {
            "cuboids": annotation
        }
        with open(file, 'w', encoding='utf-8') as nf:
            json.dump(final_json, nf)
    print(mark_err)


if __name__ == '__main__':
    in_path = r"C:\Users\EDY\Downloads\json_44247_110745_20221122165544\wshh-测试数据\3d_url - 副本"
    pount_json_path = r"D:\Desktop\Project_file\王满顺\文思海辉\test_data_cuboids\test_data_cuboids"
    trans_json(in_path, pount_json_path)

    # is_stationary(in_path)