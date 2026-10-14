from apis.account.model import *
from apis.account.module import *
from flask import session, request
from base_api import CustomResource
from werkzeug.exceptions import HTTPException
import json

# 定義函數以及文件說明
def get_json_data(): 
    # 給他基本定義
    """通用 JSON 提取方法，兼容任何 Content-Type""" 
    # 初始化空字典，用來存放最終解析出來的 JSON 資料。
    data = {}
    # 優先嘗試 Flask-RESTx 的 api.payload
    # 當使用 Swagger UI 或標準 POST 請求時，框架會自動解析 Body 並儲存在 api.payload
    if api.payload: 
        data = api.payload
    # 若無 payload，退而嘗試 Flask 原生的 request.json
    # 適用於其他標準 HTTP 客戶端（如前端 fetch/axios 或 Python requests）
    elif request.json:
        data = request.json 
    # 若上述皆未提及到，最後嘗試強行手動解析原始請求內容（request.data）
    else: 
        # 開啟異常處理區塊
        try:
            # 如果 request.data 裡面有資料 (不是空的)，網路傳過來的原始位元組（Byte）。
            if request.data:
                # 將 Bytes 解碼轉換為 Unicode 字串（String）
                data = json.loads(request.data.decode('utf-8'))
            # 如果 request.data 是空的
            else:
                # 給予空字典保底
                data = {}
        except:
            # 若格式非合法 JSON 或解碼失敗，為避免程式崩潰，捕捉異常並歸零為空字典。
            data = {} 
    # 回傳最終解析出的 JSON 資料字典
    # 請求內容必須是 JSON 物件，如果是陣列、數字等其他型態（例如 [1,2]）就當作空的，後面會回 400，不會讓程式出錯
    return data if isinstance(data, dict) else {} 

#======================================================================
#==========                  1. 帳號登入（完成）                ==========
#======================================================================

# 設定 API 路由路徑，搭配 Namespace 前綴，完整路徑為 /account/login。
@api.route("/login")
# CustomResource 是本來就有的，Login是命名。
class Login(CustomResource):
    # Swagger 文件標注：宣告此 API 預期接收的 JSON Payload 結構（輸入規格）
    # except 是本來就有的
    @api.expect(account_input_payload)
    # Swagger 文件標注與回應過濾：定義並自動格式化回傳給前端的 JSON 結構（輸出規格）
    # marshal_with 是本來就有的
    @api.marshal_with(account_output_payload)
    # 代表 HTTP 的 POST 請求動作
    def post(self):
        # 文件字串，也算是這隻 API 的摘要說明。
        """帳號登入"""
        # 去前端發送過來的 Request 裡面，把我填寫的 JSON 資料解析並且抓出來。
        data = get_json_data()
        # 開啟異常處理區塊
        try:
            # 呼叫 Account 模組的靜態方法 login 進行帳密驗證
            # email:取出前端 JSON 資料中的 "user" 欄位值
            # password:取出前端 JSON 資料中的 "password" 欄位值
            result = Account.login(
                email=data.get("user"),
                password=data.get("password")
            )
        # 捕捉從模組拋出的 HTTP 異常
        except HTTPException as e:
            # 回傳格式化的失敗訊息 JSON 物件，以及對應的 HTTP 狀態碼 (例如 401 或 500)。
            return {"result": 1, "message": e.description}, e.code
        # 判斷驗證結果：當 result 狀態碼為 0 時代表帳號密碼驗證成功
        if result["result"] == 0:
            # 將從資料庫動態查詢到的角色清單 (List) 寫入伺服器的 Session 中
            # 用於後續其他 API 進行使用者權限與身份驗證，避免權限寫死。
            session["roles"] = result["role"]
        # 回傳登入成功的結果字典，Flask-RESTx 會自動將其轉為 JSON 並套用 account_output_payload 格式。
        return result

#======================================================================
#==========                 2. 獲取帳號列表（完成）              ==========
#======================================================================

