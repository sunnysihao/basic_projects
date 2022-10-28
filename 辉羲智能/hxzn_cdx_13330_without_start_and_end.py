
import os
import uuid
from tqdm import tqdm
from scipy.special import comb
import json
import numpy as np
from matplotlib import pyplot as plt


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_list.append(os.path.join(root, file))
    return file_list


def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def bernstein_poly(i, n, ts):
    return comb(n, i) * (ts ** i) * ((1 - ts) ** (n - i))


def bezier_curve(points, max_distance=10):
    num_points = len(points)

    num_segments = 1 + int(np.ceil(np.linalg.norm(points[-1] - points[0]) / max_distance))
    ts = np.linspace(0.0, 1.0, num_segments)

    polynomial_coef = np.stack([
        bernstein_poly(i, num_points - 1, ts)
        for i in range(num_points)
    ], axis=1)

    return polynomial_coef @ points


def plot_points(points, img=None):
    _, ax = plt.subplots(figsize=(16, 8))
    if img is not None:
        W, H = img.size
        ax.imshow(img, extent=[0, W, 0, H])

        points[:, 1] = img.size[1] - points[:, 1]

    ax.plot(points[:, 0], points[:, 1])
    ax.plot(points[:, 0], points[:, 1], "r.")
    plt.show()


def point_from_obj(obj):
    p = np.array([obj[k] for k in 'xy'])
    return p


def bezier_from_point_objs(obj1, obj2):
    points = np.stack([
        point_from_obj(obj)
        for obj in [obj1, obj1['handle'], obj2['handle2'], obj2]
    ], axis=0)
    return points


def simplify_polyline(points, threshold=1, max_distance=20):
    _points = [points[0]]
    for i in range(1, len(points) - 1):
        p1 = _points[-1]
        p, p2 = points[i: i + 2]

        if np.linalg.norm(p2 - p1) > max_distance:
            _points.append(p)
        else:
            dt = p2 - p1
            if abs(dt[0]) > 1e-9:
                dx = (p - p1)[0]
                p_ = np.array([p[0], p1[1] + dx * dt[1] / dt[0]])
                if np.linalg.norm(p_ - p) > threshold:
                    _points.append(p)
    _points.append(points[-1])

    print(f"remove {len(points) - len(_points)} points to {len(_points)}")
    return np.stack(_points, axis=0)


def bezier2poits(coordinate, max_distance=20):
    points = np.vstack([
        bezier_curve(bezier_from_point_objs(*coordinate[i: i + 2]), max_distance=max_distance * 0.3)[
        0 if i == 0 else 1:]
        for i in range(len(coordinate) - 1)
    ])
    # simplify_polyline(points, threshold=2, max_distance=max_distance)
    return points


