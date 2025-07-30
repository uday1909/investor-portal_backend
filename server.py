from flask import Flask, jsonify, render_template
import os
import json

app = Flask(__name__, static_folder="static", template_folder="templates")

DRIVE_LINKS_JSON = "drive_links.json"

@app.route("/")
def homepage():
    return render_template("index.html")  # 🏠 This will be the new homepage (StocksLedger)

@app.route("/investor-desk")
def investor_desk():
    return render_template("investor_desk.html")  # 📁 Existing dashboard goes here

@app.route("/api/presentations")
def get_presentations():
    if not os.path.exists(DRIVE_LINKS_JSON):
        return jsonify({"error": "drive_links.json not found", "data": {}}), 200

    with open(DRIVE_LINKS_JSON, "r") as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))