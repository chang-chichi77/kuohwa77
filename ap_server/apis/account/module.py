# -*- coding: UTF-8 -*-
import hashlib
import json
import random
import re
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.exceptions import BadRequest, InternalServerError, Unauthorized

from utils.mysql_utils import MysqlAccess
from configs import SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD

class Account(object):

#======================================================================
#==========                1. 帳號登入（完成）                  ==========
#======================================================================

    # 靜態修飾器
    # 告訴 Python 這個 login 函式雖然在 Account 類別裡，但他獨立的工具函示，不需傳入 self 或 cls。
    # 如果沒加靜態修飾器， 就需要每個都寫實力化物件才可以用，加了的話就可以直接呼叫做使用。
    @staticmethod
    # 定義函式，名為login，讓它接受兩個輸入參數，當呼叫這個函式時，必須傳入使用者填寫的電子信箱及密碼。
    def login(email, password):
        # 函式的文件字串，用來說明這個函式的主要功能是"帳號登入"
        """帳號登入"""
        # 開啟異常處理區塊，用來捕捉執行過程中可能發生的錯誤（語法錯誤或資料庫連線失敗）。
        try:
            # 撰寫 SQL 查詢字串：從 TBL_USER_ACCOUNT 資料庫表中，尋找 EMAIL 與 PASSWORD 同時吻合的資料，並取出 USER_ID、ROLE、EMAIL 三個欄位。
            sql = "SELECT USER_ID, ROLE, EMAIL FROM TBL_USER_ACCOUNT WHERE EMAIL = %s AND PASSWORD = %s"
            # 呼叫 MYSQL 工具執行查詢，將前端傳來的 [email, password] 以參數化方式帶入 SQL 中的 ％s 位置
            raw = MysqlAccess.query(sql, [email, password])

            # 檢查假數查不到資料，代表帳號或密碼錯誤或空陣列
            if not raw:
                # 拋出 401 錯誤，提示使用者帳號或密碼錯誤
                raise Unauthorized("帳號或密碼錯誤")
            # 取得查詢結果的第一筆資料（dict字典結構）
            row = raw[0]
            # 解析角色資料：因為資料庫儲存的是 JSON 字串（如"["Admin"]"）
            # 使用 json.loads()將字串轉回 Python 的清單/陣列結構（List）
            role_list = json.loads(row["ROLE"])
            # 登入成功，把 UPDATE_TIME 更新成現在，列表顯示的就是上次登入時間
            MysqlAccess.execute("UPDATE TBL_USER_ACCOUNT SET UPDATE_TIME = NOW() WHERE USER_ID = %s", [row["USER_ID"]])
            # 驗證成功：回傳包含 result＝0 與使用者資訊的資料字典
            # row["USER_ID"] 是指幫我從 row 這個字典裡面，拿叫做"USER_ID"的值，拿"chichi"。
            return {
                "result": 0,
                "message": "",
                "user_id": row["USER_ID"],
                "role": role_list,
                "email": row["EMAIL"]
            }
        # 異常處理區塊
        except Unauthorized:
            # 若為剛才主動拋出的帳密錯誤，直接原封不動向上拋出，讓 Flask 回傳 HTTP 401 狀態碼。
            raise
        # 若為其他非預期的系統錯誤（資料庫連線中斷、json.loads失敗等...）
        except Exception as e:
            # 封裝為 500 內部伺服器錯誤向上拋出
            raise InternalServerError(f"登入失敗: {str(e)}")

