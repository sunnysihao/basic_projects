import os
import json
from tqdm import tqdm


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.pcd':
                file_name = os.path.splitext(file)[0]
                file_list.append(file_name)
    return file_list

data = {
  "3d_img0": {
    "camera_internal": {
      "fx": 1280,
      "fy": 1292,
      "cx": 953,
      "cy": 543
    },
    "camera_external": [
      -0.013918,
      0.999902,
      -0.001556,
      0.037634,
      0.011519,
      -0.001396,
      -0.999933,
      -0.59,
      -0.999837,
      -0.013935,
      -0.011498,
      -0.938253,
      0.0,
      0.0,
      0.0,
      1.0
    ]
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
