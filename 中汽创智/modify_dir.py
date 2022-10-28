# _*_ coding=: utf-8 _*_
import os
import shutil

def list_files(in_path: str, ending: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == ending:  # 只读取ending后缀的文件
                file_name = os.path.splitext(file)[0]
                file_list.append(file_name)
            else:
                continue
    return file_list



dir_mapping = {
    "front_left_image_raw": "3d_img0",
    "front_long_image_raw": "3d_img1",
    "front_right_image_raw": "3d_img2",
    "front_wide_image_raw": "3d_img3",
    "rear_left_image_raw": "3d_img4",
    "rear_right_image_raw": "3d_img5",
}


def modify(img_dir_path, pcd_path):
    for dir_name in os.listdir(img_dir_path):
        if dir_name in dir_mapping.keys():
            img_dir = os.path.join(img_dir_path, dir_name)
            pcd_file_list = list_files(pcd_path, '.pcd')
            i = 0
            if os.path.isdir(img_dir):
                new_img_dir = os.path.join(os.path.dirname(img_dir_path), dir_mapping[dir_name])
                if not os.path.exists(new_img_dir):
                    os.mkdir(new_img_dir)
                else:
                    continue
                for img_file in list_files(img_dir, '.jpg'):
                    old_img_file = os.path.join(img_dir, img_file + '.jpg')
                    new_img_file = os.path.join(new_img_dir, pcd_file_list[i] + '.jpg')
                    os.rename(old_img_file, new_img_file)
                    i += 1
        elif dir_name == 'perception_pcd_in_map_temp':
            new_pcd_path = os.path.join(os.path.dirname(img_dir_path), '3d_url')
            if not os.path.exists(new_pcd_path):
                os.mkdir(new_pcd_path)
            else:
                continue
            for pcd_file in list_files(pcd_path, '.pcd'):
                old_pcd_file = os.path.join(pcd_path, pcd_file + '.pcd')
                new_pcd_file = os.path.join(new_pcd_path, pcd_file + '.pcd')
                shutil.copy(old_pcd_file, new_pcd_file)
        else:
                continue


img_dir_path = r"D:\Desktop\BasicProject\王满顺\static\static"
pcd_path = r"D:\Desktop\BasicProject\王满顺\static\static\perception_pcd_in_map_temp"

modify(img_dir_path, pcd_path)
