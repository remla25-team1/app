from flask import Flask, request, jsonify, send_from_directory, render_template

from versionutil import VersionUtil

import logging
import os
import requests

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


MODEL_SERVICE_URL = os.getenv("MODEL_SERVICE_URL")

@app.route("/")
def index():
    version = VersionUtil.get_version()  # Get version
    return render_template("index.html", version=version)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    logging.info(f"Received: {data}")
    logging.info(f"Version: {VersionUtil.get_version()}")

    try:
        # forward request to model-service
        response = requests.post(MODEL_SERVICE_URL, json=data)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        logger.error(f"Failed to contact model-service: {e}")
        return jsonify({"error": "Failed to contact model-service"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)