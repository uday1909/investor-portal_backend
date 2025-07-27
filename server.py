from flask import Flask, jsonify, send_from_directory, abort, render_template
import os
import json

app = Flask(__name__, static_folder="static", template_folder="templates")

DRIVE_LINKS_JSON = "drive_links.json"

@app.route("/")
def homepage():
    return render_template("index.html")  # Show frontend search UI

@app.route("/api/presentations")
def get_presentations():
    # ✅ Serve directly from drive_links.json
    if not os.path.exists(DRIVE_LINKS_JSON):
        return jsonify({
            "error": "drive_links.json not found",
            "data": {}
        }), 200

    with open(DRIVE_LINKS_JSON, "r") as f:
        data = json.load(f)

    return jsonify(data)

# Note: /data route is no longer needed since we're not serving local files anymore

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))