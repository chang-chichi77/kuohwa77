# -*- coding: UTF-8 -*-
from flask_restplus import Namespace, fields

api = Namespace("table", description=u"表格檢測管理", path="")

# 1. 基礎回應結構
base_output_payload = api.model(u'基礎輸出參數定義', {
    'result': fields.Integer(required=True, example=0, description=u"0=成功, 1=失敗"),
    'message': fields.String(required=True, example="", description=u"訊息說明")
})

# 2. 定義 Cells 單元格結構
cell_model = api.model(u'Cell數據結構', {
    'name': fields.String(example="cell_id1", description=u"單元格名稱"),
    'upper_left': fields.String(example="99,82", description=u"左上座標"),
    'upper_right': fields.String(example="99,857", description=u"右上座標"),
    'lower_right': fields.String(example="2356,857", description=u"右下座標"),
    'lower_left': fields.String(example="2356,82", description=u"左下座標"),
    'start_row': fields.Integer(example=0, description=u"起始行"),
    'end_row': fields.Integer(example=2, description=u"結束行"),
    'start_col': fields.Integer(example=0, description=u"起始列"),
    'end_col': fields.Integer(example=3, description=u"結束列"),
    'content': fields.String(example="example", description=u"內容")
})

# 3. 定義 Table 表格結構
table_id_model = api.model(u'Table數據結構', {
    'upper_left': fields.String(example="99,82", description=u"表格左上座標"),
    'upper_right': fields.String(example="99,857", description=u"表格右上座標"),
    'lower_right': fields.String(example="2356,857", description=u"表格右下座標"),
    'lower_left': fields.String(example="2356,82", description=u"表格左下座標"),
    'cells': fields.List(fields.Nested(cell_model), description=u"單元格列表")
})

# 4. 定義 Page 頁碼結構
page_number_model = api.model(u'Page數據結構', {
    'table_id': fields.Nested(table_id_model)
})

# 5. 定義 Data 完整結構
detect_table_data_model = api.model(u'檢測表格數據', {
    'page_number': fields.Nested(page_number_model)
})

############# 1. 獲取檢測表格 (GET 輸出結構) ##############
get_detect_table_output = api.clone(u'獲取檢測表格輸出', base_output_payload, {
    'data': fields.Nested(detect_table_data_model, description=u"表格嵌套物件")
})

############### 2. 自動保存檢測表格 (POST 輸入與輸出) ################
autosave_detect_table_input = api.model(u'自動保存檢測表格輸入', {
    'uuid': fields.String(required=True, example="sa5e122hy215cb3degrt", description=u"文件 UUID"),
    'data': fields.Nested(detect_table_data_model, required=True, description=u"包含頁碼、表格與 cells 的 JSON 物件")
})

autosave_detect_table_output = base_output_payload