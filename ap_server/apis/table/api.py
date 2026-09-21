# -*- coding: UTF-8 -*-
from flask import request
from apis.table.model import *
from apis.table.module import *
from base_api import CustomResource

############# 1. 獲取檢測表格：get_detect_table (GET 方法 + Query 參數) ##############
@api.route("/get_detect_table")  # 若想改為 /detect_table/get 可直接在此替換
class GetDetectTable(CustomResource):
    @api.doc(params={'uuid': '文件 UUID'})
    @api.marshal_with(get_detect_table_output)
    def get(self):
        """獲取檢測表格 API (GET)"""
        uuid = request.args.get('uuid')
        return DetectTable.get_detect_table(uuid=uuid)

############### 2. 自動保存檢測表格：autosave_detect_table (POST 方法) ################
@api.route("/autosave_detect_table")  # 若想改為 /detect_table/autosave 可直接在此替換
class AutosaveDetectTable(CustomResource):
    @api.expect(autosave_detect_table_input)
    @api.marshal_with(autosave_detect_table_output)
    def post(self):
        """自動保存檢測表格 API (POST)"""
        data = api.payload or {}
        return DetectTable.autosave_detect_table(
            uuid=data.get('uuid'),
            table_data=data.get('data')
        )