from flask_restplus import Namespace, Resource, fields, model

api = Namespace("account", description=u"帳號及權限管理") #description是欄位的文字說明

base_input_payload = api.model(u'基礎輸入參數定義', {
    'result': fields.Integer(required=True, default=0),
    'message': fields.String(required=True, default=""),
})

################# 1. 帳號登入 #################
account_input_payload = api.model(u'帳號登入輸入', {
    'user': fields.String(required=True, example="itri@kuohwa.com"),
    'password': fields.String(required=True, example="7c4a8d09ca3762af61e59520943dc26494f8941b")
})

account_output_payload = base_input_payload

################# 2. 獲取帳號列表 #################
account_item = api.model(u'帳號項', {
    'user_id': fields.String(),
    'role': fields.List(fields.String()),
    'email': fields.String(),
    'update_time': fields.String()
})

get_account_list_output = api.clone(u'獲得帳號列表輸出', base_input_payload, {
    'data': fields.List(fields.Nested(account_item))
})

################# 3. 新增帳號 #################
add_account_input = api.model(u'新增帳號輸入', {
    'user_id': fields.String(required=True, description=u"用戶ID", example="chichi"),
    'role': fields.List(fields.String(), required=True, description=u"角色列表 (可包含一個或多個角色，只能是 Admin / Super User / General User。例如：['Admin'] 或 ['Admin', 'Super User'])", example=["Admin"]),
    'email': fields.String(required=True, description=u"信箱 (必須以 @gmail.com 結尾)", example="jolin20060131@gmail.com"),
    'password': fields.String(required=True, description=u"密碼", example="apple777")
})

add_account_output = base_input_payload

################# 4. 更新帳號 #################
update_account_data = api.model(u'更新帳號詳細資料', {
    'new_user_id': fields.String(required=False),
    'new_role': fields.List(fields.String(), required=False),
    'new_email': fields.String(required=False)
})

update_account_input = api.model(u'更新帳號輸入', {
    'old_user_id': fields.String(required=True, description=u"舊用戶ID"),
    'data': fields.Nested(update_account_data, required=True)
})

update_account_output = base_input_payload

################# 5. 刪除帳號 #################
delete_account_input = api.model(u'刪除帳號輸入', {
    'user_id': fields.String(required=True, description=u"用戶ID")
})

delete_account_output = base_input_payload

################# 6. 忘記密碼 #################
forget_password_input = api.model(u'忘記密碼輸入', {
    'user_id': fields.String(required=True, description=u"信箱帳號", example="itri@kuohwa.com")
})

forget_password_output = base_input_payload
