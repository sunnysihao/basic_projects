import os
import json
from tqdm import tqdm
import numpy as np
from numpy.linalg import inv


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.pcd':
                file_name = os.path.splitext(file)[0]
                file_list.append(file_name)
    return file_list

cam_ext = np.array([[0, -1, 0, 0],
                    [0, 0, -1, 0],
                    [1, 0, 0, 0],
                    [0, 0, 0, 1]])
ext = cam_ext
data = {
  "3d_img0": {
    "camera_internal": {
      "fx": 292.1274058,
      "fy": 292.1628842,
      "cx": 335.0661855,
      "cy": 238.4474201
    },
    "camera_external": ext.flatten().tolist()
  }
}


def set_config(pcd_path: str):
    config_path = os.path.join(os.path.dirname(pcd_path), 'camera_config')
    if not os.path.exists(config_path):
        os.mkdir(config_path)
    for file in tqdm(list_files(pcd_path)):
        with open(os.path.join(config_path, file + '.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps(data))
    print(f"----------------------------------\n输出文件在{config_path}")


def main():
    pcd_path = input("请输入pcd点云文件路径:\n")
    while not os.path.exists(pcd_path):
        print(f"=====>路径错误,请重新输入:")
        pcd_path = input()
    else:
        set_config(pcd_path)
        input("已完成， 按任意键退出")

if __name__ == "__main__":

    main()
