# -*- coding: UTF-8 -*-
from utils.mysql_utils import MysqlAccess

class DetectTable(object):

    ############## 1. 獲取檢測表格 ##############
    @staticmethod
    def get_detect_table(uuid=None):
        """依據 UUID 讀取資料並組成規格書指定的 JSON 回傳"""
        try:
            if not uuid:
                return {'result': 1, 'message': 'uuid 不能為空', 'data': {}}

            sql = """
                SELECT UPPER_LEFT, UPPER_RIGHT, LOWER_RIGHT, LOWER_LEFT,
                       NAME, CELLS_UPPER_LEFT, CELLS_UPPER_RIGHT, CELLS_LOWER_RIGHT, CELLS_LOWER_LEFT,
                       START_ROW, END_ROW, START_COL, END_COL, CONTENT
                FROM USER_DETECT_TABLE
                WHERE UUID = %s
            """
            raw = MysqlAccess.query(sql, [uuid])

            if raw and len(raw) > 0:
                # 取第一筆當作 Table 層級的座標 (MysqlAccess 回傳字典 dict)
                first_row = raw[0]
                tbl_ul = first_row.get('UPPER_LEFT') or first_row.get('upper_left') or ""
                tbl_ur = first_row.get('UPPER_RIGHT') or first_row.get('upper_right') or ""
                tbl_lr = first_row.get('LOWER_RIGHT') or first_row.get('lower_right') or ""
                tbl_ll = first_row.get('LOWER_LEFT') or first_row.get('lower_left') or ""

                # 遍歷所有記錄組合完整的 cells 陣列
                cells_list = []
                for row in raw:
                    cells_list.append({
                        "name": row.get('NAME') or row.get('name') or "",
                        "upper_left": row.get('CELLS_UPPER_LEFT') or row.get('cells_upper_left') or "",
                        "upper_right": row.get('CELLS_UPPER_RIGHT') or row.get('cells_upper_right') or "",
                        "lower_right": row.get('CELLS_LOWER_RIGHT') or row.get('cells_lower_right') or "",
                        "lower_left": row.get('CELLS_LOWER_LEFT') or row.get('cells_lower_left') or "",
                        "start_row": int(row.get('START_ROW') or row.get('start_row') or 0),
                        "end_row": int(row.get('END_ROW') or row.get('end_row') or 0),
                        "start_col": int(row.get('START_COL') or row.get('start_col') or 0),
                        "end_col": int(row.get('END_COL') or row.get('end_col') or 0),
                        "content": row.get('CONTENT') or row.get('content') or ""
                    })

                table_data = {
                    "page_number": {
                        "table_id": {
                            "upper_left": tbl_ul,
                            "upper_right": tbl_ur,
                            "lower_right": tbl_lr,
                            "lower_left": tbl_ll,
                            "cells": cells_list
                        }
                    }
                }
                return {'result': 0, 'message': '', 'data': table_data}
            else:
                return {'result': 0, 'message': '查無資料', 'data': {}}

        except Exception as e:
            print(f"[ERROR] get_detect_table 失敗: {str(e)}")
            return {'result': 1, 'message': f'獲取檢測表格失敗: {str(e)}', 'data': {}}

    ############## 2. 自動保存檢測表格 ##############
    @staticmethod
    def autosave_detect_table(uuid, table_data):
        """解析 JSON 輸入並寫入資料庫"""
        try:
            if not uuid:
                return {'result': 1, 'message': 'uuid 不能為空'}

            # 1. 刪除舊 UUID 資料
            del_sql = "DELETE FROM USER_DETECT_TABLE WHERE UUID = %s"
            MysqlAccess.execute(del_sql, [uuid])

            insert_sql = """
                INSERT INTO USER_DETECT_TABLE (
                    UUID, UPPER_LEFT, UPPER_RIGHT, LOWER_RIGHT, LOWER_LEFT,
                    NAME, CELLS_UPPER_LEFT, CELLS_UPPER_RIGHT, CELLS_LOWER_RIGHT, CELLS_LOWER_LEFT,
                    START_ROW, END_ROW, START_COL, END_COL, CONTENT
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # 2. 走訪 JSON 階層將所有 cell 寫入 DB
            if isinstance(table_data, dict):
                for p_key, p_val in table_data.items():
                    if isinstance(p_val, dict):
                        for t_key, t_val in p_val.items():
                            tbl_ul = t_val.get('upper_left', '')
                            tbl_ur = t_val.get('upper_right', '')
                            tbl_lr = t_val.get('lower_right', '')
                            tbl_ll = t_val.get('lower_left', '')
                            cells = t_val.get('cells', [])

                            # 正確走訪 cells 陣列裡的所有單元格
                            for c in cells:
                                params = [
                                    uuid, tbl_ul, tbl_ur, tbl_lr, tbl_ll,
                                    c.get('name', ''),
                                    c.get('upper_left', ''),
                                    c.get('upper_right', ''),
                                    c.get('lower_right', ''),
                                    c.get('lower_left', ''),
                                    c.get('start_row', 0),
                                    c.get('end_row', 0),
                                    c.get('start_col', 0),
                                    c.get('end_col', 0),
                                    c.get('content', '')
                                ]
                                MysqlAccess.execute(insert_sql, params)

            return {'result': 0, 'message': ''}

        except Exception as e:
            print(f"[ERROR] autosave_detect_table 失敗: {str(e)}")
            return {'result': 1, 'message': f'保存檢測表格失敗: {str(e)}'}