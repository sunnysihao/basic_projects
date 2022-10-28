# _*_ coding=: utf-8 _*_
import os
import json


def list_files(path):
    flist = []
    for root, _, files in os.walk(path):
        for file in files:
            flist.append(file)
    return flist

files = list_files(path)

