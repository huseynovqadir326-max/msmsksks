import os
import subprocess
import uuid
from flask import Flask, request, send_file

app = Flask(__name__)
UPLOAD_DIR = "v"
os.makedirs(UPLOAD_DIR, exist_ok=True)

HTML = """
<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ultra Video Studio & FPS</title>
    <style>
        body { background: #0f172a; color: #fff; font-family: sans-serif; padding: 20px; margin: 0; }
        .box { max-width: 400px; margin: auto; background: #1e293b; padding: 20px; border-radius: 14px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        h2 { color: #38bdf8; text-align: center; margin-top: 0; }
        label { display: block; margin-top: 15px; font-weight: bold; font-size: 14px; color: #cbd5e1; }
        select, input[type="file"] { width: 100%; padding: 10px; margin-top: 6px; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: #fff; box-sizing: border-box; }
        button { width: 100%; padding: 14px; margin-top: 22px; background: #2563eb; color: #fff; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; }
        #st { display: none; color: #facc15; text-align: center; margin-top: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="box">
        <h2>🎬 Ultra Video Studio</h2>
        <form action="/go" method="post" enctype="multipart/form-data" onsubmit="document.getElementById('st').style.display='block'">
            <label>1. Videonu Seçin (Ölçü pozulmur):</label>
            <input type="file" name="video" accept="video/*" required>

            <label>2. FPS Seçimi (Axıcılıq):</label>
            <select name="fps">
                <option value="60">60 FPS</option>
                <option value="120" selected>120 FPS</option>
                <option value="240">240 FPS</option>
                <option value="520">520 FPS (Super Axıcı)</option>
            </select>

            <label>3. Keyfiyyət və Kəskinlik:</label>
            <select name="quality">
                <option value="normal">Normal Təmiz Görüntü</option>
                <option value="high" selected>Yüksək HD Kəskinlik + Canlı Rəng</option>
                <option value="ultra">Ultra Kristal Keyfiyyət</option>
            </select>

            <button type="submit">🚀 Hazırla & Endir</button>
            <p id="st">⏳ Video hazırlanır, zəhmət olmasa gözləyin...</p>
        </form>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    return HTML

@app.route("/go", methods=["POST"])
def go():
    try:
        f = request.files.get("video")
        if not f:
            return "Video seçilməyib!", 400

        fps = request.form.get("fps", "120")
        quality = request.form.get("quality", "high")
        
        uid = str(uuid.uuid4())[:5]
        inp = os.path.join(UPLOAD_DIR, f"in_{uid}.mp4")
        out = os.path.join(UPLOAD_DIR, f"Ultra_{fps}fps_{uid}.mp4")
        f.save(inp)

        if quality == "normal":
            q_filter = "unsharp=5:5:0.8:5:5:0.0"
        elif quality == "high":
            q_filter = "unsharp=5:5:1.3:5:5:0.0,eq=contrast=1.04:saturation=1.08"
        else:
            q_filter = "unsharp=5:5:1.8:5:5:0.0,eq=contrast=1.06:saturation=1.12"

        # Videonun orijinal ölçüsünü qoruyan, sürəti yavaşlatmayan stabil filtr
        vf = f"{q_filter},fps={fps}"

        cmd = [
            "ffmpeg", "-y", "-i", inp,
            "-vf", vf,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "18",
            "-preset", "ultrafast",
            "-c:a", "aac",
            out
        ]

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0 or not os.path.exists(out):
            return f"FFmpeg Xətası: {res.stderr[-400:]}", 500

        return send_file(out, as_attachment=True)
    except Exception as e:
        return f"Xəta baş verdi: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
    