# -*- coding: UTF-8 -*-
import hashlib
import json
import random
import re
import secrets
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pymysql.err import IntegrityError
from werkzeug.exceptions import BadRequest, HTTPException, InternalServerError, Unauthorized

from utils.mysql_utils import MysqlAccess
from configs import SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD

# 用來定義基礎物件叫Account
class Account:

    # 共用工具：產生臨時密碼、寄信（新增帳號使用）
    # 靜態修飾器
    # 告訴 Python 這個 _generate_temp_password 與 _send_mail 函式雖然在 Account 類別裡，但他獨立的工具函式，不需傳入 self 或 cls。
    # 如果沒加靜態修飾器， 就需要每個都寫實力化物件才可以用，加了的話就可以直接呼叫做使用。
    @staticmethod
    # 靜態方法 + 單底線前綴 (_)：代表這是類別內部的私有工具函式
    def _generate_temp_password(length=8):
        # 函式的文件字串，用來說明這個函式的主要功能是"產生臨時密碼"。
        """產生臨時密碼（英文大小寫加數字），用 secrets 比 random 更不容易被猜中"""
        chars = string.ascii_letters + string.digits
        return "".join(secrets.choice(chars) for _ in range(length))

    # 靜態修飾器
    # 告訴 Python 這個 login 函式雖然在 Account 類別裡，但他獨立的工具函式，不需傳入 self 或 cls。
    # 如果沒加靜態修飾器， 就需要每個都寫實力化物件才可以用，加了的話就可以直接呼叫做使用。
    @staticmethod
    # 靜態方法 + 單底線前綴 (_)：代表這是類別內部的私有工具函式
    def _send_mail(to_email, subject, body):
        # 函式的文件字串，用來說明這個函式的主要功能是"寄送信件"。
        """寄送純文字信件，寄送失敗就丟出 500"""
        # 開啟異常處理區塊，用來捕捉執行過程中可能發生的錯誤（語法錯誤或資料庫連線失敗）。
        try:
            # timeout=10：郵件伺服器 10 秒沒回應就放棄，避免請求一直卡住
            # smtplib.SMTP Python 內建用來處理 SMTP 協定（簡單郵件傳輸協定） 的標準模組。
            # .SMTP：呼叫類別建立一個 SMTP 連線物件，用來處理與郵件伺服器之間的所有通訊與連線。
            smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
            # 啟動 TLS 加密傳輸通道
            # 作用：將連線升級為安全加密連線，防止帳號密碼與信件內容在網路上被竊聽或擷取。
            smtp.starttls()
            # 登入 SMTP 郵件伺服器
            # 傳入系統公用發信帳號 (SENDER_EMAIL) 與應用程式密碼 (SENDER_PASSWORD) 進行身份驗證
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            # 建立一個空的 MIME 多部分 (Multipart) 郵件容器物件，用來盛裝 From、To、Subject 及內文等資訊           
            message = MIMEMultipart()
            message["From"] = SENDER_EMAIL # 設定寄件者顯示名稱/信箱
            message["To"] = to_email # 設定收件者信箱
            message["Subject"] = subject # 設定信件標題/主旨
            # "plain" 代表這封信的內文是 「純文字（Text / Plain）」 格式，並指定 UTF-8 編碼 (防止中文內文變成亂碼)，附加到信件物件中。
            # attach 的英文意思是 「附加、貼上」
            message.attach(MIMEText(body, "plain", "utf-8"))
            # 發送信件並安全關閉 SMTP 連線
            # 透過已建立且登入成功的 SMTP 連線，將組裝完成的 message 郵件物件發送出去。
            smtp.send_message(message)
            # 寄信完成，向 SMTP 伺服器發送 QUIT 指令，安全地斷開與關閉網路連線，釋放系統資源。
            smtp.quit()
        # 捕捉寄信失敗異常 (如 SMTP 驗證失敗、連線逾時、無效的收件者地址等)
        # e 是 「Exception（異常/錯誤）」 這個單字的英文縮寫
        except Exception as e:
            # 拋出 500 內部伺服器錯誤，附帶 Exception 類別名稱，便於除錯與告知前端。
            raise InternalServerError(f"寄送密碼信件失敗，帳號未建立 ({type(e).__name__})")

