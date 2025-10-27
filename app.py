from flask import Flask, request, send_file
import subprocess, tempfile, os, requests

app = Flask(__name__)

# Filter definitions
FILTERS = {
    "dark":   {"color": "#707D88", "strength": "55%", "opacity": "66", "mode": "Multiply"},
    "grey":   {"color": None,      "strength": None,  "opacity": None, "mode": None},
    "red":    {"color": "#FF4076", "strength": "51%", "opacity": "62", "mode": "Multiply"},
    "purple": {"color": "#935EB2", "strength": "57%", "opacity": "43", "mode": "Multiply"}
}

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
        if style not in FILTERS:
            return {"error": f"Unknown style '{style}'. Must be one of {list(FILTERS.keys())}"}, 400

        f = FILTERS[style]
        inp  = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        tmp  = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        out  = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")

        # Download image via Python instead of curl
        print(f"Downloading from: {url}")
        r = requests.get(url, stream=True)
        if r.status_code != 200:
            return {"error": f"Failed to download image, status {r.status_code}"}, 400
        with open(inp.name, 'wb') as f_out:
            for chunk in r.iter_content(chunk_size=8192):
                f_out.write(chunk)

        if style == "grey":
            subprocess.run(["magick", inp.name, "-colorspace", "Gray", out.name], check=True)
        else:
            # Step 1: grayscale + colorize
            subprocess.run([
                "magick", inp.name, "-colorspace", "Gray",
                "-fill", f["color"], "-colorize", f["strength"], tmp.name
            ], check=True)
            # Step 2: overlay same image
            subprocess.run([
                "magick", tmp.name, inp.name,
                "-compose", f["mode"],
                "-define", f"compose:args={f['opacity']},100",
                "-composite", out.name
            ], check=True)

        print("✅ Image processing done, returning file")
        return send_file(out.name, mimetype="image/jpeg")

    except subprocess.CalledProcessError as e:
        print(f"❌ Subprocess failed: {e}")
        return {"error": f"Subprocess failed: {str(e)}"}, 500
    except Exception as e:
        print(f"❌ General error: {e}")
        return {"error": str(e)}, 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
