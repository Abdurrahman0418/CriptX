"""
nlp_engine.py
Runtime inference wrapper around the trained intent classification model.
Loads vectorizer + classifier + label encoder + response templates and
exposes a simple get_response(text) function used by the chat UI.
"""
import os
import random
import joblib
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")

CONFIDENCE_THRESHOLD = 0.28  # below this -> treat as "unknown"

CYBER_JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
    "There are only 10 types of people: those who understand binary and those who don't.",
    "I changed my password to 'incorrect' so whenever I forget it, my computer tells me 'Your password is incorrect.'",
    "Why did the hacker break up with the internet? Too many trust issues.",
    "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
    "Why don't hackers ever get cold? They always have a lot of firewalls.",
    "My password is the last 8 digits of pi. Good luck.",
    "Why was the phone afraid? It lost its Trust... and its 2FA.",
]

# Special intents that require a dynamically computed answer rather than a
# static templated response — this is what makes the assistant feel 'live'.
DYNAMIC_HANDLERS = {
    "get_time": lambda: f"🕒 The current time is {datetime.now().strftime('%I:%M %p')}.",
    "get_date": lambda: f"📅 Today's date is {datetime.now().strftime('%A, %d %B %Y')}.",
    "tell_joke": lambda: random.choice(CYBER_JOKES),
}


class IntentEngine:
    def __init__(self):
        vec_path = os.path.join(MODEL_DIR, "vectorizer.pkl")
        model_path = os.path.join(MODEL_DIR, "intent_model.pkl")
        enc_path = os.path.join(MODEL_DIR, "label_encoder.pkl")
        resp_path = os.path.join(MODEL_DIR, "responses_map.pkl")

        if not all(os.path.exists(p) for p in [vec_path, model_path, enc_path, resp_path]):
            from ml.train_intent_model import train_and_save
            train_and_save()

        self.vectorizer = joblib.load(vec_path)
        self.model = joblib.load(model_path)
        self.encoder = joblib.load(enc_path)
        self.responses_map = joblib.load(resp_path)

    def predict_intent(self, text: str):
        X = self.vectorizer.transform([text.lower()])
        probs = self.model.predict_proba(X)[0]
        best_idx = probs.argmax()
        confidence = probs[best_idx]
        tag = self.encoder.inverse_transform([best_idx])[0]
        if confidence < CONFIDENCE_THRESHOLD:
            tag = "unknown"
        return tag, float(confidence)

    def get_response(self, text: str):
        tag, confidence = self.predict_intent(text)

        if tag in DYNAMIC_HANDLERS:
            response = DYNAMIC_HANDLERS[tag]()
            return response, tag, confidence

        responses = self.responses_map.get(tag, self.responses_map.get("unknown"))
        response = random.choice(responses)
        return response, tag, confidence


_engine_instance = None


def get_engine():
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = IntentEngine()
    return _engine_instance
