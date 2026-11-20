import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Snap n Savoury", layout="centered")

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Snap n Savoury — Culinary Photo Scavenger Hunt</title>
  <style>
    :root {
      --bg: #1c1917;
      --card: #292524;
      --accent: #f97316;
      --accent-hover: #ea580c;
      --text: #fafaf9;
      --muted: #a8a29e;
      --success: #22c55e;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; }
    body { background-color: var(--bg); color: var(--text); display: flex; justify-content: center; min-height: 100vh; padding: 16px; }
    .app-container {
      width: 100%; max-width: 440px; background: var(--card); border-radius: 20px;
      padding: 20px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
      display: flex; flex-direction: column; gap: 16px;
    }
    header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #44403c; padding-bottom: 12px; }
    h1 { font-size: 1.3rem; color: var(--accent); letter-spacing: -0.5px; }
    .stats { display: flex; gap: 12px; font-weight: 700; font-size: 0.95rem; }
    .badge { background: #44403c; padding: 4px 10px; border-radius: 999px; }
    .prompt-box { background: #1c1917; border: 2px dashed var(--accent); border-radius: 14px; padding: 16px; text-align: center; }
    .prompt-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; color: var(--muted); margin-bottom: 4px; }
    .prompt-text { font-size: 1.25rem; font-weight: 800; color: #fff; }
    .viewfinder {
      position: relative; width: 100%; aspect-ratio: 4 / 3; background: #0c0a09;
      border-radius: 14px; overflow: hidden; display: flex; align-items: center; justify-content: center;
    }
    video, canvas, img { width: 100%; height: 100%; object-fit: cover; }
    .hidden { display: none !important; }
    .controls { display: flex; flex-direction: column; gap: 10px; }
    button, .file-label {
      background: var(--accent); color: white; border: none; padding: 14px; border-radius: 12px;
      font-size: 1rem; font-weight: 700; cursor: pointer; text-align: center; transition: background 0.2s;
    }
    button:hover, .file-label:hover { background: var(--accent-hover); }
    button.secondary { background: #44403c; }
    button.secondary:hover { background: #57534e; }
    button.success { background: var(--success); color: #052e16; }
    .row { display: flex; gap: 10px; }
    .row > * { flex: 1; }

    /* End-of-game Question & Results */
    .question-box {
      background: #1c1917; border: 2px solid var(--accent); border-radius: 14px;
      padding: 16px; text-align: center; display: flex; flex-direction: column; gap: 12px;
    }
    .question-text { font-size: 1.1rem; font-weight: 800; color: #fff; }
    .gallery { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 8px; }
    .gallery-item {
      background: #1c1917; border: 2px solid #44403c; border-radius: 10px;
      overflow: hidden; display: flex; flex-direction: column;
    }
    .gallery-item img { aspect-ratio: 4 / 3; width: 100%; object-fit: cover; }
    .gallery-caption {
      font-size: 0.75rem; padding: 6px 8px; color: var(--text);
      background: #0c0a09; text-align: center; font-weight: 600;
    }
  </style>
</head>
<body>
  <div class="app-container">
    <header>
      <h1>📸 Snap n Savoury</h1>
      <div class="stats">
        <span class="badge">⏱️ <span id="timer">60</span>s</span>
        <span class="badge">⭐ <span id="score">0</span></span>
      </div>
    </header>

    <div class="prompt-box">
      <div class="prompt-label">Your Savoury Target</div>
      <div class="prompt-text" id="promptText">Press Start to Hunt!</div>
    </div>

    <div class="viewfinder">
      <video id="video" autoplay playsinline class="hidden"></video>
      <canvas id="canvas" class="hidden"></canvas>
      <div id="placeholder" style="color: var(--muted); text-align: center; padding: 20px;">
        Camera preview will appear here
      </div>
    </div>

    <div class="controls">
      <button id="startBtn">Start 60-Second Hunt</button>
      
      <div id="activeControls" class="hidden controls">
        <button id="snapBtn">📸 Snap Dish!</button>
        <div class="row">
          <button id="skipBtn" class="secondary">Skip (-5s)</button>
          <label class="file-label secondary">
            📁 Upload Photo <input type="file" id="fileInput" accept="image/*" class="hidden" />
          </label>
        </div>
      </div>

      <div id="confirmControls" class="hidden row">
        <button id="retakeBtn" class="secondary">Retake</button>
        <button id="claimBtn" class="success">Claim +100 Pts!</button>
      </div>
    </div>

    <!-- End-of-game Question Box -->
    <div id="questionBox" class="question-box hidden">
      <div class="question-text">Do you want to see the pics u snapped?</div>
      <button id="yesBtn" class="success">Yes</button>
    </div>

    <!-- Instant Results Gallery -->
    <div id="resultsSection" class="hidden">
      <div class="prompt-label" style="text-align: center; font-size: 0.85rem; color: var(--accent);">
        Your Snapped Savouries (<span id="picCount">0</span>)
      </div>
      <div class="gallery" id="gallery"></div>
    </div>
  </div>

  <script>
    const PROMPTS = [
      "Something Crispy & Fried", "A Spicy Street Snack", "Melted Cheese Goodness",
      "A Tangy Chutney or Dip", "Fresh Herbs or Garnish", "Something Roasted or Grilled",
      "A Savoury Baked Pastry", "Noodles, Rice, or Grains", "Something Pickled or Salty",
      "A Steaming Hot Beverage or Soup"
    ];

    let score = 0;
    let timeLeft = 60;
    let timerInterval = null;
    let currentPrompt = "";
    let stream = null;
    let snappedPics = [];

    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");
    const placeholder = document.getElementById("placeholder");
    const promptText = document.getElementById("promptText");
    const timerEl = document.getElementById("timer");
    const scoreEl = document.getElementById("score");
    const gallery = document.getElementById("gallery");
    const startBtn = document.getElementById("startBtn");
    const activeControls = document.getElementById("activeControls");
    const confirmControls = document.getElementById("confirmControls");
    const snapBtn = document.getElementById("snapBtn");
    const skipBtn = document.getElementById("skipBtn");
    const retakeBtn = document.getElementById("retakeBtn");
    const claimBtn = document.getElementById("claimBtn");
    const fileInput = document.getElementById("fileInput");

    const questionBox = document.getElementById("questionBox");
    const yesBtn = document.getElementById("yesBtn");
    const resultsSection = document.getElementById("resultsSection");
    const picCount = document.getElementById("picCount");

    function nextPrompt() {
      const available = PROMPTS.filter(p => p !== currentPrompt);
      currentPrompt = available[Math.floor(Math.random() * available.length)];
      promptText.textContent = currentPrompt;
    }

    async function initCamera() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false });
        video.srcObject = stream;
        video.classList.remove("hidden");
        placeholder.classList.add("hidden");
      } catch (err) {
        placeholder.textContent = "Camera unavailable — use Upload Photo below!";
      }
    }

    function stampPhoto(sourceElement, width, height) {
      canvas.width = width;
      canvas.height = height;
      ctx.drawImage(sourceElement, 0, 0, width, height);
      ctx.fillStyle = "rgba(0, 0, 0, 0.65)";
      ctx.fillRect(0, height - 60, width, 60);
      ctx.fillStyle = "#f97316";
      ctx.font = "bold 18px sans-serif";
      ctx.fillText("SNAP N SAVOURY", 14, height - 34);
      ctx.fillStyle = "#ffffff";
      ctx.font = "14px sans-serif";
      ctx.fillText("✓ " + currentPrompt, 14, height - 14);
      video.classList.add("hidden");
      placeholder.classList.add("hidden");
      canvas.classList.remove("hidden");
      activeControls.classList.add("hidden");
      confirmControls.classList.remove("hidden");
    }

    startBtn.addEventListener("click", async () => {
      score = 0;
      timeLeft = 60;
      snappedPics = [];
      scoreEl.textContent = score;
      timerEl.textContent = timeLeft;
      gallery.innerHTML = "";
      
      // Reset and hide post-game sections
      questionBox.classList.add("hidden");
      resultsSection.classList.add("hidden");
      
      startBtn.classList.add("hidden");
      activeControls.classList.remove("hidden");
      confirmControls.classList.add("hidden");
      canvas.classList.add("hidden");
      await initCamera();
      nextPrompt();
      clearInterval(timerInterval);
      timerInterval = setInterval(() => {
        timeLeft--;
        timerEl.textContent = Math.max(0, timeLeft);
        if (timeLeft <= 0) endGame();
      }, 1000);
    });

    snapBtn.addEventListener("click", () => {
      if (!stream) {
        alert("No live camera detected. Use the Upload Photo button instead!");
        return;
      }
      stampPhoto(video, video.videoWidth || 640, video.videoHeight || 480);
    });

    fileInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const img = new Image();
      img.onload = () => {
        stampPhoto(img, 640, 480);
      };
      img.src = URL.createObjectURL(file);
    });

    skipBtn.addEventListener("click", () => {
      timeLeft = Math.max(0, timeLeft - 5);
