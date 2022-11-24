# -*- coding: utf-8 -*- 
# @Time : 2022/11/24
# @Author : zhangsihao@basicfinder.com
"""
"""
import os
import json
from tqdm import tqdm
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString


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


def json2xml(json_dir, xml_dir):
    mark_err = []
    for file in tqdm(list_files(json_dir, '.json')):
        file_name = os.path.splitext(os.path.basename(file))[0]
        object = []
        jc = load_json(file)
        data_id = jc['data_id']
        img_url = jc['data']['image_url']
        width = jc['result']['resourceinfo']['width']
        height = jc['result']['resourceinfo']['height']
        folder = img_url.split('/')[-3]
        boxes = jc['result']['data']
        for box in boxes:
            int_id = box['intId']
            label = box['label']
            if not label:
                label_err = f"{data_id} | {int_id}框 未选择标签"
                mark_err.append(label_err)
                continue
            else:
                name = label[0]
                xl = []
                yl = []
                for point in box['coordinate']:
                    xl.append(point['x'])
                    yl.append(point['y'])

            obj = {
                "name": name,
                "pose": "Unspecified",
                "truncated": "0",
                "difficult": "0",
                "bndbox": {
                    "xmin": min(xl),
                    "ymin": min(yl),
                    "xmax": max(xl),
                    "ymax": max(yl)
                }
            }
            object.append(obj)


        final_data = {
             "folder": folder,
             "filename": file_name + '.jpg',
             "path": img_url,
             "source": {
                 "database": "Unknown"
             },
             "size": {
                 "width": width,
                 "height": height,
                 "depth": "3"
             },
             "segmented": "0",
             "object": object
        }
        xml_file = os.path.join(xml_dir, file_name + '.xml')
        my_item_func = lambda x: 'object'
        xml = dicttoxml(final_data, custom_root='Annotations', item_func=my_item_func, attr_type=False)
        dom = parseString(xml)
        with open(xml_file, 'w', encoding='UTF-8') as xml_file:
            xml_file.write(dom.toprettyxml())


if __name__ == '__main__':
    json_dir = r"C:\Users\EDY\Downloads\下载结果_json_44993_113842_20221124121357\yolo-data.rar\yolo-data\20221118"
    xml_dir = r"C:\Users\EDY\Downloads\下载结果_json_44993_113842_20221124121357\yolo-data.rar\yolo-data\xml"
    json2xml(json_dir, xml_dir)
