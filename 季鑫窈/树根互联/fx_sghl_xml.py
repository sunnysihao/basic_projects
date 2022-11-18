# -*- coding: utf-8 -*- 
# @Time : 2022/11/16
# @Author : zhangsihao@basicfinder.com
"""
"""
import os
import json
import uuid
import xmltodict
from tqdm import tqdm
from PIL import Image


label_cate_mapping = {
    "head": '人头', "person": '人体', "helment": '特指安全帽', "hat": '除安全帽外的所有帽子', "face": '人脸',
    "mask": '戴口罩的人脸', "cigarette": '香烟', "smog": '烟雾', "fire": '火苗', "uniform": '特指反光衣',
    "nonUniform": '除反光衣外的所有上衣', "phone": '手机', "glass": '护目镜、眼镜', "block": '拥堵物', "earflap": '黑色耳罩'
}


def list_files(in_path: str, match):
    file_name_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == match:
                file_name_list.append(os.path.join(root, file))
    return file_name_list


def parse_xml(xml_file):
    #获取xml文件
    xml_file = open(xml_file, 'r')
    #读取xml文件内容
    xml_str = xml_file.read()
    #将读取的xml内容转为json
    json = xmltodict.parse(xml_str)
    return json['annotation']


def parse_result(xml_file, image_file):
    content = parse_xml(xml_file)
    file_name = os.path.splitext(os.path.basename(xml_file))[0] + '.png'
    iw, ih = Image.open(image_file).size
    result_data = []
    int_id = 1
    boxes = content['object']
    if type(boxes) == list:
        for box in boxes:
            label = box['name']
            code = label_cate_mapping[label]
            coor = box['bndbox']
            x = float(coor['xmin'])
            y = float(coor['ymin'])
            x1 =float(coor['xmax'])
            y1 =float(coor['ymax'])
            w = x1-x
            h = y1-y
            box_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, file_name + str(int_id)))
            box = {
                "type": 'rect',
                "id": box_id,
                "color": "",
                "label": [label],
                "code": [code],
                "category": [label],
                "catetips": [code],
                "label_id": [],
                "text": "",
                "labelAttrs": [],
                "width": w,
                "height": h,
                "area": w*h,
                "intId": int_id,
                "points": [
                    {
                        "x": x/iw,
                        "y": y/ih
                    },
                    {
                        "x": x1/iw,
                        "y": y/ih,
                    },
                    {
                        "x": x1/iw,
                        "y": y1/ih
                    },
                    {
                        "x": x/iw,
                        "y": y1/ih
                    }
                ],
                "coordinate": [
                    {
                      "x": x,
                      "y": y
                    },
                    {
                      "x": x1,
                      "y": y
                    },
                    {
                      "x": x1,
                      "y": y1
                    },
                    {
                      "x": x,
                      "y": y1
                    }
                ],
                "ih": iw,
                "iw": ih
            }
            result_data.append(box)
            int_id += 1
    # 当只有一条结果的时候 boxes是字典
    else:
        box = boxes
        label = box['name']
        code = label_cate_mapping[label]
        coor = box['bndbox']
        x = float(coor['xmin'])
        y = float(coor['ymin'])
        x1 = float(coor['xmax'])
        y1 = float(coor['ymax'])
        w = x1 - x
        h = y1 - y
        box_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, file_name + str(int_id)))
        box = {
            "type": 'rect',
            "id": box_id,
            "color": "",
            "label": [label],
            "code": [code],
            "category": [label],
            "catetips": [code],
            "label_id": [],
            "text": "",
            "labelAttrs": [],
            "width": w,
            "height": h,
            "area": w * h,
            "intId": int_id,
            "points": [
                {
                    "x": x / iw,
                    "y": y / ih
                },
                {
                    "x": x1 / iw,
                    "y": y / ih,
                },
                {
                    "x": x1 / iw,
                    "y": y1 / ih
                },
                {
                    "x": x / iw,
                    "y": y1 / ih
                }
            ],
            "coordinate": [
                {
                    "x": x,
                    "y": y
                },
                {
                    "x": x1,
                    "y": y
                },
                {
                    "x": x1,
                    "y": y1
                },
                {
                    "x": x,
                    "y": y1
                }
            ],
            "ih": iw,
            "iw": ih
        }
        result_data.append(box)
        int_id += 1

    data = {
        "data": {
            "image_url": file_name
        },
        "result": {
            "data": result_data,
            "groupinfo": [],
            "resourceinfo": {
                "width": iw,
                "height": ih,
                "rotation": 0
            },
            "data_deleted_file": ""
        }
    }
    return data


def main(total_path):
    img_path = os.path.join(total_path, 'img')
    txt_path = os.path.join(total_path, 'txt')
    match = '.png'
    for img_file in tqdm(list_files(img_path, match)):
        txt_file = img_file.replace(img_path, txt_path).replace(match, '.txt')
        exc_json = img_file.replace(match, '.json')
        if not os.path.exists(txt_file):
            print(f"{txt_file}不存在")
        else:
            data = parse_result(txt_file, img_file)
            with open(exc_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)


def main2(total_path):
    for img_file in tqdm(list_files(total_path, '.png')):
        xml_file = img_file.replace('.png', '.xml')
        exc_json = img_file.replace('.png', '.json')
        if not os.path.exists(xml_file):
            print(f"{xml_file}不存在")
        else:
            data = parse_result(xml_file, img_file)
            with open(exc_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='arg parser')
    parser.add_argument('total_dir', type=str, help='total directory')
    args = parser.parse_args()
    total_path = args.total_dir
    # total_path = r"D:\Desktop\Project_file\季鑫窈\测试\测试"
    main2(total_path)
