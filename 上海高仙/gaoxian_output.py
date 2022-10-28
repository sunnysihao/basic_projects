# _*_ coding=: utf-8 _*_
# @Time    : 2022/07/14
# @Author  : zhangsihao@basicfinder.com
"""
功能：高仙点云连续帧结果针对平台'3D一帧一结果'脚本打包的数据进行转换导出。
使用方法：pip install scipy
    运行程序，根据命令提示输入对应信息，输出文件在原json文件上级目录的“results”路径下。
"""
import json
import os
import math
from scipy.spatial.transform import Rotation as R


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_name = os.path.splitext(file)[0]
                file_list.append(file_name)
            else:
                continue
    return file_list


def list_dir(in_path: str):
    dir_list = []
    for _dir in os.listdir(in_path):
        if os.path.isdir(os.path.join(in_path, _dir)):
            dir_list.append(_dir)
        else:
            continue
    return dir_list


# 读取json文件内容返回python类型的对象
def load_json(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content

def alpha_in_pi(a):
    pi = math.pi
    return a - math.floor((a + pi) / (2 * pi)) * 2 * pi


def write_json(json_path: str):
    result_path = os.path.join(os.path.dirname(json_path), 'results')
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    all_err = {}
    batch_list = []
    frame_count = 0
    for file in list_files(json_path):
        json_file = os.path.join(json_path, file + '.json')
        json_content = load_json(json_file)
        frame_number = json_content['data']['frameNumber']
        boxs = json_content['result']['data']
        annotations = []
        one_file_err = []
        for box in boxs:  # 读取每个3D框数据
            x, y, z = box['3Dcenter'].values()
            translation = [x, y, z]
            width = box['3Dsize']['width']
            height = box['3Dsize']['height']
            deep = box['3Dsize']['deep']
            alpha = alpha_in_pi(box['3Dsize']['alpha'])
            size = [height, width, deep]
            rotation = R.from_rotvec([0, 0, alpha]).as_quat().tolist()
            int_id = box['intId']
            categorys = box['attr']['category']
            check_list = []
            for check_cat in categorys:
                for j in check_cat.split('-'):
                    check_list.append(j)
            if check_list.count('type') > 1:  # 检查一个框是否只包含一个标签
                job_id = box['cBy']
                int_id = box['intId']
                one_box_err = f"创建人{job_id}, {int_id}号框标签数大于1个"
                one_file_err.append(one_box_err)
                continue
            elif check_list.count('type') == 1:
                _type = categorys[0].split('-')[-1]
                label = box['attr']['label'][0]
            else:
                _type = 'null'
                label = 'null'

            if "attribute-occlusion" in categorys:
                occlusion = box['attr']['label'][box['attr']['category'].index("attribute-occlusion")]
            else:
                occlusion = ""

            if "attribute-truncated" in categorys:
                truncated = box['attr']['label'][box['attr']['category'].index("attribute-truncated")]
            else:
                truncated = ""

            if "attribute-anno_reliability" in categorys:
                anno_reliability = box['attr']['label'][box['attr']['category'].index("attribute-anno_reliability")]
            else:
                anno_reliability = ""

            if "attribute-manned" in categorys:
                manned = box['attr']['label'][box['attr']['category'].index("attribute-manned")]
            else:
                manned = ""

            box_data = {
                "box3d": {
                    "translation": translation,  # 3d box center point. # unit: meter
                    "rotation": rotation,  # rotation in quaternion #四元素
                    "size": size
                },  # boundingbox length, width, hight # unit: meter # 大小 长, 宽, 高
                "instance_id": int_id,
                "category": {
                    f"{_type}": label,
                },
                "attributes": {
                    "occlusion": occlusion,
                    "truncated": truncated,
                    "anno_reliability": anno_reliability,
                    "manned": manned

                }
            }
            annotations.append(box_data)
        image_quality = json_content['result']['frameAttr'][0]['value'].split('/')[-1]
        illumination = json_content['result']['frameAttr'][1]['value'].split('/')[-1]
        data = {
            "version": "v1.0.0",
            "image_attrs": [{
                "ft_cam": {
                    "image_quality": image_quality,
                    "illumination": illumination
                },
            },
                {
                    "bk_cam": "unknown"
                }
            ],
            "annotations": annotations

        }
        new_json_file = os.path.join(result_path, file + '.json')
        if not one_file_err:  # 若此文件未检测出标注错误，则转换文件，否则记录错误文件
            with open(new_json_file, 'w', encoding='utf-8') as nf:
                nf.write(json.dumps(data))
        else:
            print(one_file_err)
            batch_id = json_content['data_id']
            batch_list.append(batch_id)
            one_batch_err = {}
            if f"第{frame_number}帧" not in one_batch_err.keys():
                one_batch_err[f"第{frame_number}帧"] = [one_file_err]
            else:
                one_batch_err[f"{batch_id}第{frame_number}帧"].append(one_file_err)

            if f"{batch_id}" not in all_err.keys():
                all_err[f"{batch_id}"] = [one_batch_err]
            else:
                all_err[f"{batch_id}"].append(one_batch_err)
            continue
        frame_count += 1
    print(f"数据转换完成--共{frame_count}帧\n"
          f"结果保存路径为： {result_path}")
    error = {
            "errors": all_err
    }
    err_file = os.path.join(os.path.dirname(json_path), 'errors.json')

    with open(err_file, 'w', encoding='utf-8') as ef:
        ef.write(json.dumps(error))


if __name__ == "__main__":
    json_files_path = input("请输入平台'3D一帧一结果'脚本打包的原json结果文件夹路径:\n")
    while not os.path.exists(json_files_path):
        print(f"未找到路径：{json_files_path} ")
        json_files_path = input("请重新输入:\n")
    else:
        write_json(json_files_path)
        input("程序运行完成\n按任意键退出")

