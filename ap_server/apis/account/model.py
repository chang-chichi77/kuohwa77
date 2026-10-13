from flask_restplus import Namespace, Resource, fields, model

# 建立一個名為 account 的 API 命名空間（Namespace）
# 第一個參數"account":是用來定義網址路徑的前綴（路由會包含 /account）
# description:在 Swagger API 文件頁面上顯示的模組中文說明
# u代表這個字串包含中文或其他非英文字元，請用Unicode解碼，不要出現亂碼，因為一班字串只支援英文及數字（ASCII）。
api = Namespace("account", description=u"帳號及權限管理")

#  api.model 定義通用的 JSON 回應格式類型（Data MOdel）
# 用於 Swagger 文件渲染與回應格式驗證
# u代表這個字串包含中文或其他非英文字元，請用Unicode解碼，不要出現亂碼，因為一班字串只支援英文及數字（ASCII）。
base_input_payload = api.model(u"基礎輸入參數定義", {
    # fields 代表型態，驗證格式，輸出轉換，依照指定型態轉成標準的 JSON 格式丟給前端。
    # "result":fields.Integer 為整數型態，required為True代表為必填欄位，預設值給0（通常代表成功狀態碼）。
    "result": fields.Integer(required=True, default=0),
    # "message":fields.String 為字串型態，required為True代表為必填欄位，預設值為空字串（用於回傳處理結果訊息）。
    "message": fields.String(required=True, default=""),
})

#======================================================================
#==========                   1. 帳號登入（完成）               ==========
#======================================================================

# 使用 api.model 定義一個名為"帳號登入輸入"的 JSON 格式規格。
# u代表這個字串包含中文或其他非英文字元，請用Unicode解碼，不要出現亂碼，因為一班字串只支援英文及數字（ASCII）。
account_input_payload = api.model(u"帳號登入輸入", {
    # fields.String為字串型態，必填欄位，也寫了一個範例。
    "user": fields.String(required=True, description=u"登入信箱", example="itri@kuohwa.com"),
    # fields.String為字串型態，必填欄位，也寫了一個範例。
    "password": fields.String(required=True, example="7c4a8d09ca3762af61e59520943dc26494f8941b")
})
# 登入後，後端回傳給前端的資料
account_output_payload = base_input_payload

#======================================================================
#==========                 2. 獲取帳號列表                    ==========
#======================================================================

account_item = api.model("帳號項", {
    'user_id': fields.String(),
    'role': fields.List(fields.String()),
    'email': fields.String(),
    'update_time': fields.String()
})

get_account_list_output = api.clone(u'獲得帳號列表輸出', base_input_payload, {
    'data': fields.List(fields.Nested(account_item))
})

#======================================================================
#==========                    3.新增帳號                     ==========
#======================================================================

add_account_input = api.model("新增帳號輸入", {
    'user_id': fields.String(required=True, description=u"用戶ID", example="chichi"),
    'role': fields.List(fields.String(), required=True, description=u"角色列表 (可包含一個或多個角色，只能是 Admin / Super User / General User。例如:['Admin'] 或 ['Admin', 'Super User'])", example=["Admin"]),
    'email': fields.String(required=True, description=u"信箱 (必須以 @gmail.com 結尾)", example="jolin20060131@gmail.com"),
    'password': fields.String(required=True, description=u"密碼 (前端先經過 SHA1 hash 的 40 字元字串)", example="d2bed8c8516662bf2f4bc934bc2ffa5aa1ffeab5")
})

add_account_output = base_input_payload

#======================================================================
#==========                     4. 更新帳號                   ==========
#======================================================================

update_account_data = api.model("更新帳號詳細資料", {
    'new_user_id': fields.String(required=False),
    'new_role': fields.List(fields.String(), required=False),
    'new_email': fields.String(required=False)
})

update_account_input = api.model("更新帳號輸入", {
    'old_user_id': fields.String(required=True, description=u"舊用戶ID"),
    'data': fields.Nested(update_account_data, required=True)
})

update_account_output = base_input_payload


#======================================================================
#==========                     5. 刪除帳號                   ==========
#======================================================================

delete_account_input = api.model("刪除帳號輸入", {
    'user_id': fields.String(required=True, description=u"用戶ID")
})

delete_account_output = base_input_payload


#======================================================================
#==========                     6. 忘記密碼                   ==========
#======================================================================

forget_password_input = api.model("忘記密碼輸入", {
    'user_id': fields.String(required=True, description=u"信箱帳號", example="itri@kuohwa.com")
})

forget_password_output = base_input_payload
