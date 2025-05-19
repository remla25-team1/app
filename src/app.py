from flask import Flask, jsonify, request, send_from_directory
from flasgger import Swagger,swag_from
from swagger_template import generate_swagger_doc
from versionutil import VersionUtil
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Gauge, Histogram
import requests
import os
import json

app = Flask(__name__, static_folder="static", template_folder="template")
swagger = Swagger(app) 
APP_VERSION = os.environ.get("APP_VERSION", "0.0.0")
PORT = int(os.environ.get("PORT", 8080))
MODEL_SERVICE_HOST = os.getenv("MODEL_SERVICE_HOST", "localhost")
MODEL_SERVICE_PORT = os.getenv("MODEL_SERVICE_PORT", 8081)
MODEL_SERVICE_URL = f"http://{MODEL_SERVICE_HOST}:{MODEL_SERVICE_PORT}"
MODEL_SERVICE_VERSION = os.environ.get("MODEL_SERVICE_VERSION", "0.0.0")

metrics = PrometheusMetrics(app, path='/metrics')
metrics.info('app_info', 'app info', version=APP_VERSION, model_version=MODEL_SERVICE_VERSION)
sentiment_prediction_counter = Counter(
    'sentiment_requests_total', 
    'Total number of sentiment prediction',
    ['prediction']
)

in_progress_gauge = Gauge(
    'sentiment_requests_in_progress', 
    'Number of /sentiment requests in progress',
    ['model_version']
)

sentiment_response_time_hist = Histogram(
    'sentiment_response_time_seconds', 
    'Histogram of /sentiment response time',
    ['model_version'],
    buckets=[0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0]

)

correction_request_counter = Counter(
    'correction_requests_total', 
    'Total number of /correction requests',
    ['correction', 'prediction']
)



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
    model_version = MODEL_SERVICE_VERSION
    label = "unknown"
    with in_progress_gauge.labels(model_version=model_version).track_inprogress():
        with sentiment_response_time_hist.labels(model_version=model_version).time():
            try:
                res = requests.post(f"{MODEL_SERVICE_URL}/predict", json={"tweet": tweet}, timeout=3)
                res.raise_for_status()
                pred = res.json().get("result")
                label = "positive" if pred == 1 else "negative"
                label.labels(prediction=label).inc()
                return jsonify({"tweet": tweet, "result": label})
            except requests.RequestException as e:
                return jsonify({"error": "model-service unreachable", "details": str(e), "model_service_url": MODEL_SERVICE_URL }), 502



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
    correction_request_counter(correction = correction, prediction = prediction).inc()
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
    response_example={"lib_version": "v0.1.0",
                      "app_version": "v0.1.0",
                      "ml_version" : "v0.1.0",},
    has_body=False
))
def version():
    lib_version = VersionUtil.get_version()
    return jsonify({
        "lib_version": lib_version,
        "app_version": APP_VERSION,
        "model_version" : MODEL_SERVICE_VERSION
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug = True)
