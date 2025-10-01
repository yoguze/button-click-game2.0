// ----------------------
// 画面要素
// ----------------------
const titleScreen = document.getElementById("titleScreen");
const matchScreen = document.getElementById("matchScreen");
const gameScreen = document.getElementById("gameScreen");
const resultScreen = document.getElementById("resultScreen");

const highScoreEl = document.getElementById("highScore");
const startBtn = document.getElementById("startBtn");
const backToTitleBtn = document.getElementById("backToTitle");

const matchMessage = document.getElementById("matchMessage");
const countdownEl = document.getElementById("countdown");

const clickBtn = document.getElementById("clickButton");
const clickCountElA = document.getElementById("scoreA");
const clickCountElB = document.getElementById("scoreB");
const timeLeftEl = document.getElementById("timeLeft");
const messageEl = document.getElementById("message");

const resultMessage = document.getElementById("resultMessage");

// ----------------------
// ハイスコア
// ----------------------
let highScore = Number(localStorage.getItem("highScore") || 0);
highScoreEl.textContent = highScore;

// ----------------------
// Socket.IO
// ----------------------
let socket = null;

// ----------------------
// 画面切り替え関数
// ----------------------
function showTitle() {
  titleScreen.classList.remove("hidden");
  matchScreen.classList.add("hidden");
  gameScreen.classList.add("hidden");
  resultScreen.classList.add("hidden");
}
function showMatch() {
  titleScreen.classList.add("hidden");
  matchScreen.classList.remove("hidden");
  gameScreen.classList.add("hidden");
  resultScreen.classList.add("hidden");
}
function showGame() {
  titleScreen.classList.add("hidden");
  matchScreen.classList.add("hidden");
  gameScreen.classList.remove("hidden");
  resultScreen.classList.add("hidden");
  clickBtn.disabled = true;
  clickCountElA.textContent = "0";
  clickCountElB.textContent = "0";
  timeLeftEl.textContent = "30";
  messageEl.textContent = "";
}
function showResult() {
  titleScreen.classList.add("hidden");
  matchScreen.classList.add("hidden");
  gameScreen.classList.add("hidden");
  resultScreen.classList.remove("hidden");
}

// ----------------------
// ゲームスタート
// ----------------------
startBtn.addEventListener("click", () => {
  showMatch();

  socket = io();

  socket.on("connect", () => console.log("Socket connected:", socket.id));

  socket.on("waiting", (data) => {
    matchMessage.textContent = data.message;
    countdownEl.textContent = "12";
  });

  socket.on("matched", (data) => {
    matchMessage.textContent = `あなたは ${data.role} です`;
  });

  socket.on("countdown", (data) => {
    countdownEl.textContent = data.count;
  });

  socket.on("game_start", (data) => {
    showGame();
    clickBtn.disabled = false;
    timeLeftEl.textContent = data.duration;
  });

  socket.on("update", (data) => {
    if (data.scores) {
      clickCountElA.textContent = data.scores.A;
      clickCountElB.textContent = data.scores.B;
    }
    if (data.time_left !== undefined) {
      timeLeftEl.textContent = data.time_left;
    }
  });

  socket.on("game_over", (data) => {
    showResult();
    resultMessage.textContent = `スコア: A=${data.scores.A}, B=${data.scores.B}, 勝者: ${data.winner}`;

    const myRole = data.role || "A"; // 任意
    const myScore = data.scores[myRole];
    if (myScore > highScore) {
      highScore = myScore;
      localStorage.setItem("highScore", highScore);
      highScoreEl.textContent = highScore;
    }
  });

  socket.on("opponent_left", (data) => {
    messageEl.textContent = data.message;
    clickBtn.disabled = true;
  });
});

// ----------------------
// ボタンクリック
// ----------------------
clickBtn.addEventListener("click", () => {
  if (socket) socket.emit("click");
});

// ----------------------
// タイトルに戻る
// ----------------------
backToTitleBtn.addEventListener("click", () => {
  showTitle();
  if (socket) {
    socket.disconnect();
    socket = null;
  }
});

// 初期画面
showTitle();