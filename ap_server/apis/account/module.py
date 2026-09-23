# -*- coding: UTF-8 -*-
import json
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.exceptions import BadRequest

# 1. 替換為 MySQL 工具
from utils.mysql_utils import MysqlAccess
from configs import SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD

class Account(object):

    ############# 0. 登入 API ##############
    @staticmethod
    def login(user, password):
        """帳號登入"""
        try:
            sql = "SELECT USER_ID, ROLE, EMAIL FROM TBL_USER_ACCOUNT WHERE USER_ID = %s AND PASSWORD = %s"
            raw = MysqlAccess.query(sql, [user, password])

            if raw and len(raw) > 0:
                row = raw[0]
                role_val = row.get('role')
                try:
                    role_list = json.loads(role_val) if isinstance(role_val, str) else role_val
                    if not isinstance(role_list, list):
                        role_list = [str(role_val)]
                except Exception:
                    role_list = [str(role_val)]

                return {
                    "result": 0,
                    "message": "",
                    "user_id": str(row.get('USER_ID', '')),
                    "role": role_list,
                    "email": str(row.get('EMAIL', ''))
                }
            else:
                return {
                    "result": 1,
                    "message": "帳號或密碼錯誤",
                    "user_id": "",
                    "role": [],
                    "email": ""
                }
        except Exception as e:
            return {
                "result": 1,
                "message": f"登入失敗: {str(e)}",
                "user_id": "",
                "role": [],
                "email": ""
            }

    ############# 1. 獲取帳號列表 ##############
    @staticmethod
    def get_account_list(page=1, limit=10):
        """獲取帳號列表"""
        try:
            offset = (page - 1) * limit
            sql = """
                SELECT USER_ID, ROLE, EMAIL, UPDATE_TIME
                FROM TBL_USER_ACCOUNT
                LIMIT %s OFFSET %s
            """
            raw = MysqlAccess.query(sql, [limit, offset])

            data = []
            if raw:
                for row in raw:
                    role_val = row.get('role')
                    if role_val:
                        try:
                            role_list = json.loads(role_val) if isinstance(role_val, str) else role_val
                            if not isinstance(role_list, list):
                                role_list = [str(role_val)]
                        except Exception:
                            role_list = [str(role_val)]
                    else:
                        role_list = []

                    data.append({
                        'user_id': str(row.get('USER_ID') or ''),
                        'role': role_list,
                        'email': str(row.get('EMAIL') or ''),
                        'update_time': str(row.get('UPDATE_TIME') or '')
                    })

            return {
                'result': 0,
                'message': '',
                'data': data
            }
        except Exception as e:
            return {
                'result': 1,
                'message': f'獲取列表失敗: {str(e)}',
                'data': []
            }

#======================================================================
#==========                    2.新增帳號                     ==========
#======================================================================

    @staticmethod
    def add_account(user_id, role, email, password):
        """新增帳號"""
        try:
            # 驗證 role
            valid_roles = ["Admin", "Super User", "General User"]
            if isinstance(role, list):
                for r in role:
                    if r not in valid_roles:
                        raise BadRequest(f'角色 {r} 無效，只能是 {", ".join(valid_roles)}')
            else:
                if role not in valid_roles:
                    raise BadRequest(f'角色 {role} 無效，只能是 {", ".join(valid_roles)}')

            # 驗證 email
            if not email or not email.endswith('@gmail.com'):
                raise BadRequest('信箱必須以 @gmail.com 結尾 (例如: 111@gmail.com)')

            # 驗證 password
            if not password:
                raise BadRequest('密碼不能為空')

            role_str = json.dumps(role) if isinstance(role, list) else json.dumps([role])

            sql = """
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

    ############# 3. 刪除帳號 ##############
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

    ############# 4. 更新帳號 ##############
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

    ############# 5. 忘記密碼 ##############
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
            MysqlAccess.execute(update_sql, [temp_password, email])

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