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
        "status": 'PARSE_COMPLETED',
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


def write_summary(team_id, dataset_id, data_id, source_id, object_count, source_type, created_at, validity):
    summary = {
        "id": [None]*len(team_id),
        "team_id": team_id,
        "dataset_id": dataset_id,
        "data_id": data_id,
        "source_type": source_type,
        "source_id": source_id,
        "validity": validity,
        "object_count": object_count,
        "classification_ids": [None]*len(team_id),
        "class_ids": [None]*len(team_id),
        "created_at": created_at,
        "created_by": team_id,
        "updated_at": [None]*len(team_id),
        "updated_by": [None]*len(team_id)
    }
    data_summary = pd.DataFrame(summary)

    data_summary.to_sql('data_annotation_result_summary', con=target_engine, index=False, if_exists='append')


def trans_3D_data(data_ids, dataset_id, team_id, dataset_result_id, class_name_id_mapping, name_attr_mapping, ready_data_ids):

    # 根据dataset_id 生成class_name, class_id  及   attr_name,attr_id 映射关系
    # csv_class = r"D:\Desktop\Project_file\韩国\dataset_class.csv"
    # data_class = pd.read_csv(csv_class)
    # data_class_df = data_class[(data_class['dataset_id'] == dataset_id)]
    # 获取一个data下所有原始结果

    for sli in range(0, len(data_ids), 500):
        class_ids = []
        t1 = time.time()
        d_team_id = []
        d_dataset_id = []
        d_data_id = []
        d_version = []
        d_source_type = []
        d_source_id = []
        d_validity = []
        d_objects = []
        d_created_at = []
        d_created_by = []
        d_updated_at = []
        d_object_count = []
        d_validity2 = []
        for data_id in tqdm(data_ids[sli:sli+500], desc=f"{dataset_id}:{sli}-{sli+500}"):
            if data_id in ready_data_ids:
                continue
            else:
                data_annotation_object_sql = f'''
                select * from data_annotation_object where data_id={data_id}
                '''
                df = pd.read_sql(data_annotation_object_sql, result_engine)
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
                            elif class_name not in class_name_id_mapping.keys():
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
                                    try:
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
                                    except:
                                        continue

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
                                    "classId": class_id,
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
                                    "classId": class_id,
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
                        if 'classType' in box_data.keys():
                            class_name = box_data['classType']
                            if not class_name:
                                class_id = ''
                            elif class_name not in class_name_id_mapping.keys():
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
                                    try:
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
                                    except:
                                        continue
                            obj_t = box_data['objType']
                            coordinate = box_data['coordinate']
                            x_l = []
                            y_l = []
                            for point in coordinate:
                                x_l.append(point['x'])
                                y_l.append(point['y'])
                            if obj_t == 'rectangle':
                                points = [{"x": min(x_l), "y": min(y_l)},
                                          {"x": max(x_l), "y": max(y_l)}]
                            else:
                                points = coordinate
                            obj = {
                                "classId": class_id,
                                "className": class_name,
                                "classValues": classValues,
                                "contour": {
                                    "points": points
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
                                    "version": 1.0,
                                    "classType": class_name,
                                },
                                "modelClass": box_data['modelClass'],
                                "modelConfidence": None,
                                "trackId": 1,
                                "trackName": 1,
                                "type": obj_t.upper(),
                                "version": 1.0
                            }
                            objects.append(obj)
                        else:
                            continue

                d_team_id.append(team_id)
                d_dataset_id.append(dataset_id)
                d_data_id.append(data_id)
                d_version.append(1.0)
                d_source_type.append('EXTERNAL_GROUND_TRUTH')
                d_source_id.append(dataset_result_id)
                d_validity.append('UNKNOWN')
                d_objects.append(json.dumps(objects, ensure_ascii=False, cls=JsonEncoder))
                d_created_at.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                d_created_by.append(team_id)
                d_updated_at.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                d_object_count.append(len(objects))
                d_validity2.append('VALID')

        data_annotation_result_write = {
            "id": [None]*len(d_team_id),
            "team_id": d_team_id,
            "dataset_id": d_dataset_id,
            "data_id": d_data_id,
            "version": d_version,
            "source_type": d_source_type,
            "source_id": d_source_id,
            "validity": d_validity,
            "classification_values": [None]*len(d_team_id),
            "objects": d_objects,
            "created_at": d_created_at,
            "created_by": d_created_by,
            "updated_at": d_updated_at,
            "updated_by": [None]*len(d_team_id)
        }
        data_annotation_result = pd.DataFrame(data_annotation_result_write)
        t3 = time.time()
        print(f"数据转换耗时:{t3-t1}")

        data_annotation_result.to_sql('data_annotation_result', con=target_engine, index=False, if_exists='append')
        t4 = time.time()
        print(f"写数据库耗时:{t4 - t3}")

        write_summary(team_id=d_team_id, dataset_id=d_dataset_id, data_id=d_data_id, source_id=d_source_id,
                      object_count=d_object_count, source_type=d_source_type, created_at=d_created_at, validity=d_validity2)


