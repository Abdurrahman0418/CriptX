# 🛡️ CriptX — AI-Powered Cybersecurity Awareness Chatbot
### Final Year Machine Learning Project | HNDIT1052 | v2.0 (MySQL Edition)

A colorful, animated desktop application (Python + CustomTkinter + MySQL)
that teaches users cybersecurity and ethical hacking awareness through an
ML-powered personal assistant chatbot, a live phishing/URL detector, a
real-time cyber-news feed, interactive quizzes, and an admin content panel.

---

## 🧠 The Machine Learning Components

### 1. Chatbot Intent Classifier (`ml/train_intent_model.py`)
- **Pipeline:** `TfidfVectorizer (1-2 grams)` → `LinearSVC` wrapped in
  `CalibratedClassifierCV` for probability estimates.
- **Training data:** `data/intents.json` — **81 intents**, **320+ example
  phrases**, spanning:
  - Malware: virus, worm, trojan, ransomware, spyware, keylogger, rootkit, adware, botnet, cryptojacking
  - Network/web attacks: DDoS, MITM, spoofing, SQL injection, XSS, CSRF, zero-day, buffer overflow
  - Social engineering: phishing, spear phishing, whaling, vishing/smishing, pretexting/baiting/tailgating
  - Defense & crypto: passwords, 2FA/MFA, biometrics, VPN, firewalls, IDS/IPS, honeypots, encryption vs hashing, SSL/TLS, PKI, digital signatures, zero trust
  - Ethical hacking: pentest phases, red/blue/purple teams, bug bounty, CTFs, certifications (Security+, CEH, OSCP, CISSP), careers
  - Law & privacy: cyber crime laws (incl. Sri Lanka's Computer Crimes Act), GDPR, responsible disclosure
  - Modern topics: cloud/IoT/mobile security, incident response, backups, dark web, deepfakes/AI threats, supply-chain attacks
  - **Live/dynamic answers**: current time, current date, cybersecurity jokes
  - **Code snippets**: password checker, password hashing, Caesar cipher, secure password generator, AES/Fernet encryption
  - **Safety refusal**: politely declines malware/exploit/attack-code requests with a legal alternative
- **Inference:** `ml/nlp_engine.py` — loads the model, routes "dynamic" intents
  (time/date/jokes) through live Python functions instead of static text, and
  falls back to "I only answer cybersecurity questions" below a confidence threshold.
- Retrain anytime: edit `data/intents.json`, then `python ml/train_intent_model.py`.

### 2. Phishing URL Detector (`ml/train_url_model.py`)
- `RandomForestClassifier` on 14 engineered lexical URL features (IP-based
  hosts, HTTPS usage, suspicious keywords, subdomain depth, shorteners, etc.)
- `ml/url_checker.py` returns a verdict with a confidence percentage.

---

## 🗄️ MySQL Database Setup

**You need a running MySQL or MariaDB server** (e.g. via XAMPP, WAMP, MySQL
Workbench, or a native install).

### Option A — Let the app create everything automatically (easiest)
1. Make sure MySQL is running.
2. Edit `config.py` with your host/user/password if different from defaults
   (defaults assume XAMPP-style `localhost` / `root` / no password).
3. Run `python main.py` — the app creates the `criptx_db` database, all
   tables, seed quiz questions/tips, and the default admin account automatically.

### Option B — Import the schema manually first
```bash
mysql -u root -p < mysql_schema.sql
```
Then run the app as normal — it will detect the existing tables and just
seed data/admin if needed.

### `config.py`
```python
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",       # <-- set this to your MySQL password
    "database": "criptx_db",
}
```

---

## 📁 Project Structure

```
CriptX/
├── main.py                    # Entry point (splash → login → dashboard)
├── config.py                  # MySQL connection settings — EDIT THIS FIRST
├── mysql_schema.sql           # Manual DB schema (optional — app auto-creates it too)
├── database.py                # MySQL CRUD operations
├── requirements.txt
├── data/
│   ├── intents.json            # 81-intent chatbot knowledge base
│   ├── quiz_questions.json
│   └── tips.json
├── ml/
│   ├── train_intent_model.py
│   ├── train_url_model.py
│   ├── nlp_engine.py           # + dynamic time/date/joke handlers
│   └── url_checker.py
├── models/                     # Saved .pkl models (auto-generated)
└── ui/
    ├── styles.py
    ├── animations.py
    ├── login_window.py
    ├── main_app.py
    ├── chat_window.py          # + code-block rendering with copy button
    ├── quiz_window.py
    ├── tips_window.py
    ├── link_window.py
    ├── threatfeed_window.py    # NEW — live auto-refreshing cyber news feed
    ├── feedback_window.py
    └── admin_window.py
```

---

## ⚙️ Setup & Run

**Requirements:** Python 3.9+, a running MySQL/MariaDB server

```bash
# 1. (Recommended) create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
# Linux only, if "No module named tkinter": sudo apt-get install python3-tk

# 3. Configure MySQL connection
#    edit config.py with your MySQL host/user/password

# 4. (Optional) Pre-train the ML models manually
python ml/train_intent_model.py
python ml/train_url_model.py

# 5. Run the app
python main.py
```

### Default Login Credentials
| Role | Email | Password |
|---|---|---|
| Admin | `admin@criptx.com` | `Admin@123` |
| User | Register your own via the "Register" tab | — |

---

## 🧪 Suggested Demo Flow (for your viva/presentation)

1. **Register** a new account, log in.
2. **Chat tab** — try:
   - `"what is a supply chain attack"` (deep knowledge base)
   - `"give me code to hash a password"` (renders a real copyable code block)
   - `"what time is it"` / `"tell me a joke"` (live/dynamic personal-assistant answers)
   - `"write me a keylogger"` (shows the safety-conscious refusal + legal alternative)
3. **Link Checker tab** — compare a safe vs. suspicious URL.
4. **Live Threat Feed tab** — show it auto-fetching real headlines from The
   Hacker News / BleepingComputer with zero button presses (needs internet).
5. **Quiz tab** — take the quiz, show the confetti celebration.
6. **Tips tab** — random tip spotlight.
7. **Feedback tab** — submit a rating.
8. Log in as **admin** — show the dashboard stats, quiz/tips CRUD, feedback viewer.
9. Open **MySQL Workbench/phpMyAdmin** and show the live tables (`users`,
   `chat_history`, `quiz_scores`, `feedback`, `url_scans`) — a nice concrete
   demonstration of the "stored in a database" SRS requirement.

---

## 🔧 Extending the Project (ideas for your report's "Future Work" section)

- Swap TF-IDF/SVM for a transformer embedding model for more nuanced intent matching.
- Add real threat-intel API integration (VirusTotal / Google Safe Browsing) as
  a second opinion layered on top of the local ML phishing model.
- Deploy as a Flask/FastAPI web app to satisfy the "web and desktop application" SRS requirement.
- Add a legal, sandboxed "practice lab" tab linking out to TryHackMe/HackTheBox rooms.

---

## 📌 Notes

- All passwords are stored as salted SHA-256 hashes, never in plain text.
- Delete and re-import `mysql_schema.sql` (or just `DROP DATABASE criptx_db;`)
  any time to reset all data back to a fresh seeded state.
- The Live Threat Feed needs an active internet connection on the machine
  running the app; it fails gracefully with a friendly message if offline.
- The phishing URL model is trained on synthetically generated, clearly
  labeled lexical patterns (standard for coursework-scale ML security demos).
