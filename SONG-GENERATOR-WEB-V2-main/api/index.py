from flask import Flask, request, jsonify, render_template_string
import requests
import time

app = Flask(__name__)

# --- CONFIGURATION ---
HEADERS = {
    "Host": "notegpt.io",
    "sec-ch-ua-platform": '"Android"',
    "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36",
    "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    "sec-ch-ua-mobile": "?1",
    "accept": "*/*",
    "origin": "https://notegpt.io",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://notegpt.io/ai-music-generator",
    "accept-language": "en-US,en;q=0.9,ta;q=0.8,id;q=0.7,hi;q=0.6,es;q=0.5,zh-CN;q=0.4,zh;q=0.3",
    "cookie": (
        "sbox-guid=MTc1OTIxMzI4OHwyNDb8OTMyMzkyODUx; "
        "_uab_collina=175921328966673937153408; "
        "anonymous_user_id=cc84469bb9ecc8ddbc4d4090d60870d2; "
        "is_first_visit=true; "
        "_gid=GA1.2.1424805809.1759213294; "
        "_trackUserId=G-1759213293000; "
        "crisp-client%2Fsession%2F02aa9b53-fc37-4ca7-954d-7a99fb3393de=session_2a8117e6-3b4e-4575-992e-135612fb912a; "
        "_ga_PFX3BRW5RQ=GS2.1.s1759213292$o1$g1$t1759213539$j55$l0$h2030709755; "
        "_ga=GA1.2.1342138808.1759213292"
    ),
    "priority": "u=1, i"
}

API_GENERATE = "https://notegpt.io/api/v2/music/generate"
API_STATUS = "https://notegpt.io/api/v2/music/status"

