from flask import Flask, jsonify, render_template, request, redirect
import os
import json

app = Flask(__name__, static_folder="static", template_folder="templates")

DRIVE_LINKS_JSON = "drive_links.json"
REQUESTS_JSON = "data_requests.json"

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/investor-desk")
def investor_desk():
    return render_template("investor_desk.html")

@app.route("/api/presentations")
def get_presentations():
    if not os.path.exists(DRIVE_LINKS_JSON):
        return jsonify({"error": "drive_links.json not found", "data": {}}), 200
    with open(DRIVE_LINKS_JSON, "r") as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/request")
def request_page():
    return render_template("request_form.html")

@app.route("/submit-request", methods=["POST"])
def submit_request():
    company = request.form.get("company", "").strip()
    quarter = request.form.get("quarter", "")
    missing_type = request.form.get("type", "")

    new_request = {
        "company": company,
        "quarter": quarter,
        "type": missing_type
    }

    # Save to file
    if os.path.exists(REQUESTS_JSON):
        with open(REQUESTS_JSON, "r") as f:
            all_requests = json.load(f)
    else:
        all_requests = []

    all_requests.append(new_request)

    with open(REQUESTS_JSON, "w") as f:
        json.dump(all_requests, f, indent=2)

    return render_template("request_form.html", message="✅ Your request has been submitted.")

if __name__ == "__main__":
    app.run(debug=True)
