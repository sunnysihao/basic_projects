# _*_ coding=: utf-8 _*_
# @Time    : 2022/07/08
# @Author  : zhangsihao@basicfinder.com
import json
import os
import math
import numpy as np


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list


def list_dir(in_path: str):
    dir_list = []
    for _dir in os.listdir(in_path):
        if os.path.isdir(os.path.join(in_path, _dir)):
            dir_list.append(_dir)
        else:
            continue
    return dir_list

# 将alpha角度取值范围限制在-pi到pi
def alpha_in_pi(alpha):
    pi = math.pi
    return alpha - math.floor((alpha + pi) / (2 * pi)) * 2 * pi


# 读取json文件内容返回python类型的对象
def load_json(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def write_result(json_dir: str, result_path, check_file):
    count_2d = 0
    count_3d = 0
    for _dir in list_dir(json_dir):
        json_path = os.path.join(json_dir, _dir, '3d_url')
        set_name = _dir
        all_err = {}
        batch_list = []
        for file in list_files(json_path):
            json_file = os.path.join(json_path, file + '.json')
            json_content = load_json(json_file)
            frame_number = json_content['data']['frameNumber']
            boxs = json_content['result']['data']
            if '3d_img1' not in json_content['data'].keys():
                ext = np.array([-0.01535546, 0.02280838, 0.99962192, 0.0,
                                -0.99984817, -0.00858586, -0.01516303, 0.0,
                                0.00823677, -0.99970299, 0.02293675, 0.0,
                                -0.0651113, -0.37164303, 0.14304646, 1.0]).reshape((4, 4))

            elif json_content['data']['3d_img0'] == "":
                ext = np.array([-0.01535546, 0.02280838, 0.99962192, 0,
                                -0.99984817, -0.00858586, -0.01516303, 0,
                                0.00823677, -0.99970299, 0.02293675, 0,
                                -0.0651113, -0.37164303, 0.14304646, 1]).reshape((4, 4))
            else:
                ext = np.array([0.00577052, 0.01929861, 0.99979711, 0,
                                -0.99997176, 0.0049242, 0.00567648, 0,
                                -0.00481365, -0.99980164, 0.01932648, 0,
                                0.02264536, -0.12140267, -0.04125111, 1]).reshape((4, 4))
            cam_ext = ext.T

            one_file_err = []
            line_data = []

            for box in boxs:
                type = box['classType']
                if type == "DontCare":
                    label = type
                    truncated = -1
                    occluded = -1
                    alpha = -10
                    x_list = []
                    y_list = []
                    for one_point in box['points']:
                        x_list.append(one_point['x'])
                        y_list.append(one_point['y'])
                    xmin = min(x_list)
                    xmax = max(x_list)
                    ymin = min(y_list)
                    ymax = max(y_list)
                    scal = f"{xmin:.2f} {ymin:.2f} {xmax:.2f} {ymax:.2f}"
                    height, width, length = -1, -1, -1
                    x, y, z = -1000, -1000, -1000
                    size = f"{height} {width} {length}"
                    bottom_center = f"{x} {y} {z}"
                    rotation_y = -10
                    string = f"{label} {truncated} {occluded} {alpha} {scal} {size} {bottom_center} {rotation_y}\n"
                    line_data.append(string)
                    count_2d += 1
                else:
                    if box['attrs'] != None:
                        label = type
                        if 'truncated' in box['attrs'].keys():
                            truncated = "%.2f" % float(box['attrs']['truncated'])
                        else:
                            truncated = "%.2f" % 0
                        if 'occluded' in box['attrs'].keys():
                            occluded = box['attrs']['occluded']
                        elif '遮挡' in box['attrs'].keys():
                            occluded = box['attrs']['遮挡']
                        else:
                            occluded = 0

                        basic_alpha = alpha_in_pi(box['3Drotation']['z'])
                        scal = "-1 -1 -1 -1"
                        length, width, height = box['3Dsize'].values()
                        x, y, z = box['3Dcenter'].values()
                        z = z - (height / 2)
                        size = f"{height:.2f} {width:.2f} {length:.2f}"
                        center = np.array([x, y, z, 1])
                        n_center = cam_ext @ center
                        nx, ny, nz = n_center[0:3]
                        theta = math.atan2(nx, nz)
                        bottom_center = f"{nx:.2f} {ny:.2f} {nz:.2f}"
                        r_y = -1 * alpha_in_pi(basic_alpha + (math.pi / 2))
                        rotation_y = "%.2f" % r_y
                        alpha = "%.2f" % alpha_in_pi(float(r_y - theta))
                        string = f"{label} {truncated} {occluded} {alpha} {scal} {size} {bottom_center} {rotation_y}\n"
                        line_data.append(string)
                        count_3d += 1
                    else:
                        job_id = box['cBy']
                        int_id = box['intId']

                        one_box_err = f"创建人{job_id}, {int_id}号框标注不符合规范(2d和点云映射数据同时标注)"
                        one_file_err.append(one_box_err)
                        continue
            txt_file_name = f"day_{set_name}_{file}"
            txt_file = os.path.join(result_path, txt_file_name + '.txt')
            if not one_file_err:
                with open(txt_file, 'w', encoding='utf-8') as f:
                    f.writelines(line_data)
            else:
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


        error = {
            "errors": all_err,
            "whitch_batch": list(set(batch_list)),

        }
        err_file = os.path.join(os.path.dirname(result_path), 'errors.json')

        with open(err_file, 'w', encoding='utf-8') as ef:
            ef.write(json.dumps(error))
    check_content = {
        "count_2D&3D": [
            f"2D框数量: {count_2d}",
            f"3D框数量: {count_3d}"
        ]
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


if __name__ == "__main__":
    # import argparse
    #
    # parser = argparse.ArgumentParser()
    # parser.add_argument('result_json_path', type=str)
    # parser.add_argument('output_path', type=str)
    # parser.add_argument('check_file', type=str)
    # args = parser.parse_args()
    #
    # result_json_path = args.result_json_path
    # output_path = args.output_path
    # check_file = args.check_file

    result_json_path = r"C:\Users\EDY\Downloads\json_43585_more_20221205141413\r"
    output_path = r"C:\Users\EDY\Downloads\json_43585_more_20221205141413\kit"
    check_file = r"C:\Users\EDY\Downloads\json_43585_more_20221205141413\c.json"
    write_result(result_json_path, output_path, check_file)

