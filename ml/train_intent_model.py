"""
train_intent_model.py
Trains a TF-IDF + LinearSVC (with probability calibration) text classification
model on the cybersecurity intents dataset, and saves the model + vectorizer
+ label encoder + responses map to /models for use by the chatbot at runtime.
"""
import json
import os
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import LabelEncoder

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "intents.json")
MODEL_DIR = os.path.join(BASE_DIR, "models")


def load_training_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    texts, labels = [], []
    responses_map = {}
    for intent in data["intents"]:
        tag = intent["tag"]
        responses_map[tag] = intent["responses"]
        for pattern in intent["patterns"]:
            texts.append(pattern.lower())
            labels.append(tag)
    return texts, labels, responses_map


def train_and_save():
    os.makedirs(MODEL_DIR, exist_ok=True)
    texts, labels, responses_map = load_training_data()

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), lowercase=True)
    X = vectorizer.fit_transform(texts)

    encoder = LabelEncoder()
    y = encoder.fit_transform(labels)

    base_clf = LinearSVC()
    clf = CalibratedClassifierCV(base_clf, cv=3)
    clf.fit(X, y)

    joblib.dump(vectorizer, os.path.join(MODEL_DIR, "vectorizer.pkl"))
    joblib.dump(clf, os.path.join(MODEL_DIR, "intent_model.pkl"))
    joblib.dump(encoder, os.path.join(MODEL_DIR, "label_encoder.pkl"))
    joblib.dump(responses_map, os.path.join(MODEL_DIR, "responses_map.pkl"))

    print(f"[OK] Intent model trained on {len(texts)} samples across {len(set(labels))} intents.")
    return clf, vectorizer, encoder, responses_map


if __name__ == "__main__":
    train_and_save()
