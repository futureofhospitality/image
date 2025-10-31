from flask import Flask, request, send_file
import subprocess, tempfile, os, requests
from flask import Flask, request, render_template_string

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

        # Step 3: overlay frame only for 'red'
        if style == "red":
            overlay_url = "https://fohpodcast.b-cdn.net/Website%20thumbnail/OverlayRed.png"
            overlay_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            print(f"Downloading overlay from: {overlay_url}")
            o = requests.get(overlay_url, stream=True)
            if o.status_code == 200:
                with open(overlay_tmp.name, 'wb') as f_overlay:
                    for chunk in o.iter_content(chunk_size=8192):
                        f_overlay.write(chunk)
                subprocess.run([
                    "magick", out.name, overlay_tmp.name,
                    "-compose", "Over", "-composite", out.name
                ], check=True)
            else:
                print(f"⚠️ Failed to download overlay: {o.status_code}")

        print("✅ Image processing done, returning file")
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

        # Maak tijdelijke bestanden
        tmp_frame = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")

        # ✅ Run FFmpeg (1 frame op opgegeven tijd) met overwrite
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


@app.route("/typebot-demo")
def typebot_demo():
    # Read query param (you can later fetch real data from a DB or WP API)
    demo_id = request.args.get("id", "123")

    # Temporary demo data (later replace with actual lookup logic)
    if demo_id == "123":
        guest = "John Doe"
        guest_description = "Hotel Manager at Ocean View"
        forwho = "Hoteliers"
        chapters = "Welcome, Experience, Technology"
        transcript = "This is a test transcript text that normally would be long."
    else:
        guest = "Unknown"
        guest_description = ""
        forwho = ""
        chapters = ""
        transcript = "Demo transcript fallback."

    # Build Typebot URL
    base_url = "https://typebot.co/faq-8hhmccv"
    query = f"guest={guest}&guest_description={guest_description}&forwho={forwho}&chapters={chapters}&transcript_url={transcript}"
    iframe_url = f"{base_url}?{query}"

    # Render HTML with iframe
    html = f"""
    <html>
      <head><title>Typebot Demo</title></head>
      <body style="margin:0;padding:0;">
        <iframe src="{iframe_url}" width="100%" height="600" style="border:none;" allow="clipboard-read; clipboard-write"></iframe>
      </body>
    </html>
    """
    return render_template_string(html)

@app.route("/typebot-loader")
def typebot_loader():
    # Get the long Typebot URL from query parameter
    typebot_url = request.args.get("url")

    if not typebot_url:
        return "<p style='font-family:sans-serif;color:red;'>❌ Missing ?url= parameter.</p>", 400

    # Render the HTML page that loads the Typebot iframe
    html = f"""
    <html>
      <head><title>Typebot Loader</title></head>
      <body style="margin:0;padding:0;overflow:hidden;">
        <iframe src="{typebot_url}" width="100%" height="100%" style="border:none;" allow="clipboard-read; clipboard-write"></iframe>
      </body>
    </html>
    """
    return render_template_string(html)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
