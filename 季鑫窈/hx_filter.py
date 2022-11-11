# _*_ coding=: utf-8 _*_
import os
from tqdm import tqdm
import json
import shutil


def list_files(in_path: str, match):
    file_name_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == match:
                file_name_list.append(os.path.splitext(os.path.basename(file))[0])
    return file_name_list


def list_dir(path):
    dir_l = []
    for dir in os.listdir(path):
        if os.path.isdir(os.path.join(path, dir)):
            dir_l.append(dir)
        else:
            continue
    return dir_l

def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def rename_dir(path, save_path, json_file):
    json_content = load_json(json_file)
    name_list = json_content['name']
    for dir1 in list_dir(path):
        for dir2 in tqdm(list_dir(os.path.join(path, dir1))):
            for dir3 in list_dir(os.path.join(path, dir1, dir2)):
                fp = os.path.join(path, dir1, dir2, dir3)

                if dir3 == 'image_n':
                    for file in list_files(fp, '.jpg'):
                        if file not in name_list:
                            old_file = os.path.join(fp, file + '.jpg')
                            new_path = os.path.join(save_path, dir1, dir2, '3d_img0')
                            if not os.path.exists(new_path):
                                os.makedirs(new_path, exist_ok=True)
                            new_file = os.path.join(new_path, file + '.jpg')
                            shutil.copyfile(old_file, new_file)
                elif dir3 == 'image_w':
                    for file in list_files(fp, '.jpg'):
                        if file not in name_list:
                            old_file = os.path.join(fp, file + '.jpg')
                            new_path = os.path.join(save_path, dir1, dir2, '3d_img1')
                            if not os.path.exists(new_path):
                                os.makedirs(new_path, exist_ok=True)
                            new_file = os.path.join(new_path, file + '.jpg')
                            shutil.copyfile(old_file, new_file)
                elif dir3 == 'pcd':
                    for file in list_files(fp, '.pcd'):
                        if file not in name_list:
                            old_file = os.path.join(fp, file + '.pcd')
                            new_path = os.path.join(save_path, dir1, dir2, '3d_url')
                            if not os.path.exists(new_path):
                                os.makedirs(new_path, exist_ok=True)
                            new_file = os.path.join(new_path, file + '.pcd')
                            shutil.copyfile(old_file, new_file)
                else:
                    continue


if __name__ == '__main__':
    # import argparse
    #
    # parser = argparse.ArgumentParser()
    # parser.add_argument('in_path', type=str)
    # args = parser.parse_args()
    # in_path = args.in_path

    path = r"/tmp/root/model_saas_data/uploadfile/jxy3 (admin)/orignal/mnt/nas/usr/bo.cao/to_anno/send_beisai/third_20220927"
    save_path = r"/tmp/root/model_saas_data/uploadfile/jxy3 (admin)/third_set2"
    json_file = r"/tmp/root/model_saas_data/uploadfile/jxy3 (admin)/name_list_set3.json"
    rename_dir(path, save_path, json_file)
