# _*_ coding=: utf-8 _*_
import os
import json


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list

def load_json(json_path:str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content

def write_data_to_json(json_path:str, result_path:str):
    fram = 0
    box_data = []
    urls = []
    for file in list_files(json_path):
        one_url = {
            "3d_url": f"{file}.pcd",
            "3d_img0": f"{file}.jpg",
            "3d_img1": f"{file}.jpg",
            "3d_img2": f"{file}.jpg",
            "3d_img3": f"{file}.jpg",
            "3d_img4": f"{file}.jpg",
            "3d_img5": f"{file}.jpg",
            "camera_config": f"{file}.json"
        }
        urls.append(one_url)
        old_json_file = os.path.join(json_path, file + '.json')
        json_content = load_json(old_json_file)
        objects = json_content['objects_full']
        for obj in objects:
            int_id = obj['id']
            x, y, z = obj['position']['x'], obj['position']['y'], obj['position']['z']
            pitch, roll, yaw = obj['rotation']['pitch'], obj['rotation']['roll'], obj['rotation']['yaw']
            length, width, height = obj['dimension']['length'], obj['dimension']['width'], obj['dimension']['height']
            crowding, occlusion, truncation = obj['2D_attributes']['crowding'], obj['2D_attributes']['occlusion'], obj['2D_attributes']['truncation']
            class_type = obj['className']


            one_box = {
                "id": "",
                "trackId": "",
                "objType": "3d",
                "imageUrl": "",
                "intId": int_id,
                "index": "",
                "3Dcenter": {
                    "x": x,
                    "y": y,
                    "z": z
                },
                "3Drotation": {
                    "x": pitch,
                    "y": roll,
                    "z": yaw
                },
                "3Dsize": {
                    "x": length,
                    "y": width,
                    "z": height
                },
                "type": "pcl_nu",
                "points": [],
                "pointN": -1,
                "attrs": {
                    "occlusion": occlusion,
                    "truncation": truncation,
                    "crowding": crowding,
                    "ignore": ""
                },
                "classType": class_type,
                "cubeMap": [],
                "frame": fram,
                "cBy": "",
                "cTime": "",
                "cStep": "",
                "eBy": "",
                "eStep": "",
                "eTime": "",
                "vBy": "",
                "vStep": "",
                "vTime": "",
                "mBy": "",
                "mStep": "",
                "mTime": ""
            }
            box_data.append(one_box)

        fram += 1
    data = {
    "data": {
        "urls": urls,

    },
    "result": {
    "data": box_data
    }
    }

    new_json_file = os.path.join(result_path, 'all_result' + '.json')
    with open(new_json_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data))


if __name__ == "__main__":
    json_path = r"D:\Desktop\BasicProject\任从辉\毫末\62a6b078439ffb7afdb69a6f\62a6b078439ffb7afdb69a6f"
    result_path = r"D:\Desktop\BasicProject\任从辉\毫末\毫末\ai_result"
    write_data_to_json(json_path, result_path)
