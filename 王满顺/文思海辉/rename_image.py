# _*_ coding=: utf-8 _*_
import os
from tqdm import tqdm


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.png':
                file_list.append(os.path.join(root, file))
    return file_list


def main(path):
    for dir in tqdm(os.listdir(path)):
        one_path = os.path.join(path, dir)
        files = list_files(one_path)
        for i in range(len(files)):
            result_path = os.path.join(path, f'3d_image{i}')
            if not os.path.exists(result_path):
                os.mkdir(result_path)
            file = files[i]
            new_file = os.path.join(result_path, dir + '.png')
            os.rename(file, new_file)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('old_json_dir', type=str)
    args = parser.parse_args()

    old_json_dir = args.old_json_dir
    main(old_json_dir)

