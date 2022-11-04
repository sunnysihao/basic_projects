# _*_ coding=: utf-8 _*_
import os


def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.zip':
                file_list.append(os.path.join(root, file))
    return file_list


def main(in_path, save_path):
    for dir in os.listdir(in_path):
        pcd_file = os.path.join(in_path, dir, 'velodyne_points', 'velodyne.pcd')
        new_pcd_file = os.path.join(save_path, '3d_url', dir + '.pcd')
        os.rename(pcd_file, new_pcd_file)

        image1 = os.path.join(in_path, dir, r'images\fc30', 'image.jpeg')
        nimage1 = os.path.join(save_path, '3d_img0', dir + '.jpeg')
        os.rename(image1, nimage1)

        image1 = os.path.join(in_path, dir, r'images\fc120', 'image.jpeg')
        nimage1 = os.path.join(save_path, '3d_img1', dir + '.jpeg')
        os.rename(image1, nimage1)

        image1 = os.path.join(in_path, dir, r'images\fl', 'image.jpeg')
        nimage1 = os.path.join(save_path, '3d_img2', dir + '.jpeg')
        os.rename(image1, nimage1)

        image1 = os.path.join(in_path, dir, r'images\fr', 'image.jpeg')
        nimage1 = os.path.join(save_path, '3d_img3', dir + '.jpeg')
        os.rename(image1, nimage1)

        image1 = os.path.join(in_path, dir, r'images\rl', 'image.jpeg')
        nimage1 = os.path.join(save_path, '3d_img4', dir + '.jpeg')
        os.rename(image1, nimage1)

        image1 = os.path.join(in_path, dir, r'images\rr', 'image.jpeg')
        nimage1 = os.path.join(save_path, '3d_img5', dir + '.jpeg')
        os.rename(image1, nimage1)


if __name__ == '__main__':
    in_path = r"D:\Desktop\BasicProject\youdao\新建文件夹"
    save_path = r"D:\Desktop\BasicProject\youdao\yd_upload_file"
    main(in_path, save_path)
