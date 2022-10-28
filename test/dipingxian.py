import os
import json

label_nums = {
'Road':1,
'sidewalk':2,
'lane line':3,
'stop line':4,
'cross line':5,
'lane arrow':6,
'curb':7,
'bump':8,
'building':9,
'trunk':10,
'vegetation':11,
'terrain':12,
'separation':13,
'fence':14,
'pole':15,
'traffic light':16,
'traffic sign':17,
'electricity_box':18,
'Flower bed':19,
'Cone':20,
'Water-filled barrier':21,
'Parking reserve barrier':22,
'Ground lock':23,
'Parking line':24,
'Limitator':25,
'blocking objects':26,
'bus':27,
'truck':28,
'car':29,
'construction vehicle':30,
'bicycle':31,
'motorcycle':32,
'bicyclist':33,
'motorcyclist':34,
'pedestrian':35,
'cart':36,
'animal':37,
'pedicab':38,
'moving object':39,
'shadow':40,
'Ignore':41,
}


def write_pcd(save_path, write_data, mode="r"):
    dir_name = os.path.dirname(save_path)
    basename = os.path.basename(save_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    with open(save_path, mode, encoding='utf-8') as f:
        f.writelines(write_data)

def load_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
        f.close()
    return json_content

def read_pcd(pcd_path):
    with open(pcd_path, 'r') as f:
        f_line = f.readlines()
        f.close()
    pcd_header = f_line[0:10]
    pcd_points = f_line[10:]

    return [pcd_header, pcd_points]

def load_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = json.loads(content)
        f.close()
    return json_content

def json_to_pcd(pcd_path, json_path):
    all_label_dict = {}
    for root, _, files in os.walk(pcd_path):
        for file in files:
            result_points = []
            pcd_data = read_pcd(os.path.join(pcd_path, file))
            pcd_points = pcd_data[1]
            pcd_header = pcd_data[0]
            json_name = file.replace(".pcd", ".json")
            json_contents = load_json(os.path.join(json_path, json_name))
            label_nums_keys = label_nums.keys()
            #  得到所有点和标签id对应的字典
            for re_data in json_contents['result']['data']:
                if (not len(re_data['attr']['label'])):
                    continue
                label_key = re_data['attr']['label'][0]
                if label_key not in label_nums_keys:
                    print("{} 中{} 标签不存在".format(json_name, label_key))
                    continue
                label_id = label_nums[label_key]
                index_list = re_data['indexs']
                label_dict = {}
                for point_index in index_list:
                    label_dict[point_index] = label_id
                all_label_dict.update(label_dict)
            new_pcd_path = os.path.join(pcd_path, 'result', file)
            #  将原pcd中的点数据里  index  替换为对应的标签id
            for point in pcd_points:
                x, y, z, i, index = point
                result_points.append(point.replace(index, all_label_dict[index]))
                with open(new_pcd_path, 'a+'):



def merge_pcd(pcd_path):
    result_points = []
    for root, _, files in os.walk(pcd_path):
        for file in files:
            pcd_data = read_pcd(os.path.join(pcd_path, file))
            pcd_points = pcd_data[1]
            pcd_header = pcd_data[0]
            result_points.append(pcd_points)
    new_pcd_path = os.path.join(pcd_path, 'result')
    with open(new_pcd_path, 'a+', encoding='ascii') as f:
        N = len(result_points)
        list = [
            '# .PCD v0.7 - Point Cloud Data file format\n',
            'VERSION 0.7\n',
            'FIELDS x y z i\n',
            'SIZE 4 4 4 4\n',
            'TYPE F F F F\n',
            'COUNT 1 1 1 1\n']
        f.writelines(list)
        f.write(f'WIDTH {N}\n')
        f.write('HEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\n')
        f.write(f'POINTS {N}\n')
        f.write('DATA ascii')
        for line in result_points:
            x, y, z, i = line
            f.write(f"\n{x} {y} {z} {i}")









