# _*_ coding=: utf-8 _*_
# _*_ coding=: utf-8 _*_
# @Time    : 2022/07/19
# @Author  : zhangsihao@basicfinder.com
"""
功能：经纬恒润新点云连续帧结果结果导出，针对平台'3D一帧一结果'脚本打包的数据进行转换导出。
使用方法：
    运行程序，根据命令提示输入对应信息，输出文件在原路径上一级的“results”目录下。
"""
import json
import os
import numpy as np
# import open3d as o3d
from tqdm import tqdm
from pathlib import Path
from numpy.lib.recfunctions import repack_fields
import re

# import lzf

numpy_pcd_type_mappings = [
    (np.dtype('float32'), ('F', 4)),
    (np.dtype('float64'), ('F', 8)),
    (np.dtype('uint8'), ('U', 1)),
    (np.dtype('uint16'), ('U', 2)),
    (np.dtype('uint32'), ('U', 4)),
    (np.dtype('uint64'), ('U', 8)),
    (np.dtype('int16'), ('I', 2)),
    (np.dtype('int32'), ('I', 4)),
    (np.dtype('int64'), ('I', 8))]
numpy_type_to_pcd_type = dict(numpy_pcd_type_mappings)
pcd_type_to_numpy_type = dict((q, p) for (p, q) in numpy_pcd_type_mappings)


