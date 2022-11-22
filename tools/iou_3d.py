import numpy as np


EPS = 1e-8


def rot_mat(angle):
    return np.asarray([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle), np.cos(angle)],
    ])


def point_cmp(a, b, center):
    return np.arctan2(*(a - center)[::-1]) > np.arctan2(*(b - center)[::-1])


def check_in_box2d(box, point):
    """
    :params box: (7) [x, y, z, dx, dy, dz, heading]
    """
    MARGIN = 1e-2

    # rotate the point in the opposite direction of box
    p = rot_mat(-box[6]) @ (point - box[:2])
    return (np.abs(p) < box[3:5]/2 + MARGIN).all()


def intersection(line1, line2):
    # fast exclusion: check_rect_cross
    if (
        not (line1.min(axis=0) < line2.max(axis=0)).all()
        or not (line1.max(axis=0) > line2.min(axis=0)).all()
    ):
        return None

    # check cross standing
    points = np.vstack([line1, line2])
    points_1 = points - line1[0]
    points_2 = points - line2[0]

    cross1 = np.cross(points_1[[2, 1]], points_1[[1, 3]])
    cross2 = np.cross(points_2[[0, 3]], points_2[[3, 1]])
    if cross1.prod() <= 0 or cross2.prod() <= 0:
        return None

    # calculate intersection of two lines
    # s1, s2 = cross1
    # s3, s4 = cross2
    s1 = cross1[0]
    s5 = np.cross(points_1[3], points_1[1])

    p0, p1 = line1
    q0, q1 = line2

    if abs(s5 - s1) > EPS:
        x = (s5 * q0[0] - s1 * q1[0]) / (s5 - s1)
        y = (s5 * q0[1] - s1 * q1[1]) / (s5 - s1)

    else:
        a0 = p0[1] - p1[1]
        b0 = p1[0] - p0[0] 
        c0 = p0[0] * p1[1] - p1[0] * p0[1]

        a1 = q0[1] - q1[1]
        b1 = q1[0] - q0[0]
        c1 = q0[0] * q1[1] - q1[0] * q0[1]

        D = a0 * b1 - a1 * b0

        x = (b0 * c1 - b1 * c0) / D
        y = (a1 * c0 - a0 * c1) / D

    return np.array([x, y])


def box2corners(center, half_size, angle):
    corners = np.stack([-half_size, half_size], axis=0)
    corners = np.stack([
        corners[[0, 1, 1, 0], 0],
        corners[[0, 0, 1, 1], 1]
    ], axis=1)

    corners = corners @ rot_mat(angle).T + center
    return corners


def box_overlap(box_a: np.ndarray, box_b: np.ndarray):
    """
    :params box_a: [x, y, z, dx, dy, dz, heading]
    :params box_b: [x, y, z, dx, dy, dz, heading]
    """
    box_a_corners = box2corners(box_a[:2], box_a[3:5] / 2, box_a[6])
    box_b_corners = box2corners(box_b[:2], box_b[3:5] / 2, box_b[6])

    box_a_corners = np.vstack([box_a_corners, box_a_corners[:1]])
    box_b_corners = np.vstack([box_b_corners, box_b_corners[:1]])

    cnt = 0
    cross_points = np.zeros((16, 2))
    poly_center = np.zeros((2, ))
    for i in range(4):
        for j in range(4):
            cp = intersection(box_a_corners[i: i+2], box_b_corners[j: j+2])
            if cp is not None:
                cross_points[cnt] = cp
                poly_center +=  cp
                cnt += 1
    
    # check corners
    for k in range(4):
        if check_in_box2d(box_a, box_b_corners[k]):
            poly_center = poly_center + box_b_corners[k]
            cross_points[cnt] = box_b_corners[k]
            cnt += 1
            
        if check_in_box2d(box_b, box_a_corners[k]):
            poly_center = poly_center + box_a_corners[k]
            cross_points[cnt] = box_a_corners[k]
            cnt += 1

    if cnt < 3:
        assert cnt == 0
        return 0.0
        
    poly_center /= cnt

    # sort the points of polygon
    for j in range(cnt - 1):
        for i in range(cnt - j - 1):
            if point_cmp(cross_points[i], cross_points[i + 1], poly_center):
                cross_points[i:i+2] = cross_points[i:i+2][::-1]

    # get the overlap areas
    vectors = (cross_points[:cnt] - cross_points[0])[1:]
    area = np.cross(vectors[:-1], vectors[1:]).sum()

    return abs(area) / 2.0


def iou_bev(box_a, box_b):
    """
    :params box_a: [x, y, z, dx, dy, dz, heading]
    :params box_b: [x, y, z, dx, dy, dz, heading]
    """
    sa = box_a[3] * box_a[4]
    sb = box_b[3] * box_b[4]
    s_overlap = box_overlap(box_a, box_b)
    return s_overlap / max(sa + sb - s_overlap, EPS)


def iou_3d(boxes_a: np.ndarray, boxes_b: np.ndarray):
    """
    Args:
        boxes_a: (N, 7) [x, y, z, dx, dy, dz, heading]
        boxes_b: (M, 7) [x, y, z, dx, dy, dz, heading]

    Returns:
        ans_iou: (N, M)
    """
    assert len(boxes_a) == len(boxes_b) == 7

    # height overlap
    boxes_a_height_max = (boxes_a[2] + boxes_a[5] / 2)
    boxes_a_height_min = (boxes_a[2] - boxes_a[5] / 2)
    boxes_b_height_max = (boxes_b[2] + boxes_b[5] / 2)
    boxes_b_height_min = (boxes_b[2] - boxes_b[5] / 2)

    # bev overlap
    overlaps_bev = box_overlap(boxes_a, boxes_b)

    max_of_min = max(boxes_a_height_min, boxes_b_height_min)
    min_of_max = min(boxes_a_height_max, boxes_b_height_max)
    overlaps_h = (min_of_max - max_of_min).clip(min=0)

    # 3d iou
    overlaps_3d = overlaps_bev * overlaps_h

    vol_a = (boxes_a[3] * boxes_a[4] * boxes_a[5])
    vol_b = (boxes_b[3] * boxes_b[4] * boxes_b[5])

    iou3d = overlaps_3d / (vol_a + vol_b - overlaps_3d).clip(min=1e-6)

    return iou3d


def main():
    boxes = np.array([

        [0, 0, 0, 1, 2, 1, 0],
        [1.1, 0, 0, 1, 2, 3, 0],
        [1.2, 0, 0, 1, 2, 3, 0.5],
        [0.5, 1, 0, 1, 2, 3, 1.5],
        [-1.5, 1, 0, 1, 2, 3, 2.5],

        # [-4.738579,   13.21626,    -1.1789553,   2.0536785,   0.81731683,  1.4574084, -2.2514746 ],
        # [-3.1748693, 13.156894,  -1.1951844,  1.9391056,  0.8340628,  1.5417628, -2.1293018]
    ], np.float32)

    N = len(boxes)

    result = np.zeros((N, N))
    for i, box1 in enumerate(boxes):
        for j in range(i, len(boxes)):
            result[i, j] = result[j, i] = iou_3d(box1, boxes[j]) > 0

    np.set_printoptions(suppress=True, precision=3)
    print(result)


if __name__ == '__main__':
    main()
