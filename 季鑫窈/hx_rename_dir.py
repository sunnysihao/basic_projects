# _*_ coding=: utf-8 _*_
import os
from tqdm import tqdm


def list_dir(path):
    dir_l = []
    for dir in os.listdir(path):
        if os.path.isdir(os.path.join(path, dir)):
            dir_l.append(dir)
        else:
            continue
    return dir_l


def rename_dir(path):
    for dir1 in list_dir(path):
        for dir2 in tqdm(list_dir(os.path.join(path, dir1))):
            for dir3 in list_dir(os.path.join(path, dir1, dir2)):
                fp = os.path.join(path, dir1, dir2, dir3)
                if dir3 == 'image_n':
                    os.rename(fp, os.path.join(path, dir1, dir2, '3d_img0'))
                elif dir3 == 'image_w':
                    os.rename(fp, os.path.join(path, dir1, dir2, '3d_img1'))
                elif dir3 == 'pcd':
                    os.rename(fp, os.path.join(path, dir1, dir2, '3d_url'))
                else:
                    continue


if __name__ == '__main__':
    path = r"/tmp/root/model_saas_data/uploadfile/jxy1209 (admin)/mnt/nas/usr/bo.cao/to_anno/send_beisai/11th_20221207"
    # path = r"D:\Desktop\9127389"
    rename_dir(path)