# --- HTML PAGE ---
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ABBAS MUSIC AI | Sonic Engine</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
  :root {
    --primary: #4f46e5;
    --secondary: #ec4899;
    --bg-dark: #0f172a;
    --card-bg: rgba(30, 41, 59, 0.4);
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --border: rgba(255, 255, 255, 0.08);
    --glow: 0 0 50px rgba(79, 70, 229, 0.25);
  }

  * { box-sizing: border-box; outline: none; }

  body {
    margin: 0;
    font-family: 'Plus Jakarta Sans', sans-serif;
    background-color: var(--bg-dark);
    background-image: 
      radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
      radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
      radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
    color: var(--text-main);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
  }

  .container {
    width: 100%;
    max-width: 600px;
    animation: fadeIn 0.8s ease-out;
  }

  @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

  .glass-panel {
    background: var(--card-bg);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 40px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7), var(--glow);
    position: relative;
    overflow: hidden;
  }
  
  /* Animated border effect */
  .glass-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, var(--primary), var(--secondary), transparent);
    animation: borderGlow 3s linear infinite;
  }
  
  @keyframes borderGlow { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }

  .header { text-align: center; margin-bottom: 35px; }
  
  .logo-icon {
    font-size: 3rem; 
    background: linear-gradient(135deg, #fff, #cbd5e1);
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent;
    margin-bottom: 15px; 
    filter: drop-shadow(0 0 15px rgba(255,255,255,0.2));
  }

  h1 { font-size: 2rem; font-weight: 700; margin: 0; letter-spacing: -0.5px; }
  p.subtitle { color: var(--text-muted); font-size: 0.95rem; margin-top: 8px; }

  .form-group { margin-bottom: 20px; }
  
  label {
    display: block; margin-bottom: 8px; font-size: 0.8rem; font-weight: 600;
    color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; padding-left: 4px;
  }

  input, textarea {
    width: 100%;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid var(--border);
    color: #fff;
    padding: 16px;
    border-radius: 12px;
    font-size: 1rem;
    font-family: inherit;
    transition: all 0.3s ease;
  }
  
  input:focus, textarea:focus {
    border-color: var(--secondary);
    box-shadow: 0 0 0 4px rgba(236, 72, 153, 0.1);
    background: rgba(15, 23, 42, 0.8);
  }

  textarea { resize: vertical; min-height: 100px; line-height: 1.6; }

  button.btn-generate {
    width: 100%;
    padding: 18px;
    border: none;
    border-radius: 12px;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: white;
    font-weight: 700;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4);
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
    position: relative;
    overflow: hidden;
  }

  button.btn-generate:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(79, 70, 229, 0.5); }
  button.btn-generate:active { transform: scale(0.98); }
  button.btn-generate:disabled { opacity: 0.7; cursor: not-allowed; filter: grayscale(1); transform: none; }

  /* LOADING UI */
  .loading-area { display: none; margin-top: 30px; text-align: center; }
  
  .progress-track {
    width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden;
    margin-bottom: 10px;
  }
  
  .progress-fill {
    height: 100%; width: 0%; background: linear-gradient(90deg, var(--primary), var(--secondary));
    border-radius: 10px; transition: width 0.3s ease; box-shadow: 0 0 10px var(--secondary);
  }
  
  .status-text { color: var(--text-muted); font-size: 0.9rem; display: flex; align-items: center; justify-content: center; gap: 8px; }

  /* ERROR MESSAGE */
  #error-box {
    display: none; margin-top: 20px; padding: 15px; border-radius: 8px;
    background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); color: #fca5a5;
    font-size: 0.9rem; text-align: center;
  }

  /* RESULT CARD */
  .result-area {
    display: none; margin-top: 30px; background: rgba(0,0,0,0.3); border-radius: 16px; padding: 25px;
    border: 1px solid var(--border); text-align: center; animation: fadeIn 0.5s ease;
  }

  .cover-art {
    width: 120px; height: 120px; border-radius: 16px; object-fit: cover; margin: 0 auto 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1);
  }

  .track-title { font-size: 1.2rem; font-weight: 700; margin: 0 0 5px; }
  .track-meta { font-size: 0.8rem; color: var(--secondary); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 20px; }

  audio { width: 100%; height: 40px; margin-bottom: 20px; filter: invert(1) hue-rotate(180deg); opacity: 0.8; }
  audio:hover { opacity: 1; }

  .btn-download {
    display: inline-flex; align-items: center; gap: 8px; padding: 10px 24px;
    background: white; color: #0f172a; border-radius: 50px; text-decoration: none;
    font-weight: 700; font-size: 0.9rem; transition: 0.3s; box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  }
  .btn-download:hover { transform: translateY(-2px); background: #f1f5f9; }

</style>
</head>
<body>

<div class="container">
  <div class="glass-panel">
    <div class="header">
      <i class="fa-solid fa-wave-square logo-icon"></i>
      <h1>ABBAS MUSIC AI</h1>
      <p class="subtitle">Pro-Grade Neural Audio Synthesis</p>
    </div>

    <form id="genForm">
      <div class="form-group">
        <label for="prompt">Theme / Genre</label>
        <input type="text" id="prompt" placeholder="e.g. Cinematic, Sad Hindi, Cyberpunk" required>
      </div>

      <div class="form-group">
        <label for="lyrics">Lyrics (Optional)</label>
        <textarea id="lyrics" placeholder="Paste lyrics for better results..."></textarea>
      </div>

      <button type="submit" class="btn-generate" id="submitBtn">
        <i class="fa-solid fa-bolt"></i> Generate Masterpiece
      </button>
    </form>

    <!-- Loading Animation -->
    <div class="loading-area" id="loader">
      <div class="progress-track">
        <div class="progress-fill" id="progressBar"></div>
      </div>
      <div class="status-text">
        <i class="fa-solid fa-circle-notch fa-spin"></i> <span id="progressText">Initializing AI... 0%</span>
      </div>
    </div>

    <!-- Error Box -->
    <div id="error-box"></div>

    <!-- Result Area -->
    <div class="result-area" id="result">
      <img src="" id="thumb" class="cover-art">
      <h3 class="track-title" id="title">AI Generated Track</h3>
      <p class="track-meta">High Fidelity Audio</p>
      
      <audio id="audioPlayer" controls></audio>
      
      <a id="dlBtn" href="#" target="_blank" class="btn-download">
        <i class="fa-solid fa-download"></i> Download MP3
      </a>
    </div>
  </div>
</div>

<script>
const form = document.getElementById('genForm');
const btn = document.getElementById('submitBtn');
const loader = document.getElementById('loader');
const result = document.getElementById('result');
const errBox = document.getElementById('error-box');
const pBar = document.getElementById('progressBar');
const pText = document.getElementById('progressText');

let timer;

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  // Reset State
  errBox.style.display = 'none';
  result.style.display = 'none';
  document.getElementById('audioPlayer').pause();
  document.getElementById('audioPlayer').src = "";
  
  const prompt = document.getElementById('prompt').value.trim();
  const lyrics = document.getElementById('lyrics').value.trim();

  // UI Loading State
  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Processing...';
  loader.style.display = 'block';
  
  // Fake Progress Animation (0% -> 90%)
  let progress = 0;
  pBar.style.width = '0%';
  pText.innerText = 'Initializing AI... 0%';
  
  timer = setInterval(() => {
    if (progress < 90) {
      // Random increments to simulate work
      progress += Math.floor(Math.random() * 5) + 1;
      if (progress > 90) progress = 90;
      pBar.style.width = `${progress}%`;
      
      if (progress < 30) pText.innerText = `Initializing AI... ${progress}%`;
      else if (progress < 70) pText.innerText = `Synthesizing Audio... ${progress}%`;
      else pText.innerText = `Finalizing Track... ${progress}%`;
    }
  }, 800);

  try {
    const res = await fetch('/api/song', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ prompt, lyrics })
    });

    const data = await res.json();

    if (!res.ok || data.error) {
      throw new Error(data.error || "Generation failed");
    }

    // Success Flow
    clearInterval(timer);
    pBar.style.width = '100%';
    pText.innerText = 'Complete! 100%';
    
    setTimeout(() => {
      loader.style.display = 'none';
      
      // Fill Data
      document.getElementById('thumb').src = data.thumbnail_url || `https://picsum.photos/seed/${Math.random()}/200/200`;
      document.getElementById('title').innerText = prompt.length > 25 ? prompt.substring(0,25)+"..." : prompt;
      document.getElementById('audioPlayer').src = data.music_url;
      document.getElementById('dlBtn').href = data.music_url;
      
      result.style.display = 'block';
      document.getElementById('audioPlayer').play().catch(() => {}); // Try autoplay

    }, 600);

  } catch (err) {
    clearInterval(timer);
    loader.style.display = 'none';
    errBox.innerText = "❌ " + err.message;
    errBox.style.display = 'block';
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-bolt"></i> Generate Masterpiece';
  }
});
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/api/song", methods=["POST"])
def generate_song():
    try:
        # 1. Parse Data
        data = request.get_json(force=True)
        prompt = data.get("prompt", "").strip()
        lyrics = data.get("lyrics", "").strip()

        if not prompt:
            return jsonify({"error": "Theme is required."}), 400

        # 2. Initiate Generation
        payload = {
            "prompt": prompt,
            "lyrics": lyrics if lyrics else "",
            "duration": 0
        }
        
        print(f"[START] Generating song for: {prompt}")

        try:
            gen_resp = requests.post(API_GENERATE, json=payload, headers=HEADERS, timeout=20)
            gen_resp.raise_for_status()
            gen_json = gen_resp.json()
        except Exception as e:
            print(f"[ERROR] Gen API failed: {str(e)}")
            if "403" in str(e) or "401" in str(e):
                return jsonify({"error": "Auth Failed. Cookies expired."}), 503
            return jsonify({"error": "Failed to start generation."}), 502

        # 3. Extract Conversation ID
        conv_id = gen_json.get("data", {}).get("conversation_id")
        # Fallback check
        if not conv_id: 
            conv_id = gen_json.get("conversation_id")

        if not conv_id:
            print("[ERROR] No ID found.")
            return jsonify({"error": "Server did not return a Task ID."}), 500

        print(f"[ID] Conversation ID: {conv_id}")

        # 4. Polling Loop (Robust)
        max_attempts = 80  # Approx 4 minutes (80 * 3s)
        sleep_interval = 3

        for attempt in range(max_attempts):
            try:
                status_resp = requests.get(API_STATUS, params={"conversation_id": conv_id}, headers=HEADERS, timeout=15)
                status_resp.raise_for_status()
                status_json = status_resp.json()
                
                data_block = status_json.get("data", {})
                status_text = data_block.get("status", "").lower()

                # Log occasionally
                if attempt % 10 == 0:
                    print(f"[POLL] Attempt {attempt+1}: {status_text}")

                # --- FAILURE CHECK ---
                if status_text == "failed":
                    print("[FAIL] API Reported Failure.")
                    return jsonify({"error": "Generation Failed. Try longer lyrics or a different theme."}), 400

                # --- SUCCESS CHECK ---
                if status_text == "success":
                    music_url = data_block.get("music_url")
                    thumb_url = data_block.get("thumbnail_url")
                    
                    # Ensure URL exists
                    if music_url:
                        print("[SUCCESS] Song Ready.")
                        return jsonify({
                            "success": True,
                            "music_url": music_url,
                            "thumbnail_url": thumb_url or "https://picsum.photos/seed/music/200/200"
                        })
                
                # --- PENDING: WAIT ---
                time.sleep(sleep_interval)

            except requests.exceptions.RequestException as e:
                # If a single poll fails, don't crash the whole loop, just wait and retry
                print(f"[WARN] Poll Error on attempt {attempt+1}: {str(e)}")
                time.sleep(sleep_interval)
                continue

        # 5. Timeout Handler
        print("[TIMEOUT] Max attempts reached.")
        return jsonify({"error": "Timeout: The AI took too long. Try a simpler prompt."}), 504

    except Exception as e:
        print(f"[CRITICAL] Server Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
