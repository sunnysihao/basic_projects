# _*_ coding=: utf-8 _*_
"""
将图片以空白填充为指定分辨率
"""
import os.path
from PIL import Image


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list


def fill_image(img_path):
    new_img_path = os.path.join(os.path.dirname(img_path), 'new_img')
    if not os.path.exists(new_img_path):
        os.mkdir(new_img_path)
    for file in list_files(img_path):
        image = Image.open(os.path.join(img_path, file +'.jpg'))
        target_size = (2048, 1024)
        iw, ih = image.size  # 原始图像的尺寸
        w, h = target_size # 目标图像的尺寸
    # print("original size: ", (iw, ih))
    # print("new size: ", (w, h))

        scale = min(w / iw, h / ih)  # 转换的最小比例

    # 保证长或宽，至少一个符合目标图像的尺寸 0.5保证四舍五入
        nw = int(iw * scale + 0.5)
        nh = int(ih * scale + 0.5)

    # print("now nums are: ", (nw, nh))

        image = image.resize((nw, nh), Image.BICUBIC)  # 更改图像尺寸，双立法插值效果很好
    # image.show()
        new_image = Image.new('RGB', target_size, (0, 0, 0))  # 生成黑色图像
    # // 为整数除法，计算图像的位置
        new_image.paste(image, ((w - nw) // 2, (h - nh) // 2))  # 将图像填充为中间图像，两侧为黑色的样式
    # new_image.show()

        new_image.save(os.path.join(new_img_path, file + '.jpg'))


if __name__ == '__main__':
    # img_path = r'C:\Users\EDY\Downloads\img'  # 图片路径
    img_path = input("请输入图片路径:\n")
    fill_image(img_path)
    input("按任意键退出")