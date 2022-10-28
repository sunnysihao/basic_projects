# _*_ coding=: utf-8 _*_
# _*_ coding=: utf-8 _*_
import os
import json
from numpy.linalg import inv
import numpy as np
import time
import threading

pcd_path = r"D:\Desktop\BasicProject\任从辉\faben\3d_url"
config_path = r"D:\Desktop\BasicProject\任从辉\faben\camera_config"
external = [-0.06822605, -0.99759301, 0.01238581, 0.08573602,
            0.01423414, -0.0133868 , -0.99980915, 1.34397046,
            0.99756869, -0.0680367 ,  0.01511317, -1.99482219,
            0.        ,  0.        ,  0.        ,  1.        ]

external = np.asarray(external).reshape((4, 4))
cam_external = inv(external).flatten().tolist()

data = {
        "3d_img0": {
            "camera_internal": {
                "fx": 688.103,
                "cx": 747.014,
                "cy": 444.738,
                "fy": 692.076
            },
            "camera_external": cam_external
        }
    }

def list_files(in_path:str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list

files = list_files(pcd_path)
def create_congigs(file, config_path:str):
    #for file in list_files(pcd_path):
    with open(os.path.join(config_path, file + ".json"), '+a', encoding='utf-8') as f:
        f.write(json.dumps(data))

def multi_thread():
    threads = []
    for file in files:
        threads.append(
                threading.Thread(target=create_congigs, args=(file, config_path))
            )
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

if __name__ == "__main__":

    start = time.time()
    multi_thread()
    print(time.time()-start)

