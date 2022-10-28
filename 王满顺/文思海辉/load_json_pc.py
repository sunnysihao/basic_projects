import base64
import numpy as np
import json
import os
from tqdm import tqdm


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_list.append(os.path.join(root, file))
    return file_list


def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def main(json_dir):
    pcd_dir = os.path.join(os.path.dirname(json_dir), '3d_url')
    if not os.path.exists(pcd_dir):
        os.mkdir(pcd_dir)
    for file in tqdm(list_files(json_dir)):
        file_name = os.path.splitext(os.path.basename(file))[0]
        pcd_file = os.path.join(pcd_dir, file_name + '.pcd')
        with open(file, 'r') as f:
            json_content = json.load(f)
        points = json_content['points']
        intensities = json_content['intensities']
        xyz_buffer = base64.urlsafe_b64decode(points)
        i_buffer = base64.urlsafe_b64decode(intensities)
        xyz = np.frombuffer(xyz_buffer, np.float32).reshape((-1, 3))
        i = np.frombuffer(i_buffer, np.float32).reshape((-1, 1))
        points = np.hstack((xyz, i))

        with open(pcd_file, 'w', encoding='ascii') as pcd_file:
            point_num = points.shape[0]
            heads = [
                '# .PCD v0.7 - Point Cloud Data file format',
                'VERSION 0.7',
                'FIELDS x y z i',
                'SIZE 4 4 4 4',
                'TYPE F F F F',
                'COUNT 1 1 1 1',
                f'WIDTH {point_num}',
                'HEIGHT 1',
                'VIEWPOINT 0 0 0 1 0 0 0',
                f'POINTS {point_num}',
                'DATA ascii'
            ]

            pcd_file.write('\n'.join(heads))
            for i in range(point_num):
                string_point = '\n' + str(points[i, 0]) + ' ' + str(points[i, 1]) + ' ' + str(points[i, 2]) + ' ' + str(
                    points[i, 3])
                pcd_file.write(string_point)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('old_json_dir', type=str)
    args = parser.parse_args()

    old_json_dir = args.old_json_dir
    main(old_json_dir)
