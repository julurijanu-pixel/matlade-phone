import os
from datetime import datetime
from typing import List, Dict, Any
from flask import Flask, render_template, request, jsonify

from sms_translator import SAMPLE_ALERTS, translate_sms_to_telugu

app = Flask(__name__)

HISTORY_LOG: List[Dict[str, Any]] = []


def _has_optional_key() -> bool:
    return bool(os.environ.get("OPTIONAL_CLOUD_KEY", "").strip())


@app.route("/")
def index():
    return render_template(
        "index.html",
        samples=SAMPLE_ALERTS,
        has_optional_key=_has_optional_key(),
    )


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "ok",
            "app": "Matlade Phone Prototype",
            "requires_secret_key": False,
            "optional_key_configured": _has_optional_key(),
        }
    )


@app.route("/api/translate", methods=["POST"])
def api_translate():
    payload = request.get_json(silent=True) or {}
    sms_text = payload.get("sms_text", "")
    result = translate_sms_to_telugu(sms_text=sms_text, has_optional_key=_has_optional_key())

    if not result.get("ok"):
        return jsonify(result), 400

    entry = {
        "timestamp": datetime.utcnow().strftime("%H:%M:%S UTC"),
        "category": result["category"],
        "original_sms": result["original_sms"],
        "telugu_text": result["telugu_text"],
    }
    HISTORY_LOG.insert(0, entry)
    del HISTORY_LOG[10:]

    result["history"] = HISTORY_LOG
    return jsonify(result)


@app.route("/api/history", methods=["GET"])
def api_history():
    return jsonify({"history": HISTORY_LOG})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)