# _*_ coding=: utf-8 _*_
import os
import json
import math
import argparse


# def list_files(in_path: str):
#     file_list = []
#     for root, _, files in os.walk(in_path):
#         for file in files:
#             file_name = os.path.splitext(file)[0]
#             file_list.append(file_name)
#     return file_list


def count_category(cate_list: list):  #对列表里的每一个元素计数，返回字典格式的结果
    result = {}
    for i in set(cate_list):
        result[i] = cate_list.count(i)
    return result


def alpha_in_pi(a):
    pi = math.pi
    return a - math.floor((a + pi) / (2 * pi)) * 2 * pi


def result_output(result_json_path: str, output_path: str):
    for root, _, files in os.walk(result_json_path):
        for file in files:
            with open(os.path.join(result_json_path, file), 'r', encoding='utf-8') as f:
                json_data = f.read()
                json_content = json.loads(json_data)
                category_list = []
                items_3d = []
                items_2d = []
                num = 0
                for obj in json_content['result']['data']:
                    num += 1
                    item_3d_data = {
                        "score": 1,  # 置信度，人工标注默认为1
                        "meta": {
                            "geometry": {  # 坐标、长宽高、几种角度，参考上面“点云格式”
                                "x": obj['3Dcenter']['x'],
                                "length": obj['3Dsize']['height'],
                                "width": obj['3Dsize']['width'],
                                "roll": obj['3Dsize']['rx'],
                                "y": obj['3Dcenter']['y'],
                                "z": obj['3Dcenter']['z'],
                                "pitch": obj['3Dsize']['rz'],
                                "yaw": obj['3Dsize']['ry'],  # 偏转角度
                                "height": obj['3Dsize']['deep']
                            },
                            "type": "CUBE",  # 默认CUBE
                            "direction": alpha_in_pi(obj['3Dsize']['alpha'])  # 是方向和坐标X轴的夹角，数值代表的是弧度，范围是-π~π
                        },
                        "category": obj['attr']['code'],  # 模板中配置的标签提示名
                        "categoryId": obj['attr']['label'],  # 模板配置中代码值
                        "seq": num  # 根据导出顺序递增
                    }
                    items_3d.append(item_3d_data)

                    item_2d_data = {
                        "score": 1,  # 置信度，人工标注默认为1
                        "meta": {
                            "geometry": {
                                # 3D框在图片中的8个顶点位置
                                "points": obj['cubeMap'][0]['cubePoints']
                            },
                            "type": "CUBE",  # 默认为CUBE
                            "direction": alpha_in_pi(obj['3Dsize']['alpha'])  # 同3D的direction
                        },
                        "category": obj['attr']['code'],  # 同3D的category
                        "seq": num  # 同3D的seq
                    }

                    items_2d.append(item_2d_data)
                    if len(obj['attr']['code']) == 0:
                        category_list.append("未命名标签")
                        print(f"id为{obj['intId']}处标签未命名")
                        continue
                    else:
                        category_list.append(obj['attr']['code'][0])

                meta = count_category(category_list)

                data = {
                    "uri": os.path.basename(json_content['data']['3d_url']).split("-")[0]+".pcd",  # pcd地址（需要还原成原pcd名称）
                    "annotationType": 3,  # 默认为3
                    "supplierCode": "ADS",  # 默认为ADS
                    "resultUrl": r"\\N",  # 默认为空
                    "resultInfo": {
                        "meta": {
                            "statistics": {  # 3D结果按标签统计
                                "categoryCounts": meta  # 前面是标签名称，后面是数量

                            }
                        },
                        "resultUrl": r"\\N",  # 默认为空
                        "type": "CUBE",  # 默认CUBE
                        "items": items_3d
                    },
                    "subAnnoResults": [      # 关联文件标注（点云关联的图片）
                                        {
                        #"dataInfoId": 378998001464938496, 线下不需要提供
                        "width": 1440,  # 图片宽
                        "height": 930,  # 图片高
                        "uri": json_content['data']['3d_img0'].split("-")[1],  # 图片地址（需要还原成原png名称）
                        "annotationType": 3, # 默认为3
                        "supplierCode": "ADS",  # 默认为ADS
                        "resultInfo": {
                        "meta": {
                            "statistics": { # 2D结果按标签统计
                                "categoryCounts": meta  # 前面是标签名称，后面是数量

                            }
                        },
                "type": "CUBE",  # 默认CUBE
                "items": items_2d
            }
        }
    ]
}

            to_path = os.path.join(output_path, os.path.splitext(file)[0].split("-")[0])
            with open(to_path+".json", "+a", encoding='utf-8') as f:
                f.write(json.dumps(data))

            with open(os.path.join(output_path, "pcd与png文件对应关系.txt"), '+a', encoding='utf-8') as txt_f:
                txt = str(json_content['data']['3d_img0'].split("-")[1]+",  "+os.path.basename(json_content['data']['3d_url']).split("-")[0]+".pcd"+";"+"\n")
                txt_f.write(txt)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('result_json_path', type=str)
    parser.add_argument('output_path', type=str)
    args = parser.parse_args()

    result_json_path = args.result_json_path
    output_path = args.output_path

    result_output(result_json_path, output_path)
