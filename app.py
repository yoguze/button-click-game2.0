#http://localhost:5000/
import eventlet
eventlet.monkey_patch()  # 必ず最初

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import time
import os

# ----------------------
# Flask アプリ
# ----------------------
app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

# ----------------------
# マッチング管理
# ----------------------
waiting_players = []  # 待機中プレイヤーリスト
games = {}            # { room_id: { 'players': [sidA, sidB], 'scores': {'A':0,'B':0}, 'start_time':float } }

GAME_DURATION = 30    # 秒
COUNTDOWN = 12        # 秒

# ----------------------
# ルーティング
# ----------------------
@app.route("/")
def index():
    return render_template("index.html")

# ----------------------
# ユーティリティ関数
# ----------------------
def countdown_and_start(room_id):
    for i in range(COUNTDOWN, 0, -1):
        socketio.emit('countdown', {'count': i}, to=room_id)
        socketio.sleep(1)
    # ゲーム開始
    games[room_id]['start_time'] = time.time()
    socketio.emit('game_start', {'duration': GAME_DURATION}, to=room_id)
    # ゲーム進行
    socketio.start_background_task(target=game_timer, room_id=room_id)

def game_timer(room_id):
    while True:
        game = games.get(room_id)
        if not game:
            return
        elapsed = time.time() - game.get('start_time', 0)
        time_left = max(0, GAME_DURATION - int(elapsed))
        socketio.emit('update', {'scores': game['scores'], 'time_left': time_left}, to=room_id)
        if time_left <= 0:
            # 勝者判定
            scoreA = game['scores']['A']
            scoreB = game['scores']['B']
            if scoreA > scoreB:
                winner = 'A'
            elif scoreB > scoreA:
                winner = 'B'
            else:
                winner = '引き分け'
            # 各プレイヤーに role を追加して送信
            for idx, sid in enumerate(game['players']):
                role = 'A' if idx == 0 else 'B'
                socketio.emit('game_over', {'scores': game['scores'], 'winner': winner, 'role': role}, to=sid)
            del games[room_id]
            return
        socketio.sleep(0.25)

# ----------------------
# Socket.IO イベント
# ----------------------
@socketio.on('connect')
def on_connect():
    sid = request.sid
    print(f"Player connected: {sid}")
    waiting_players.append(sid)
    emit('waiting', {'message': '対戦相手を探しています…'})

    # 2人揃ったらマッチング
    if len(waiting_players) >= 2:
        p1, p2 = waiting_players[:2]
        waiting_players[:] = waiting_players[2:]
        room_id = f"room_{p1}_{p2}"
        join_room(room_id, sid=p1)
        join_room(room_id, sid=p2)
        games[room_id] = {'players': [p1, p2], 'scores': {'A':0, 'B':0}}

        # 役割通知
        socketio.emit('matched', {'role':'A'}, to=p1)
        socketio.emit('matched', {'role':'B'}, to=p2)

        # カウントダウン開始
        socketio.start_background_task(countdown_and_start, room_id)

@socketio.on('click')
def on_click():
    sid = request.sid
    # どのゲームか判定
    for room_id, game in games.items():
        if sid in game['players']:
            role = 'A' if sid == game['players'][0] else 'B'
            game['scores'][role] += 1
            break

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    print(f"Player disconnected: {sid}")
    # 待機中リストから削除
    if sid in waiting_players:
        waiting_players.remove(sid)
    # ゲーム中だった場合、相手に通知
    for room_id, game in list(games.items()):
        if sid in game['players']:
            other_sid = [p for p in game['players'] if p != sid][0]
            socketio.emit('opponent_left', {'message': '相手が切断しました'}, to=other_sid)
            del games[room_id]

# ----------------------
# サーバー起動
# ----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render が割り当てるポート
    socketio.run(app, host="0.0.0.0", port=port)
