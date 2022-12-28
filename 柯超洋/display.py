# -*- coding: utf-8 -*- 
# @Time : 2022/12/27
# @Author : zhangsihao@basicfinder.com
"""
"""
import json
import uuid
from nanoid import generate


def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def main():
    anno_file = r"C:\Users\EDY\Downloads\无点云融合\无点云融合\导出结果\annotation_3d(1).json"
    save_path = r"C:\Users\EDY\Downloads\无点云融合\upload_files\ai_result\TPV-100.json"
    jc = load_json(anno_file)
    objs = jc['100']['bbox_3d']
    results = []
    box_num = 1
    for obj in objs:
        x, y, z, l, w, h, theta = obj

        box_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, ''.join([str(x), str(y), str(z)])))
        box = {
            "uuid": box_id,
            "objType": "3d",
            "id": box_id,
            "trackId": generate(size=16),
            "trackName": box_num,
            "classType": "",
            "attrs": {},
            "center3D": {
                "x": x,
                "y": y,
                "z": z
            },
            "rotation3D": {
                "x": 0,
                "y": 0,
                "z": theta
            },
            "size3D": {
                "x": l,
                "y": w,
                "z": h
            },
            "frame": 0,
            "type": "pcl_nu_beta"
        }
        results.append(box)
        box_num += 1

    data = {
        "3d_url": "TPV-100.pcd",
        "3d_img0": "TPV-100.jpg",
        "3d_img1": "TPV-100.jpg",
        "3d_img2": "TPV-100.jpg",
        "3d_img3": "TPV-100.jpg",
        "3d_img4": "TPV-100.jpg",
        "3d_img5": "TPV-100.jpg",
        "3d_img6": "TPV-100.jpg",
        "3d_img7": "TPV-100.jpg",
        "camera_config": "TPV-100.json",
    }
    data = {
        "data": data,
        "result": {
            "data": results
        }
    }
    with open(save_path, 'w') as sf:
        json.dump(data, sf)


if __name__ == '__main__':
    main()
