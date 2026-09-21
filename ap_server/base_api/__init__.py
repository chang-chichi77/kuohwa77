# -*- coding: UTF-8 -*-
from flask import Blueprint, Flask, request, session
from base_api.custom_cls import CustomMethodView, CustomRequestParser, CustomResource
from utils.mysql_utils import MysqlAccess

from .custom_cls import Api
from apis.account.api import api as account_ns
from apis.table.api import api as table_ns
from apis.mapping.api import api as mapping_ns
from apis.image.api import api as image_ns

api_blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_blueprint, version="0.0.1", description='', title='Kuohwa API Service', doc="/doc", ordered=True)

# 初始化 MySQL 資料庫
MysqlAccess.initialise()

# init app
app = Flask(__name__, template_folder="../templates", static_folder="../static", static_url_path="")
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
app.config.SWAGGER_UI_REQUEST_DURATION = True
app.secret_key = "test123456789"
app.config['JSON_AS_ASCII'] = False

# register blueprint
app.register_blueprint(api_blueprint)

# register swagger api
api.add_namespace(account_ns)
api.add_namespace(table_ns)
api.add_namespace(mapping_ns)
api.add_namespace(image_ns, path='')