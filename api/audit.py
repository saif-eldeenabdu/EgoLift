"""Vercel serverless function — POST /api/audit"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request

from auditor import SycophancyAuditor, parse_log, report_to_dict

app = Flask(__name__)
_auditor = SycophancyAuditor()


@app.route("/api/audit", methods=["POST"])
@app.route("/", methods=["POST"])
def audit():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "Empty filename"}), 400

    fname = f.filename.lower()
    if not (fname.endswith(".txt") or fname.endswith(".json")):
        return jsonify({"error": "Only .txt and .json files are supported"}), 400

    try:
        content = f.read()
        messages = parse_log(content, f.filename)
        if not messages:
            return jsonify({"error": "No messages found in file"}), 400
        report = _auditor.audit(messages)
        return jsonify(report_to_dict(report, f.filename))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
