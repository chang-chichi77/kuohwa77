#從 base_api 模組匯入已初始化好的 Flask 應用程式物件（app）
from base_api import app 

#設定根目錄"/"的路由處理邏輯
#當使用者以GET方法存取網站首頁（例如 http://localhost:5000/）時觸發
@app.route('/') 
def home(): #定義根目錄路由對應的處理函式
    return "OK" #回傳"OK"狀態文字，代表伺服器正常運作。

#判斷是否直接執行此程式檔
if __name__ == '__main__':
    #啟動 Flask 開發伺服器，僅限本機（127.0.0.1）存取，監聽 Port 5000。
    app.run(host="127.0.0.1", port=5000)
