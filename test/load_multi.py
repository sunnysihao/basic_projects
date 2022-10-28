# _*_ coding=: utf-8 _*_
import numpy as np
import open3d as o3d
import time
import os
import threading


# start = time.time()
# pcd=o3d.io.read_point_cloud(r"D:\Desktop\数据\02.pcd")
# points=np.asarray(pcd.points)
# print(type(points))
# end = time.time()
# print(start - end)

pcd_path = r"D:\Desktop\3548_2048\3548_2048\3d_url"
def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list
files = list_files(pcd_path)

def load(file):
    pcd = o3d.io.read_point_cloud(os.path.join(pcd_path, file + '.pcd'))
    points = np.asarray(pcd.points)



def multi_thread():
    threads = []
    for file in files:
        threads.append(
            threading.Thread(target=load, args=(file,))
        )
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

if __name__ == "__main__":

    start = time.time()
    multi_thread()
    print(time.time()-start)