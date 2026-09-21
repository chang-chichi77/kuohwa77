from apis.account.model import *
from apis.account.module import *
from flask import session, request
from base_api import CustomResource
import json

ROLE_ADMIN = "Admin"

def get_json_data():
    """通用 JSON 提取方法，兼容任何 Content-Type"""
    data = {}
    if api.payload:
        data = api.payload
    elif request.json:
        data = request.json
    else:
        try:
            data = json.loads(request.data.decode('utf-8')) if request.data else {}
        except:
            data = {}
    return data

################# 1. 帳號登入 #################
@api.route("/login")
class Login(CustomResource):
    @api.expect(account_input_payload)
    @api.marshal_with(account_output_payload)
    def post(self):
        """帳號登入"""
        session["roles"] = [ROLE_ADMIN]
        data = get_json_data()
        return Account.login(
            user=data.get("user"),
            password=data.get("password")
        )

################# 2. 獲取帳號列表 #################
@api.route("/list")
class GetAccountList(CustomResource):
    @api.doc(params={
        'page': '頁碼 (預設 1)',
        'limit': '每頁筆數 (預設 10)'
    })
    @api.marshal_with(get_account_list_output)
    def get(self):
        """獲取帳號列表"""
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        return Account.get_account_list(page=page, limit=limit)

################# 3. 新增帳號 #################
@api.route("/add")
class AddAccount(CustomResource):
    @api.expect(add_account_input)
    @api.marshal_with(add_account_output)
    def post(self):
        """新增帳號"""
        data = get_json_data()
        return Account.add_account(
            user_id=data.get('user_id'),
            role=data.get('role', []),
            email=data.get('email')
        )

################# 4. 更新帳號 #################
@api.route("/update")
class UpdateAccount(CustomResource):
    @api.expect(update_account_input)
    @api.marshal_with(update_account_output)
    def post(self):
        """更新帳號"""
        data = get_json_data()
        old_user_id = data.get('old_user_id')
        update_data = data.get('data', {})

        return Account.update_account(
            old_user_id=old_user_id,
            update_data=update_data
        )

################# 5. 刪除帳號 #################
@api.route("/delete")
class DeleteAccount(CustomResource):
    @api.expect(delete_account_input)
    @api.marshal_with(delete_account_output)
    def post(self):
        """刪除帳號"""
        data = get_json_data()
        return Account.delete_account(user_id=data.get('user_id'))

################# 6. 忘記密碼 #################
@api.route("/forget")
class ForgetPassword(CustomResource):
    @api.expect(forget_password_input)
    @api.marshal_with(forget_password_output)
    def post(self):
        """忘記密碼"""
        data = get_json_data()
        return Account.forget_password(user_id=data.get('user_id'))