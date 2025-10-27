from flask import Flask, request, send_file
import subprocess, tempfile

app = Flask(__name__)

# Filter definitions
FILTERS = {
    "dark":   {"color": "#707D88", "strength": "55%", "opacity": "66", "mode": "Multiply"},
    "grey":   {"color": None,      "strength": None,  "opacity": None, "mode": None},
    "red":    {"color": "#FF4076", "strength": "51%", "opacity": "62", "mode": "Multiply"},
    "purple": {"color": "#935EB2", "strength": "57%", "opacity": "43", "mode": "Multiply"}
}

@app.route("/filter", methods=["POST"])
def filter_image():
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

    # Download image
    subprocess.run(["curl", "-s", "-o", inp.name, url])

    if style == "grey":
        subprocess.run(["magick", inp.name, "-colorspace", "Gray", out.name])
    else:
        # Step 1: grayscale + colorize
        subprocess.run([
            "magick", inp.name, "-colorspace", "Gray",
            "-fill", f["color"], "-colorize", f["strength"], tmp.name
        ])
        # Step 2: overlay same image
        subprocess.run([
            "magick", tmp.name, inp.name,
            "-compose", f["mode"],
            "-define", f"compose:args={f['opacity']},100",
            "-composite", out.name
        ])

    return send_file(out.name, mimetype="image/jpeg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
