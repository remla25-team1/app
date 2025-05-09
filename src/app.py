from flask import Flask, jsonify, request, send_from_directory
from flasgger import Swagger,swag_from
from swagger_template import generate_swagger_doc
from versionutil import VersionUtil
import requests
import os
import json

app = Flask(__name__, static_folder="static", template_folder="template")
swagger = Swagger(app) 

MODEL_SERVICE_URL = os.getenv("MODEL_SERVICE_URL", "http://localhost:8080")


@app.route("/")
def serve_index():
    return send_from_directory(app.template_folder, "index.html")

# Analyze tweets sentiment
@app.route("/sentiment", methods = ["POST"])
@swag_from(generate_swagger_doc(
    summary="Analyze sentiment of a tweet",
    request_example= {"tweet": "Hello World!"},
    response_example= {"result": "positive"},
    required_fields=["tweet"]
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


@app.route("/correction", methods = ["POST"])
@swag_from(generate_swagger_doc(
    summary= "Collect the correction from users.",
    request_example= {"tweet": "Hello World!",
                      "prediction": "negative",
                      "correction": "positive",},
    response_example={"status": "received"},                  
    required_fields=["tweet", "prediction", "correction"]
                    ))
def collect_corrections():
    data = request.get_json()
    tweet = data.get("tweet")
    prediction = data.get("prediction")
    correction = data.get("correction")

    if not all([tweet, prediction, correction]):
        return jsonify({"error": "Missing fields"}), 400

    record = {
        "tweet": tweet,
        "prediction": prediction,
        "correction": correction,
    }
    with open("corrections.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")

    return "", 200


def get_ml_version():
    res = requests.get(f"{MODEL_SERVICE_URL}/version")
    return res.json().get("version", "unknown")
    

#Get version
@app.route("/version", methods=["GET"])
@swag_from(generate_swagger_doc(
    summary= "Get current version of the app and machine learning model.",
    response_example={"app_version": "v0.1.0",
                      "ml_version" : "v0.1.0"},
    has_body=False
))
def version():
    app_version = VersionUtil.get_version()
    ml_version = get_ml_version()
    return jsonify({
        "app_version": app_version,
        "ml_version" : ml_version
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
