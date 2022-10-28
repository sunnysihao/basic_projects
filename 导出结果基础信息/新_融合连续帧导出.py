# _*_ coding=: utf-8 _*_
import os
import json


# 获取多层目录下的指定格式的包含绝对路径及后缀的文件列表
def list_files(in_path: str):
    files_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                files_list.append(os.path.join(root, file))
            else:
                continue
    return files_list


# 读取json文件内容返回python类型的对象
def load_json(json_path:str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def convert_data(in_path: str):
    for file in list_files(in_path):
        json_content = load_json(file)
        boxs = json_content['result']['data']
        annotations = []
        for box in boxs:  # 读取每个3D框数据
            x, y, z = box['3Dcenter'].values()
            nx, ny, nz = box['3Dsize'].values()
            alpha = box['3Drotation']['z']
            int_id = box['intId']
            label = box['classType']
            if not box['cubeMap']:
                bbox = None
                err_list.append(f"{file}---含空2D框结果\n")
            else:
                cube_points = box['cubeMap'][0]['cubePoints']
                xl = []
                yl = []
                for coordinate in cube_points:
                    xl.append(coordinate['x'])
                    yl.append(coordinate['y'])
                x_min = min(xl)
                y_min = min(yl)
                x_max = max(xl)
                y_max = max(yl)
                bbox = {
                    "x": x_min,
                    "y": y_min,
                    "rw": x_max - x_min,
                    "rh": y_max - y_min
                }
            box_data = {
                "id": int_id,
                "type": label,
                "x": x,
                "y": y,
                "z": z,
                "long": nx,
                "width": ny,
                "height": nz,
                "alpha": alpha_in_pi(alpha),
                "points_3d": [
                    {
                        "x": x - nx / 2,
                        "y": y + ny / 2,
                        "z": z + nz / 2
                    },
                    {
                        "x": x - nx / 2,
                        "y": y - ny / 2,
                        "z": z + nz / 2
                    },
                    {
                        "x": x - nx / 2,
                        "y": y - ny / 2,
                        "z": z - nz / 2
                    },
                    {
                        "x": x - nx / 2,
                        "y": y + ny / 2,
                        "z": z - nz / 2
                    },
                    {
                        "x": x + nx / 2,
                        "y": y + ny / 2,
                        "z": z + nz / 2
                    },
                    {
                        "x": x + nx / 2,
                        "y": y - ny / 2,
                        "z": z + nz / 2
                    },
                    {
                        "x": x + nx / 2,
                        "y": y - ny / 2,
                        "z": z - nz / 2
                    },
                    {
                        "x": x + nx / 2,
                        "y": y + ny / 2,
                        "z": z - nz / 2
                    }
                ],
                "bbox": bbox
            }
            annotations.append(box_data)
        with open(file, 'w', encoding='utf-8') as nf:
            nf.write(json.dumps(annotations))
