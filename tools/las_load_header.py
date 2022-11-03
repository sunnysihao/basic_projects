# _*_ coding=: utf-8 _*_
# _*_ coding=: utf-8 _*_
import laspy
import numpy as np
from tqdm import tqdm


class_mapping = {
    "0": ['road', 'vegetation', 'terrain',
          'box', 'tower', 'noise'],
    "1": 'building',
    "2": 'tree',
    "3": 'electricity_pole',
    "4": 'pole',
    "5": 'electricity _ wire',
    "6": 'wire',
    "7": 'electricity_box'
}



las=laspy.read(r"D:\Desktop\Project file\胡婷\Lone_Drone\新建文件夹\Merged Millwood Park - Cloud_01 - Cloud.las")
#获取文件头
header=las.header
#点类型
point_format=las.point_format
#属性字段名
dimension_name=point_format.dimension_names
#点集外边框
mins=header.mins
maxs=header.maxs
#点个数
point_num=header.point_count
#获取坐标和颜色
las_x= np.array(las.x)
las_y= np.array(las.y)
las_z= np.array(las.z)

ave_x = np.average(las_x)
ave_y = np.average(las_y)
ave_z = np.average(las_z)

las_X=np.array(las.X)
las_Y= np.array(las.Y)
las_Z= np.array(las.Z)
las_i= np.array(las.intensity)
las_r= np.array(las.red)
las_g= np.array(las.green)
las_b= np.array(las.blue)
#堆叠
points=np.stack([las_x,las_y,las_z],axis=1)  #type(points)--->numpy.ndarray
colors=np.stack([las_r,las_g,las_b],axis=1)  #type(colors)--->numpy.ndarray
points_U=np.stack([las_X,las_Y,las_Z],axis=1)
print(min(las_x)-max(las_x))

print(max(las_x))
print(min(las_y)-max(las_y))
print(max(las_y))
pc = []
for x, y, z in points:
    if min(las_x) + 300 < x < min(las_x) + 305 and min(las_y) + 200 < y < min(las_y) + 205:
        pc.append([x-ave_x, y-ave_y, z-ave_z])
pc = np.array(pc)

with open(r"D:\Desktop\BasicProject\胡婷\Lone_Drone\test01.pcd", 'w', encoding='ascii') as pcd_file:
    point_num = pc.shape[0]
    heads = [
        '# .PCD v0.7 - Point Cloud Data file format',
        'VERSION 0.7',
        'FIELDS x y z',
        'SIZE 4 4 4',
        'TYPE F F F',
        'COUNT 1 1 1',
        f'WIDTH {point_num}',
        'HEIGHT 1',
        'VIEWPOINT 0 0 0 1 0 0 0',
        f'POINTS {point_num}',
        'DATA ascii'
    ]

    pcd_file.write('\n'.join(heads))
    for i in tqdm(range(point_num)):
        string_point = '\n' + str(pc[i, 0]) + ' ' + str(pc[i, 1]) + ' ' + str(pc[i, 2])
        pcd_file.write(string_point)