# 設定 API 路由路徑，搭配 Namespace 前綴，完整路徑為 /account/list。
@api.route("/list")
# CustomResource 是本來就有的，GetAccountList是命名。
class GetAccountList(CustomResource):
    # Swagger 文件標註：在測試網頁上顯示參數說明與預設行為。
    @api.doc(params={'page': "頁碼 (預設 1,每頁固定 10 筆，必須是整數)"})
    # Swagger 文件標註與回應過濾：定義並自動將回傳字典轉為 get_account_list_output 格式。
    @api.marshal_with(get_account_list_output)
    # 代表 HTTP 的 GET 請求動作
    def get(self):
        # 文件字串，也算是這隻 API 的摘要說明。
        """獲取帳號列表"""
        # 不在這裡轉成整數，因為 type=int 轉失敗時會偷偷改用預設值 1，所以原始值交給 module 判斷。
        page = request.args.get("page", 1)
        # 開啟異常處理區塊
        try:
            # 呼叫 Account 模組的靜態方法，傳入 page 執行分頁查詢。
            return Account.get_account_list(page=page)
        # 捕捉模組層拋出的 HTTP 異常 (頁碼格式錯誤的 400，或資料庫異常的 500)
        except HTTPException as e:
            # 回傳格式化的失敗 JSON 物件，以及對應的 HTTP 狀態碼。
            return {"result": 1, "message": e.description}, e.code

#======================================================================
#==========                  3.新增帳號（完成）                 ==========
#======================================================================

# 設定 API 路由路徑，搭配 Namespace 前綴，完整路徑為 /account/add。
@api.route("/add")
# CustomResource 是本來就有的，AddAccountList是命名。
class AddAccountList(CustomResource):
    # Swagger 文件標注：宣告此 API 預期接收的 JSON Payload 結構（輸入規格）
    # expect 是本來就有的
    @api.expect(add_account_list_input)
    # Swagger 文件標注與回應過濾：定義並自動格式化回傳給前端的 JSON 結構（輸出規格）
    # marshal_with 是本來就有的
    @api.marshal_with(add_account_list_output)
    # 代表 HTTP 的 POST 請求動作
    def post(self):
        # 文件字串，也算是這隻 API 的摘要說明。
        # 去前端發送過來的 Request 裡面，把我填寫的 JSON 資料解析並且抓出來。
        """新增帳號"""
        # 開啟異常處理區塊，用來捕捉執行過程中可能發生的錯誤 (如 400 驗證失敗或 500 寄信/資料庫錯誤)        
        try:
        # 呼叫通用工具函式 get_json_data()，將前端發送過來的 HTTP Request Body 內容解析並提取為字典 (data)。    
            data = get_json_data()
            # 呼叫 Account 模組的靜態方法執行新增帳號作業 (注意：此處依據模組定義應為 Account.add_account)
            # 透過 .get('key') 從 data 字典中安全提取前端帶入的欄位，對接至後端 Module 的參數名稱。
            return Account.add_account_list(
                user_id=data.get('user_id'),
                role=data.get('role'),
                email=data.get('email')
            )
        # 捕捉模組層拋出的 HTTP 異常
        except HTTPException as e:
            # 當 user_id/email 重複、格式不符時：捕捉到 400 BadRequest
            # 當寄送信件失敗或 SQL 執行異常時：捕捉到 500 InternalServerError
            # e.code ➔ HTTP 狀態碼 (HTTP Status Code)
            # e.description 的內容是："user_id "chichi" 已存在，無法重複新增"
            # e 是 「Exception（異常/錯誤）」 這個單字的英文縮寫
            return {'result': 1, 'message': e.description}, e.code

#======================================================================
#==========                     4. 更新帳號                   ==========
#======================================================================

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

#======================================================================
#==========                     5. 刪除帳號                   ==========
#======================================================================

@api.route("/delete")
class DeleteAccount(CustomResource):
    @api.expect(delete_account_input)
    @api.marshal_with(delete_account_output)
    def post(self):
        """刪除帳號"""
        data = get_json_data()
        return Account.delete_account(user_id=data.get('user_id'))


#======================================================================
#==========                     6. 忘記密碼                   ==========
#======================================================================

@api.route("/forget")
class ForgetPassword(CustomResource):
    @api.expect(forget_password_input)
    @api.marshal_with(forget_password_output)
    def post(self):
        """忘記密碼"""
        data = get_json_data()
        return Account.forget_password(user_id=data.get('user_id'))