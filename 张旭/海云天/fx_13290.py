import os
import json
import matplotlib.image as mpimg
from copy import deepcopy
from common_funcs import data_persistence, get_json_img_dict, pair_checker, ReverseDisplay

INPUT_PATH = 'OCR试标'
OUTPUT_PATH = 'OCR_result'


def url_changer(org_path, file_name):
    temp = org_path.split('/')
    temp[-1] = file_name
    return '/'.join(temp)


def resource_changer(img):
    y, x, channel = img.shape
    return {
        'width': x,
        'height': y
    }


def to_null():
    return {
        'cBy': "",
        'cTime': None,
        'cStep': "",
        'vBy': "",
        'vStep': "",
        'vTime': ""
    }


if __name__ == '__main__':
    # 读取模板，之后在这个模板的基础上改
    with open('sample.json', mode='r', encoding='utf-8') as f:
        sample = json.load(f)

    json_img_dict = get_json_img_dict(INPUT_PATH)
    # 以精确模式检查是否匹配不上，这里匹配错误原因是json文件命名不规范
    print(pair_checker(json_img_dict, mode=1))
    # 以模糊模式再次检查
    print(pair_checker(json_img_dict, mode=0))

    for k, v in json_img_dict.items():
        # 先将客户标注的json和img都读上来
        with open(os.path.join(INPUT_PATH, k), mode='r', encoding='utf-8') as f:
            customer_json = json.load(f)
        customer_img = mpimg.imread(os.path.join(INPUT_PATH, v))

        # 复制一份模板
        reverse_display = ReverseDisplay(sample, ['rect'])

        # 更改路径
        reverse_display.info['data']['image_url'] = url_changer(reverse_display.info['data']['image_url'], v)

        # 更改resourceinfo，即图源属性
        resource_info = resource_changer(customer_img)
        reverse_display.info['result']['resourceinfo'].update(resource_info)

        # 置空原data id
        reverse_display.info['data_id'] = None

        idx = 0
        # 更改框数据
        for int_id, box in customer_json.items():
            cur_rect = deepcopy(reverse_display.ann_sample[0])

            # 置空原来的一些属性
            cur_rect['id'] = str(k[:-9]) + str(idx)
            cur_rect.update(to_null())

            # 更改显示文本
            cur_rect['text'] = box['txt']

            # 更改int_id和_index
            cur_rect['intId'] = int(int_id)
            cur_rect['_index'] = idx
            idx += 1

            # 更改框宽高、面积
            x0, y0, x3, y3 = eval(box['box'])
            cur_rect['width'] = x3 - x0
            cur_rect['height'] = y3 - y0
            cur_rect['area'] = cur_rect['width'] * cur_rect['height']

            # 更改iw、ih
            iw = resource_info['width']
            ih = resource_info['height']
            cur_rect['iw'] = iw
            cur_rect['ih'] = ih

            # 更改coordinate字段
            cur_rect['points'], cur_rect['coordinate'] = ReverseDisplay.get_rect_pos(x0, y0, x3, y3, iw, ih, mode='abs')
            reverse_display.info['result']['data'].append(cur_rect)

        data_persistence(OUTPUT_PATH, k[:-9] + '.json', reverse_display.info)
