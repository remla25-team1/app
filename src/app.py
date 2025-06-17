from flask import Flask, jsonify, request, send_from_directory, Response
from versionutil import VersionUtil
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
import requests
import os
import json

app = Flask(__name__, static_folder="static", template_folder="template")
APP_VERSION = os.environ.get("APP_VERSION", "0.0.0")
PORT = int(os.environ.get("PORT", 8080))
MODEL_SERVICE_HOST = os.getenv("MODEL_SERVICE_HOST", "localhost")
MODEL_SERVICE_PORT = os.getenv("MODEL_SERVICE_PORT", "8081")
MODEL_SERVICE_URL = f"http://{MODEL_SERVICE_HOST}:{MODEL_SERVICE_PORT}"


# Get model service version
def get_ml_version():
    """
    Retrieve the version of the model service by making a GET request to its /version endpoint.
    """
    res = requests.get(f"{MODEL_SERVICE_URL}/version", timeout=3)
    return res.json().get("version", "unknown")

model_service_version = get_ml_version()

metrics = PrometheusMetrics(app, path=None)
metrics.info('app_info', 'app info', version=APP_VERSION, model_version=model_service_version)

@app.route("/metrics")
def metrics_endpoint():
    """
    Exposes Prometheus metrics for monitoring.
    ---
    tags:
      - Metrics
    summary: Expose Prometheus metrics
    description: Returns the metrics in a format that Prometheus can scrape.
    responses:
      200:
        description: Prometheus metrics in text format.
        content:
          text/plain:
            schema:
              type: string
              example: |
                # HELP app_info app info
                # TYPE app_info gauge
                app_info{version="0.1.0",model_version="1.0.0"} 1.0
                # HELP sentiment_requests_total Total number of sentiment prediction
                # TYPE sentiment_requests_total counter
                sentiment_requests_total{prediction="positive"} 100
                sentiment_requests_total{prediction="negative"} 50
                # HELP sentiment_requests_in_progress Number of /sentiment requests in progress
                # TYPE sentiment_requests_in_progress gauge
                sentiment_requests_in_progress{model_version="1.0.0",app_version="0.1.0"} 5
                sentiment_requests_in_progress{model_version="1.0.0",app_version="0.1.0"} 3
    """
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


sentiment_prediction_counter = Counter(
    'sentiment_requests_total', 
    'Total number of sentiment prediction',
    ['prediction', "app_version", 'source'],
)

in_progress_gauge = Gauge(
    'sentiment_requests_in_progress', 
    'Number of /sentiment requests in progress',
    ['model_version', 'app_version']
)

sentiment_response_time_hist = Histogram(
    'sentiment_response_time_seconds', 
    'Histogram of /sentiment response time',
    ['model_version','source', 'app_version'],
    buckets=[0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0]
)


correction_request_counter = Counter(
    'correction_requests_total', 
    'Total number of /correction requests',
    ['correction', 'prediction','model_version', 'app_version']
)



@app.route("/")
def serve_index():
    """ 
    Serve the index.html file.
    ---
    tags:      - Index
    summary: Serve the index.html file
    description: Returns the index.html file from the template folder.
    responses:
      200:
        description: The index.html file.
        content:
          text/html:
            schema:
              type: string
              example: "<!DOCTYPE html> <html>...</html>"
    """
    return send_from_directory(app.template_folder, "index.html")

# Analyze tweets sentiment
@app.route("/sentiment", methods = ["POST"])
def sentiment():
    """
    Analyze sentiment of a tweet.
    ---
    tags:
      - Sentiment
    summary: Analyze sentiment of a tweet
    description: Returns the sentiment (positive/negative) of the given tweet using the model-service.
    consumes:
      - application/json
    parameters:
      - name: input_data
        in: body
        description: tweet to be classified.
        required: True
        schema:
          type: object
          required: tweet
          properties:
            tweet:
              type: string
              example: Hello World!
    responses:
      200:
        description: The result of the classification: 'positive' or 'negative'.
    """
    data = request.get_json()
    tweet = data.get("tweet")
    if not tweet:
        return jsonify({"error": "Missing tweet field"}), 400
    label = "unknown"
    with in_progress_gauge.labels(model_version=model_service_version, app_version=APP_VERSION).track_inprogress():
        with sentiment_response_time_hist.labels(model_version=model_service_version, app_version=APP_VERSION, source="model").time():
            try:
                res = requests.post(f"{MODEL_SERVICE_URL}/predict", json={"tweet": tweet}, timeout=3)
                res.raise_for_status()
                pred = res.json().get("result")
                label = "positive" if pred == 1 else "negative"
                sentiment_prediction_counter.labels(prediction=label, app_version = APP_VERSION, source = "model").inc()
                return jsonify({"tweet": tweet, "result": label})
            except requests.RequestException as e:
                return jsonify({"error": "model-service unreachable", "details": str(e), "model_service_url": MODEL_SERVICE_URL }), 502



@app.route("/correction", methods = ["POST"])
def collect_corrections():
    """
    Collect the correction from users.
    ---
    tags:
      - Correction
    summary: Collect the correction from users.
    description: Collects user feedback on prediction corrections.
    consumes:
      - application/json
    parameters:
      - name: input_data
        in: body
        description: Correction data from user.
        required: True
        schema:
          type: object
          required:
            - tweet
            - prediction
            - correction
          properties:
            tweet:
              type: string
              example: Hello World!
            prediction:
              type: string
              example: negative
            correction:
              type: string
              example: positive
    responses:
      200:
        description: Correction received successfully.
    """
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
    correction_request_counter.labels(correction = correction, prediction = prediction, app_version = APP_VERSION, model_version = model_service_version).inc()
    with open("corrections.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    return "", 200
    

#Get version
@app.route("/version", methods=["GET"])
def version():
    """
    Get current version of the app and machine learning model.
    ---
    tags:
      - Version
    summary: Get current version of the app and machine learning model.
    description: Returns the version information for the app, library, and model-service.
    responses:
      200:
        description: Version info retrieved successfully
        content:
          application/json:
            example:
              lib_version: v0.1.0
              app_version: v0.1.0
              ml_version: v0.1.0
    """
    lib_version = VersionUtil.get_version()
    return jsonify({
        "lib_version": lib_version,
        "app_version": APP_VERSION,
        "model_version" : model_service_version
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug = True)