#======================================================================
#==========                1. 帳號登入（完成）                  ==========
#======================================================================

    # 靜態修飾器
    # 告訴 Python 這個 login 函式雖然在 Account 類別裡，但他獨立的工具函式，不需傳入 self 或 cls。
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
    # 告訴 Python 這個 get_account_list 函式雖然在 Account 類別裡，但他獨立的工具函式，不需傳入 self 或 cls。
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
#==========                   3.新增帳號（完成）                ==========
#======================================================================

    # 靜態修飾器
    # 告訴 Python 這個 get_account_list 函式雖然在 Account 類別裡，但他獨立的工具函式，不需傳入 self 或 cls。
    # 如果沒加靜態修飾器， 就需要每個都寫實力化物件才可以用，加了的話就可以直接呼叫做使用。
    @staticmethod
    # 定義函式，名為add_account_list，讓它接受三個輸入參數，當呼叫這個函式時，必須傳入使用者填寫的 ID 、角色及電子信箱。
    def add_account_list(user_id, role, email):
        # 函式的文件字串，用來說明這個函式的主要功能是"新增帳號"
        """新增帳號（初始密碼由系統產生，寄到新帳號的信箱）"""
        # 開啟異常處理區塊，用來捕捉執行過程中可能發生的錯誤（語法錯誤或資料庫連線失敗）。
        try:
            # ===== 第一階段：驗證必填欄位與型別 =====
            # 欄位必須是文字／清單，不是的話後面的檢查會出錯，所以先擋掉。
            if not isinstance(user_id, str) or not user_id.strip():
                # 拋出 BadRequest (HTTP 400) 異常，並附上錯誤說明訊息。
                raise BadRequest('user_id 為必填欄位，且必須是文字')
            # strip() 去掉前後空白，" bob " 會被當成 "bob"
            user_id = user_id.strip()
            # 判斷 role 是否非清單 (list) 型態，或者清單長度為 0 (沒有任何元素)。
            if not isinstance(role, list) or len(role) == 0:
                # 拋出 BadRequest (HTTP 400) 異常，並附上錯誤說明訊息。
                raise BadRequest('role 為必填欄位，必須是清單，例如 ["Admin", "Super user"]')
            # 欄位必須是文字／清單，不是的話後面的檢查會出錯，所以先擋掉。
            if not isinstance(email, str) or not email.strip():
                # 拋出 BadRequest (HTTP 400) 異常，並附上錯誤說明訊息。
                raise BadRequest('email 為必填欄位，且必須是文字')
            # strip() 去掉前後空白，" jolin20060131@gmail.com " 會被當成 "jolin20060131@gmail.com"
            email = email.strip()

            # ===== 第二階段：驗證邏輯 (重複性) =====
            # 驗證 user_id 是否重複
            # 撰寫 SQL 語法，查詢資料庫中是否已有相同的 USER_ID。
            check_sql = "SELECT USER_ID FROM TBL_USER_ACCOUNT WHERE USER_ID = %s"
            # 執行查詢，若 MysqlAccess.query 回傳有資料。
            if MysqlAccess.query(check_sql, [user_id]):
                # 拋出 BadRequest (HTTP 400) 異常，並附上錯誤說明訊息。
                raise BadRequest(f'user_id "{user_id}" 已存在，無法重複新增')

            # 驗證 email 是否重複
            # 由於系統登入時會透過 EMAIL 比對帳號，若 EMAIL 重複會導致登入時查錯人，因此 EMAIL 也必須保持唯一性。
            check_email_sql = "SELECT USER_ID FROM TBL_USER_ACCOUNT WHERE EMAIL = %s"
            # 執行查詢，若回傳有資料 (代表信箱已被註冊)。
            if MysqlAccess.query(check_email_sql, [email]):
                # 拋出 BadRequest (HTTP 400) 異常，並附上錯誤說明訊息。
                raise BadRequest(f'email "{email}" 已被使用，無法重複新增')

            # ===== 第三階段：驗證內容格式 =====
            # 字串長度邊界檢查：防止傳入過長字串導致 MySQL 資料庫欄位溢位報錯。
            # USER_ID 資料庫欄位上限為 VARCHAR(50)
            if len(user_id) > 50:
                # 拋出 BadRequest (HTTP 400) 異常，並附上錯誤說明訊息。
                raise BadRequest('user_id 長度不能超過 50 個字元')
            # EMAIL 資料庫欄位上限為 VARCHAR(100)
            if len(email) > 100:
                # 拋出 BadRequest (HTTP 400) 異常，並附上錯誤說明訊息。
                raise BadRequest('email 長度不能超過 100 個字元')

            # 角色權限清單 (role) 格式與內容驗證
            # 定義系統中合法存在的 3 種白名單角色名稱
            valid_roles = ["Admin", "Super user", "General user"]
            # 使用 for 迴圈檢查前端傳入清單中的每一個角色，是否皆存在於白名單中。
            for r in role:
                # 如果不在名單當中
                if r not in valid_roles:
                    # 拋出 BadRequest (HTTP 400) 異常，並附上錯誤說明訊息。
                    raise BadRequest(f'角色 "{r}" 無效，只能是 "Admin", "Super user", "General user"')
            # 利用 set() 轉為集合去重的特性，若去重後的元素數量不等於原陣列長度，代表陣列內有重複的角色 (例如 ["Admin", "Admin"])。
            if len(set(role)) != len(role):
                # 拋出 BadRequest (HTTP 400) 異常，並附上錯誤說明訊息。
                raise BadRequest('role 不能有重複的角色')

            # email 格式正規表示式嚴格驗證
            # 規則說明：[^@\s]+ (非 @ 且非空白字元) + @ + [^@\s]+ + \. (點號) + [^@\s]+
            # 確保信箱只有一個 @、@ 前後都不能是空的、網域中要有 "."，且整體不能有空白
            if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
                # 拋出 BadRequest (HTTP 400) 異常，並附上錯誤說明訊息。
                raise BadRequest('email 格式錯誤，例如 itri@kuohwa.com')

            # ===== 第四階段：產生臨時密碼、寄信、寫入資料庫 =====
            # 呼叫私有類別方法，隨機產生一組符合安全標準的臨時明碼密碼 (例如 "aB3#x9K2")
            temp_password = Account._generate_temp_password()
            # 發送 Email 通知 (採用「先寄信再寫庫」的防範機制)
            # 理由：若先寫入資料庫，萬一發信伺服器 (SMTP) 斷線或信箱不存在，資料庫會殘留一個無法登入且沒人知道密碼的無效帳號。
            # 先寄信可確保寄信成功後才繼續執行資料庫寫入，寄信失敗則直接在中途拋出 Exception 觸發 Rollback。
            Account._send_mail(
                email,
                '敏捷訂單系統 - 帳號建立通知',
                f"親愛的用戶：\n\n您的帳號「{user_id}」已建立。\n您的臨時密碼為：{temp_password}\n請儘速登入並修改密碼。"
            )

            # 密碼資安安全處理 (SHA-1 雜湊加密)
            # 資料庫絕不能儲存明文密碼！將明碼轉為 UTF-8 編碼位元組後，計算 SHA-1 雜湊值 (Hash) 並轉為 16 進位字串
            # 前端登入時送出的密碼也會先經由 SHA-1 加密，因此資料庫只需比對兩邊的雜湊值即可
            # hexdigest()是把剛剛計算好的雜湊結果轉乘16位進制的小寫文字字串
            password_hash = hashlib.sha1(temp_password.encode("utf-8")).hexdigest()
            # 角色轉成 JSON 字串存進資料庫，例如 '["Admin", "Super user"]'
            role_str = json.dumps(role)
            # 撰寫 SQL 新增語法：將帳號、角色 JSON 字串、信箱、密碼雜湊值以及當下時間 (NOW()) 寫入資料庫。
            sql = """
                INSERT INTO TBL_USER_ACCOUNT (USER_ID, ROLE, EMAIL, PASSWORD, UPDATE_TIME)
                VALUES (%s, %s, %s, %s, NOW())
            """
            # 執行寫入指令：呼叫 MysqlAccess.execute (注意非 query)，並以參數化傳送防範。
            # 拿資料或查詢、讀取用"query"，改資料或寫入、異動、變更用"execute"。
            MysqlAccess.execute(sql, [user_id, role_str, email, password_hash])
            # 新增成功：回傳 result = 0 代表作業成功執行完畢
            return {'result': 0, 'message': ''}
        # 上面主動丟的 400、寄信失敗的 500。
        except HTTPException:
            # 原封不動往外丟，由 api.py 轉成對應的狀態碼
            raise
        # 併發衝突防護：
        # 若兩個請求同時發送新增同一個 user_id 或 email，前面的 SELECT 查重可能同時通過。
        # 但 MySQL 資料庫內建的 PRIMARY KEY 或 UNIQUE 索引會擋下第二個請求並拋出 IntegrityError。
        # 這裡將其捕捉並封裝為友善的 400 BadRequest 回傳給前端
        except IntegrityError:
            # 兩個請求同時新增相同的 user_id 或 email，查重都通過，資料庫的唯一鍵會擋下第二個
            # 拋出 BadRequest (HTTP 400) 異常，並附上錯誤說明訊息。
            raise BadRequest('user_id 或 email 已存在，無法重複新增')
        # 捕捉其他非預期的資料庫或系統異常
        except Exception as e:
            # 封裝為 500 InternalServerError 拋出
            raise InternalServerError(f'新增帳號失敗: {str(e)}')

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