"""
url_checker.py
Runtime inference wrapper for the phishing URL detection ML model.
"""
import os
import joblib
from ml.train_url_model import extract_features

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")


class URLChecker:
    def __init__(self):
        model_path = os.path.join(MODEL_DIR, "url_model.pkl")
        if not os.path.exists(model_path):
            from ml.train_url_model import train_and_save
            train_and_save()
        self.model = joblib.load(model_path)

    def check(self, url: str):
        if not url or not url.strip():
            return None
        features = [extract_features(url.strip())]
        proba = self.model.predict_proba(features)[0]
        pred = self.model.predict(features)[0]
        confidence = float(proba[pred])
        verdict = "Suspicious / Likely Phishing" if pred == 1 else "Looks Safe"
        return {
            "url": url,
            "verdict": verdict,
            "is_suspicious": bool(pred == 1),
            "confidence": round(confidence * 100, 2),
        }


_checker_instance = None


def get_checker():
    global _checker_instance
    if _checker_instance is None:
        _checker_instance = URLChecker()
    return _checker_instance
