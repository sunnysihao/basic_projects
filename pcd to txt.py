# _*_ coding=: utf-8 _*_
import os
import time
#定义一个三维点类
class Point(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            file_name = os.path.splitext(file)[0]
            file_list.append(file_name)
    return file_list

def write_points2txt(pcd_path):
    for file in list_files(pcd_path):
        new_pcd_path = os.path.join(pcd_path, file + '.pcd')
        points = []
        with open(new_pcd_path, 'r') as f:
            for line in f.readlines()[11:len(f.readlines()) - 1]:
                strs = line.split(' ')
                points.append(Point(strs[0], strs[1], strs[2].strip()))
        with open(os.path.join(os.path.dirname(pcd_path), 'txt_results', file + '.txt'), 'w', encoding='utf-8') as fw:
            for i in range(len(points)):
                linev = points[i].x + " " + points[i].y + " " + points[i].z + "\n"
                fw.writelines(linev)
    # #读取pcd文件,从pcd的第12行开始是三维点
    # with open(filename+'.pcd') as f:
    #     for line in f.readlines()[11:len(f.readlines())-1]:
    #         strs = line.split(' ')
    #         points.append(Point(strs[0], strs[1], strs[2].strip()))
    # ##strip()是用来去除换行符
    # ##把三维点写入txt文件
    # fw = open(filename+'.txt','w')
    # for i in range(len(points)):
    #      linev = points[i].x+" "+points[i].y+" "+points[i].z+"\n"
    #      fw.writelines(linev)
    # fw.close()

if __name__ == "__main__":
    pcd_path = r"D:\Desktop\3548_2048\3548_2048\3d_url"
    start = time.time()
    write_points2txt(pcd_path)
    print(time.time()-start)