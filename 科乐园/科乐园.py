# _*_ coding=: utf-8 _*_
import os
import pandas as pd
import shutil


def list_files(in_path: str):
    files = os.listdir(in_path)
    file_list = []
    for file in files:
        if os.path.isfile(os.path.join(in_path, file)):
            file_list.append(file)
        else:
            continue
    return file_list

def find_pcd_file(in_path):
    files = os.listdir(in_path)
    for file in files:
        if os.path.isfile(os.path.join(in_path, file)):
            if os.path.splitext(file)[-1] == '.pcd':
                pcd_file_name = os.path.splitext(file)[0]
                return pcd_file_name



def list_dir(in_path):
    dirs = os.listdir(in_path)
    dir_list = []
    for odir in dirs:
        if os.path.isdir(os.path.join(in_path, odir)):
            dir_list.append(odir)
        else:
            continue
    return dir_list


def rename_image(dir_path: str, out_put_path: str):
    for f_dir in list_dir(dir_path):
        one_dir_path = os.path.join(dir_path, f_dir)
        csv_file = os.path.join(one_dir_path, 'camera_mapping' + '.csv')
        try:
            img_map = pd.read_csv(csv_file, engine='python')
            image_file_name = find_pcd_file(one_dir_path)

            for file in list_files(one_dir_path):
                if os.path.splitext(file)[-1] == '.pcd':
                    old_pcd_file = os.path.join(one_dir_path, file)
                    new_pcd_file = os.path.join(out_put_path, '3d_url', file)
                    shutil.copyfile(old_pcd_file, new_pcd_file)
                elif os.path.splitext(file)[-1] == '.jpg':
                    dir_dict = dict({'left_front': '3d_img0', 'front_left': '3d_img1', 'front_right': '3d_img2', 'right_front': '3d_img3',
                                'right_rear': '3d_img4', 'rear': '3d_img5', 'left_rear': '3d_img6'})
                    key = img_map.location.values[img_map.uuid.values.tolist().index(os.path.splitext(file)[0])]
                    new_img_file = os.path.join(out_put_path, dir_dict[key], image_file_name + '.jpg')
                    os.rename(os.path.join(one_dir_path, file), new_img_file)
                else:
                    continue
        except Exception as e:
            print(f"{f_dir}-camera_mapping文件为空")


if __name__ == "__main__":
    dir_path = r"D:\Desktop\BasicProject\任从辉\科乐园\test(2)\test"
    out_put_path = r"D:\Desktop\BasicProject\任从辉\科乐园"
    rename_image(dir_path, out_put_path)
    # shutil_pcd(dir_path, out_put_path)