#======================================================================
#==========                 2. 獲取帳號列表（完成）              ==========
#======================================================================

    # 靜態修飾器
    # 告訴 Python 這個 get_account_list 函式雖然在 Account 類別裡，但他獨立的工具函示，不需傳入 self 或 cls。
    # 如果沒加靜態修飾器， 就需要每個都寫實力化物件才可以用，加了的話就可以直接呼叫做使用。
    @staticmethod
    # 定義函式，名為get_account_list，定義它接收名為page的輸入參數，並將預設直設為1。
    def get_account_list(page=1):
        # 函式的文件字串，用來說明這個函式的主要功能是"獲取帳號列表"
        """獲取帳號列表（每頁固定 10 筆）"""
        # 開啟異常處理區塊，用來捕捉執行過程中可能發生的錯誤（語法錯誤或資料庫連線失敗）。
        try:
            # 規格規定每頁只顯示 10 筆
            page_size = 10
            # page 參數通常為字串型態
            # 使用正則表達式 re.fullmatch 嚴格驗證是否僅由純半形數字組成 (可帶負號)
            # 目的：阻擋國字、英文、符號、小數、空白或 Python int() 會誤放行的全形數字與 "1_0" 等格式。
            if not re.fullmatch(r"-?[0-9]+", str(page)):
                # 拋出 BadRequest (HTTP 400) 異常，並附上錯誤說明訊息。
                # 當前端傳入的 page 參數包含字母、符號、小數或空白時觸發。
                raise BadRequest('page 必須是整數')
            # 轉型為整數型態
            page = int(page)
            # 如果判定數字小於1
            if page < 1:
                # 拋出"page 必須大於等於 1"的文字敘述
                raise BadRequest("page 必須大於等於 1")
            # 第 1 頁從第 0 筆開始，第 2 頁從第 10 筆開始，以此類推。
            offset = (page - 1) * page_size
            # 頁碼大到超過 MySQL 能處理的範圍時，一定沒有資料，直接回空陣列，不要讓資料庫報錯
            if offset > 2 ** 63 - 1:
                return {'result': 0, 'message': '', 'data': []}
            # ORDER BY 讓每次查詢的順序固定，翻頁才不會重複或漏掉資料
            sql = """
                SELECT USER_ID, ROLE, EMAIL, UPDATE_TIME
                FROM TBL_USER_ACCOUNT
                ORDER BY USER_ID
                LIMIT %s OFFSET %s
            """
            # 執行 SQL 查詢：帶入 [page_size, offset] 陣列參數，防止 SQL Injection 注入攻擊。
            raw = MysqlAccess.query(sql, [page_size, offset])
            # 初始化空清單，用來存放格式化後的使用者資料字典。
            data = []
            # 使用 for 迴圈逐筆處理從資料庫查出的原始資料 (raw 為字典清單)
            for row in raw:
                # 將每筆使用者資料整理成符合 API 規格的模型格式，並新增至 data 清單中。
                data.append({
                    # 使用者帳號 ID 為字串型態
                    "user_id": row["USER_ID"],
                    # ROLE 存的是 JSON 字串，例如 '["Admin"]'，轉回 list。
                    "role": json.loads(row["ROLE"]),
                    # 電子郵件為字串型態
                    "email": row["EMAIL"],
                    # UPDATE_TIME 允許空值，沒有時間就回空字串。
                    "update_time": str(row["UPDATE_TIME"] or "")
                })
            # 成功查無異常：回傳 result = 0 代表成功，並附帶整理好的 data 帳號清單。
            return {"result": 0, "message": "", "data": data}
        # 異常處理區塊
        except BadRequest:
            # 若為頁碼格式錯誤等 BadRequest 異常，直接原封不動向上拋出，讓 Flask 回傳 HTTP 400 狀態碼。
            raise
        # 若都不是
        except Exception as e:
            # 若為其他非預期錯誤 (資料庫連線中斷、json.loads 解析失敗)，封裝為 500 拋出。
            raise InternalServerError(f"獲取列表失敗: {str(e)}")

#======================================================================
#==========                    3.新增帳號                     ==========
#======================================================================

    @staticmethod
    def add_account(user_id, role, email, password):
        """新增帳號"""
        try:
            # ===== 第一階段：驗證必填欄位 =====
            # 驗證 user_id
            if not user_id:
                raise BadRequest('user_id 為必填欄位')

            # 驗證 role
            if not role or (isinstance(role, list) and len(role) == 0) or (isinstance(role, list) and all(not r for r in role)):
                raise BadRequest('role 為必填欄位，只能是 Admin, Super user, General user')

            # 驗證 email
            if not email:
                raise BadRequest('email 為必填欄位')

            # 驗證 password
            if not password:
                raise BadRequest('密碼不能為空')

            # ===== 第二階段：驗證邏輯 (重複性等) =====
            check_sql = "SELECT USER_ID FROM TBL_USER_ACCOUNT WHERE USER_ID = %s"
            check_result = MysqlAccess.query(check_sql, [user_id])
            if check_result:
                raise BadRequest(f'user_id "{user_id}" 已存在，無法重複新增')

            # 登入是用 email 查帳號，email 重複會對到錯的人，所以 email 也不能重複
            check_email_sql = "SELECT USER_ID FROM TBL_USER_ACCOUNT WHERE EMAIL = %s"
            if MysqlAccess.query(check_email_sql, [email]):
                raise BadRequest(f'email "{email}" 已被使用，無法重複新增')

            # ===== 第三階段：驗證內容格式 =====
            # 驗證 role 內容
            valid_roles = ["Admin", "Super user", "General user"]
            if isinstance(role, list):
                for r in role:
                    if r and r not in valid_roles:
                        raise BadRequest(f'角色 "{r}" 無效，只能是 "Admin", "Super user", "General user"')
            else:
                if role not in valid_roles:
                    raise BadRequest(f'角色 "{role}" 無效，只能是 "Admin", "Super user", "General user"')

            # 驗證 email 格式
            if not email.endswith('@gmail.com'):
                if '@' in email:
                    domain = email.split('@')[1] if len(email.split('@')) > 1 else ''
                    raise BadRequest(f'email 格式錯誤，您輸入的是 @{domain}，只接受 @gmail.com')
                else:
                    raise BadRequest('email 缺少 @gmail.com,請輸入完整的 email (例如: chichi@gmail.com)')
            elif email == '@gmail.com' or not email.split('@')[0]:
                raise BadRequest('email 格式錯誤，@ 前面必須至少有一個字符 (例如: chichi@gmail.com)')

            # 驗證 password 格式：前端會先做 SHA1，所以必須是 40 個 16 進位字元，避免明碼被存進資料庫
            if not isinstance(password, str) or not re.fullmatch(r'[0-9a-fA-F]{40}', password):
                raise BadRequest('password 格式錯誤，必須是經過 SHA1 雜湊的 40 字元字串')

            # 角色转换为 JSON 字符串
            if isinstance(role, list):
                # 如果是列表，直接轉成 JSON 字符串
                role_str = json.dumps(role)
                print(role_str)
                # 輸出："["Admin", "Super user"]"
            else:
                # 如果不是列表，先包裝成列表，再轉成 JSON 字符串
                role_str = json.dumps([role])
                print(role_str)

            sql = """ #insert寫入資料
                INSERT INTO TBL_USER_ACCOUNT (USER_ID, ROLE, EMAIL, PASSWORD, UPDATE_TIME)
                VALUES (%s, %s, %s, %s, NOW())
            """
            MysqlAccess.execute(sql, [user_id, role_str, email, password])

            return {
                'result': 0,
                'message': ''
            }
        except BadRequest:
            raise
        except Exception as e:
            return {
                'result': 1,
                'message': f'新增帳號失敗: {str(e)}'
            }

