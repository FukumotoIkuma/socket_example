from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time
import random
from flask_cors import CORS
from gevent import monkey

# 非同期処理の最適化を行う
monkey.patch_all()

app = Flask(__name__)
CORS(app)  # CORSを許可
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="gevent")

# フラグでタスクの重複実行を防ぐ
is_task_running = False

@app.route("/")
def index():
    return render_template("index.html")

# カードデータをシミュレーションで取得する
def read_card_data():
    global is_task_running
    if is_task_running:
        return
    is_task_running = True
    
    while True:
        data = random.randint(0, 5)  # 実際にはICカードリーダーからデータを取得する
        data_msg = f"Card Data: {data}"
        socketio.emit('card_data', {'data': data_msg})  # クライアントにデータを送信
        print(f"Sent data: {data_msg}")
        time.sleep(3)  # データ送信間隔を調整

# クライアント接続時にバックグラウンドタスクを開始
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.start_background_task(read_card_data)

if __name__ == "__main__":
    try:
        socketio.run(app, debug=True)
    except KeyboardInterrupt:
        print("Server interrupted.")
