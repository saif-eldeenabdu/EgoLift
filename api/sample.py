"""Vercel serverless function — GET /api/sample"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify

from auditor import SycophancyAuditor, report_to_dict, SAMPLE_MESSAGES

app = Flask(__name__)
_auditor = SycophancyAuditor()


@app.route("/api/sample")
@app.route("/")
def sample():
    try:
        report = _auditor.audit(SAMPLE_MESSAGES)
        return jsonify(report_to_dict(report, "sample_sycophantic.json"))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
