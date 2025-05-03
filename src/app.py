from flask import Flask, jsonify, request, send_from_directory
from flasgger import swag_from
from swagger_template import generate_swagger_doc
from versionutil import VersionUtil
import requests
import os

app = Flask(__name__, static_folder="static", template_folder="template")


MODEL_SERVICE_URL = os.getenv("MODEL_SERVICE_URL", "http://localhost:8080")


@app.route("/")
def serve_index():
    return send_from_directory(app.template_folder, "index.html")

# Analyze tweets sentiment
@app.route("/sentiment", methods = ["POST"])
@swag_from(generate_swagger_doc(
    summary="Analyze sentiment of a tweet"
))
def sentiment():
    data = request.get_json()
    tweet = data.get("tweet")
    if not tweet:
        return jsonify({"error": "Missing tweet field"}), 400
    try:
        res = requests.post(f"{MODEL_SERVICE_URL}/predict", json={"tweet": tweet}, timeout=3)
        res.raise_for_status()
        pred = res.json().get("result")
        label = "positive" if pred == 1 else "negative"
        return jsonify({"tweet": tweet, "result": label})
    except requests.RequestException as e:
        return jsonify({"error": "model-service unreachable", "details": str(e)}), 502


    

#Get version
@app.route("/version", methods=["GET"])
@swag_from(generate_swagger_doc(
    summary= "Get current version of the app."
))
def version():
    version = VersionUtil.get_version()
    return jsonify({
        "app_version": version
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
