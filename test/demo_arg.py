# -*- coding: utf-8 -*- 
# @Time : 2022/11/2
# @Author : zhangsihao@basicfinder.com
"""
"""
def main():
    import argparse

    parser = argparse.ArgumentParser(description='arg parser')
    parser.add_argument('las_dir', type=str, help='las files directory')
    parser.add_argument('--pcd_dir', type=str, default=None, nargs='?', help='The pcd files save_path')
    parser.add_argument('--fields', type=str, default='x,y,z', nargs='*', help='The fields of point')
    parser.add_argument('--huge_coordinate_value', type=str, default=False, nargs='?', help='Whether the coordinate value reaches millions')
    args = parser.parse_args()
    las_dir = args.las_dir
    pcd_dir = args.pcd_dir
    fields = args.fields
    huge_coordinate_value = args.huge_coordinate_value

    print(las_dir)
    print(pcd_dir)
    print(fields)
    print(huge_coordinate_value)


if __name__ == '__main__':
    main()