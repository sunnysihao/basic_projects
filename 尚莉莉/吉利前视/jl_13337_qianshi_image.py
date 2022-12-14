import os
import json
from tqdm import tqdm


def load_json(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
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


two_label_list = ["Car", "Truck", "Bus", "Tram", "Engineer-Car", "Cart", "Tricycle", "Motorcycle", "ElectricBicycle",
                  "Bicycle", "Fence", "No-Entry", "Gate-Machine", "Trash"]

one_label_list = ['Pedestrian', 'Pillar', 'Park-Stop', 'Tire-Rod', 'Park-Lock-OFF', 'Park-Lock-ON', 'Cylinder-Barrels',
                  'Conical-Barrels', 'Water-Horse', 'Speed-Bump', 'Auto-Shutter', 'Iron-Gate', 'Fire-Extinguisher-Box',
                  'Advertising-Board', 'Traffic-Signs', 'Ground-Charging-Pile', 'Hang-Charging-Pile', 'Electronic-Box',
                  'LampStandard', '3D-Slot-Separate', '3D-Solt-Pillar', 'Animal', 'Others', 'Carriage-Wheel']

no_group_label = ['Fence', 'Gate-Machine', 'Park-Lock-OFF', 'Park-Lock-ON', 'Water-Horse', 'Auto-Shutter', 'Iron-Gate',
                  'Fire-Extinguisher-Box', 'Advertising-Board', 'Traffic-Signs', 'Hang-Charging-Pile', '3D-Slot-Separate',
                  'Animal', 'Others']
label_point_mapping = {
    "Car": ['车辆接地点（四点）（红色可见绿色不可见）', '购物车、婴儿车4轮（四点）', '所有矩形体目标：停车场立柱、落地充电桩、电箱等',
            '警示牌（4点，红色可见，绿色不可见）', '防撞桶（同石柱）、反光锥', '减速带'],
    "Pillar": ['车辆接地点（四点）（红色可见绿色不可见）', '购物车、婴儿车4轮（四点）', '所有矩形体目标：停车场立柱、落地充电桩、电箱等',
            '警示牌（4点，红色可见，绿色不可见）', '防撞桶（同石柱）、反光锥', '减速带'],
    "Tricycle": ['三轮车（三点）（红色可见，绿色不可见）', '石柱、警示柱（三点）', '石球、圆形垃圾桶（三点）'],
    "Pedestrian": ['工地手推车、婴儿车3轮（两点）', '行人（两点）', '轮挡、轮胎挡杆']
}


def jl_output(json_dir: str, check_file: str):
    err_list = []
    empty_label = []
    outside_point_count = 0
    for file in tqdm(list_files(json_dir)):
        features = []
        json_content = load_json(file)
        data_id = json_content['data']['data_id']

        group_info = json_content['result']['groupinfo']
        group_mapping = {}
        point_mapping = {}
        group_label_mapping = {}
        for info in group_info:
            group_id = info['id']
            group_intid = info['intId']
            child_l = []
            bonepoint_count = 0
            for child in info['children']:
                child_id = child['id']
                child_type = child['type']
                child_l.append(child_id)
                if child_type == "bonepoint":
                    bonepoint_count += 1
            group_mapping[group_intid] = child_l
            if bonepoint_count > 1:
                bonepoint_err_str = f"作业id:{data_id}-{group_intid}号编组关键点组数量大于 1"
                err_list.append(bonepoint_err_str)

        boxes = json_content['result']['data']

        for box in boxes:
            box_id = box['id']
            box_type = box['type']
            if box_type == 'rect':
                if not box['label']:
                    continue
                else:
                    if len(box['label']) == 1 and box['category'][0] in two_label_list:
                        category = box['category'][0]
                    elif len(box['label']) == 1 and box['category'][0] in one_label_list:
                        category = box['category'][0]
                    else:
                        continue
                    if category in ['Car', 'Pillar', 'Tricycle', 'Pedestrian']:
                        for rk, rv in group_mapping.items():
                            if box_id in rv:
                                group_label_mapping[rk] = category
                            else:
                                continue
                    else:
                        continue

        for box in boxes:
            box_id = box['id']
            try:
                int_id = box['intId']
            except Exception:
                int_id = 0
            box_type = box['type']
            frame = box['frame'] + 1
            if box_type == 'bonepoint':
                nodes = box['nodes']
                title = box['name']
                image_w = box['iw']
                image_h = box['ih']
                for node in nodes:
                    point_id_l = []
                    point_coordinate = node['coordinate']
                    point_x = point_coordinate[0]
                    point_y = point_coordinate[1]

                    if point_x < 0 or point_x > image_w or point_y < 0 or point_y > image_h:
                        outside_point_count += 1
                        continue
                    else:
                        point_id = node['id']
                        point_id_l.append(point_id)
                        point_mapping[box_id] = point_id_l
                        point_color = node['color']
                        visible = node['attr']['label']
                        attr_text = node['attr']['text']

                        if not node['code']:
                            empty_str = f"作业id:{data_id}-第{frame}帧-{int_id}号框未选择标签"
                            empty_label.append(empty_str)
                            continue
                        else:
                            opoint_label = node['code'][0]
                            if opoint_label in ['Left-Anterior(左前)', 'Left-Fron(左前)']:
                                point_label = 'Left-Front'
                            elif opoint_label in ['Light-Front(右前)', 'Right-Front(右前)']:
                                point_label = 'Right-Front'
                            else:
                                point_label = opoint_label

                            point_group = ''
                            for pk, pv in point_mapping.items():
                                if point_id in pv:
                                    for gk, gv in group_mapping.items():
                                        if pk in gv:
                                            point_group = gk
                                            break
                                        else:
                                            continue
                                else:
                                    continue
                            if not point_group:
                                group_err_str = f"作业id:{data_id}-第{frame}帧-{int_id}号框未编组或编组信息错误"
                                err_list.append(group_err_str)
                                continue
                            else:
                                try:
                                    gl = group_label_mapping[point_group]
                                    if title not in label_point_mapping[gl]:
                                        point_check = False
                                    else:
                                        point_check = True
                                except:
                                    point_check = True

                                if not point_check:
                                    point_err_str = f"作业id:{data_id}-第{frame}帧-{int_id}号关键点组选择错误"
                                    err_list.append(point_err_str)
                                    continue
                                else:

                                    fea_point = {
                                        "type": "Feature",
                                        "properties": {
                                            "objectId": point_id,
                                            "id": point_id,
                                            "layerId": point_id,
                                            "content": {
                                                "label": "Ground-Points",
                                                "Category": point_label,
                                                "Visibleproperties": visible
                                            },
                                            "ocrContent": {},
                                            "generateMode": 1,
                                            "quality": {
                                                "errorType": {
                                                    "attributeError": [],
                                                    "targetError": [],
                                                    "otherError": ""
                                                },
                                                "changes": {
                                                    "attribute": [],
                                                    "target": []
                                                },
                                                "qualityStatus": "unqualified"
                                            },
                                            "labelColor": point_color,
                                            "groups": [
                                                {
                                                    "id": point_group,
                                                    "name": f"组{point_group}"
                                                }
                                            ],
                                            "assembleId": point_group
                                        },
                                        "title": title,
                                        "geometry": {
                                            "type": "Point",
                                            "coordinates": point_coordinate
                                        }
                                    }
                                    features.append(fea_point)

            elif box_type == 'rect':
                area = box['area']
                rect_color = box['color']
                points = box['points']
                image_w = box['iw']
                image_h = box['ih']
                coordinate = []
                for point in points:
                    x = point['x'] * image_w
                    y = point['y'] * image_h
                    coordinate.append({"x": x, "y": y})
                if not box['label']:
                    empty_str = f"作业id:{data_id}-第{frame}帧-{int_id}号框未选择标签"
                    empty_label.append(empty_str)
                    continue
                else:
                    if len(box['label']) == 3:
                        if 'Carriage-Wheel' in box['category'] and "Visible-Scale" in box['category'] and "Direction" in box['category']:
                            label = label_c = 'Wheel'
                            visible_scale = box['label'][box['category'].index("Visible-Scale")]
                            direction = box['label'][box['category'].index("Direction")]
                            f_label = f"{label}/{direction}/{visible_scale}"
                        else:
                            wheel_err_str = f"作业id:{data_id}-第{frame}帧-{int_id}号框车轮标签选择错误"
                            err_list.append(wheel_err_str)
                            label = label_c = None
                            direction = None
                            visible_scale = None
                            if 'Carriage-Wheel' in box['category']:
                                label = label_c = 'Wheel'
                            if "Visible-Scale" in box['category']:
                                visible_scale = box['label'][box['category'].index("Visible-Scale")]
                            if "Direction" in box['category']:
                                direction = box['label'][box['category'].index("Direction")]
                            f_label = f"{label}/{direction}/{visible_scale}"
                    # elif len(box['label']) == 2:
                    #     if "Visible-Scale" in box['category'] and 'Carriage-Wheel' in box['category']:
                    #         label = 'Carriage-Wheel'
                    #         label_c = label
                    #         visible_scale = box['label'][box['category'].index("Visible-Scale")]
                    #         f_label = f"{label}/{visible_scale}"
                    #         wheel_str = f"作业id:{data_id}-{int_id}号框未标注车辆方向"
                    #         no_direction.append(wheel_str)
                    #     elif "Visible-Scale" in box['category'] and 'Direction' in box['category']:
                    #         label = 'Carriage-Wheel'
                    #         label_c = label
                    #         label_direction = box['label'][box['category'].index("Direction")]
                    #         visible_scale = box['label'][box['category'].index("Visible-Scale")]
                    #         f_label = f"{label}/{label_direction}/{visible_scale}"

                    elif len(box['label']) == 1 and box['category'][0] in two_label_list:
                        category = box['category'][0]
                        label = box['label'][0]
                        label_code = box['code']
                        if label_code == 'MPV':
                            label = 'MPV'
                        else:
                            label = label
                        f_label = f"{category}/{label}"
                        if label in no_group_label or category in no_group_label:
                            label_c = category
                        else:
                            label_c = label
                    elif len(box['label']) == 1 and box['category'][0] in one_label_list:
                        f_label = box['label'][0]
                        label = f_label
                        label_c = label
                    elif len(box['label']) == 0:
                        empty_str = f"作业id:{data_id}-第{frame}帧-{int_id}号框未选择标签"
                        empty_label.append(empty_str)
                        continue
                    else:
                        err_str = f"作业id:{data_id}-第{frame}帧-{int_id}号框标签选择错误"
                        err_list.append(err_str)
                        continue

                    if label_c in no_group_label:
                        fea_rect = {
                            "type": "Feature",
                            "properties": {
                                "objectId": box_id,
                                "id": box_id,
                                "layerId": box_id,
                                "content": {
                                    "label": f_label
                                },
                                "ocrContent": {},
                                "generateMode": 1,
                                "quality": {
                                    "errorType": {
                                        "attributeError": [],
                                        "targetError": [],
                                        "otherError": ""
                                    },
                                    "changes": {
                                        "attribute": [],
                                        "remark": "",
                                        "target": []
                                    },
                                    "qualityStatus": "unqualified"
                                },
                                "labelColor": rect_color,
                                "area": area,
                                "groups": [],
                                "assembleId": ""
                            },
                            "title": "",
                            "geometry": {
                                "type": "rect",
                                "coordinates": coordinate
                            }
                        }
                        features.append(fea_rect)

                    else:
                        rect_group = ''
                        for rk, rv in group_mapping.items():
                            if box_id in rv:
                                rect_group = rk
                            else:
                                continue

                        if not rect_group:
                            group_err_str = f"作业id:{data_id}-第{frame}帧-{int_id}号框未编组或编组信息错误"
                            err_list.append(group_err_str)
                            continue

                        fea_rect = {
                            "type": "Feature",
                            "properties": {
                                "objectId": box_id,
                                "id": box_id,
                                "layerId": box_id,
                                "content": {
                                    "label": f_label
                                },
                                "ocrContent": {},
                                "generateMode": 1,
                                "quality": {
                                    "errorType": {
                                        "attributeError": [],
                                        "targetError": [],
                                        "otherError": ""
                                    },
                                    "changes": {
                                        "attribute": [],
                                        "remark": "",
                                        "target": []
                                    },
                                    "qualityStatus": "unqualified"
                                },
                                "labelColor": rect_color,
                                "area": area,
                                "groups": [
                                    {
                                        "id": rect_group,
                                        "name": f"组{rect_group}"
                                    }
                                ],
                                "assembleId": rect_group
                            },
                            "title": "",
                            "geometry": {
                                "type": "rect",
                                "coordinates": coordinate
                            }
                        }
                        features.append(fea_rect)

            elif box_type == 'trapezoid':
                area = box['area']
                rect_color = box['color']
                points = box['points']
                image_w = box['iw']
                image_h = box['ih']
                coordinate = []
                for point in points:
                    x = point['x'] * image_w
                    y = point['y'] * image_h
                    coordinate.append({"x": x, "y": y})
                if not box['label']:
                    empty_str = f"作业id:{data_id}-第{frame}帧-{int_id}号框未选择标签"
                    empty_label.append(empty_str)
                    continue
                else:
                    label = box['label'][0]
                    if label not in ['Front', 'Back']:
                        err_str = f"作业id:{data_id}-第{frame}帧-{int_id}号框标签选择错误"
                        err_list.append(err_str)
                        continue
                    else:
                        if label == 'Front':
                            f_label = 'FrontFace'
                        else:
                            f_label = 'RearFace'
                        fea_trapezoid = {
                            "type": "Feature",
                            "properties": {
                                "objectId": box_id,
                                "id": box_id,
                                "layerId": box_id,
                                "content": {
                                    "label": f_label
                                },
                                "ocrContent": {},
                                "generateMode": 1,
                                "quality": {
                                    "errorType": {
                                        "attributeError": [],
                                        "targetError": [],
                                        "otherError": ""
                                    },
                                    "changes": {
                                        "attribute": [],
                                        "remark": "",
                                        "target": []
                                    },
                                    "qualityStatus": "unqualified"
                                },
                                "labelColor": rect_color,
                                "area": area,
                                "groups": [],
                                "assembleId": ""
                            },
                            "title": "",
                            "geometry": {
                                "type": "trapezoid",
                                "coordinates": coordinate
                            }
                        }
                        features.append(fea_trapezoid)
                # print(data_id)
            else:
                err_str = f"作业id:{data_id}-第{frame}帧-{int_id}号框标签选择错误"
                err_list.append(err_str)
                continue

        result_content = {
            "qualityResult": {
                "type": "FeatureCollection",
                "features": []
            },
            "markResult": {
                "type": "FeatureCollection",
                "features": features
            },
            "workload": {
                "tagCount": 0,
                "qualifiedCount": 0,
                "unqualifiedCount": 0,
                "tagCount1": 0,
                "qualifiedCount1": 0,
                "unqualifiedCount1": 0,
                "tagCount2": 0,
                "tagCount3": 0,
                "label": {
                    "LampStandard": 0,
                    "Ground-Points": 0
                },
                "extent": {
                    "tagCount": 0,
                    "qualifiedCount": 0,
                    "unqualifiedCount": 0,
                    "tagCount1": 0,
                    "qualifiedCount1": 0,
                    "unqualifiedCount1": 0,
                    "label": {
                        "LampStandard": 0
                    }
                },
                "point": {
                    "tagCount": 0,
                    "qualifiedCount": 0,
                    "unqualifiedCount": 0,
                    "tagCount1": 0,
                    "qualifiedCount1": 0,
                    "unqualifiedCount1": 0,
                    "label": {
                        "Ground-Points": 0
                    }
                }
            },
            "info": {
                "depth": 3,
                "width": 1920,
                "height": 1080
            }
        }

        with open(file, 'w', encoding='utf-8') as nf:
            nf.write(json.dumps(result_content))
    count_l = count_m(json_dir)
    check_content = {
        "marking_errors": err_list,
        "empty_label": empty_label,
        "count_info": count_l,
        "count_outside_point": outside_point_count
    }
    if not os.path.exists(check_file):
        with open(check_file, 'w', encoding='utf-8') as cf:
            cf.write(json.dumps(check_content, ensure_ascii=False))
    else:
        with open(check_file, 'r', encoding='utf-8-sig') as of:
            of_content = json.loads(of.read())
            of_content["marking_errors"] = check_content
        with open(check_file, 'w', encoding='utf-8') as cf:
            cf.write(json.dumps(of_content, ensure_ascii=False))



def count_m(json_dir: str):
    count_list = []
    dir_list = []
    for file in list_files(json_dir):
        dir_list.append(os.path.dirname(file))
    path_list = set(dir_list)
    for one_path in path_list:
        path_name = one_path.replace(json_dir, '')
        rect_num = 0
        point_num = 0
        trapezoid_num = 0
        wheel_num = 0
        for file in tqdm(list_files(one_path)):
            json_content = load_json(file)
            fs = json_content['markResult']['features']
            for f in fs:
                mtype = f['geometry']['type']
                if mtype == 'rect':
                    rect_num += 1
                elif mtype == 'Point':
                    point_num += 1
                else:
                    trapezoid_num += 1

                label = f['properties']['content']['label']
                if 'Wheel' in label.split('/'):
                    wheel_num += 1
        count_str = f"{path_name}---矩形框(不含车轮框):{rect_num-wheel_num}|点:{point_num}|车轮框:{wheel_num}|梯形:{trapezoid_num}"
        count_list.append(count_str)
    return count_list

    # err_file = os.path.join(json_dir, 'errors.txt')
    # with open(err_file, 'w', encoding='utf-8') as tf:
    #     tf.writelines(err_list)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('json_dir', type=str)
    parser.add_argument('check_file', type=str)
    args = parser.parse_args()

    json_dir = args.json_dir
    check_file = args.check_file

    # json_dir = r"C:\Users\EDY\Downloads\json_44312_111311,111312_20221230174040\拆分批次-停车场1和停车场2 - 副本"
    # check_file = r"C:\Users\EDY\Downloads\json_44312_111311,111312_20221230174040\拆分批次-停车场1和停车场2 - 副本\check file.json"
    jl_output(json_dir, check_file)
    # print(count_m(json_dir))
