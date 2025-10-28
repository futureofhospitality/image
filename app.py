from flask import Flask, request, send_file
import subprocess, tempfile, os, requests

app = Flask(__name__)

@app.route("/ping")
def ping():
    return {"status": "ok"}


@app.route("/filter", methods=["POST"])
def filter_image():
    try:
        data = request.get_json()
        url = data.get("image_url")
        style = data.get("style", "").lower()

        if not url:
            return {"error": "Missing image_url"}, 400
        if style not in ["red", "purple", "dark", "grey"]:
            return {"error": f"Unknown style '{style}'. Must be one of ['red', 'purple', 'dark', 'grey']"}, 400

        inp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        out = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")

        # Download image via Python
        print(f"Downloading from: {url}")
        r = requests.get(url, stream=True)
        if r.status_code != 200:
            return {"error": f"Failed to download image, status {r.status_code}"}, 400
        with open(inp.name, 'wb') as f_out:
            for chunk in r.iter_content(chunk_size=8192):
                f_out.write(chunk)

        # 🎨 Canva-style duotone definitions
        if style == "red":
            highlight, shadow, intensity = "#ff4076", "#021f53", "75"
        elif style == "purple":
            highlight, shadow, intensity = "#935eb2", "#242659", "75"
        elif style == "dark":
            highlight, shadow, intensity = "#939ba9", "#041f23", "100"
        elif style == "grey":
            highlight, shadow, intensity = "#eeeeee", "#111111", "100"

        # 🪄 True duotone effect in ImageMagick
        subprocess.run([
            "magick", inp.name, "-colorspace", "Gray",
            "(", "-clone", "0", "-fill", shadow, "-colorize", "100", ")",
            "(", "-clone", "0", "-fill", highlight, "-colorize", "100", ")",
            "-compose", "blend", "-define", f"compose:args={intensity},100",
            "-composite", "-set", "colorspace", "sRGB", out.name
        ], check=True)

        print(f"✅ Duotone ({style}) applied successfully")
        return send_file(out.name, mimetype="image/jpeg")

    except subprocess.CalledProcessError as e:
        print(f"❌ Subprocess failed: {e}")
        return {"error": f"Subprocess failed: {str(e)}"}, 500
    except Exception as e:
        print(f"❌ General error: {e}")
        return {"error": str(e)}, 500


@app.route("/frame", methods=["POST"])
def extract_frame():
    """
    Extract a frame from a video URL using FFmpeg.
    Example payload:
    { "video_url": "https://vz-xxx.b-cdn.net/video.mp4", "timestamp": 2089 }
    """
    try:
        data = request.get_json()
        video_url = data.get("video_url")
        timestamp = float(data.get("timestamp", 0))

        if not video_url:
            return {"error": "Missing video_url"}, 400

        tmp_frame = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")

        # ✅ Run FFmpeg (1 frame at specific timestamp)
        subprocess.run([
            "ffmpeg", "-y", "-ss", str(timestamp), "-i", video_url,
            "-vframes", "1", "-q:v", "2", tmp_frame.name
        ], check=True)

        print(f"✅ Frame extracted at {timestamp}s from {video_url}")
        return send_file(
            tmp_frame.name,
            mimetype="image/jpeg",
            as_attachment=True,
            download_name="frame.jpg"
        )

    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg failed: {e}")
        return {"error": f"FFmpeg failed: {str(e)}"}, 500
    except Exception as e:
        print(f"❌ General error: {e}")
        return {"error": str(e)}, 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
