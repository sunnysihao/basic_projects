# _*_ coding=: utf-8 _*_
# 安装：pip install numpy scipy argparse
# 使用：Sens.py <结果json源文件目录路径>(--若文件夹名称带空格，路径需加双引号--）

import os
import json
from scipy.spatial.transform import Rotation as R


def get_and_write_data(result_json_dir: str):
    save_path = os.path.join(os.path.dirname(result_json_dir), "result_new_json")
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    for root, _, files in os.walk(result_json_dir):
        for file in files:
            with open(os.path.join(result_json_dir, file), 'r', encoding='utf-8') as f:
                str_data = f.read()
                json_content = json.loads(str_data)
                name_from_strs = json_content['data']['urls'][0]['3d_url'].split('/')
                name_index = name_from_strs.index("3d_url") - 1
                new_json_name = name_from_strs[name_index]
                data = json_content['data']
                result_data = []
                frameAttrs = []
                for result in json_content['result']['data']:
                    x, y, z = result['3Dcenter'].values()
                    width = result['3Dsize']['width']
                    height = result['3Dsize']['height']
                    deep = result['3Dsize']['deep']
                    alpha = result['3Dsize']['alpha']
                    r = R.from_euler('z', alpha)
                    ori_x, ori_y, ori_z, ori_w = r.as_quat()
                    id = result['id']
                    frame = result['frame']

                    if "object_class-object_class" in result['attr']['category']:
                        object_class = result['attr']['label'][result['attr']['category'].index("object_class-object_class")]
                    else:
                        object_class = "null"

                    if "annotation_uncertainty-shape" in result['attr']['category']:
                        shape = result['attr']['label'][result['attr']['category'].index("annotation_uncertainty-shape")]
                    else:
                        shape = 0

                    if "annotation_uncertainty-orientation" in result['attr']['category']:
                        orientation = result['attr']['label'][result['attr']['category'].index("annotation_uncertainty-orientation")]
                    else:
                        orientation = 0

                    new_result_data = {
                        "position": {
                            "x": x,
                            "y": y,
                            "z": z
                        },
                        "orientation": {
                            "x": ori_x,
                            "y": ori_y,
                            "z": ori_z,
                            "w": ori_w
                        },
                        "shape": {
                            "x": height,
                            "y": width,
                            "z": deep
                        },
                        "object_class": object_class,
                        "annotation_uncertainty": {
                            "shape": shape,
                            "orientation": orientation
                        },
                        "object_id": id,
                        "frame": frame
                    }
                    result_data.append(new_result_data)
                frameAttrs = json_content['result']['frameAttrs']
                curindex = json_content['result']['curindex']
                data_deleted_file = json_content['result']['data_deleted_file']

                final_json = {
                    "data": data,
                    "result": {
                        "data": result_data,
                        "curindex": curindex,
                        "frameAttrs": frameAttrs,
                        "data_deleted_file": data_deleted_file
                    }
                }
                with open(os.path.join(save_path, new_json_name + ".json"), "a+", encoding='utf-8') as nf:
                    nf.write(json.dumps(final_json))


if __name__ == "__main__":
    # json文件目录路径
    # result_json_dir = r"D:\Desktop\BasicProject\任从辉\Sens\Download tasks_json_20909_more_20220525021953"

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('result_json_dir', type=str)
    args = parser.parse_args()
    result_json_dir = args.result_json_dir

    get_and_write_data(result_json_dir)
