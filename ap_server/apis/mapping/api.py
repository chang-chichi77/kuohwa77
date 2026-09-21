# -*- coding: utf-8 -*-
from flask import request
from apis.mapping.model import *
from apis.mapping.module import Mapping as MappingModule
from base_api import CustomResource


############# 1. 獲取 Key-Value 映射 API #############
@api.route("/get_key_value_mapping")
class GetKeyValueMapping(CustomResource):
    @api.doc(params={
        'vendor': '廠商名稱',
        'file_type': '檔案類型'
    })
    @api.marshal_with(get_key_value_mapping_output)
    def get(self):
        """獲取 Key-Value 映射 API (GET)"""
        vendor = request.args.get('vendor', '')
        file_type = request.args.get('file_type', '')
        return MappingModule.get_key_value_mapping(vendor=vendor, file_type=file_type)


############# 2. 自動保存 Key-Value 映射 API #############
@api.route("/autosave_key_value_mapping")
class AutosaveKeyValueMapping(CustomResource):
    @api.expect(autosave_key_value_mapping_input)
    @api.marshal_with(autosave_key_value_mapping_output)
    def post(self):
        """自動保存 Key-Value 映射 API (POST)"""
        payload = api.payload or {}
        data_list = payload.get('data', [])
        return MappingModule.autosave_key_value_mapping(data_list=data_list)