def write_new_json(old_json_dir: str, check_file: str):
    group_type_list = ['double solid', 'double dash', 'dash solid', 'solid dash', 'merge', 'split']
    result_path = os.path.join(old_json_dir, 'hx_result')
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    result_content = []
    label_list = []
    detection = {}
    missing_group_l = []
    sp_point_error = []
    mark_error = []
    for file in tqdm(list_files(old_json_dir)):
        json_content = load_json(file)
        img_url_l = json_content['data']['image_url']
        groupinfo = json_content['result']['groupinfo']

        all_group_id = []
        for id_info in groupinfo:
            for child_id in id_info['children']:
                all_group_id.append(child_id['id'])

        point_id_mapping = {}
        line_id_color_mapping = {}
        data_id = json_content['data_id']
        for img in img_url_l:
            hardcase = False
            skip = False
            lines = []
            frame_match = img_url_l.index(img)
            image_title = img.split('/')[-1]
            image_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, image_title))
            group = {}

            grouped_lines_with_no_label = []
            for info in groupinfo:
                frame_n = info['frame']
                if frame_n == frame_match:
                    child_type = []
                    for child in info['children']:
                        child_type.append(child['type'])
                    if "point" in child_type:
                        continue
                    else:
                        for child in info['children']:
                            line_id = child['id']
                            grouped_lines_with_no_label.append(line_id)

            for line in json_content['result']['data']:
                frame_number = line['frame']
                int_id = line['intId']
                line_type = line['type']
                ih = line['ih']
                iw = line['iw']
                if frame_number == frame_match:
                    if line_type == 'beziercurve':
                        pointattr = line['pointAttr']
                        coordinate = line['coordinate']
                        for point in coordinate:
                            if "pid" in point.keys():
                                pid_id = point['pid']
                                do_x = point['x']
                                do_y = point['y']
                        if len(coordinate) < 2:
                            sp_err = f"作业id:{data_id}-第{frame_number + 1}帧-{int_id}号标注错误"
                            sp_point_error.append(sp_err)
                            continue
                        else:
                            points = bezier2poits(coordinate).tolist()
                        # try:
                        #     points = bezier2poits(coordinate).tolist()
                        # except:
                        #     print(data_id)
                        #     print(frame_number)
                        #     print(int_id)
                        #     print(coordinate)
                        line_id = line['id']
                        label = line['label']
                        category = line['category']
                        if '颜色' in category:
                            color = label[category.index('颜色')]
                        else:
                            color = 'other'
                        line_id_color_mapping[line_id] = color
                        if '大类别' in category:
                            f_class = label[category.index('大类别')]
                            label_list.append(f_class)
                        else:
                            if line_id in grouped_lines_with_no_label:
                                f_class = 'line'
                            else:
                                no_label1_err = f"作业id:{data_id}-第{frame_number + 1}帧-{int_id}号未选择大类别"
                                mark_error.append(no_label1_err)
                                continue

                        if '线形+起止标签' in category:
                            subclass0 = label[category.index('线形+起止标签')]
                            if subclass0 in ['dash', 'solid', 'other']:
                                subclass = subclass0
                            else:
                                no_label1_err = f"作业id:{data_id}-第{frame_number + 1}帧-{int_id}号用贝塞尔曲线标注起止点"
                                mark_error.append(no_label1_err)
                                continue
                        else:
                            subclass = 'other'

                        if '双线' in category:
                            if line_id not in all_group_id:
                                missing_groups = f"作业id:{data_id}-第{frame_number+1}帧-{int_id}号标注双线无编组"
                                missing_group_l.append(missing_groups)

                        one_line = {
                            "line_id": line_id,
                            "points": points,
                            "color": color,
                            "class": f_class,
                            "subclass": subclass
                        }
                        lines.append(one_line)

                    elif line_type == "point":
                        point_id = line['id']
                        point_type = line['label']
                        sp_point = line['points']
                        sp_x = sp_point[0] * iw
                        sp_y = sp_point[1] * ih
                        sp_coordinate = [sp_x, sp_y]
                        point_id_mapping[point_id] = [sp_coordinate, point_type]

                    elif line_type == 'rect':
                        label = line['label']
                        category = line['category']
                        if '跳过样本' in category and len(label) == 1:
                            data_attr = label[category.index('跳过样本')]
                            if data_attr == 'skip':
                                skip = True
                            else:
                                hardcase = True
                        else:
                            no_label1_err = f"作业id:{data_id}-第{frame_number + 1}帧-{int_id}号用贝塞尔曲线标注起止点"
                            mark_error.append(no_label1_err)
                            continue

            group_mapping = {}

            for info in groupinfo:
                frame_n = info['frame']
                group_id = info['id']
                group_intid = info['intId']
                if frame_n == frame_match:
                    child_type = []
                    for child in info['children']:
                        child_type.append(child['type'])
                    if "point" in child_type:
                        group_line_id = []
                        group_point_id = ''
                        color_check = []
                        for child in info['children']:
                            if child['type'] == 'beziercurve':
                                g_line_id = child['id']
                                group_line_id.append(g_line_id)
                                color_check.append(line_id_color_mapping[g_line_id])
                            elif child['type'] == 'point':
                                g_point_id = child['id']
                                group_point_id = g_point_id
                        if len(set(color_check)) == 1:
                            group_color = list(set(color_check))[0]
                        else:
                            group_color = 'other'

                        group_mapping[group_point_id] = group_line_id
                        line_ids = group_mapping[group_point_id]
                        if len(line_ids) == 2:
                            try:
                                if point_id_mapping[group_point_id][1][0] in group_type_list:
                                    group_info = {
                                        "line_ids": line_ids,
                                        "type": point_id_mapping[group_point_id][1][0],
                                        "color": group_color,
                                        "sp_point": point_id_mapping[group_point_id][0]
                                    }
                                else:
                                    group_label_err = f"作业id:{data_id}-第{frame_n + 1}帧-{group_intid}号编组标签选择错误"
                                    missing_group_l.append(group_label_err)
                                    continue
                            except:
                                sp_err = f"作业id:{data_id}-第{frame_n + 1}帧-{group_intid}号标注错误"
                                sp_point_error.append(sp_err)
                                continue
                        else:
                            group_label_err = f"作业id:{data_id}-第{frame_n + 1}帧-{group_intid}号编组标签选择错误"
                            missing_group_l.append(group_label_err)
                            continue


                    else:
                        line_ids = []
                        g_line_type = None
                        g_line_color = None
                        for child in info['children']:
                            line_id = child['id']
                            line_ids.append(line_id)
                            if '双线' not in info['category']:
                                group_label_err = f"作业id:{data_id}-第{frame_n + 1}帧-{group_intid}号编组标签选择错误"
                                missing_group_l.append(group_label_err)
                                continue
                            else:
                                g_line_type = info['label'][info['category'].index('双线')]

                            if '颜色' not in info['category']:

                                group_label_err = f"作业id:{data_id}-第{frame_n + 1}帧-{group_intid}号编组标签选择错误"
                                missing_group_l.append(group_label_err)
                                continue
                            else:
                                g_line_color = info['label'][info['category'].index('颜色')]
                        if len(line_ids) == 2:
                            group_info = {
                                "line_ids": line_ids,
                                "type": g_line_type,
                                "color": g_line_color,
                                "sp_point": None
                            }
                        else:
                            group_label_err = f"作业id:{data_id}-第{frame_n + 1}帧-{group_intid}号编组标注错误"
                            missing_group_l.append(group_label_err)
                            continue

                    group[group_id] = group_info


            image_data = {
                "image_id": image_id,
                "image_title": image_title,
                "is_hardcase": hardcase,
                "is_skip": skip,
                "lines": lines,
                "group": group
            }
            result_content.append(image_data)
    result_file = os.path.join(result_path, 'hxzn_result.json')

    with open(result_file, 'w', encoding='utf-8') as rf:
        # print(len(json.dumps(result_content)))
        rf.write(json.dumps(result_content))
    label_set = set(label_list)
    detection["总标签数"] = f"{len(label_list)}"
    for one_label in label_set:
        detection[f"{one_label}"] = label_list.count(one_label)
    detection_info = {
        "count_label": detection,
        "missing_group": missing_group_l,
        "sp_point_errors": sp_point_error,
        "marking_errors": mark_error
    }
    if not os.path.exists(check_file):
        with open(check_file, 'w', encoding='utf-8') as df:
            df.write(json.dumps(detection_info))
    else:
        with open(check_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            detection_content = json.loads(content)
            detection_content['detection_info'] = detection_info
            with open(check_file, 'w', encoding='utf-8') as df:
                df.write(json.dumps(detection_content))

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('old_json_dir', type=str)
    parser.add_argument('check_file', type=str)
    args = parser.parse_args()

    old_json_dir = args.old_json_dir
    check_file = args.check_file

    # old_json_dir = r"C:\Users\EDY\Downloads\下载结果_json_44116_110277_20221020152415"
    # check_file = r"C:\Users\EDY\Downloads\下载结果_json_44116_110277_20221020152415\check_file.json"

    write_new_json(old_json_dir, check_file)
