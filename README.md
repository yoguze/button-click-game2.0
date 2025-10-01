🔹 今回学んだことを具体的に解説
1. Flask-SocketIO の基本
リアルタイム通信の仕組みを体験できた
今回のゲームでは、サーバー側でプレイヤーを ルームに入れる (join_room) 処理や、イベント送信 (emit) を使ってスコアやタイマー情報を全クライアントに伝えた
   具体例：
    @socketio.on('click')
   
    def handle_click(data):
   
      room = data['room']
   
      game = games[room]
   
      game['scores'][data['role']] += 1
   
      emit('update', {'scores': game['scores']}, to=room)
   
学び: 「クライアントが行った操作を即座にサーバーで処理し、同じルームの全員に情報を送る」という基本パターンを理解できた

3. Eventlet と monkey_patch の重要性
Flask-SocketIO を リアルタイムかつ非同期で安定動作させるためには Eventlet が必要
さらに、eventlet.monkey_patch() を最初に呼ぶことが重要
Python 標準の time.sleep() や socket を Eventlet 用に置き換えることで、複数クライアントをブロックせず同時処理可能になる
    具体例：
    import eventlet
   
    eventlet.monkey_patch()
   
    from flask import Flask
   
    from flask_socketio import SocketIO
   
学び: 「非同期処理を扱うときは、ライブラリによって環境設定や順序が重要」だと体感できた

5. リアルタイム同期の工夫
クライアント側のスコア表示は サーバーからの更新イベントで同期
サーバーは定期的に socketio.sleep(0.25) で全員にスコア更新を送信
さらに JS 側で ボタンを押した瞬間にローカルでカウントアップ することで、見た目上の遅延をゼロに近づけた
    具体例：
    clickBtn.addEventListener("click", () => {
   
        localClickCount++;
   
        clickCountEl.textContent = localClickCount;
   
        socket.emit("click", {role: myRole, room: roomId});
    });
学び: 「サーバーとクライアント間の同期を工夫することで、リアルタイム感を体感的に改善できる」と理解できた

7. カウントダウン機能の実装
マッチング後に 12秒カウントダウン を表示してからゲームを開始
サーバー側でタイマーを管理し、クライアントに毎秒更新イベントを送信
クライアント側では受信した数字を表示
    具体例：
    for i in range(12, 0, -1):
   
        socketio.emit('countdown', {'time_left': i}, to=room)
   
        socketio.sleep(1)
学び: 「サーバー側で状態を管理し、イベントでクライアントに通知することで、正確な同期カウントダウンが実現できる」と体験できた

