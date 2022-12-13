# -*- coding: utf-8 -*- 
# @Time : 2022/12/13
# @Author : zhangsihao@basicfinder.com
"""
"""
import json
import pandas as pd
import sqlalchemy
from datetime import datetime
import numpy as np
from id_worker import IdWorker


class JsonEncoder(json.JSONEncoder):
    """Convert numpy classes to JSON serializable objects."""

    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating, np.bool_)):
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(JsonEncoder, self).default(obj)


obj_type_mapping = {
    "3d": '3D_BOX',
    "box2d": '2D_BOX',
    "rect": '2D_RECT'
}
worker = IdWorker(1, 2, 0)


engine = sqlalchemy.create_engine('mysql+pymysql://basicai:mP3L0S93@nlb.alidev.beisai.com:4000/basicai_dataset')



def write_upload_record(upload_id, team_id):
    upload_record = [{
        "id": upload_id,
        "team_id": team_id,
        "serial_number": worker.get_id(),
        "file_url": None,
        "file_name": None,
        "error_message": None,
        "total_file_size": None,
        "downloaded_file_size": None,
        "total_data_num": None,
        "parsed_data_num": None,
        "status": None,
        "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "created_by": None,
        "updated_at": None,
        "updated_by": None
    }]
    data = pd.DataFrame(upload_record)

    data.to_sql('upload_record', con=engine, index=False, if_exists='append')


def write_dataset_result_source(dataset_result_id, team_id, dataset_id, upload_id):
    dataset_result_source_write = {
        "id": [dataset_result_id],
        "team_id": [team_id],
        "dataset_id": [dataset_id],
        "result_name": [f'{dataset_id}_results'],
        "source_id": [upload_id],
        "source_type": ['EXTERNAL_GROUND_TRUTH'],
        "created_at": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        "created_by": [600002],
        "updated_at": None,
        "updated_by": None
    }
    data_result_source = pd.DataFrame(dataset_result_source_write)

    data_result_source.to_sql('dataset_result_source', con=engine, index=False, if_exists='append')


def trans_3D_data(engine, data_id, dataset_id, team_id, dataset_result_id):
    # 根据dataset_id 生成class_name, class_id  及   attr_name,attr_id 映射关系
    csv_class = r"D:\Desktop\Project_file\韩国\dataset_class.csv"
    data_class = pd.read_csv(csv_class)
    data_class_df = data_class[(data_class['dataset_id'] == dataset_id)]
    class_name_id_mapping = {}
    name_attr_mapping = {}
    for x in data_class_df.iloc:
        class_name = x['name']
        class_id = x['id']
        class_name_id_mapping[class_name] = str(class_id)
        class_atts = json.loads(x['attributes'])
        attr_id_mapping = {}
        for att in class_atts:
            name = att['name']
            id = att['id']
            attr_id_mapping[name] = id
        name_attr_mapping[class_name] = attr_id_mapping


    # 获取一个data下所有原始结果
    data_annotation_object_sql = f'''
    select * from data_annotation_object where data_id={data_id}
    '''
    df = pd.read_sql(data_annotation_object_sql, engine)
    objects = []
    # 遍历结果添加进objects
    for box in df.iloc:
        id = box['id']
        team_id = box['team_id']
        dataset_id = box['dataset_id']
        model_class_name = box['model_class_name']
        box_data = json.loads(box['class_attributes'])
        if 'attrs' in box_data.keys():
            obj_t = box_data['objType']
            obj_type = obj_type_mapping[obj_t]
            class_name = box_data['classType']
            if obj_t == '3d':
                obj = {
                    "classId": class_name_id_mapping[class_name],
                    "className": class_name,
                    "classValues": [],
                    "contour": {
                        "center3D": box_data['center3D'],
                        "pointN": box_data['pointN'],
                        "points": box_data['points'],
                        "rotation3D": box_data['rotation3D'],
                        "size3D": box_data['size3D'],
                        "viewIndex": box_data['viewIndex']
                    },
                    "createdAt": str(box['created_at']),
                    "createdBy": box['created_by'],
                    "id": box_data['id'],
                    "meta": {
                        "annotateType": "3D_LABEL",
                        "resultStatus": "True_value",
                        "resultType": "",
                        "valid": 'UNKNOWN'
                    },
                    "modelClass": box_data['modelClass'],
                    "modelConfidence": box['model_confidence'],
                    "trackId": box_data['trackId'],
                    "trackName": box_data['trackName'],
                    "type": obj_type,
                    "version": 1.0
                }
                objects.append(obj)
            elif obj_t == 'box2d':
                obj = {
                    "id": box_data['id'],
                    "type": "2D_BOX",
                    "annotateType": "2D_LABEL",
                    "version": "1",
                    "createdBy": box['created_by'],
                    "createdAt": str(box['created_at']),
                    "trackId": box_data['trackId'],
                    "trackName": box_data['trackName'],
                    "classId": class_name_id_mapping[class_name],
                    "className": class_name,
                    "classValues": [],
                    "contour": {
                        "points": box_data['points'],
                        "viewIndex": box_data['viewIndex']
                    },

                    "meta": {}
                }
                objects.append(obj)
            else:
                obj = {
                    "id": box_data['id'],
                    "type": "2D_RECT",
                    "version": "1",
                    "createdBy": box['created_by'],
                    "createdAt": str(box['created_at']),
                    "trackId": box_data['trackId'],
                    "trackName": box_data['trackName'],
                    "classId": class_name_id_mapping[class_name],
                    "className": class_name,
                    "classValues": [],
                    "contour": {
                        "points": box_data['points'],
                        "viewIndex": box_data['viewIndex']
                    },

                    "meta": {
                        "annotateType": "2D_LABEL"
                    }
                }
                objects.append(obj)

        else:
            continue
    data_annotation_result_write = {
        "id": [600002],
        "team_id": [team_id],
        "dataset_id": [dataset_id],
        "data_id": [data_id],
        "version": [1.0],
        "source_type": ['EXTERNAL_GROUND_TRUTH'],
        "source_id": [dataset_result_id],
        "validity": ['UNKNOWN'],
        "classification_values": None,
        "objects": [json.dumps(objects, ensure_ascii=False, cls=JsonEncoder)],
        "created_at": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        "created_by": [600002],
        "updated_at": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        "updated_by": None
    }
    data_annotation_result = pd.DataFrame(data_annotation_result_write)

    data_annotation_result.to_sql('data_annotation_result', con=engine, index=False, if_exists='append')


