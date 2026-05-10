"""
Local development server.

Usage:
    pip install -r requirements.txt
    python run.py
    open http://localhost:5000
"""
import os
import sys

# Add api/ to the path so 'from auditor import ...' finds api/auditor.py
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "api"))

from flask import Flask, jsonify, request, send_file

from auditor import SycophancyAuditor, parse_log, report_to_dict, SAMPLE_MESSAGES

ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
_auditor = SycophancyAuditor()


@app.route("/")
def index():
    return send_file(os.path.join(ROOT, "public", "index.html"))


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "version": "1.0"})


@app.route("/api/sample")
def sample():
    try:
        report = _auditor.audit(SAMPLE_MESSAGES)
        return jsonify(report_to_dict(report, "sample_sycophantic.json"))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/audit", methods=["POST"])
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


if __name__ == "__main__":
    app.run(debug=True, port=5000)
