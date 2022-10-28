# _*_ coding=: utf-8 _*_
import os
import glob
import shutil
from tqdm import tqdm


class FileMatch:
    def __init__(self, dir_path):
        file_dir = glob.glob(dir_path + "/*")
        self.filepath = []
        for f in file_dir:
            if f.endswith(".bag"):
                pass
            else:
                self.filepath.append(f)

    def match(self):
        for i in self.filepath:
            pcd_file = os.listdir(i + '\pcd')
            img_file = os.listdir(i + "\jpg")
            # print(img_file)
            for pcd in tqdm(pcd_file):
                # print(i, pcd)
                pcd_prefix = os.path.splitext(pcd)[0]
                dict = {k: eval(pcd_prefix) - eval(os.path.splitext(k)[0]) for k in img_file}

                value = 0
                img_key, diff_val = min(dict.items(), key=lambda x: abs(value - x[1]))
                # print(img_key, diff_val, pcd)
                src_img = os.path.join(i, "jpg", img_key)
                new_img_path = i + "/img_new"
                if not os.path.exists(new_img_path):
                    os.makedirs(new_img_path)
                new_img = os.path.join(new_img_path, pcd_prefix + '.jpg')
                # print(src_img)
                # print(new_img)
                shutil.copyfile(src_img, new_img)


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.pcd':
                file_list.append(file)
                # file_list.append(os.path.join(root, file))
    return file_list


def match_2(pcd, jpg):
    pcd_file = list_files(pcd)
    img_file = list_files(jpg)
    # print(img_file)
    for pcd in tqdm(pcd_file):
        pcd_prefix = os.path.splitext(pcd)[0]
        dict = {k: eval(pcd_prefix) - eval(os.path.splitext(k)[0]) for k in img_file}

        value = 0
        img_key, diff_val = min(dict.items(), key=lambda x: abs(value - x[1]))
        print(img_key, diff_val, pcd)
        src_img = os.path.join(jpg, img_key)
        new_img_path = jpg + "/img_new"
        if not os.path.exists(new_img_path):
            os.makedirs(new_img_path)
        new_img = os.path.join(new_img_path, pcd_prefix + '.jpg')
        # print(src_img)
        # print(new_img)
        shutil.copyfile(src_img, new_img)

# pcd = r"D:\Desktop\BasicProject\刘晓龙\军事科学院\3d_url"
# jpg = r"D:\Desktop\BasicProject\刘晓龙\军事科学院\image_color"
# match(pcd, jpg)

a = FileMatch("E:\标注\吉利\点云\新建文件夹")
a.match()