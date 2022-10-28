# _*_ coding=: utf-8 _*_
import os


def list_files(file_path: str, suffix: str):
    file_list = []
    for root, _, files in os.walk(file_path):
        for file in files:
            if os.path.splitext(file)[-1] == suffix:
                file_list.append(os.path.join(root, file))
    return file_list


def rename_image(image_dir):
    for file in list_files(image_dir, '.jpg'):
        old_file_name = os.path.basename(file)
        new_name = old_file_name.split('_')[0] + '.jpg'
        new_file = os.path.join(os.path.dirname(file), new_name)
        os.rename(file, new_file)

image_dir = r"C:\Users\EDY\Downloads\点云港口试标\点云港口试标"
rename_image(image_dir)
