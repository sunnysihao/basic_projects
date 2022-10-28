# _*_ coding=: utf-8 _*_
import open3d
import matplotlib
import numpy as np
import json
import laspy
import os


box_colormap = [
    [1, 1, 1],
    [0, 1, 0],
    [0, 1, 1],
    [1, 1, 0],

    [1, 0, 0],
    [1, 0, 1],
    [0, 0, 1],

    [0.5, 1, 1],
    [0.5, 1, 0],
    [0.5, 0, 0],
    [0.5, 0, 1],
]


# def get_coor_colors(obj_labels):
#     colors = matplotlib.colors.XKCD_COLORS.values()
#     max_color_num = obj_labels.max()
#
#     color_list = list(colors)[:max_color_num+1]
#     colors_rgba = [matplotlib.colors.to_rgba_array(color) for color in color_list]
#     label_rgba = np.array(colors_rgba)[obj_labels]
#     label_rgba = label_rgba.squeeze()[:, :3]
#
#     return label_rgba


def draw_scenes(points, gt_boxes=None, ref_boxes=None, ref_labels=None, ref_scores=None, point_colors=None, draw_origin=False):
    vis = open3d.visualization.Visualizer()
    vis.create_window()

    vis.get_render_option().point_size = 1.0
    vis.get_render_option().background_color = np.zeros(3)

    # draw origin
    if draw_origin:
        axis_pcd = open3d.geometry.TriangleMesh.create_coordinate_frame(size=1.0, origin=[0, 0, 0])
        vis.add_geometry(axis_pcd)

    pts = open3d.geometry.PointCloud()
    pts.points = open3d.utility.Vector3dVector(points[:, :3])

    vis.add_geometry(pts)
    if point_colors is None:
        pts.colors = open3d.utility.Vector3dVector(np.ones((points.shape[0], 3)))
    else:
        pts.colors = open3d.utility.Vector3dVector(point_colors)

    if gt_boxes is not None:
        vis = draw_box(vis, gt_boxes, (0, 0, 1))

    if ref_boxes is not None:
        vis = draw_box(vis, ref_boxes, (0, 1, 0), ref_labels, ref_scores)

    vis.run()
    vis.destroy_window()


def translate_boxes_to_open3d_instance(gt_boxes):
    """
             4-------- 6
           /|         /|
          5 -------- 3 .
          | |        | |
          . 7 -------- 1
          |/         |/
          2 -------- 0
    """
    center = gt_boxes[0:3]
    lwh = gt_boxes[3:6]
    axis_angles = np.array([0, 0, gt_boxes[6] + 1e-10])
    rot = open3d.geometry.get_rotation_matrix_from_axis_angle(axis_angles)
    box3d = open3d.geometry.OrientedBoundingBox(center, rot, lwh)

    line_set = open3d.geometry.LineSet.create_from_oriented_bounding_box(box3d)

    lines = np.asarray(line_set.lines)
    lines = np.concatenate([lines, np.array([[1, 4], [7, 6]])], axis=0)

    line_set.lines = open3d.utility.Vector2iVector(lines)

    return line_set, box3d


def draw_box(vis, gt_boxes, color=(0, 1, 0), ref_labels=None, score=None):
    for i in range(gt_boxes.shape[0]):
        gt_box = gt_boxes[i]
        line_set, box3d = translate_boxes_to_open3d_instance(gt_box)
        if ref_labels is None:
            line_set.paint_uniform_color(color)
        else:
            line_set.paint_uniform_color(box_colormap[ref_labels[i]])

        vis.add_geometry(line_set)

        # draw offset
        if len(gt_box) >= 9:
            center = gt_box[0:3]
            offset = np.hstack([gt_box[7:9], np.zeros((1,))])
            end = center + offset
            points = [center, end]
            lines = [[0, 1]]
            line_set = open3d.geometry.LineSet()
            line_set.points = open3d.utility.Vector3dVector(points)
            line_set.lines = open3d.utility.Vector2iVector(lines)
            if ref_labels is None:
                line_set.paint_uniform_color(color)
            else:
                line_set.paint_uniform_color(box_colormap[ref_labels[i]])
            vis.add_geometry(line_set)
    return vis

def load_points(pcd_file: str):
    pcd = open3d.io.read_point_cloud(pcd_file)  #type(pcd)--->open3d.cpu.pybind.geometry.PointCloud
    pc = np.asarray(pcd.points)
    return pc


def load_las_points(las_file):
    las = laspy.read(las_file)
    las_x = np.array(las.x)
    las_y = np.array(las.y)
    las_z = np.array(las.z)
    las_X = np.array(las.X)
    las_Y = np.array(las.Y)
    las_Z = np.array(las.Z)
    ax = np.average(las_x)
    ay = np.average(las_y)
    az = np.average(las_z)
    points = np.stack([las_x, las_y, las_z], axis=1)
    points2 = np.stack([las_X, las_Y, las_Z], axis=1)
    return points


def load_result_json(json_file: str):
    with open(json_file, "r", encoding='utf-8') as f:
        json_content = json.load(f)
        boxes = []
        for box in json_content['result']['data']:
            x = box['3Dcenter']['x'] *10
            y = box['3Dcenter']['y']*10
            z = box['3Dcenter']['z']*10
            dx = box['3Dsize']['height']*10
            dy = box['3Dsize']['width']*10
            dz = box['3Dsize']['deep']*10
            alpha = box['3Dsize']['alpha']
            # x = box['3Dcenter']['x']
            # y = box['3Dcenter']['y']
            # z = box['3Dcenter']['z']
            # dx = box['3Dsize']['x']
            # dy = box['3Dsize']['y']
            # dz = box['3Dsize']['z']
            # alpha = box['3Drotation']['z']
            boxes.append([x, y, z, dx, dy, dz, alpha])
        boxes = np.asarray(boxes)
    return boxes


def load_txt_result(txt_file):
    with open(txt_file, 'r', encoding='utf-8') as tf:
        boxes = []
        for line in tf.readlines():
            box = line.strip('\n').split(' ')
            x = float(box[11])
            y = float(box[12])
            z = float(box[13])
            dx = float(box[10])
            dy = float(box[9])
            dz = float(box[8])
            alpha = float(box[14])
            boxes.append([x, y, z, dx, dy, dz, alpha])
        boxes = np.asarray(boxes)
    return boxes


def list_files(in_path: str, match):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == match:
                file_list.append(os.path.join(root, file))
    return file_list


if __name__ == "__main__":

    pcd_file = r"D:\Desktop\BasicProject\王满顺\时旭\时旭科技数据\时旭科技数据\AA_6to12_pcd\AA_6to12_pcd\1cloud_AA_6to12.pcd"
    json_file = r"C:\Users\EDY\Downloads\sx1010\AA_6to12_pcd.zip\AA_6to12_pcd\6cloud_6to12.json"
    las_path = r"D:\Desktop\BasicProject\王满顺\时旭\SX一作业一结果\las_one"
    txt_path = r"D:\Desktop\BasicProject\王满顺\时旭\SX一作业一结果\sx_拉框results_矫正_1018"
    # load_txt_result(txt_file)
    # draw_scenes(points=load_las_points(las_file))
    i = 20
    las_file = list_files(las_path, '.las')[i]
    txt_file = list_files(txt_path, '.txt')[i]
    draw_scenes(points=load_las_points(las_file), ref_boxes=load_txt_result(txt_file))
    # draw_scenes(points=load_points(pcd_file), ref_boxes=load_result_json(json_file))
