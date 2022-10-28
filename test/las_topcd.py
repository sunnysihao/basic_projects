# _*_ coding=: utf-8 _*_
# -*- coding: utf-8 -*-

import numpy as np
import pcl
import random,math
from liblas.file import File
from liblas import header
from liblas.point import Point

import pcl.pcl_visualization


def getCloud():
    file = r"C:\Users\Downloads\python-master\test\data\20190921155916_ZYW_HUBEI_DSX116_LiDAR_1_0054.las"
    inFile = File(file, mode="r")
    in_header = inFile.get_header()
    point_count=in_header.get_count()

    cloud = pcl.PointCloud_PointXYZRGB()

    points = np.zeros((point_count, 4), dtype=np.float32)
    print(point_count)
    # Generate the data
    for i in range(0, point_count):
        point=inFile.read(i)
        points[i][0] = point.get_x()
        points[i][1] = point.get_y()
        points[i][2] = point.get_z()
        color = point.get_color()
        r1 = color.get_red()
        g1 = color.get_green()
        b1 = color.get_blue()

        r2 = math.ceil((float(r1)/65536)*256.0)
        g2 = math.ceil((float(g1)/65536)*256.0)
        b2 = math.ceil((float(b1)/65536)*256.0)
        rgb = (int(r2)) << 16 | (int(g2)) << 8 | (int(b2))

        points[i][3] = rgb

    cloud.from_array(points)
    return cloud

def main():
    cloud=getCloud()
    pcl.save(cloud,r"C:\Users\Downloads\python-master\test\data\20190921155916_ZYW_HUBEI_DSX116_LiDAR_1_0054.pcd")


if __name__ == '__main__':
    main()