#======================================================================
#==========                     4. 更新帳號                   ==========
#======================================================================

    @staticmethod
    def update_account(old_user_id, update_data):
        """更新帳號"""
        try:
            check_sql = "SELECT USER_ID FROM TBL_USER_ACCOUNT WHERE USER_ID = %s"
            check_result = MysqlAccess.query(check_sql, [old_user_id])

            if not check_result:
                return {
                    'result': 1,
                    'message': f'帳號 {old_user_id} 不存在'
                }

            update_fields = []
            values = []

            new_user_id = update_data.get('new_user_id')
            new_role = update_data.get('new_role')
            new_email = update_data.get('new_email')

            if new_user_id:
                update_fields.append("USER_ID = %s")
                values.append(new_user_id)

            if new_role is not None:
                role_str = json.dumps(new_role) if isinstance(new_role, list) else json.dumps([new_role])
                update_fields.append("ROLE = %s")
                values.append(role_str)

            if new_email:
                update_fields.append("EMAIL = %s")
                values.append(new_email)

            if not update_fields:
                return {
                    'result': 1,
                    'message': '沒有要更新的欄位'
                }

            values.append(old_user_id)
            sql = f"""
                UPDATE TBL_USER_ACCOUNT
                SET {', '.join(update_fields)}, UPDATE_TIME = NOW()
                WHERE USER_ID = %s
            """
            MysqlAccess.execute(sql, values)

            return {
                'result': 0,
                'message': ''
            }
        except Exception as e:
            return {
                'result': 1,
                'message': f'更新帳號失敗: {str(e)}'
            }

#======================================================================
#==========                     5. 刪除帳號                   ==========
#======================================================================

    @staticmethod
    def delete_account(user_id):
        """刪除帳號"""
        try:
            sql = "DELETE FROM TBL_USER_ACCOUNT WHERE USER_ID = %s"
            MysqlAccess.execute(sql, [user_id])

            return {
                'result': 0,
                'message': ''
            }
        except Exception as e:
            return {
                'result': 1,
                'message': f'刪除帳號失敗: {str(e)}'
            }


#======================================================================
#==========                     6. 忘記密碼                   ==========
#======================================================================

    @staticmethod
    def forget_password(user_id):
        """忘記密碼 (user_id 輸入為信箱)"""
        try:
            email = user_id
            check_sql = "SELECT USER_ID FROM TBL_USER_ACCOUNT WHERE EMAIL = %s"
            check_result = MysqlAccess.query(check_sql, [email])

            if not check_result:
                return {
                    'result': 1,
                    'message': f'找不到信箱 {email} 對應的帳號'
              }

            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

            update_sql = """
                UPDATE TBL_USER_ACCOUNT
                SET PASSWORD = %s, UPDATE_TIME = NOW()
                WHERE EMAIL = %s
            """
            # 資料庫存 SHA1 雜湊值（前端登入時送的也是雜湊值），信裡寄的才是明碼臨時密碼
            temp_password_hash = hashlib.sha1(temp_password.encode("utf-8")).hexdigest()
            MysqlAccess.execute(update_sql, [temp_password_hash, email])

            # 嘗試寄信
            try:
                smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                smtp.starttls()
                smtp.login(SENDER_EMAIL, SENDER_PASSWORD)

                message = MIMEMultipart()
                message['From'] = SENDER_EMAIL
                message['To'] = email
                message['Subject'] = '敏捷訂單系統 - 密碼重設'

                body = f"親愛的用戶：\n\n您的臨時密碼為：{temp_password}\n請儘速登入並修改密碼。"
                message.attach(MIMEText(body, 'plain', 'utf-8'))

                smtp.send_message(message)
                smtp.quit()

                return {
                    'result': 0,
                    'message': ''
                }
            except Exception:
                return {
                    'result': 0,
                    'message': f'已更新臨時密碼為: {temp_password} (郵件發送失敗)'
                }

        except Exception as e:
            return {
                'result': 1,
                'message': f'忘記密碼處理失敗: {str(e)}'
            }