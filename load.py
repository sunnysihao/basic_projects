# _*_ coding=: utf-8 _*_
import threading
import os
import time
import open3d as o3d
import numpy as np
import requests


def func_cost(func):
    def wrapper(*args, **kwargs):
        t1 = time.time()
        res = func(*args, **kwargs)
        t2 = time.time()
        print(func.__name__ + "执行耗时" + str(t2 - t1))
        return res

    return wrapper


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list


def load(pcd_path):
    for file in list_files(pcd_path):
        pcd = o3d.io.read_point_cloud(os.path.join(pcd_path, file + '.pcd'))
        points = np.asarray(pcd.points)



def main():
    save_path = r"D:\Desktop\数据\test\save_o1.pcd"
    t0 = time.time()
    rps = requests.get(
        "https://basicai-alidev-app-dataset.oss-cn-shanghai.aliyuncs.com/1653901307243-30093/point_cloud/01.pcd",
        allow_redirects=True)
    print(f"请求耗时：{time.time() - t0}")
    t1 = time.time()
    string = rps.content
    #print(f"转换成文本耗时：{time.time() - t1}")
    t2 = time.time()
    with open(save_path, 'wb') as f2:
        f2.write(string)
    #print(f"保存耗时：{time.time() - t2}")
    t3 = time.time()
    load(save_path)
    print(f"保存及加载耗时：{time.time() - t1}")

if __name__ == "__main__":
    main()

    # start = time.time()
    # save_path = r"D:\Desktop\数据\test\save_o1.pcd"
    # rps = requests.get(
    #     "https://basicai-alidev-app-dataset.oss-cn-shanghai.aliyuncs.com/1653901307243-30093/point_cloud/01.pcd",
    #     allow_redirects=True)
    # string = rps.text
    # with open(save_path, 'w', encoding='utf-8') as f2:
    #     f2.write(string)
    #
    # load(save_path)
    # # print(time.time() - start)