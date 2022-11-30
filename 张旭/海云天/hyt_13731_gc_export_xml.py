# -*- coding: utf-8 -*- 
# @Time : 2022/11/24
# @Author : zhangsihao@basicfinder.com
"""
海云天短文改错 xml导出脚本
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


def json2xml(json_dir, xml_dir, check_file):
    mark_err = []
    for file in tqdm(list_files(json_dir, '.json')):
        file_name = os.path.splitext(os.path.basename(file))[0]
        jc = load_json(file)
        data_id = jc['data_id']
        img_url = jc['data']['image_url']
        folder = '/'.join(img_url.split('/')[3:])
        boxes = jc['result']['data']

        doc = Document()
        root = doc.createElement('annotation')
        doc.appendChild(root)

        _folder = doc.createElement('folder')
        root.appendChild(_folder)
        folder_text = doc.createTextNode(folder)
        _folder.appendChild(folder_text)

        filename = doc.createElement('filename')
        root.appendChild(filename)
        filename_text = doc.createTextNode(file_name + '.xml')
        filename.appendChild(filename_text)

        for box in boxes:
            int_id = box['intId']
            label = box['label']

            if not label:
                label_err = f"{data_id} | {int_id}框 未选择标签"
                mark_err.append(label_err)
                continue
            else:
                category = box['category'][0]
                xl = []
                yl = []
                for point in box['coordinate']:
                    xl.append(int(point['x']))
                    yl.append(int(point['y']))
                if category == '印刷体标注':
                    name = label[0]
                else:
                    if box['text']:
                        name = box['text']
                    else:
                        label_err = f"{data_id} | {int_id}框"
                        mark_err.append(label_err)
                        continue

            _object = doc.createElement('object')
            root.appendChild(_object)

            _name = doc.createElement('name')
            _object.appendChild(_name)
            name_text = doc.createTextNode(name)
            _name.appendChild(name_text)

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

    check_content = {
        "手写无转录内容": mark_err
    }
    if not os.path.exists(check_file):
        with open(check_file, 'w', encoding='utf-8') as cf:
            cf.write(json.dumps(check_content, indent=1, ensure_ascii=False))
    else:
        with open(check_file, 'r', encoding='utf-8-sig') as of:
            of_content = json.loads(of.read())
            of_content["marking_errors"] = check_content
        with open(check_file, 'w', encoding='utf-8') as cf:
            cf.write(json.dumps(of_content, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('json_dir', type=str)
    parser.add_argument('xml_dir', type=str)
    parser.add_argument('check_file', type=str)
    args = parser.parse_args()

    json_dir = args.json_dir
    xml_dir = args.xml_dir
    check_file = args.check_file
    # json_dir = r"C:\Users\EDY\Downloads\下载结果_json_45108_114425_20221130143408\gaicuo1.zip"
    # xml_dir = r"C:\Users\EDY\Downloads\下载结果_json_45108_114425_20221130143408\out_xml"
    # check_file = r"C:\Users\EDY\Downloads\下载结果_json_45108_114425_20221130143408\check_file.json"
    json2xml(json_dir, xml_dir, check_file)
