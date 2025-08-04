from flask import Flask, jsonify, render_template, request
import os
import json
import logging

app = Flask(__name__, static_folder="static", template_folder="templates")

DRIVE_LINKS_JSON = "drive_links.json"
REQUESTS_JSON = "/tmp/data_requests.json"
SYMBOL_NAME_FILE = "symbol_to_name.json"
SEARCH_MAP_FILE = os.path.join("static", "search_map.json")


def generate_search_map():
    if not os.path.exists(SYMBOL_NAME_FILE):
        print(f"❌ Missing {SYMBOL_NAME_FILE}, cannot generate search map.")
        return

    try:
        with open(SYMBOL_NAME_FILE, "r") as f:
            symbol_to_name = json.load(f)

        search_map = {}

        for symbol, name in symbol_to_name.items():
            symbol_lower = symbol.strip().lower()
            name_lower = name.strip().lower()

            search_map[symbol_lower] = symbol
            search_map[name_lower] = symbol

            # Add short variation like "tata consultancy"
            tokens = name_lower.replace("limited", "").strip().split()
            if len(tokens) >= 2:
                short_name = " ".join(tokens[:2])
                if short_name not in search_map:
                    search_map[short_name] = symbol

        os.makedirs("static", exist_ok=True)
        with open(SEARCH_MAP_FILE, "w") as f:
            json.dump(search_map, f, indent=2)

        print(f"✅ Generated {SEARCH_MAP_FILE} with {len(search_map)} entries.")
    except Exception as e:
        print(f"❌ Error generating search map: {e}")


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

    try:
        with open(DRIVE_LINKS_JSON, "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        print(f"❌ Error reading drive_links.json: {e}")
        return jsonify({"error": "drive_links.json is invalid or corrupted", "data": {}}), 200

@app.route("/company/<symbol>")
def company_page(symbol):
    symbol = symbol.upper()

    # Load company name from symbol_to_name.json
    if not os.path.exists(SYMBOL_NAME_FILE):
        return f"Company mapping not available.", 500

    with open(SYMBOL_NAME_FILE, "r") as f:
        symbol_to_name = json.load(f)

    if symbol not in symbol_to_name:
        return f"No data found for company symbol: {symbol}", 404

    company_name = symbol_to_name[symbol]

    # Load drive_links.json to get that company's data
    if not os.path.exists(DRIVE_LINKS_JSON):
        return f"No data found.", 500

    with open(DRIVE_LINKS_JSON, "r") as f:
        data = json.load(f)

    company_data = data.get(symbol, {})

    return render_template("company_page.html", symbol=symbol, company_name=company_name, company_data=company_data)

@app.route("/request")
def request_page():
    return render_template("request_form.html")


@app.route("/submit-request", methods=["POST"])
def submit_request():
    company = request.form.get("company", "").strip()
    quarter = request.form.get("quarter", "")
    missing_type = request.form.get("type", "")

    print("📥 Received request:", company, quarter, missing_type)

    new_request = {
        "company": company,
        "quarter": quarter,
        "type": missing_type
    }

    all_requests = []
    if os.path.exists(REQUESTS_JSON):
        try:
            with open(REQUESTS_JSON, "r") as f:
                all_requests = json.load(f)
        except json.JSONDecodeError:
            print("⚠️ JSON decode error. Reinitializing file.")
            all_requests = []

    all_requests.append(new_request)

    try:
        with open(REQUESTS_JSON, "w") as f:
            json.dump(all_requests, f, indent=2)
        print(f"✅ Request saved to {REQUESTS_JSON}")
    except Exception as e:
        print(f"❌ Error writing to {REQUESTS_JSON}: {e}")

    return render_template("request_form.html", message="✅ Your requet has been submitted.")

@app.route("/robots.txt")
def robots():
    return app.send_static_file("robots.txt")

from flask import Response

from flask import Response

@app.route("/sitemap.xml")
def sitemap():
    import json
    import os

    # Load company symbols from your drive_links.json or similar source
    with open("drive_links.json") as f:
        data = json.load(f)

    base_url = "https://investor-portal-backend.onrender.com"
    urls = [f"{base_url}/investor-desk"]

    for symbol in data:
        urls.append(f"{base_url}/company/{symbol}")

    # Generate proper XML format
    xml_items = [
        f"""  <url>
    <loc>{url}</loc>
  </url>""" for url in urls
    ]

    xml_string = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(xml_items)}
</urlset>"""

    return Response(xml_string, mimetype="application/xml")

@app.route("/health")
def health_check():
    return "✅ Server is running", 200

if __name__ == "__main__":
    generate_search_map()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
