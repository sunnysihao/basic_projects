# _*_ coding=: utf-8 _*_
import cv2   #pip install opencv-python
import numpy as np
from PIL import Image
import os
from tqdm import tqdm
import json
import threading
from concurrent.futures import ProcessPoolExecutor
import time


def undistortion(image: np.ndarray, intrinsic: np.ndarray, d_coeffs: np.ndarray, method2=True):
    """
    :param image: (H, W, C)
    :param intrinsic: camera intrinsic, (3, 3)
    :param d_coeffs: distortion coefficients, (3, )
    :param method2:
    :return: undistorted image: (H, W, C)
    """
    H, W, C = image.shape

    # 1. build undistorted image uv coordinates
    us = np.arange(W).reshape(-1, 1).repeat(H, axis=1).flatten()
    vs = np.arange(H).reshape(1, -1).repeat(W, axis=0).flatten()
    uv_pinhole = np.stack([us, vs], axis=1)

    # 2. uv => point3d: (x, y, 1)
    f_uv = intrinsic[[0, 1], [0, 1]]
    c_uv = intrinsic[[0, 1], [2, 2]]

    xy = (uv_pinhole - c_uv) / f_uv

    # 3. point3d => fisheye camera image
    r = np.linalg.norm(xy, axis=1)
    if not method2:
        # 3.1 distortion: theta_d = theta(1 + k1*theta^2 + ...)
        theta = np.arctan2(r, 1)
        theta_powers = np.stack([
            np.power(theta, 2+i)
            for i in range(1, len(d_coeffs)*2, 2)
        ], axis=1)

        theta_d = theta_powers @ d_coeffs + theta
        xy_p = (theta_d / r)[:, None] * xy

    else:
        # 3.1 distortion: x_p = x(1 + k1*r^2 + ...)
        r_powers = np.stack([
            np.power(r, 2*i + 2)
            for i in range(len(d_coeffs))
        ], axis=1)

        xy_p = (r_powers @ d_coeffs + 1)[:, None] * xy

    # 3.2 project to image plane
    uv_fisheyey = (xy_p * f_uv + c_uv)
    uv_fisheyey = uv_fisheyey.round().astype(int)

    # 3.3 filter uvs that out of range
    mask = (
        (uv_fisheyey[:, 0] >= 0) & (uv_fisheyey[:, 0] < W) &
        (uv_fisheyey[:, 1] >= 0) & (uv_fisheyey[:, 1] < H)
    )
    uv_pinhole_v = uv_pinhole[mask]
    uv_fisheyey_v = uv_fisheyey[mask]

    # 4. build image
    undistorted_image = np.zeros((H, W, C), dtype=image.dtype)
    undistorted_image[uv_pinhole_v[:, 1], uv_pinhole_v[:, 0]] = image[uv_fisheyey_v[:, 1], uv_fisheyey_v[:, 0]]
    # print(type(undistorted_image))
    return undistorted_image
#相机内参
# K = np.array([[959.021606445312, 0, 966.002258300781],
#               [0, 956.644897460938, 565.31298828125],
#               [0, 0, 1]
# ])
#     #相机畸变参数
# D = np.array([-0.0338808558881283, -0.00246503087691963, -0.00735991634428501, 0.00388033338822424])
#
# K = np.array([[1965.8002929, 0, 934.8499755],
#              [0, 1968.1374511, 533.8405151],
#              [0, 0, 1]
# ])
#     #相机畸变参数
# D = np.array([-0.57033282518, 0.287149816751, 0.0, 0.001661069924, 0.0009303900296])
#
# img2 = Image.open(r"D:\Desktop\BasicProject\毛岩\恺望\恺望-7v融合&amp;单帧分割5帧试标-20220712\62c2a4a30523b0812bd48a86\images\3d_img0\20220621163347087_BW_0.jpg")  #鱼眼图像路径
# image2 = np.asarray(img2)
# new_a = undistortion(image2, K, D, method2=True)  # 畸变5个参数，methon=True，  畸变4个参数methon=False
# # im = Image.fromarray(cv2.undistort(image2, K, D, None, K))
# # im.save(r"D:\Desktop\BasicProject\毛岩\恺望\恺望-7v融合&amp;单帧分割5帧试标-20220712\62c2a4a30523b0812bd48a86\images\3d_img3\new.jpg")   #复原后的图像保存路径
# new = Image.fromarray(new_a)
# new.save(r"D:\Desktop\BasicProject\毛岩\恺望\恺望-7v融合&amp;单帧分割5帧试标-20220712\62c2a4a30523b0812bd48a86\images\3d_img0\new2.jpg")   #复原后的图像保存路径

def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.jpg':
                file_list.append(os.path.join(root, file))
    return file_list


def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def dir_undis(dir):
    image_path = r"E:\迅雷云盘\辉羲新规则数据"
    out_path = r"E:\迅雷云盘\辉羲新规则数据\out_put_path"
    path2 = os.path.join(image_path, dir)
    for file in tqdm(list_files(path2), desc=f"{dir}"):
        cam_name = os.path.basename(os.path.dirname(file))
        file_name = os.path.basename(file)
        dst_path = os.path.join(out_path, dir)
        if not os.path.exists(dst_path):
            os.mkdir(dst_path)
        dst_file = os.path.join(dst_path, file_name)
        cam_json = os.path.join(out_path, 'calibration_beisai_8171_0929.json')
        with open(cam_json, 'r') as f:
            calibs = json.load(f)
        camlib = calibs[dir]
        k = [
            camlib["camera_internal"]['fx'],
            0,
            camlib["camera_internal"]['cx'],
            0,
            camlib["camera_internal"]['fy'],
            camlib["camera_internal"]['cy'],
            0, 0, 1]
        k = np.array(k).reshape(3, 3)
        distort = np.array(camlib['distortion_params'])
        img = Image.open(file)
        image = np.asarray(img)
        # new_arr = undistortion(image, k, distort, method2=False)
        # new_arr = cv2.undistort(image, k, distort, None, k)
        if dir in ['3d_img4', '3d_img6']:
            new_arr = cv2.undistort(image, k, distort, None, k)
        else:
            new_arr = cv2.fisheye.undistortImage(image, k, distort, Knew=k)
        new = Image.fromarray(new_arr)
        if dir in ['3d_img3', '3d_img5']:
            out_arr = new.transpose(Image.ROTATE_180)
            out_arr.save(dst_file)
        else:
            new.save(dst_file)
        # new.save(dst_file)


def multi_thread(dirs):
    threads = []
    for dir in dirs:
        threads.append(
            threading.Thread(target=dir_undis, args=(dir, ))
        )
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


if __name__=='__main__':
    dirs = ['3d_img0', '3d_img1', '3d_img2', '3d_img3', '3d_img4', '3d_img5', '3d_img6']
    # image_path = r"D:\Desktop\BasicProject\季鑫窈\辉曦智能\测试\测试"
    # out_path = r"D:\Desktop\BasicProject\季鑫窈\辉曦智能\测试\out"
    # dir = '3d_img4'
    # dir_undis(dir)
    # t1 = time.time()
    # multi_thread(dirs)
    # print(time.time() - t1)
    #
    t1 = time.time()
    with ProcessPoolExecutor() as executor:
        executor.map(dir_undis, dirs)
    # print(time.time() - t1)




