# pip install numpy open3d
from pathlib import Path
import json
import numpy as np
import open3d

from iou_3d import iou_3d


def parse_box(box):
    return [
        *[box['3Dcenter'][k] for k in 'xyz'],
        *[box['3Dsize'][k] for k in ['height', 'width', 'deep']], #  # error ['height', 'deep', 'width']
        box['3Dsize']['alpha'],
    ]

def load_boxes(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        boxes = np.array(json.load(f)["result"]['data'])
        bboxes = np.array([
            parse_box(box)
            for box in boxes
        ])
    return bboxes, boxes

def boxes_iou(boxes1, boxes2):
    result = np.zeros((len(boxes1), len(boxes2), 3))
    for i, box1 in enumerate(boxes1):
        for j, box2 in enumerate(boxes2):
            result[i, j] = iou_3d(box1, box2)
    return result

def indices_by_drop(n, drop_indices):
    mask = np.ones(n, dtype=bool)
    mask[drop_indices] = False
    indices = np.arange(n)[mask]
    return indices


def merge_boxes(boxes1, boxes2, iou_max=0.7):
    ious_all = boxes_iou(boxes1, boxes2)

    mask1 = ious_all.max(axis=1).max(axis=-1) > iou_max
    mask2 = ious_all.max(axis=0).max(axis=-1) > iou_max

    iou_overlap = ious_all[mask1][:, mask2]
    if len(iou_overlap) == 0:
        drop_indices1 = drop_indices2 = np.empty((0,), dtype=int)
    else:
        overlap_mask = iou_overlap.max(axis=-1) > iou_max

        prefer1_flag = iou_overlap[:, :, 1] < iou_overlap[:, :, 2]
        drop1 = (~prefer1_flag & overlap_mask).max(axis=1) == 1
        drop2 = (prefer1_flag & overlap_mask).max(axis=0) == 1

        drop_indices1 = np.arange(len(mask1))[mask1][drop1]
        drop_indices2 = np.arange(len(mask2))[mask2][drop2]

    return indices_by_drop(len(boxes1), drop_indices1), indices_by_drop(len(boxes2), drop_indices2)


def merge_boxes_in_files(file1, file2, iou_max=0.7):
    bboxes1, boxes1 = load_boxes(file1)
    bboxes2, boxes2 = load_boxes(file2)
    indices1, indices2 = merge_boxes(bboxes1, bboxes2, iou_max=iou_max)
    bboxes1_left, bboxes2_left = bboxes1[indices1], bboxes2[indices2]
    boxes1_left, boxes2_left = boxes1[indices1], boxes2[indices2]
    
    return [bboxes1_left, bboxes2_left], [boxes1_left, boxes2_left]


def merge_boxes_in_folder(folder_path, iou_max=0.7):
    files = list(Path(folder_path).glob('*.json'))
    if not files:
        return
    bboxes1, boxes1 = load_boxes(files[0])
    total_count = len(boxes1)
    for file in files[1:]:
        bboxes2, boxes2 = load_boxes(file)
        total_count += len(boxes2)
        indices1, indices2 = merge_boxes(bboxes1, bboxes2, iou_max=iou_max)
        bboxes1 = np.vstack([bboxes1[indices1], bboxes2[indices2]])
        boxes1 = np.hstack([boxes1[indices1], boxes2[indices2]])

    final_count = len(boxes1)
    remove_count = total_count-final_count
    print(f'{remove_count} / {total_count} ({remove_count/total_count:.1%}) boxes removed')
    return bboxes1, boxes1

######### Visualize
def translate_boxes_to_open3d_instance(gt_boxes, heading: bool):
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
    if heading:
        lines = np.concatenate([lines, np.array([[1, 4], [7, 6]])], axis=0)

    line_set.lines = open3d.utility.Vector2iVector(lines)

    return line_set, box3d


def draw_box(vis, gt_boxes, color=(0, 1, 0), heading=True):
    for i in range(gt_boxes.shape[0]):
        gt_box = gt_boxes[i]
        line_set, _ = translate_boxes_to_open3d_instance(gt_box, heading=heading)
        line_set.paint_uniform_color(color)

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
            line_set.paint_uniform_color(color)
            vis.add_geometry(line_set)
    return vis


colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1)]

def draw_boxes(boxes_list):
    vis = open3d.visualization.Visualizer()
    vis.create_window()

    vis.get_render_option().background_color = np.zeros(3)

    for idx, boxes in enumerate(boxes_list):
        draw_box(vis, boxes, colors[idx], heading=False)

    vis.run()
    vis.destroy_window()


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--json_dir', type=str, default=None, nargs='?')
    parser.add_argument('-v', action='store_true')
    args = parser.parse_args()


    json_dir = Path(args.json_dir or r'C:\Users\EDY\Downloads\sx拉框\时旭科技滑块80点云拉框.zip\3d_url - 副本\21cloud')
    bboxes, boxes = merge_boxes_in_folder(json_dir)

    # save result
    result_obj = {
        'result': {
            'data': boxes.tolist()
        }
    }
    result_path = json_dir.with_name(f"{json_dir.name}_merge.json")
    with open(result_path, 'w') as f:
        json.dump(result_obj, f)
        print(f"result saved to {result_path}")

    # visualize
    if args.v:
        draw_boxes([bboxes])


if __name__ == '__main__':
    main()
