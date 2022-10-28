# _*_ coding=: utf-8 _*_
import os
import json
import re
import math


sensor_map = {
    "3d_img0": "Backward",
    "3d_img1": "Forward_Wide",
    "3d_img2": "Forward_Ahead",
    "3d_img3": "Left_Forward",
    "3d_img4": "Left_Backward",
    "3d_img5": "Right_Backward",
    "3d_img6": " Right_Forward"
}
scene_map = {
    "02-天气条件": "env_weather_condition",
    "03-道路场景": "road_scenario",
    "04-其他异常场景": "event",
    "05-路面情况": "env_pavement_condition",
    "06-光照条件": "env_weather_condition",
    "07-拥堵程度": "road_congestion_degree",
    "08-临时作业": "tep_temporary_operation",
    "09-目标行为": "target_behavior",
}

occlusion_type_map = {
    "不确定": "unknown",
    "标注目标": "objects",
    "非标注目标": "non_objects"
}

img_file = sensor_map.keys()


def list_files_name(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_name = os.path.splitext(file)[0]
                file_list.append(file_name)
            else:
                continue
    return file_list


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_name = os.path.splitext(file)[0]
                file = os.path.join(root, file)
                file_list.append(file)
            else:
                continue
    return file_list


def alpha_in_pi(alpha):
    pi = math.pi
    return alpha - math.floor((alpha + pi) / (2 * pi)) * 2 * pi


def load_json(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def get_meta(json_file, num):
    scene_list = ["62c2a4a30523b0812bd48a86",
                  "62c2a4a70523b0812bd48a87",
                  "62c2a4ab0523b0812bd48a88",
                  "62c2a4ae0523b0812bd48a89",
                  "62c2a4b20523b0812bd48a8a"]
    json_content = load_json(json_file)
    cj_result = json_content['result']

    scene_id = scene_list[num]
    scene = {
        "scene_id": scene_id,
    }
    result_info = cj_result['info'][0]
    scene.update({f"{scene_map[result_info['header']]}": f"{result_info['value'].split('-')[-1]}"})
    frameattr = cj_result['frameAttrs'][2]
    for attr_obj in frameattr:
        header = attr_obj['header']
        new_pair = {f"{scene_map[header]}": f"{attr_obj['value'].split('-')[-1]}"}
        scene.update(new_pair)
    image_urls = json_content['data']['image_url']
    sensors = []
    for url in image_urls:
        img_name = url.split('/')[-1]
        timestamp = img_name.split('_')[0]
        if re.findall('BW', img_name):
            sensor_id = "Backward"
        elif re.findall('FW', img_name):
            sensor_id = "Forward_Wide"
        elif re.findall('FA', img_name):
            sensor_id = "Forward_Ahead"
        elif re.findall('LF', img_name):
            sensor_id = "Left_Forward"
        elif re.findall('LB', img_name):
            sensor_id = "Left_Backward"
        elif re.findall('RB', img_name):
            sensor_id = "Right_Backward"
        elif re.findall('RF', img_name):
            sensor_id = " Right_Forward"
        else:
            sensor_id = "null"
        sensor = {
            "sensor_id": sensor_id,
            "sensor_data": img_name,
            "timestamp": int(timestamp),
            "width": 1920,
            "height": 1080,
            "channel": 3,
            "url": f"annotation/migration/sentanno/2022-05-05/FUSION202205050001/camera/{img_name}"
        }
        sensors.append(sensor)

    meta = {
        "scene": scene,
        "sensors": sensors
    }
    return meta

def get_pc3d(json_file):
    json_content = load_json(json_file)
    obj_3d = []
    for box in json_content['result']['data']:
        x, y, z = box['3Dcenter'].values()
        length, width, heigth = box['3Dsize'].values()
        alpha = alpha_in_pi(box['3Drotation']['z'])
        box_id = box['id']
        int_id = box['intId']
        point_num = box['pointN']
        class_type = box['classType']
        box_attr = box['attrs']
        if box_attr is None:
            occlusion = "null"
        else:
            occlusion = occlusion_type_map[box_attr['occlusion_type']]
        if not box['cubeMap']:
            visible_in_cam = False
        else:
            visible_in_cam = True

        pc_3d = {
            "type": "PC_3D",
            "coordinate": [[x, y, z], [0, alpha, 0], [length, width, heigth]],
            "property": {
                "sensor_id": "LiDAR_1",
                "spec_version": "v00.17",
                "category": class_type,
                "uuid": box_id,
                "instance_id": int_id,
                "task_id": "FUSION202205050001_15_0017",
                "point_num": point_num,
                "visible_in_cam": visible_in_cam,
                "occlusion_type": occlusion,
                "is_vip": ""
            }
        }
        obj_3d.append(pc_3d)

    return obj_3d


def get_2dbox(json_file):
    img_2d = []
    json_content = load_json(json_file)
    sensor = json_content['data']['image_url'].split('/')[-2]
    sensor_id = sensor_map[sensor]
    result_data = json_content['result']['data']
    group_info = json_content['result']['groupinfo']
    group_map = {}
    for i in range(1, len(group_info)+1):
        group = group_info[i-1]
        for children in group['children']:
            if f"{i}" not in group_map.keys():
                group_map[f"{i}"] = [children['id']]
            else:
                group_map[f"{i}"].append(children['id'])

    if not result_data:
        img_2d = []
    else:
        for box_2d in result_data:
            x_l = []
            y_l = []
            for cdnt in box_2d["coordinate"]:
                x_l.append(cdnt['x'])
                y_l.append(cdnt['y'])
            x_min = min(x_l)
            y_min = min(y_l)
            x_max = max(x_l)
            y_max = max(y_l)
            coordinate = [[x_min, y_min], [x_max, y_max]]

            p_category = box_2d['category']
            if not p_category:
                category = "null"
            else:
                category = p_category[0]

            u_id = box_2d['id']
            instance_id = 0
            for g_key in group_map.keys():
                if u_id in group_map.get(g_key):
                    instance_id = int(g_key)
                else:
                    continue
            box_property = {
                "sensor_id": sensor_id,
                "spec_version": "v00.17",
                "category": category,
                "uuid": u_id,
                "instance_id": instance_id,
                "task_id": "FUSION202205050001_15_0017"
            }
            for attr in box_2d['labelAttrs']:
                key = attr.get('key')
                value = attr.get('value')
                new_pair = {f"{key}": f"{value}"}
                box_property.update(new_pair)

            b_box = {
                "type": "BBOX",
                "coordinate": coordinate,
                "property": box_property
            }
            img_2d.append(b_box)
    return img_2d


def get_light_result(json_file):
    img_2d = []
    json_content = load_json(json_file)
    sensor = json_content['data']['image_url'].split('/')[-2]
    sensor_id = sensor_map[sensor]
    result_data = json_content['result']['data']
    if not result_data:
        img_2d = []
    else:
        for box_2d in result_data:
            x_l = []
            y_l = []
            for cdnt in box_2d["coordinate"]:
                x_l.append(cdnt['x'])
                y_l.append(cdnt['y'])
            x_min = min(x_l)
            y_min = min(y_l)
            x_max = max(x_l)
            y_max = max(y_l)
            coordinate = [[x_min, y_min], [x_max, y_max]]

            p_category = box_2d['category']
            p_label = box_2d['label']
            new_cate = {}
            if not p_category:
                category = "null"
            else:
                category = p_category[0]
                category_list = p_category[1:-1]
                label_list = p_label[1:-1]
                new_cate = dict(zip(category_list, label_list))



            u_id = box_2d['id']
            int_id = box_2d['intId']
            box_property = {
                "sensor_id": sensor_id,
                "spec_version": "v00.17",
                "category": category,
                "uuid": u_id,
                "instance_id": int_id,
                "task_id": "FUSION202205050001_15_0017"
            }
            box_property.update(new_cate)

            b_box = {
                "type": "BBOX",
                "coordinate": coordinate,
                "property": box_property
            }
            img_2d.append(b_box)
    return img_2d


def merge_data(cj_path, pc_path, cr_path, jtd_path, jtp_path, gy_path, result_path):
    cj_fl = list_files(cj_path)
    pc_fl = list_files(pc_path)
    gy_fl = list_files(gy_path)
    for i in range(len(pc_fl)):
        object = []
        meta = get_meta(cj_fl[i], i)
        result_pc = get_pc3d(pc_fl[i])
        object.extend(result_pc)
        result_gy = get_light_result(gy_fl[i])
        object.extend(result_gy)
        for img in img_file:
            cr_fl = list_files(os.path.join(cr_path, img))
            result_cr = get_2dbox(cr_fl[i])
            object.extend(result_cr)
        for img in img_file:
            jtd_fl = list_files(os.path.join(jtd_path, img))
            result_jtd = get_2dbox(jtd_fl[i])
            object.extend(result_jtd)
        for img in img_file:
            jtp_fl = list_files(os.path.join(jtp_path, img))
            result_jtp = get_2dbox(jtp_fl[i])
            object.extend(result_jtp)

        result = {
            "meta": meta,
            "objects": object
        }
        result_file = os.path.join(result_path, os.path.basename(pc_fl[i]))
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(result))



if __name__ == "__main__":
    cj_path = r"D:\Desktop\BasicProject\毛岩\恺望\result\kw场景测试"
    pc_path = r"D:\Desktop\BasicProject\毛岩\恺望\result\kw融合一帧一结果\恺望试标数据\3d_url"
    cr_path = r"D:\Desktop\BasicProject\毛岩\恺望\result\kw车&人\json_42072_91444_20220719175008.zip\恺望试标数据"
    jtd_path = r"D:\Desktop\BasicProject\毛岩\恺望\result\kw交通灯\json_42072_91444_20220720130750.zip\恺望试标数据"
    jtp_path = r"D:\Desktop\BasicProject\毛岩\恺望\result\kw交通牌\json_42072_91444_20220720181946.zip\恺望试标数据"
    gy_path = r"D:\Desktop\BasicProject\毛岩\恺望\result\kw通用物体&光源\恺望-2D.zip"
    result_path = r"D:\Desktop\BasicProject\毛岩\恺望\result\output"
    merge_data(cj_path, pc_path, cr_path, jtd_path, jtp_path, gy_path, result_path)


