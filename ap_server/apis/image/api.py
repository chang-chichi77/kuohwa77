# -*- coding: UTF-8 -*-
from flask import request
from apis.image.model import *
from apis.image.module import ImageModule
from base_api import CustomResource


@api.route('/autosave_image_path')
class AutosaveImagePath(CustomResource):
    @api.expect(autosave_image_path_input)
    @api.marshal_with(autosave_image_path_output)
    def post(self):
        """自動儲存圖片路徑 API (POST)"""
        payload = api.payload or {}
        uuid_val = payload.get('uuid', '')
        front_path = payload.get('front_path', '')
        back_path = payload.get('back_path', '')
        return ImageModule.autosave_image_path(
            uuid_val=uuid_val,
            front_path=front_path,
            back_path=back_path
        )


@api.route('/get_image_path')
class GetImagePath(CustomResource):
    @api.doc(params={'uuid': '單據 UUID'})
    @api.marshal_with(get_image_path_output)
    def get(self):
        """獲取圖片路徑 API (GET)"""
        uuid_val = request.args.get('uuid', '')
        return ImageModule.get_image_path(uuid_val=uuid_val)