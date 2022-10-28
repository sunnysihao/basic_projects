# _*_ coding=: utf-8 _*_
# _*_ coding=: utf-8 _*_
import os
import json
from numpy.linalg import inv
import numpy as np
import time
import threading
import open3d as o3d


class Point(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

pcd_path = r"D:\Desktop\3548_2048\3548_2048\3d_url"


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list

files = list_files(pcd_path)


def write_points2txt(file: str):
    new_pcd_path = os.path.join(pcd_path, file + '.pcd')
    points = []
    with open(new_pcd_path, 'r') as f:
        for line in f.readlines()[11:len(f.readlines()) - 1]:
            strs = line.split(' ')
            points.append(Point(strs[0], strs[1], strs[2].strip()))
    with open(os.path.join(os.path.dirname(pcd_path), 'txt_results', file + '.txt'), 'w', encoding='utf-8') as fw:
        for i in range(len(points)):
            linev = points[i].x + " " + points[i].y + " " + points[i].z + "\n"
            fw.writelines(linev)

def multi_thread():
    threads = []
    for file in files:
        threads.append(
            threading.Thread(target=write_points2txt, args=(file,))
        )
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()



if __name__ == "__main__":

    start = time.time()
    multi_thread()
    print(time.time()-start)