def trans_image_data(engine, data_id, dataset_id, team_id, dataset_result_id):
    # 根据dataset_id 生成class_name, class_id  及   attr_name,attr_id 映射关系
    csv_class = r"D:\Desktop\Project_file\韩国\dataset_class.csv"
    data_class = pd.read_csv(csv_class)
    data_class_df = data_class[(data_class['dataset_id'] == dataset_id)]
    class_name_id_mapping = {}
    name_attr_mapping = {}
    for x in data_class_df.iloc:
        class_name = x['name']
        class_id = x['id']
        class_name_id_mapping[class_name] = class_id
        class_atts = json.loads(x['attributes'])
        attr_id_mapping = {}
        for att in class_atts:
            name = att['name']
            id = att['id']
            attr_id_mapping[name] = id
        name_attr_mapping[class_name] = attr_id_mapping


    # 获取一个data下所有原始结果
    data_annotation_object_sql = f'''
    select * from data_annotation_object where data_id={data_id}
    '''
    df = pd.read_sql(data_annotation_object_sql, engine)
    objects = []
    # 遍历结果添加进objects
    for box in df.iloc:
        id = box['id']
        team_id = box['team_id']
        dataset_id = box['dataset_id']
        model_class_name = box['model_class_name']
        box_data = json.loads(box['class_attributes'])
        if 'attrs' in box_data.keys():
            obj_t = box_data['objType']
            obj_type = obj_type_mapping[obj_t]
            class_name = box_data['classType']
            if obj_t == '3d':
                obj = {
                    "id": "62383691-8077-44c2-ad8a-a6a7f54390c5",
                    "type": "2D_BOX",
                    "annotateType": "2D_LABEL",
                    "version": "1",
                    "createdBy": 1,
                    "createdAt": "2012-03-29T10:05:45Z",

                    "trackId": "c0627d18-1aa1-4788-ac88-09e8772ed9bb",
                    "trackName": "Car 1",

                    "classId": 1,
                    "className": "",
                    "classValues": {},

                    "contour": {
                        "points": [
                            { "x": 976.6271156786534, "y": 509.30442784738 },
                            { "x": 976.9704479066531, "y": 518.6737077997769 }
                        ],
                        "viewIndex": 3
                    },

                    "meta": {}
                }
                objects.append(obj)
            elif obj_t == 'box2d':
                obj = {
                    "id": box_data['id'],
                    "type": "2D_BOX",
                    "annotateType": "2D_LABEL",
                    "version": "1",
                    "createdBy": box['created_by'],
                    "createdAt": str(box['created_at']),
                    "trackId": box_data['trackId'],
                    "trackName": box_data['trackName'],
                    "classId": class_name_id_mapping[class_name],
                    "className": class_name,
                    "classValues": [],
                    "contour": {
                        "points": box_data['points'],
                        "viewIndex": box_data['viewIndex']
                    },

                    "meta": {}
                }
                objects.append(obj)
            else:
                obj = {
                    "id": box_data['id'],
                    "type": "2D_RECT",
                    "version": "1",
                    "createdBy": box['created_by'],
                    "createdAt": str(box['created_at']),
                    "trackId": box_data['trackId'],
                    "trackName": box_data['trackName'],
                    "classId": class_name_id_mapping[class_name],
                    "className": class_name,
                    "classValues": [],
                    "contour": {
                        "points": box_data['points'],
                        "viewIndex": box_data['viewIndex']
                    },

                    "meta": {
                        "annotateType": "2D_LABEL"
                    }
                }
                objects.append(obj)

        else:
            continue
    data_annotation_result_write = {
        "id": [600002],
        "team_id": [team_id],
        "dataset_id": [dataset_id],
        "data_id": [data_id],
        "version": [1.0],
        "source_type": ['EXTERNAL_GROUND_TRUTH'],
        "source_id": [dataset_result_id],
        "validity": ['UNKNOWN'],
        "classification_values": None,
        "objects": [json.dumps(objects, ensure_ascii=False, cls=JsonEncoder)],
        "created_at": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        "created_by": [600002],
        "updated_at": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        "updated_by": None
    }
    data_annotation_result = pd.DataFrame(data_annotation_result_write)

    data_annotation_result.to_sql('data_annotation_result', con=engine, index=False, if_exists='append')


