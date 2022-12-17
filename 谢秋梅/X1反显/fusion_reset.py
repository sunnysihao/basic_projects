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
from tqdm import tqdm
import time


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


class_engine = sqlalchemy.create_engine('mysql+pymysql://zhangsihao:x8FWKH0YgTqc7UPt@54.219.241.164:14000/basicai_annotation')
result_engine = sqlalchemy.create_engine('mysql+pymysql://basicai:mP3L0S93@nlb.alidev.beisai.com:4000/basicai_dataset')
target_engine = sqlalchemy.create_engine('mysql+pymysql://zhangsihao:x8FWKH0YgTqc7UPt@54.219.241.164:14000/basicai_dataset')



def write_upload_record(team_id, serial_number):
    upload_record = [{
        "id": None,
        "team_id": [team_id],
        "serial_number": [serial_number],
        "file_url": None,
        "file_name": None,
        "error_message": None,
        "total_file_size": None,
        "downloaded_file_size": None,
        "total_data_num": None,
        "parsed_data_num": None,
        "status": None,
        "created_at": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        "created_by": None,
        "updated_at": None,
        "updated_by": None
    }]
    data = pd.DataFrame(upload_record)

    data.to_sql('upload_record', con=target_engine, index=False, if_exists='append')


def write_dataset_result_source(team_id, dataset_id, upload_id):
    dataset_result_source_write = {
        "id": None,
        "team_id": [team_id],
        "dataset_id": [dataset_id],
        "result_name": [f'{dataset_id}_results'],
        "source_id": [upload_id],
        "source_type": ['EXTERNAL_GROUND_TRUTH'],
        "created_at": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        "created_by": [team_id],
        "updated_at": None,
        "updated_by": None
    }
    data_result_source = pd.DataFrame(dataset_result_source_write)

    data_result_source.to_sql('dataset_result_source', con=target_engine, index=False, if_exists='append')


def write_summary(team_id, dataset_id, data_id, source_id, object_count, classification_ids, class_ids):
    summary = {
        "id": None,
        "team_id": [team_id],
        "dataset_id": [dataset_id],
        "data_id": [data_id],
        "source_type": ['EXTERNAL_GROUND_TRUTH'],
        "source_id": [source_id],
        "validity": ['VALID'],
        "object_count": [object_count],
        "classification_ids": None,
        "class_ids": None,
        "created_at": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        "created_by": [team_id],
        "updated_at": None,
        "updated_by": None
    }
    data_summary = pd.DataFrame(summary)

    data_summary.to_sql('data_annotation_result_summary', con=target_engine, index=False, if_exists='append')


