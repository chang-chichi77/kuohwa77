# -*- coding: UTF-8 -*-
from utils.mysql_utils import MysqlAccess
import json

class Mapping(object):

    @staticmethod
    def get_key_value_mapping(vendor, file_type):
        """獲取 Key-Value 映射"""
        try:
            print(f"[DEBUG] GET Query: vendor={repr(vendor)}, file_type={repr(file_type)}")

            test_sql = "SELECT * FROM USER_MAPPING_TABLE LIMIT 5"
            test_raw = MysqlAccess.query(test_sql, [])
            print(f"[DEBUG] Test Query All Data: {test_raw}")

            sql = """
                SELECT FIELD, FIELDVALUE
                FROM USER_MAPPING_TABLE
                WHERE VENDOR = %s AND FILETYPE = %s
            """
            raw = MysqlAccess.query(sql, [vendor, file_type])
            print(f"[DEBUG] Raw Result Type: {type(raw)}, Value: {raw}")
            if raw and len(raw) > 0:
                print(f"[DEBUG] First Row: {raw[0]}")

            data = {}
            if raw:
                for row in raw:
                    field = row.get('FIELD') or row.get('field', '')
                    fieldvalue = row.get('FIELDVALUE') or row.get('fieldvalue', '[]')

                    if isinstance(fieldvalue, str):
                        try:
                            value_list = json.loads(fieldvalue)
                        except:
                            value_list = [fieldvalue]
                    else:
                        value_list = fieldvalue if isinstance(fieldvalue, list) else [fieldvalue]

                    data[field] = value_list

            return {
                'result': 0,
                'message': '',
                'data': data
            }
        except Exception as e:
            print(f"[ERROR] get_key_value_mapping 失敗: {str(e)}")
            return {
                'result': 1,
                'message': f'獲取映射失敗: {str(e)}',
                'data': {}
            }

    @staticmethod
    def autosave_key_value_mapping(data_list):
        """自動保存 Key-Value 映射"""
        try:
            if not data_list:
                return {
                    'result': 1,
                    'message': '資料列表不能為空'
                }

            del_sql = "DELETE FROM USER_MAPPING_TABLE WHERE VENDOR = %s AND FILETYPE = %s"
            insert_sql = """
                INSERT INTO USER_MAPPING_TABLE (VENDOR, FILETYPE, FIELD, FIELDVALUE)
                VALUES (%s, %s, %s, %s)
            """

            deleted_keys = set()

            for item in data_list:
                vendor = item.get('vendor', '')
                file_type = item.get('file_type', '')
                field = item.get('field', '')
                fieldvalue = item.get('fieldvalue', [])

                if not all([vendor, file_type, field]):
                    continue

                key = (vendor, file_type)
                if key not in deleted_keys:
                    MysqlAccess.execute(del_sql, [vendor, file_type])
                    deleted_keys.add(key)

                fieldvalue_str = json.dumps(fieldvalue) if isinstance(fieldvalue, list) else str(fieldvalue)
                MysqlAccess.execute(insert_sql, [vendor, file_type, field, fieldvalue_str])

            return {
                'result': 0,
                'message': ''
            }
        except Exception as e:
            print(f"[ERROR] autosave_key_value_mapping 失敗: {str(e)}")
            return {
                'result': 1,
                'message': f'保存映射失敗: {str(e)}'
            }