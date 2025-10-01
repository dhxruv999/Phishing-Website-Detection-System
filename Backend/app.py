import os
from flask_cors import CORS
import joblib
import warnings
from flask import Flask, request, jsonify
import socket

app = Flask(__name__)
CORS(app, resources={r"/predict": {"origins": "http://localhost:3000"}})


# Load model and vectorizer safely
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, "Phishing-URL-Identifier.pkl")
vectorizer_path = os.path.join(BASE_DIR, "vectorizer.pkl")

try:
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    print("Model and vectorizer loaded successfully!")
except FileNotFoundError:
    print(f"Model or vectorizer file not found in {BASE_DIR}")
    exit(1)

# API endpoint for prediction


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Transform URL and predict
    features = vectorizer.transform([url])
    prediction = model.predict(features)[0]
    result = "Phishing" if prediction == 1 else "Safe"

    return jsonify({"url": url, "prediction": result})


# Function to find a free port
def find_free_port(start_port=5000):
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
            port += 1


# Run Flask app
if __name__ == "__main__":
    free_port = find_free_port(5000)
    app.run(debug=True, port=free_port)
