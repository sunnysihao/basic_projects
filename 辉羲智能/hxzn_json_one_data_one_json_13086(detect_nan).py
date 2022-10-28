import os
import json
from tqdm import tqdm


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


def update_json(json_dir: str, check_file: str):
    null_err = []
    for file in tqdm(list_files(json_dir)):
        json_content = load_json(file)
        data = json_content['data']
        data_id = json_content['data_id']
        boxes = json_content['result']['data']
        info = json_content['result']['info']
        data_deleted_file = json_content['result']['data_deleted_file']
        box_data = []
        for box in boxes:
            x, y, z = box['center3D'].values()
            nx, ny, nz = box['size3D'].values()
            int_id = box['trackName']
            frame_number = box['frame'] + 1
            if not x or not y or not z or not nx or not ny or not nz:
                null_str = f"作业ID:{data_id} - 第{frame_number}帧 - {int_id}号框有null值"
                null_err.append(null_str)
                continue
            else:
                mark_dir = {
                    "job_id": data_id,
                    "frame_number": frame_number,
                    "box_id": int_id
                }
                box['mark_dir'] = mark_dir
                attrs = box['attrs']
                w = 0
                if attrs:
                    for obj in attrs.values():
                        if '作废标签不导出' in obj:
                            w += 1
                        else:
                            w = w
                    if not w:
                        box_data.append(box)
                    else:
                        continue
                else:
                    box_data.append(box)

        result = {
            "data": box_data,
            "info": info,
            "data_deleted_file": data_deleted_file
        }
        new_content = {
            "data": data,
            "result": result,
            "data_id": data_id
        }
        with open(file, 'w', encoding='utf-8') as nf:
            nf.write(json.dumps(new_content, ensure_ascii=False))
    detection_info = {
        "has_nan": null_err
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
    parser.add_argument('json_dir', type=str)
    parser.add_argument('check_file', type=str)
    args = parser.parse_args()

    json_dir = args.json_dir
    check_file = args.check_file

    # json_dir = r"C:\Users\EDY\Downloads\下载结果_json_43569_more_20220926154359"
    # check_file = r"C:\Users\EDY\Downloads\下载结果_json_43569_more_20220926154359\新建文件夹\check file.txt"
    update_json(json_dir, check_file)
