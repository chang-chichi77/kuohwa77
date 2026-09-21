# -*- coding: UTF-8 -*-
from utils.mysql_utils import MysqlAccess

TABLE_NAME = "USER_IMAGE_PATH_TABLE"

class ImageModule(object):

    @staticmethod
    def autosave_image_path(uuid_val, front_path, back_path):
        """自動儲存圖片路徑"""
        try:
            if not uuid_val:
                return {'result': 1, 'message': 'uuid 不能為空'}

            del_sql = f"DELETE FROM {TABLE_NAME} WHERE UUID = %s"
            MysqlAccess.execute(del_sql, [uuid_val])

            insert_sql = f"INSERT INTO {TABLE_NAME} (UUID, FRONT_PATH, BACK_PATH) VALUES (%s, %s, %s)"
            MysqlAccess.execute(insert_sql, [uuid_val, front_path, back_path])

            return {'result': 0, 'message': ''}
        except Exception as e:
            print(f"[ERROR] autosave_image_path 失敗: {str(e)}")
            return {'result': 1, 'message': f'保存圖片路徑失敗: {str(e)}'}

    @staticmethod
    def get_image_path(uuid_val):
        """獲取圖片路徑"""
        try:
            if not uuid_val:
                return {'result': 1, 'message': 'uuid 不能為空', 'data': {}}

            select_sql = f"SELECT UUID, FRONT_PATH, BACK_PATH FROM {TABLE_NAME} WHERE UUID = %s"
            raw = MysqlAccess.query(select_sql, [uuid_val])

            if not raw or len(raw) == 0:
                return {'result': 1, 'message': f'UUID {uuid_val} 不存在', 'data': {}}

            row = raw[0]
            return {
                'result': 0,
                'message': '',
                'data': {
                    'uuid': str(row.get('UUID') or row.get('uuid') or ''),
                    'front_path': str(row.get('FRONT_PATH') or row.get('front_path') or ''),
                    'back_path': str(row.get('BACK_PATH') or row.get('back_path') or '')
                }
            }
        except Exception as e:
            print(f"[ERROR] get_image_path 失敗: {str(e)}")
            return {'result': 1, 'message': f'獲取圖片路徑失敗: {str(e)}', 'data': {}}