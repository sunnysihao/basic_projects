# @Time    : 2022/10/21
# @Author  : zhangsihao@basicfinder.com

import os
from tqdm import tqdm
import json


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


def write_new_json(old_json_dir: str, check_file: str):
    label_list = []
    mark_error = []
    detection = {}
    for file in tqdm(list_files(old_json_dir)):
        annotation = []
        json_content = load_json(file)
        img_url = json_content['data']['image_url']
        image_name = os.path.basename(img_url)
        data_id = json_content['data_id']
        result_data = json_content['result']['data']
        img_width = json_content['result']['resourceinfo']['width']
        img_height = json_content['result']['resourceinfo']['height']
        if not result_data:
            abandon = 'yes'
        else:
            abandon = 'no'
            line_num = 0
            for line in result_data:
                line_id = line['id']
                label = line['label']
                category = line['category']
                int_id = line['intId']
                coordinate = line['coordinate']
                points = []
                for point in coordinate:
                    x = point['x']
                    y = point['y']
                    points.append([x, y])
                if len(label) == 5:
                    if 'type' in category:
                        line_label = label[category.index('type')]
                        label_list.append(line_label)
                    else:
                        no_type_err = f"作业id:{data_id}-{int_id}号 | 未标注类别"
                        mark_error.append(no_type_err)
                        continue
                    if 'color' in category:
                        line_color = label[category.index('color')]
                    else:
                        no_color_err = f"作业id:{data_id}-{int_id}号 | 未标注颜色"
                        mark_error.append(no_color_err)
                        continue
                    if 'ignore' in category:
                        ignore = label[category.index('ignore')]
                    else:
                        no_ignore_err = f"作业id:{data_id}-{int_id}号 | 未标注ignore"
                        mark_error.append(no_ignore_err)
                        continue
                    if 'double_line' in category:
                        double_line = label[category.index('double_line')]
                    else:
                        no_db_line_err = f"作业id:{data_id}-{int_id}号 | 未标注双线属性"
                        mark_error.append(no_db_line_err)
                        continue
                    if 'occlusion' in category:
                        occlusion = label[category.index('occlusion')]
                    else:
                        no_occlusion_err = f"作业id:{data_id}-{int_id}号 | 未标注遮挡属性"
                        mark_error.append(no_occlusion_err)
                        continue

                    box = {
                        "id": line_num, #对象 ID
                        "track_id": -1,#预留字段，暂无意义，固定取值为-1
                        "struct_type": "parsing",#标注类型，车道线标注取值为“parsing”
                        "attrs": {   #标注对象属性
                            "color": line_color,#颜色
                            "type": line_label,#类别
                            "ignore": ignore,#ignore 属性
                            "occlusion": occlusion, #遮挡属性
                            "double_line": double_line#双线属性
                            },
                        "data": points,
                        "point_attrs": [None]*len(points) # 关键点属性，预留字段，固定取值为 null，数组大小与 data 大小一致。
                    }
                    annotation.append(box)
                    line_num += 1
                else:
                    lack_attr_err = f"作业id:{data_id}-{int_id}号 | 属性标注不足"
                    mark_error.append(lack_attr_err)
                    continue

        image_data = {
            "image_key": image_name,
            "video_name": "",#预留字段，暂无意义，固定取值为空字符串
            "video_index": "",#预留字段，暂无意义，固定取值为空字符串
            "width": img_width,#图片宽度
            "height": img_height,#图片高度
            "abandoned": abandon, #默认为"no"
            "parsing": annotation   #标注对象数组，全图无标注对象时，数组为空
        }

        with open(file, 'w', encoding='utf-8') as rf:
            rf.write(json.dumps(image_data))

    label_set = set(label_list)
    detection["总标签数"] = f"{len(label_list)}"
    for one_label in label_set:
        detection[f"{one_label}"] = label_list.count(one_label)
    detection_info = {
        "count_label": detection,
        "marking_errors": mark_error
    }
    if not os.path.exists(check_file):
        with open(check_file, 'w', encoding='utf-8') as df:
            df.write(json.dumps(detection_info))
    else:
        with open(check_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            detection_content = json.loads(content)
            detection_content['detection_info'] = detection_info
            with open(check_file, 'w', encoding='utf-8') as df:
                df.write(json.dumps(detection_content))

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('old_json_dir', type=str)
    parser.add_argument('check_file', type=str)
    args = parser.parse_args()

    old_json_dir = args.old_json_dir
    check_file = args.check_file

    # old_json_dir = r"D:\Desktop\BasicProject\季鑫窈\理想\车道线2d一帧一结果\车道线.rar - 副本"
    # check_file = r"D:\Desktop\BasicProject\季鑫窈\理想\车道线2d一帧一结果\车道线.rar - 副本\check_file.json"

    write_new_json(old_json_dir, check_file)
