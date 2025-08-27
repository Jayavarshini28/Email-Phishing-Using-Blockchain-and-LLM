# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from utils import compute_final_risk  # your existing pipeline

app = Flask(__name__)
CORS(app)  # allow cross-origin calls from extension (restrict in production)

API_KEY = os.environ.get("EXT_API_KEY", "")

@app.route("/analyze", methods=["POST"])
def analyze():
    # simple API key check (improve in prod)
    if API_KEY:
        key = request.headers.get("x-api-key","")
        if key != API_KEY:
            return jsonify({"error":"invalid api key"}), 403

    data = request.get_json() or {}
    sender = data.get("sender","")
    subject = data.get("subject","")
    body = data.get("body","")
    urls = data.get("urls", [])
    # call your compute_final_risk which returns (final_risk, details)
    final_risk, details = compute_final_risk(body, sender=sender, subject=subject)
    # ensure actions exist
    actions = details.get("llm_actions") or details.get("actions") or ["No actions required"]
    # respond with sanitized JSON
    resp = {
        "final_risk": final_risk,
        "details": details,
        "llm_actions": actions,
        "llm_reason": details.get("llm_reason","")
    }
    return jsonify(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