class PointCloud:
    def __init__(self, pcd_file):
        self.metadata = None
        self.code = None

        if pcd_file is not None:
            if isinstance(pcd_file, (str, Path)):
                with open(pcd_file, 'rb') as f:
                    self.data = self._load_from_file(f)
            else:
                self.data = self._load_from_file(pcd_file)

    @property
    def fields(self):
        return self.data.dtype.names

    def valid_fields(self, fields=None):
        if fields is None:
            fields = self.data.dtype.names
        else:
            fields = [
                f
                for f in fields
                if f in self.data.dtype.names
            ]
        return fields

    def numpy(self, fields=None, dtype=np.float32):
        fields = self.valid_fields(fields)
        return np.stack([
            self.data[name].astype(dtype)
            for name in fields
        ], axis=1)

    def normalized_fields(self, extra_fields: list = None):
        all_fields = set(self.fields)

        fields = ['x', 'y', 'z']
        for f in fields:
            if f not in all_fields:
                raise ValueError(f'can not find "{f}" field in pcd file')

        if 'intensity' in all_fields:
            fields.append('intensity')
        elif 'i' in all_fields:
            fields.append('i')

        if extra_fields:
            for f in extra_fields:
                if f in all_fields:
                    fields.append(f)
        return fields

    def normalized_numpy(self, extra_fields: list = None, dtype=np.float32):
        fields = self.normalized_fields(extra_fields)
        return self.numpy(fields, dtype)

    def normalized_pc(self, extra_fields: list = None):
        fields = self.normalized_fields(extra_fields)
        return repack_fields(self.data[fields])

    @staticmethod
    def _build_dtype(metadata):
        fieldnames = []
        typenames = []

        # process dulipcated names
        fields = metadata['fields']
        fields_dict = set()
        for i in range(len(fields)):
            name = fields[i]
            if name in fields_dict:
                while name in fields_dict:
                    name += '1'
                fields[i] = name
            fields_dict.add(name)

        for f, c, t, s in zip(fields,
                              metadata['count'],
                              metadata.get('type', 'F'),
                              metadata['size']):
            np_type = pcd_type_to_numpy_type[(t, s)]
            if c == 1:
                fieldnames.append(f)
                typenames.append(np_type)
            elif c == 0:  # zero count
                continue
            elif c < 0:  # negative count
                left_count = -c
                while left_count > 0:
                    left_count -= typenames[-1].itemsize
                    fieldnames.pop()
                    typenames.pop()
            else:
                fieldnames.extend(['%s_%04d' % (f, i) for i in range(c)])
                typenames.extend([np_type] * c)
        dtype = np.dtype(list(zip(fieldnames, typenames)))
        return dtype

    def parse_header(self, lines):
        """ Parse header of PCD files.
        """
        metadata = {}
        for ln in lines:
            if ln.startswith('#') or len(ln) < 2:
                continue
            match = re.match('(\w+)\s+([\w\s\.\-]+)', ln)
            if not match:
                print("warning: can't understand line: %s" % ln)
                continue
            key, value = match.group(1).lower(), match.group(2)
            if key == 'version':
                metadata[key] = value
            elif key in ('fields', 'type'):
                metadata[key] = value.split()
            elif key in ('size', 'count'):
                metadata[key] = list(map(int, value.split()))
            elif key in ('width', 'height', 'points'):
                metadata[key] = int(value)
            elif key == 'viewpoint':
                metadata[key] = map(float, value.split())
            elif key == 'data':
                metadata[key] = value.strip().lower()
            # TODO apparently count is not required?
        # add some reasonable defaults
        if 'count' not in metadata:
            metadata['count'] = [1] * len(metadata['fields'])
        if 'viewpoint' not in metadata:
            metadata['viewpoint'] = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]
        if 'version' not in metadata:
            metadata['version'] = '.7'
        return metadata

    @staticmethod
    def _parse_points_from_buf(buf, dtype):
        return np.frombuffer(buf, dtype=dtype)

    # def parse_binary_compressed_pc_data(self, f, dtype, metadata):
    #     """ Parse lzf-compressed data.
    #     """
    #     fmt = 'II'
    #     compressed_size, uncompressed_size = struct.unpack(fmt, f.read(struct.calcsize(fmt)))
    #     compressed_data = f.read(compressed_size)
    #
    #     buf = lzf.decompress(compressed_data, uncompressed_size)
    #     if len(buf) != uncompressed_size:
    #         raise IOError('Error decompressing data')
    #     # the data is stored field-by-field
    #     pc_data = self._parse_points_from_buf(buf, dtype)
    #     return pc_data

    def _load_from_file(self, f):
        header = []
        for _ in range(11):
            ln = f.readline().decode("ascii").strip()
            header.append(ln)
            if ln.startswith('DATA'):
                metadata = self.parse_header(header)
                self.code = code = metadata['data']
                dtype = self._build_dtype(metadata)
                break
        else:
            raise ValueError("invalid file header")

        if code == 'ascii':
            pc = np.genfromtxt(f, dtype=dtype, delimiter=' ')  # np.loadtxt is too slow
            # pc = np.fromfile(f, dtype=dtype, sep=' ') # error
        elif code == 'binary':
            rowstep = metadata['points'] * dtype.itemsize
            buf = f.read(rowstep)
            pc = self._parse_points_from_buf(buf, dtype)
        else:
            raise ValueError(f'invalid pcd DATA: "{code}"')

        return pc

    @staticmethod
    def save_pcd(pc: np.ndarray, file):
        """
        :param structured ndarray
        :param file: str for file object
        """
        fields = pc.dtype.names
        if isinstance(file, str):
            f = open(file, 'wb')

        num_points = len(pc)
        num_fields = len(fields)
        dtypes = [pc.dtype[f] for f in fields]
        headers = [
            '# .PCD v0.7 - Point Cloud Data file format',
            'VERSION 0.7',
            f'FIELDS {" ".join(fields)}',
            f'SIZE {" ".join([str(d.itemsize) for d in dtypes])}',
            f'TYPE {" ".join([d.kind.upper() for d in dtypes])}',
            f'COUNT {" ".join(["1"] * num_fields)}',
            f'WIDTH {num_points}',
            'HEIGHT 1',
            'VIEWPOINT 0 0 0 1 0 0 0',
            f'POINTS {num_points}',
            'DATA binary'
        ]
        header = bytes('\n'.join(headers) + '\n', 'ascii')
        f.write(header)
        f.write(pc.tobytes())

        if isinstance(file, str):
            f.close()


def load_points(pcd_file):
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument('pcd_file', type=str)
    # args = parser.parse_args()

    # from time import time
    # start = time()
    pc = PointCloud(pcd_file)
    points = pc.normalized_numpy()
    return points


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
    return (np.abs(p) < box[3:5] / 2 + MARGIN).all()


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
    poly_center = np.zeros((2,))
    for i in range(4):
        for j in range(4):
            cp = intersection(box_a_corners[i: i + 2], box_b_corners[j: j + 2])
            if cp is not None:
                cross_points[cnt] = cp
                poly_center += cp
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
                cross_points[i:i + 2] = cross_points[i:i + 2][::-1]

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


