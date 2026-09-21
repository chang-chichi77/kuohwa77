# -*- coding: UTF-8 -*-
from flask_restplus import Namespace, fields

api = Namespace("mapping", description=u"Key-Value 映射管理", path="")

# 基礎回應結構
base_output_payload = api.model('映射基礎輸出', {
    'result': fields.Integer(required=True, example=0, description=u"0=成功, 1=失敗"),
    'message': fields.String(required=True, example="", description=u"訊息說明")
})

# 1. GET 輸出結構 (文件第 21 頁)
get_key_value_mapping_output = api.clone('獲取映射輸出', base_output_payload, {
    'data': fields.Raw(description=u"Key-Value 對照字典物件", example={
        "epr_key1": ["Bo", "Borad", "Boardnum"],
        "epr_key2": ["sta", "status", "status1"]
    })
})

# 2. POST 輸入結構 (文件第 22 頁)
mapping_item_model = api.model('映射項目', {
    'vendor': fields.String(required=True, example="77", description=u"廠商名稱"),
    'file_type': fields.String(required=True, example="png", description=u"檔案類型"),
    'field': fields.String(required=True, example="epr_key1", description=u"ERP 欄位 Key"),
    'fieldvalue': fields.List(fields.String, required=True, example=["Bo", "Board", "Boardnum"], description=u"對應候選值列表")
})

autosave_key_value_mapping_input = api.model('自動保存映射輸入', {
    'data': fields.List(fields.Nested(mapping_item_model), required=True, description=u"映射資料列表", example=[
        {
            "vendor": "xx",
            "file_type": "png",
            "field": "epr_key1",
            "fieldvalue": ["Bo", "Board", "Boardnum"]
        },
        {
            "vendor": "xx",
            "file_type": "png",
            "field": "epr_key2",
            "fieldvalue": ["sta", "status", "status1"]
        }
    ])
})

# 3. POST 輸出結構
autosave_key_value_mapping_output = base_output_payload