def main(team_id):
    # id_file = r"D:\倍赛\data_ids.json"
    # with open(id_file, 'r', encoding='utf-8') as f:
    #     data_ids = json.load(f)['ids']

    dataset_class_sql = f'''
    select * from dataset_class where team_id={team_id}
    '''
    df_class = pd.read_sql(dataset_class_sql, class_engine)
    dataset_ids = list(set(df_class['dataset_id']))

    dataset_result_sql = f'''
        select * from dataset_result_source where team_id={team_id} and source_type='EXTERNAL_GROUND_TRUTH'
        '''
    df_dataset_ids = pd.read_sql(dataset_result_sql, target_engine)
    has_dataset_ids = list(set(df_dataset_ids['dataset_id']))

    for dataset_id in dataset_ids:
        if dataset_id in [91132, 91133, 150386]:
            continue
        else:
            if dataset_id not in has_dataset_ids:
                serial_number = worker.get_id()
                write_upload_record(team_id, serial_number)
                upload_sql = f'''
                            select * from upload_record where serial_number={serial_number}
                            '''
                upload_df = pd.read_sql(upload_sql, target_engine)
                upload_id = upload_df['id'][0]
                write_dataset_result_source(team_id=team_id, dataset_id=dataset_id, upload_id=upload_id)

            result_source_sql = f'''
            select * from dataset_result_source where team_id={team_id} and dataset_id={dataset_id} and source_type='EXTERNAL_GROUND_TRUTH'
            '''
            result_source_df = pd.read_sql(result_source_sql, target_engine)
            dataset_result_id = result_source_df['id'][0]
            dataset_obj_sql = f'''
            select * from data_annotation_object where dataset_id={dataset_id}
            '''
            dataset_obj_df = pd.read_sql(dataset_obj_sql, result_engine)
            data_ids = list(set(dataset_obj_df['data_id']))

            data_result_sql = f'''
                    select * from data_annotation_result where dataset_id={dataset_id} and source_id={dataset_result_id}
                    '''
            data_result_df = pd.read_sql(data_result_sql, target_engine)
            ready_data_ids = list(set(data_result_df['data_id']))

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
                    try:
                        name = att['name']
                        id = att['id']
                        attr_id_mapping[name] = id
                    except:
                        continue

                name_attr_mapping[class_name] = attr_id_mapping
            # for data_id in tqdm(data_ids, desc=f"{dataset_id}"):
            trans_3D_data(data_ids=data_ids, dataset_id=dataset_id, team_id=team_id,
                          dataset_result_id=dataset_result_id,
                          class_name_id_mapping=class_name_id_mapping, name_attr_mapping=name_attr_mapping, ready_data_ids=ready_data_ids)


if __name__ == '__main__':
    main(team_id=150009)