def whether_overlap(boxes):
    N = len(boxes)
    result = np.zeros((N, N))
    for i, box1 in enumerate(boxes):
        for j in range(i, len(boxes)):
            result[i, j] = result[j, i] = iou_3d(box1, boxes[j]) > 0

    np.set_printoptions(suppress=True, precision=3)
    sum_r = np.sum(result)
    if sum_r <= N:
        lap = 0
    else:
        lap = 1
        # print(result)
    return lap


label_mapping = {
    "Headstock": 25,
    "FullTrailer": 25,
    "EmptyTrailer": 25,
    "Car": 18,
    "Pedestrian": 20,
    "Other_Vehicle_Trailer": 25,
    "Other_Vehicle_Car": 18
}



def list_files(in_path: str):
    file_list = []
    for root, _, files in os.walk(in_path):
        for file in files:
            if os.path.splitext(file)[-1] == '.json':
                file_list.append(os.path.join(root, file))
            else:
                continue
    return file_list


def count_points_in_3dbox(box: np.ndarray, pc: np.ndarray) -> int:
    """
    :param box: [x, y, z, dx, dy, dz, angle]
    :param pc: point cloud
    """
    angle = -box[-1]
    rot_mat = np.asarray([
        [np.cos(angle), -np.sin(angle), 0],
        [np.sin(angle), np.cos(angle), 0],
        [0, 0, 1]
    ])
    pc = (pc[:, :3] - box[:3]) @ rot_mat.T
    mask = (
            (-box[3] / 2 < pc[:, 0]) & (pc[:, 0] < box[3] / 2) &  # x
            (-box[4] / 2 < pc[:, 1]) & (pc[:, 1] < box[4] / 2) &  # y
            (-box[5] / 2 < pc[:, 2]) & (pc[:, 2] < box[5] / 2)  # z
    )
    pc = pc[mask]
    return len(pc)


def get_points(pcd_file):
    # pcd = o3d.io.read_point_cloud(pcd_file)
    points = load_points(pcd_file)
    return points


