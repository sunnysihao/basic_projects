# _*_ coding=: utf-8 _*_
import os
import json



def load_json(json_path: str):
    with open(json_path) as f:
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


def foo(p):
    for file in list_files(p):
        json_content = load_json(file)
        cam_in = json_content['3d_img0']['camera_internal']
        cam_ext = json_content['3d_img0']['camera_external']
        img = [
            {
            "camera_internal": cam_in,
            "camera_external": cam_ext
            }
        ]
        with open(file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(img))

p = r"D:\Desktop\BasicProject\谢秋梅\data_matic_upload_1013\베이직 에이아이 샘플 데이터(상용 자율주행차)_221005\88_191512_220928\sensor_raw_data"
foo(p)
