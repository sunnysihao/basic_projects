# -*- coding: utf-8 -*- 
# @Time : 2022/11/29
# @Author : zhangsihao@basicfinder.com
"""
"""
# -*- coding: utf-8 -*-
# @Time : 2022/11/24
# @Author : zhangsihao@basicfinder.com
"""
国防科技 xml导出脚本
"""
import os
import json
from tqdm import tqdm
from xml.dom.minidom import Document


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
        jc = load_json(file)
        iw = jc['result']['data'][0]['iw']
        ih = jc['result']['data'][0]['ih']
        img_url = jc['data']['image_url']
        folder = img_url.split('/')[-2]

        doc = Document()
        root = doc.createElement('annotation')
        doc.appendChild(root)

        _folder = doc.createElement('folder')
        root.appendChild(_folder)
        folder_text = doc.createTextNode(folder)
        _folder.appendChild(folder_text)

        filename = doc.createElement('filename')
        root.appendChild(filename)
        filename_text = doc.createTextNode(file_name + '.jpg')
        filename.appendChild(filename_text)

        source = doc.createElement('source')
        root.appendChild(source)
        database = doc.createElement('database')
        source.appendChild(database)
        database_text = doc.createTextNode('Unknown')
        database.appendChild(database_text)

        size = doc.createElement('size')
        root.appendChild(size)

        _width = doc.createElement('width')
        size.appendChild(_width)
        width_text = doc.createTextNode(str(iw))
        _width.appendChild(width_text)

        _height = doc.createElement('height')
        size.appendChild(_height)
        height_text = doc.createTextNode(str(ih))
        _height.appendChild(height_text)

        depth = doc.createElement('depth')
        size.appendChild(depth)
        depth_text = doc.createTextNode('3')
        depth.appendChild(depth_text)

        segmented = doc.createElement('segmented')
        root.appendChild(segmented)
        segmented_text = doc.createTextNode('0')
        segmented.appendChild(segmented_text)

        boxes = jc['result']['data']
        for box in boxes:
            label = box['label'][0]
            xl = []
            yl = []
            for point in box['coordinate']:
                xl.append(point['x'])
                yl.append(point['y'])

            _object = doc.createElement('object')
            root.appendChild(_object)

            _name = doc.createElement('name')
            _object.appendChild(_name)
            name_text = doc.createTextNode(label)
            _name.appendChild(name_text)

            _pose = doc.createElement('pose')
            _object.appendChild(_pose)
            pose_text = doc.createTextNode('Unspecified')
            _pose.appendChild(pose_text)

            _truncated = doc.createElement('truncated')
            _object.appendChild(_truncated)
            truncated_text = doc.createTextNode('0')
            _truncated.appendChild(truncated_text)

            _difficult = doc.createElement('difficult')
            _object.appendChild(_difficult)
            difficult_text = doc.createTextNode('0')
            _difficult.appendChild(difficult_text)

            _bndbox = doc.createElement('bndbox')
            _object.appendChild(_bndbox)

            xmin = doc.createElement('xmin')
            _bndbox.appendChild(xmin)
            xmin_text = doc.createTextNode(str(min(xl)))
            xmin.appendChild(xmin_text)

            ymin = doc.createElement('ymin')
            _bndbox.appendChild(ymin)
            ymin_text = doc.createTextNode(str(min(yl)))
            ymin.appendChild(ymin_text)

            xmax = doc.createElement('xmax')
            _bndbox.appendChild(xmax)
            xmax_text = doc.createTextNode(str(max(xl)))
            xmax.appendChild(xmax_text)

            ymax = doc.createElement('ymax')
            _bndbox.appendChild(ymax)
            ymax_text = doc.createTextNode(str(max(yl)))
            ymax.appendChild(ymax_text)

        xml_file = os.path.join(xml_dir, file_name + '.xml')
        with open(xml_file, 'w+') as xml_file:
            xml_file.write(doc.toprettyxml())

    # check_content = {
    #     "marking_errors": mark_err
    # }
    # if not os.path.exists(check_file):
    #     with open(check_file, 'w', encoding='utf-8') as cf:
    #         cf.write(json.dumps(check_content, ensure_ascii=False))
    # else:
    #     with open(check_file, 'r', encoding='utf-8-sig') as of:
    #         of_content = json.loads(of.read())
    #         of_content["marking_errors"] = check_content
    #     with open(check_file, 'w', encoding='utf-8') as cf:
    #         cf.write(json.dumps(of_content, ensure_ascii=False))


if __name__ == '__main__':
    # import argparse
    #
    # parser = argparse.ArgumentParser()
    # parser.add_argument('json_dir', type=str)
    # parser.add_argument('xml_dir', type=str)
    # parser.add_argument('check_file', type=str)
    # args = parser.parse_args()
    #
    # json_dir = args.json_dir
    # xml_dir = args.xml_dir
    # check_file = args.check_file
    json_dir = r"D:\Desktop\Project_file\田家林\望石智慧\journal\json_45096_114268_20221129110317 - 副本"
    xml_dir = r"D:\Desktop\Project_file\田家林\望石智慧\journal\xml_result"
    json2xml(json_dir, xml_dir)
