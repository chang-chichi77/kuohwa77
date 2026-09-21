# -*- coding: UTF-8 -*-
from flask_restplus import Namespace, fields

api = Namespace("image", description=u"圖片路徑管理", path="")

# 基礎回應結構
base_output_payload = api.model('圖片基礎輸出', {
    'result': fields.Integer(required=True, example=0, description=u"0=成功, 1=失敗"),
    'message': fields.String(required=True, example="", description=u"訊息說明")
})

# 1. autosave_image_path (POST)
autosave_image_path_input = api.model('自動保存圖片路徑輸入', {
    'uuid': fields.String(required=True, example="uuid_123456", description=u"單據 UUID"),
    'front_path': fields.String(required=True, example="/path/to/front.jpg", description=u"正面圖片路徑"),
    'back_path': fields.String(required=True, example="/path/to/back.jpg", description=u"反面圖片路徑")
})

autosave_image_path_output = base_output_payload

# 2. get_image_path (GET)
get_image_path_parser = api.parser()
get_image_path_parser.add_argument('uuid', type=str, required=True, help=u'單據 UUID', location='args')

image_path_detail_model = api.model('圖片路徑詳情', {
    'uuid': fields.String(required=True, example="uuid_123456", description=u"單據 UUID"),
    'front_path': fields.String(required=True, example="/path/to/front.jpg", description=u"正面圖片路徑"),
    'back_path': fields.String(required=True, example="/path/to/back.jpg", description=u"反面圖片路徑")
})

get_image_path_output = api.clone('獲取圖片路徑輸出', base_output_payload, {
    'data': fields.Nested(image_path_detail_model, description=u"圖片路徑物件")
})