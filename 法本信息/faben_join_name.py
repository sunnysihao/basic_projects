# _*_ coding=: utf-8 _*_
# 将pcd和jpg文件分别重命名为"pcd文件名-jpg文件名.pcd"和"pcd文件名-jpg文件名.jpg"
# 并存放至新的目标目录下

import os


def rename_pcd(pcd_path: str, jpg_path: str, to_pcd_path: str):
    pcd_filelist = os.listdir(pcd_path)[0:21]
    jpg_filelist = os.listdir(jpg_path)[0:21]

    for pcd_file in pcd_filelist:
        new_pcdfile_name = os.path.splitext(pcd_file)[0] + "-" + os.path.splitext(jpg_filelist[pcd_filelist.index(pcd_file)])[0] + ".pcd"
        os.rename(os.path.join(pcd_path, pcd_file), os.path.join(to_pcd_path, new_pcdfile_name))


def rename_jpg(pcd_path: str, jpg_path: str, to_jpg_path: str):
    pcd_filelist = os.listdir(pcd_path)[0:21]
    jpg_filelist = os.listdir(jpg_path)[0:21]
    for jpg_file in jpg_filelist:
        new_jpgfile_name = os.path.splitext(pcd_filelist[jpg_filelist.index(jpg_file)])[0] + ".png"
        os.rename(os.path.join(jpg_path, jpg_file), os.path.join(to_jpg_path, new_jpgfile_name))


if __name__ == "__main__":

    pcd_path = r"D:\BasicProject\任从辉\法本信息\new_rosbag_20220414_e01_2022-04-14-19-43-26_bag\rosbag_20220414_e01_2022-04-14-19-43-26_bag\_-_radars_concat_node_-_fusion_radar"
    jpg_path = r"D:\BasicProject\任从辉\法本信息\new_rosbag_20220414_e01_2022-04-14-19-43-26_bag\rosbag_20220414_e01_2022-04-14-19-43-26_bag\_-_cam_front_center_0_-_csi_cam_-_image_raw_resize"
    to_pcd_path = r"D:\BasicProject\任从辉\neusoft\3d_url"
    to_jpg_path = r"D:\BasicProject\任从辉\neusoft\3d_img0"
    rename_pcd(pcd_path, jpg_path, to_pcd_path)
    rename_jpg(to_pcd_path, jpg_path, to_jpg_path)
