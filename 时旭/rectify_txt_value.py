# _*_ coding=: utf-8 _*_
import os


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.txt':
                # file_name = os.path.splitext(file)[0]
                file_list.append(os.path.join(root, file))
    return file_list


def rectify_value(txt_dir, new_dir):
    for file in list_files(txt_dir):
        new_data = []
        new_file = os.path.join(new_dir, os.path.basename(file))
        with open(file, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                line_l = line.split(' ')
                print(line_l)
                label = ''.join(line_l[:-15])
                tru, occ, alpha, xmin, ymin, xmax, ymax, height, width, length, x, y, z, ry, score = line_l[-15:]
                height = float(height)*0.0001
                width = float(width)*0.0001
                length = float(length)*0.0001
                x = float(x) * 0.0001
                y = float(y) * 0.0001
                z = float(z) * 0.0001
                new_line = f"{label} {tru} {occ} {alpha} {xmin} {ymin} {xmax} {ymax} {height} {width} {length} {x} {y} {z} {ry} {score}"
                new_data.append(new_line)
        with open(new_file, 'w', encoding='utf-8') as nf:
            nf.writelines(new_data)


txt_dir = r"D:\Desktop\BasicProject\任从辉\时旭"
new_dir = r"D:\Desktop\BasicProject\王满顺\时旭\new_txt"
rectify_value(txt_dir, new_dir)
