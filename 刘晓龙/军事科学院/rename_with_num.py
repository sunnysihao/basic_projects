# _*_ coding=: utf-8 _*_
import os


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.pcd':
                file_list.append(os.path.splitext(file)[0])
    return sorted(file_list)


def foo(p):
    name_num = 1
    pcd_path = os.path.join(p, '3d_url')
    img_path = os.path.join(p, '3d_img0')
    for file in list_files(pcd_path):
        opcd = os.path.join(pcd_path, file + '.pcd')
        npcd = os.path.join(pcd_path, str(name_num) + '.pcd')
        oimg = os.path.join(img_path, file + '.jpg')
        nimg = os.path.join(img_path, str(name_num) + '.jpg')
        os.rename(opcd, npcd)
        os.rename(oimg, nimg)
        name_num += 1

p = r"D:\Desktop\BasicProject\刘晓龙\军事科学院\jskxy_upload_dataset_0927 - 副本"
foo(p)
