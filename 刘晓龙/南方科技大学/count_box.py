import json
import os
from tqdm import tqdm


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


def main(json_path):
    num_3d = 0
    num_rect = 0
    num_other = 0
    for file in tqdm(list_files(json_path, '.json')):
        json_content = load_json(file)
        boxes = json_content['result']['data']
        for box in boxes:
            box_type = box['objType']
            if box_type == '3d':
                num_3d += 1
            else:
                view_index = box['viewIndex']
                if view_index == 0:
                    num_rect += 1
                else:
                    num_other += 1
    txt_data = [
        f"点云框总数为:{num_3d}\n",
        f"主视角矩形框总数为:{num_rect}\n",
        f"其他视角矩形框数为:{num_other}"
    ]
    # txt_file = os.path.join(os.path.dirname(json_path), 'count 3d_box and rect.txt')
    # with open(txt_file, 'w', encoding='utf-8') as f:
    #     f.writelines(txt_data)
    print(f'**************************************\n'
          f"点云框总数为:{num_3d}\n"
          f"主视角矩形框总数为:{num_rect}\n"
          f"其他视角矩形框数为:{num_other}\n"
          f"**************************************\n")


if __name__ == '__main__':
    json_path = input("请输入json文件路径:\n")
    main(json_path)
    input("已完成，按任意键退出")



