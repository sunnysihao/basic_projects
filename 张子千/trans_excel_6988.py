# _*_ coding=: utf-8 _*_
# 使用：直接运行程序，然后输入excel文件所在目录路径
import pandas as pd
import json
import os
import re


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list


def get_and_write_data(excel_path: str):
    for exfile in list_files(excel_path):
        excel_file = os.path.join(excel_path, exfile + '.xlsx')
        edata = pd.read_excel(io=excel_file, sheet_name="Screen Attack Labels", header=0)
        j = 0
        methods = edata['CaptureMethod'].values
        if os.path.exists(os.path.join(excel_path, exfile, "Screen Attack Labels")):
            continue
        else:
            os.mkdir(os.path.join(excel_path, exfile))
            os.mkdir(os.path.join(excel_path, exfile, "Screen Attack Labels"))

        output_path = os.path.join(excel_path, exfile, "Screen Attack Labels")
        for method in methods:
            line_data = edata.iloc[j]
            if method == "Photo":

                data = {
                    "source": line_data[1],
                    "labels": {
                        "AttackType": line_data[3],
                        "CaptureMethod": line_data[4],
                        "SourceImagePath": line_data[5],
                        "PhoneModel": line_data[6],
                        "Distance": line_data[7],
                        "ScreenModel": line_data[8],
                        "ScreenResolution": line_data[9],
                        "ScreenSizeMm": line_data[10],
                        "ImageDisplayMode": line_data[11],
                        "ScreenFrameVisible": bool(line_data[12]),
                        "ApplicationUIVisible": bool(line_data[13])
                    }
                }

            else:
                data = {
                        "source": line_data[1],
                        "labels": {
                            "AttackType": line_data[3],
                            "CaptureMethod": line_data[4],
                            "SourceImagePath": line_data[5],
                            "PhoneModel": line_data[6],
                            "ScreenModel": line_data[8],
                            "ScreenResolution": line_data[9],
                            "ScreenSizeMm": line_data[10],
                            "ImageDisplayMode": line_data[11]
                        }
                    }
            if re.search('[/]', line_data[1]):
                file_name = line_data[1].split("/")[-1]
            else:
                file_name = line_data[1].split("\\")[-1]

            with open(os.path.join(output_path, file_name + ".json"), 'w', encoding='utf-8') as f:
                f.write(json.dumps(data))
            j += 1
        edata2 = pd.read_excel(io=excel_file, sheet_name="Print Attack labels", header=0)
        k = 0
        methods = edata2['CaptureMethod'].values
        if os.path.exists(os.path.join(excel_path, exfile, "Print Attack labels")):
            continue
        else:
            os.mkdir(os.path.join(excel_path, exfile, "Print Attack labels"))
        output_path = os.path.join(excel_path, exfile, "Print Attack labels")
        for method in methods:
            line_data = edata2.iloc[k]
            if method == "Photo":

                data2 = {
                    "source": line_data[1],
                    "labels": {
                        "AttackType": line_data[3],
                        "CaptureMethod": line_data[4],
                        "SourceImagePath": line_data[5],
                        "PhoneModel": line_data[6],
                        "Distance": line_data[7],
                        "PrinterType": line_data[8],
                        "PrinterModel": line_data[9],
                        "PrintMode": line_data[10],
                        "PrintScale": line_data[11],
                        "PaperTypw": line_data[12],
                        "Grayscale": bool(line_data[13])
                    }
                }

            else:
                data2 = {
                    "source": line_data[1],
                    "labels": {
                        "AttackType": line_data[3],
                        "CaptureMethod": line_data[4],
                        "SourceImagePath": line_data[5],
                        "PhoneModel": line_data[6],
                        "PrinterType": line_data[8],
                        "PrinterModel": line_data[9],
                        "PrintMode": line_data[10],
                        "PrintScale": line_data[11],
                        "PaperTypw": line_data[12],
                        "Grayscale": bool(line_data[13])
                    }
                }

            if re.search('[/]', line_data[1]):
                file_name = line_data[1].split("/")[-1]
            else:
                file_name = line_data[1].split("\\")[-1]

            with open(os.path.join(output_path, file_name + ".json"), 'w', encoding='utf-8') as f:
                f.write(json.dumps(data2))
            k += 1


if __name__ == "__main__":

    excel_path = r"D:\Desktop\BasicProject\张子千\excel"

    get_and_write_data(excel_path)