# 读取json文件内容返回python类型的对象
def load_json(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
    return json_content


def write_json(in_path: str, check_file: str):
    label_list = ["Headstock", "FullTrailer", "EmptyTrailer", "Car", "Pedestrian",
                  "Other_Vehicle_Trailer", "Other_Vehicle_Car"]
    count_l = []
    count_box = 0
    marking_error = []
    missing_pcd_file = []
    empty_result_file = []
    for file in tqdm(list_files(in_path)):
        json_content = load_json(file)
        if not json_content:
            empty_result_file.append(f"{file} 无标注结果")
            annotations = []
            with open(file, 'w', encoding='utf-8') as nf:
                nf.write(json.dumps(annotations))
        else:
            if not json_content['result']:
                empty_result_str = f"{file} 无标注结果"
                empty_result_file.append(empty_result_str)
                annotations = []
                with open(file, 'w', encoding='utf-8') as nf:
                    nf.write(json.dumps(annotations))
            else:
                pcd_path = r"/basicfinder/www/saas.basicfinder.com/api/resource"
                pcd_url = json_content['data']['3d_url']
                pcd_file = os.path.join(pcd_path, pcd_url)

                data_id = json_content['data_id']
                frame_number = json_content['data']['frameNumber'] + 1
                boxs = json_content['result']['data']

                # file_name = os.path.splitext(os.path.basename(file))[0] + '.pcd'
                # pcd_path = r"D:\Desktop\BasicProject\王满顺\经纬恒润\私有化\old_lidar\lidar\LIDAR_LEFT_CLOUD"
                # pcd_file = os.path.join(pcd_path, file_name)
                if not os.path.exists(pcd_file):
                    not_find_str = f"{pcd_file}"
                    missing_pcd_file.append(not_find_str)
                    annotations = []
                    with open(file, 'w', encoding='utf-8') as nf:
                        nf.write(json.dumps(annotations))

                else:
                    points = get_points(pcd_file)
                    annotations = []
                    boxes_l = []
                    for box in boxs:  # 读取每个3D框数据
                        x, y, z = box['3Dcenter'].values()
                        nx = box['3Dsize']['height']
                        ny = box['3Dsize']['width']
                        nz = box['3Dsize']['deep']
                        alpha = box['3Dsize']['alpha']
                        int_id = box['intId']
                        box_id = box['id']
                        attr_label = box['attr']
                        label_l = attr_label['label']
                        complement = False
                        box_border = np.array([x, y, z, nx, ny, nz, alpha])
                        if not label_l:
                            empty_label_str = f"作业ID:{data_id}-第{frame_number}帧-{int_id}号框缺少标签信息"
                            marking_error.append(empty_label_str)
                            continue

                        else:
                            if len(label_l) == 1:
                                if label_l[0] in label_list:
                                    label = label_l[0]
                                elif label_l[0] == '半径70m框':
                                    continue
                                else:
                                    label_chose_str = f"作业ID:{data_id}-第{frame_number}帧-box_id{int_id}标签选择错误"
                                    marking_error.append(label_chose_str)
                                    continue

                            elif len(label_l) == 2:
                                if label_l[0] in label_list and label_l[1] == 'Virtual_box':
                                    label = label_l[0]
                                    complement = True
                                elif label_l[1] in label_list and label_l[0] == 'Virtual_box':
                                    label = label_l[1]
                                    complement = True
                                else:
                                    label_chose_str2 = f"作业ID:{data_id}-第{frame_number}帧-box_id{int_id}标签选择错误"
                                    marking_error.append(label_chose_str2)
                                    continue
                            else:
                                multiple_label_str = f"作业ID:{data_id}-第{frame_number}帧-{int_id}号框标签过多"
                                marking_error.append(multiple_label_str)
                                continue
                        count_l.append(label)

                        if label == 'Virtual_box':

                            box_data = {
                                "name": label,
                                "bbox_center": [x, y, z],
                                "bbox_size": [nx, ny, nz],
                                "heading": alpha
                            }
                            annotations.append(box_data)
                            count_box += 1

                        else:
                            wide = label_mapping[f'{label}']
                            point_num = count_points_in_3dbox(box_border, points)

                            if point_num < wide:
                                border_err_str = f"作业ID:{data_id}-第{frame_number}帧-{int_id}号框点数({point_num})不符合要求"
                                marking_error.append(border_err_str)
                                box_data = {
                                    "name": label,
                                    "bbox_center": [x, y, z],
                                    "bbox_size": [nx, ny, nz],
                                    "heading": alpha,
                                    "complement": complement,
                                    "id": int_id,
                                    "pkg_id": data_id
                                }
                                annotations.append(box_data)
                                count_box += 1
                            else:
                                box_data = {
                                    "name": label,
                                    "bbox_center": [x, y, z],
                                    "bbox_size": [nx, ny, nz],
                                    "heading": alpha,
                                    "complement": complement,
                                    "id": int_id,
                                    "pkg_id": data_id
                                }
                                annotations.append(box_data)
                                count_box += 1

                        box_7 = [x, y, z, nx, ny, nz, alpha]
                        boxes_l.append(box_7)
                    boxes = np.array(boxes_l, np.float32)
                    lap = whether_overlap(boxes)
                    if lap:  # 如果有框重叠
                        overlap_err_str = f"作业ID:{data_id}-第{frame_number}有框重叠"
                        marking_error.append(overlap_err_str)
                    with open(file, 'w', encoding='utf-8') as nf:
                        nf.write(json.dumps(annotations))

    count_info = [f'框总计{count_box}个']
    for one_label in set(count_l):
        count_info.append(f"{one_label}:{count_l.count(one_label)}")
    detection_info = {
        "marking_error": marking_error,
        "count_info": count_info,
        "missing_pcd_file": missing_pcd_file,
        "empty_result_file": empty_result_file
    }
    if not os.path.exists(check_file):
        with open(check_file, 'w', encoding='utf-8') as df:
            df.write(json.dumps(detection_info))
    else:
        with open(check_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            detection_content = json.loads(content)
            detection_content['detection_info'] = detection_info
            with open(check_file, 'w', encoding='utf-8') as df:
                df.write(json.dumps(detection_content))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('result_in_path', type=str)
    parser.add_argument('check_file', type=str)
    args = parser.parse_args()

    result_json_path = args.result_in_path
    check_file = args.check_file
    # check_file = r"D:\Desktop\BasicProject\王满顺\经纬恒润\私有化\old_json\detection.check.txt"
    # result_json_path = r"D:\Desktop\BasicProject\王满顺\经纬恒润\私有化\old_json\lidar - 副本\LIDAR_LEFT_CLOUD"
    write_json(result_json_path, check_file)
