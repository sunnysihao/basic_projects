import json
import os



def list_files(in_path: str, match):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == match:
                file_list.append(os.path.join(root, file))
    return file_list


def load_json(json_file: str):
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def main(txt_path):
    for file in list_files(txt_path, '.txt'):
        line_data = []
        with open(file, 'r') as f:
            for line in f.readlines():
                nline = line.replace('plate', '0')
                line_data.append(nline)
        with open(file, 'w') as nf:
            nf.writelines(line_data)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('txt_path', type=str)
    args = parser.parse_args()

    txt_path = args.txt_path
    # txt_path = r"D:\Desktop\BasicProject\张子千\Bunch\Download tasks_YOLO_21401_18193_20221018091133\1665058321"
    # txt_path = input("请输入txt文件夹路径(支持多级目录):\n")
    main(txt_path)
    # input("已完成，按任意键退出程序!")
