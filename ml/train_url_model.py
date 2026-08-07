"""
train_url_model.py
Trains a RandomForest classifier on engineered lexical URL features
(length, dots, hyphens, digits, presence of IP address, https usage,
suspicious keywords, subdomain depth, etc.) to detect likely-phishing
URLs. This mirrors published academic approaches (e.g., "Phishing
Websites Features" datasets) using a labeled training set built from
well-known safe domains vs. classic phishing-style URL patterns.
"""
import os
import re
import random
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")

SUSPICIOUS_WORDS = [
    "login", "verify", "update", "secure", "account", "banking", "confirm",
    "signin", "webscr", "ebayisapi", "password", "suspend", "unlock",
    "alert", "billing", "invoice", "urgent", "click", "free", "bonus"
]

LEGIT_DOMAINS = [
    "google.com", "microsoft.com", "apple.com", "amazon.com", "wikipedia.org",
    "github.com", "linkedin.com", "facebook.com", "youtube.com", "netflix.com",
    "bankofceylon.lk", "peoplesbank.lk", "sliate.ac.lk", "gov.lk", "who.int",
    "python.org", "stackoverflow.com", "reddit.com", "twitter.com", "office.com",
    "dropbox.com", "adobe.com", "paypal.com", "spotify.com", "cisa.gov"
]


def extract_features(url: str) -> list:
    """Extract lexical/statistical features from a URL string."""
    url_l = url.lower()
    length = len(url)
    num_dots = url.count(".")
    num_hyphens = url.count("-")
    num_digits = sum(c.isdigit() for c in url)
    num_at = url.count("@")
    num_subdomains = max(url_l.split("//")[-1].split("/")[0].count(".") - 1, 0)
    has_ip = 1 if re.search(r"(\d{1,3}\.){3}\d{1,3}", url) else 0
    has_https = 1 if url_l.startswith("https://") else 0
    has_suspicious_word = 1 if any(w in url_l for w in SUSPICIOUS_WORDS) else 0
    has_port = 1 if re.search(r":\d{2,5}(/|$)", url) else 0
    path_len = len(url.split("/", 3)[-1]) if url.count("/") >= 3 else 0
    count_www = url_l.count("www")
    has_double_slash_redirect = 1 if url.rfind("//") > 7 else 0
    url_shortener = 1 if any(s in url_l for s in
                              ["bit.ly", "tinyurl", "t.co", "goo.gl", "ow.ly", "is.gd"]) else 0

    return [
        length, num_dots, num_hyphens, num_digits, num_at, num_subdomains,
        has_ip, has_https, has_suspicious_word, has_port, path_len,
        count_www, has_double_slash_redirect, url_shortener
    ]


def generate_synthetic_dataset(n_per_class=250, seed=42):
    """
    Build a labeled training set:
      label 0 = legitimate-style URL
      label 1 = phishing-style URL (classic academic phishing-URL patterns:
                IP-based hosts, suspicious keywords, excessive subdomains,
                url shorteners, no HTTPS, '@' redirection tricks, etc.)
    """
    random.seed(seed)
    X, y = [], []

    # Legitimate-style URLs
    paths = ["", "/home", "/products", "/about", "/docs", "/blog/post-1",
              "/user/profile", "/search?q=cybersecurity", "/en/index.html"]
    for _ in range(n_per_class):
        domain = random.choice(LEGIT_DOMAINS)
        path = random.choice(paths)
        prefix = random.choice(["https://www.", "https://"])
        url = f"{prefix}{domain}{path}"
        X.append(extract_features(url))
        y.append(0)

    # Phishing-style URLs (synthetic patterns based on well-documented indicators)
    suspicious_templates = [
        "http://{ip}/{word}/login.php",
        "http://{brand}-{word}.{tld}/{word}",
        "https://{brand}.{word}-verify.{tld}/account",
        "http://{word}.{brand}.{tld2}.{tld}/secure",
        "http://bit.ly/{rand}",
        "https://{brand}security-{word}.{tld}/{word}/{word}",
        "http://{ip}:8080/{word}",
        "https://{word}@{brand}.{tld}/login",
    ]
    brands = ["paypal", "bankofceylon", "appleid", "microsoft-support", "amazon-secure", "netflix"]
    tlds = ["com", "net", "info", "xyz", "top", "tk"]

    for _ in range(n_per_class):
        tmpl = random.choice(suspicious_templates)
        ip = ".".join(str(random.randint(1, 255)) for _ in range(4))
        url = tmpl.format(
            ip=ip,
            brand=random.choice(brands),
            word=random.choice(SUSPICIOUS_WORDS),
            tld=random.choice(tlds),
            tld2=random.choice(["secure", "id", "auth"]),
            rand="".join(random.choices("abcdefgh12345", k=6)),
        )
        X.append(extract_features(url))
        y.append(1)

    return np.array(X), np.array(y)


def train_and_save():
    os.makedirs(MODEL_DIR, exist_ok=True)
    X, y = generate_synthetic_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
    clf.fit(X_train, y_train)

    preds = clf.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"[OK] URL phishing detector trained. Test accuracy: {acc:.2%}")

    joblib.dump(clf, os.path.join(MODEL_DIR, "url_model.pkl"))
    return clf


if __name__ == "__main__":
    train_and_save()
