# -*- coding: utf-8 -*- 
# @Time : 2022/11/16
# @Author : zhangsihao@basicfinder.com
"""
"""
from PIL import Image
import os
import cv2
from tqdm import tqdm

def get_size(filename):
    # Obtain the file size: KB
    size = os.path.getsize(filename)
    return size / 1024

def compress_image(img_path, out_path, mb=10240, step=20, quality=1):
    """不改变图片尺寸压缩图像大小
    :param img_path: 压缩图像读取地址
    :param out_path: 压缩图像存储地址
    :param mb: 压缩目标，KB
    :param step: 每次调整的压缩比率
    :param quality: 初始压缩比率
    :return: 压缩文件地址，压缩文件大小
    """
    o_size = get_size(img_path)
    if o_size < mb:
        return Image.open(img_path)

    img = Image.open(img_path)

    while o_size > mb:
        img = Image.open(img_path)
        img = img.convert('RGB')
        img.save(out_path, quality=quality)
        if quality - step < 0:
            break
        quality -= step
        o_size = get_size(out_path)

    print('File size: ' + str(o_size))
    return img


def list_files(in_path: str, match):
    file_name_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == match:
                file_name_list.append(os.path.join(root, file))
    return file_name_list


def cv_compress(img_path, out_path):
    img_bgr = cv2.imread(img_path)
    print(img_bgr.shape)
    cv2.imwrite(out_path, img_bgr, [cv2.IMWRITE_JPEG_QUALITY, 10])


def main(in_path):
    for file in tqdm(list_files(in_path, '.jpg')):
        out_file = file.replace('pic', 'pic_new')
        cv_compress(file, out_file)


if __name__ == '__main__':
    print("Compress image ...")
    in_path = r"D:\Desktop\Project_file\zx\org\pic"
    img_path = r'D:\Desktop\Project_file\zx\pic\pic\IMG_01_01.jpg'
    out_path = r'D:\Desktop\Project_file\zx\pic\new.jpg' # 必须是 jpeg 类型
    # img = compress_image(img_path, out_path)
    # img.save(r'D:\Desktop\Project file\张旭\pic\new2.jpg', quality=1) # 使用quality=95保证图像大小经过存储后不变

    # cv_compress(img_path, out_path)
    main(in_path)

    print("Compress success!")
