import os
from flask_cors import CORS
import pickle
from flask import Flask, request, jsonify
import socket
from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import SnowballStemmer

app = Flask(__name__)
CORS(app, resources={r"/predict": {"origins": "http://localhost:3000"}})


# Data Preprocessing function
def preprocess_url(url):
    tokenizer = RegexpTokenizer(r'[A-Za-z]+')
    stemmer = SnowballStemmer("english")

    tokens = tokenizer.tokenize(url)
    stemmed_tokens = [stemmer.stem(word) for word in tokens]
    return ' '.join(stemmed_tokens)


# Load ML model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "model.pkl")

try:
    with open(model_path, "rb") as f:
        vectorizer, model = pickle.load(f)
    print("Model and vectorizer loaded successfully!")
except FileNotFoundError:
    print(f"Pickle file not found in {BASE_DIR}")
    exit(1)
except Exception as e:
    print(f"Error loading pickle: {e}")
    exit(1)


# API endpoint for prediction
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # Apply the SAME preprocessing as training
        processed_url = preprocess_url(url)

        # Transform using vectorizer and predict
        features = vectorizer.transform([processed_url])
        prediction = model.predict(features)[0]

        # Map model output to readable labels
        result = "Phishing" if prediction == "bad" else "Safe"

        return jsonify({"url": url, "prediction": result})
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {e}"}), 500


# Find a free port
def find_free_port(start_port=5000):
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
            port += 1


# Run Flask server
if __name__ == "__main__":
    free_port = find_free_port(5000)
    app.run(debug=True, port=free_port)
