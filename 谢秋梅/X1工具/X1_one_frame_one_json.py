import json
import os
from tqdm import tqdm


def list_files(in_path: str, match):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == match:
                file_list.append(os.path.join(root, file))
    return file_list


def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def split_folder(result_file: str):
    mark_err = []
    no_result = []
    check_file = os.path.join(os.path.dirname(result_file), 'check_info.json')
    json_data = load_json(result_file)
    dataset_name = json_data['datasetName']
    json_content = json_data['contents']
    if not json_content:
        print("This file has no annotation result")
    else:
        for j1 in json_content:
            dir_name = j1['name']
            save_path = os.path.join(os.path.dirname(result_file), dir_name)
            if not os.path.exists(save_path):
                os.mkdir(save_path)
            one_file_data = j1['data']
            frame_count = 0
            for obj in tqdm(one_file_data, desc=f"{dir_name}", unit='frame'):
                frame_count += 1
                pcd_url = obj['pointCloud']
                file_name = os.path.splitext(os.path.basename(pcd_url))[0]
                save_json_file = os.path.join(save_path, file_name + '.json')
                results = obj['results']
                if not results:
                    no_result_str = f"{dataset_name} / {dir_name} / {file_name}(frame_number:{frame_count}) | has no annotated results"
                    no_result.append(no_result_str)
                    continue
                else:
                    annotation = []
                    for result in results:
                        boxes = result['objects']
                        for box in boxes:
                            obj_type = box['objType']
                            if obj_type == '3d':
                                try:
                                    label = box['classType']
                                except:
                                    print(results)
                                try:
                                    track_id = box['trackId']
                                    view_index = box['viewIndex']
                                    track_name = box['trackName']
                                except:
                                    continue
                                if not label:
                                    no_label_str = f"{dataset_name} / {dir_name} / {file_name}(frame_number:{frame_count}) / object name:{track_name} | No label selected"
                                    mark_err.append(no_label_str)
                                    continue
                                else:
                                    size = box['size3D']
                                    center = box['center3D']
                                    rotation = box['rotation3D']
                                    box = {
                                        "Label": label,
                                        "Data_type": "worker",
                                        "Type": "Cuboid",
                                        "position": center,
                                        "scale": size,
                                        "rotation": rotation
                                    }
                                    annotation.append(box)
                            else:
                                continue

                result_json = {
                    "Source_Image_Info": {
                        "Pcd_name": file_name + '.pcd',
                        "Pcd_path": os.path.join(dir_name, file_name + '.pcd'),
                        "Copyrighter": "(주)미디어그룹사람과숲",
                        "Time_zone": "",
                        "Location": "",
                        "Gps": "",
                        "Weather": ""
                    },
                    "Annotation": annotation
                }
                with open(save_json_file, 'w', encoding='utf-8') as f:
                    json.dump(result_json, f, ensure_ascii=False)
    check_content = {
        "marking_errors": mark_err,
        "empty_label": no_result
    }
    with open(check_file, 'w', encoding='utf-8') as cf:
        cf.write(json.dumps(check_content, ensure_ascii=False))

if __name__ == '__main__':
    # result_file = input("Please enter the path of the JSON file exported by the platform\n")
    result_file = r"D:\Desktop\Project file\谢秋梅\주_비_고속_103331_N07영일3-20221102065055.json"
    split_folder(result_file)
    input("***Complete***\nPress any key to exit")