def trans_3D_data(data_id, dataset_id, team_id, dataset_result_id, class_name_id_mapping, name_attr_mapping):
    class_ids = []
    t1 = time.time()
    # 根据dataset_id 生成class_name, class_id  及   attr_name,attr_id 映射关系
    # csv_class = r"D:\Desktop\Project_file\韩国\dataset_class.csv"
    # data_class = pd.read_csv(csv_class)
    # data_class_df = data_class[(data_class['dataset_id'] == dataset_id)]
    # 获取一个data下所有原始结果
    data_annotation_object_sql = f'''
    select * from data_annotation_object where data_id={data_id}
    '''
    df = pd.read_sql(data_annotation_object_sql, result_engine)
    t2 = time.time()
    print(f"结果查询耗时：{t2-t1}")
    objects = []
    # 遍历结果添加进objects
    for box in df.iloc:
        id = box['id']
        team_id = box['team_id']
        dataset_id = box['dataset_id']
        model_class_name = box['model_class_name']
        box_data = json.loads(box['class_attributes'])
        if 'center3D' in box_data.keys():
            if 'attrs' in box_data.keys():
                obj_t = box_data['objType']
                obj_type = obj_type_mapping[obj_t]
                class_name = box_data['classType']
                if not class_name:
                    class_id = ''
                else:
                    class_id = class_name_id_mapping[class_name]
                class_ids.append(class_id)
                attrs = box_data['attrs']
                if not attrs:
                    classValues = []
                else:
                    classValues = []
                    for att_k, att_v in attrs.items():
                        class_value = {
                            "id": name_attr_mapping[class_name][att_k],
                            "pid": None,
                            "pvalue": None,
                            "name": att_k,
                            "type": "RADIO",
                            "value": att_v,
                            "alias": "",
                            "isLeaf": True
                        }
                        classValues.append(class_value)

                if obj_t == '3d':
                    obj = {
                        "classId": class_id,
                        "className": class_name,
                        "classValues": classValues,
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
                        "modelConfidence": None,
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
                        "classValues": classValues,
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
                        "classValues": classValues,
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
                obj = {
                    "contour": {
                        "center3D": box_data['center3D'],
                        "rotation3D": box_data['rotation3D'],
                        "size3D": box_data['size3D']
                    },
                    "meta": {
                        "annotateType": "3D_LABEL",
                        "resultStatus": "True_value",
                        "resultType": "",
                        "valid": 'UNKNOWN'
                    },
                    "modelClass": box_data['modelClass'],
                    "modelConfidence": None,
                    "type": obj_type_mapping[box_data['objType']],
                    "version": 1.0
                }
                objects.append(obj)
        else:  # 图片标注
            class_name = box_data['classType']
            class_ids.append(class_name_id_mapping[class_name])
            attrs = box_data['attrs']
            if not attrs:
                classValues = []
            else:
                classValues = []
                for att_k, att_v in attrs.items():
                    class_value = {
                        "id": name_attr_mapping[class_name][att_k],
                        "pid": None,
                        "pvalue": None,
                        "name": att_k,
                        "type": "RADIO",
                        "value": att_v,
                        "alias": "",
                        "isLeaf": True
                    }
                    classValues.append(class_value)
            obj_t = box_data['objType']
            points = box_data['coordinate']
            x_l = []
            y_l = []
            for point in points:
                x_l.append(point['x'])
                y_l.append(point['y'])
            obj = {
                "classId": class_name_id_mapping[class_name],
                "classValues": classValues,
                "contour": {
                    "points": [
                        {
                            "x": min(x_l),
                            "y": min(y_l)
                        },
                        {
                            "x": max(x_l),
                            "y": max(y_l)
                        }
                    ]
                },
                "createdAt": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "createdBy": team_id,
                "id": box_data['frontId'],
                "meta": {
                    "color": box_data['color'],
                    "lastTime": None,
                    "sourceId": dataset_result_id,
                    "sourceType": "EXTERNAL_GROUND_TRUTH",
                    "updateTime": None,
                    "version": 1.0
                },
                "modelClass": box_data['modelClass'],
                "modelConfidence": box_data['confidence'],
                "trackId": 1,
                "trackName": 1,
                "type": obj_t.upper(),
                "version": 1.0
            }
            objects.append(obj)
    data_annotation_result_write = {
        "id": None,
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
        "created_by": [team_id],
        "updated_at": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        "updated_by": None
    }
    data_annotation_result = pd.DataFrame(data_annotation_result_write)
    t3 = time.time()
    print(f"数据转换耗时:{t3-t2}")

    data_annotation_result.to_sql('data_annotation_result', con=target_engine, index=False, if_exists='append')
    t4 = time.time()
    print(f"写数据库耗时:{t4 - t3}")

    write_summary(team_id=team_id, dataset_id=dataset_id, data_id=data_id, source_id=dataset_result_id, object_count=len(objects), classification_ids=[], class_ids=class_ids)


def main(team_id):
    # dataset_class_sql = f'''
    # select * from dataset_class where team_id={team_id}
    # '''
    # df_class = pd.read_sql(dataset_class_sql, class_engine)
    # dataset_ids = list(set(df_class['dataset_id']))
    for dataset_id in [90512]:
    # dataset_id = 90479`
        serial_number = worker.get_id()
        write_upload_record(team_id, serial_number)
        upload_sql = f'''
        select * from upload_record where serial_number={serial_number}
        '''
        upload_df = pd.read_sql(upload_sql, target_engine)
        upload_id = upload_df['id'][0]
        write_dataset_result_source(team_id=team_id, dataset_id=dataset_id, upload_id=upload_id)
        result_source_sql = f'''
        select * from dataset_result_source where team_id={team_id} and dataset_id={dataset_id} and source_id={upload_id}
        '''
        result_source_df = pd.read_sql(result_source_sql, target_engine)
        dataset_result_id = result_source_df['id'][0]
        dataset_obj_sql = f'''
        select * from data_annotation_object where dataset_id={dataset_id}
        '''
        dataset_obj_df = pd.read_sql(dataset_obj_sql, result_engine)
        data_ids = list(set(dataset_obj_df['data_id']))
        dataset_class_sql = f'''
            select * from dataset_class where dataset_id={dataset_id}
            '''
        data_class_df = pd.read_sql(dataset_class_sql, class_engine)
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
        for data_id in tqdm(data_ids, desc=f"{dataset_id}"):
            trans_3D_data(data_id=data_id, dataset_id=dataset_id, team_id=team_id, dataset_result_id=dataset_result_id,
                          class_name_id_mapping=class_name_id_mapping, name_attr_mapping=name_attr_mapping)


if __name__ == '__main__':
    main(team_id=120231)
