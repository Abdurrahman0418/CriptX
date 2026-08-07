"""
database.py
Handles all MySQL database operations for CriptX:
users, chat_history, quiz_scores, feedback, tips, quiz_questions, url_scans

Requires a MySQL/MariaDB server running and the schema imported from
`mysql_schema.sql` (or it will be auto-created on first run via init_db()).
Connection settings are read from config.py.
"""
import hashlib
import os
import json
import secrets

import mysql.connector

from config import DB_CONFIG, DEBUG_SQL

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def get_connection(with_db=True):
    """Open a new MySQL connection. If with_db is False, connects to the
    server without selecting a database (used to create the DB itself)."""
    cfg = dict(DB_CONFIG)
    if not with_db:
        cfg.pop("database", None)
    try:
        conn = mysql.connector.connect(**cfg)
        return conn
    except mysql.connector.Error as err:
        if DEBUG_SQL:
            print(f"[MySQL ERROR] {err}")
        raise


def hash_password(password: str, salt: str = None) -> tuple:
    """Return (hash, salt) using SHA-256 with a random salt."""
    if salt is None:
        salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return h, salt


def init_db():
    """Create the database (if missing) and all tables, then seed
    quiz questions / tips / default admin account if empty."""
    try:
        conn = get_connection(with_db=False)
        cur = conn.cursor()
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} "
            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        conn.commit()
        cur.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"[MySQL ERROR] Could not create database automatically: {err}")
        print("Please ensure your MySQL server is running and config.py is correct,")
        print("or manually import mysql_schema.sql.")
        raise

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(150) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            salt VARCHAR(64) NOT NULL,
            role ENUM('user', 'admin') DEFAULT 'user',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            message TEXT,
            response TEXT,
            intent VARCHAR(100),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            question TEXT,
            option_a VARCHAR(255),
            option_b VARCHAR(255),
            option_c VARCHAR(255),
            option_d VARCHAR(255),
            correct_index TINYINT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_scores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            score INT,
            total INT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tips (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tip_text TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            message TEXT,
            rating TINYINT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS url_scans (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            url TEXT,
            verdict VARCHAR(100),
            confidence FLOAT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM quiz_questions")
    if cur.fetchone()[0] == 0:
        seed_quiz_questions(conn)

    cur.execute("SELECT COUNT(*) FROM tips")
    if cur.fetchone()[0] == 0:
        seed_tips(conn)

    cur.execute("SELECT * FROM users WHERE email = %s", ("admin@criptx.com",))
    if cur.fetchone() is None:
        h, salt = hash_password("Admin@123")
        cur.execute(
            """INSERT INTO users (full_name, email, password_hash, salt, role)
               VALUES (%s,%s,%s,%s,%s)""",
            ("System Admin", "admin@criptx.com", h, salt, "admin"),
        )
        conn.commit()

    cur.close()
    conn.close()


def seed_quiz_questions(conn):
    path = os.path.join(DATA_DIR, "quiz_questions.json")
    with open(path, "r", encoding="utf-8") as f:
        questions = json.load(f)
    cur = conn.cursor()
    for q in questions:
        cur.execute(
            """INSERT INTO quiz_questions
               (question, option_a, option_b, option_c, option_d, correct_index)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            (q["question"], q["options"][0], q["options"][1],
             q["options"][2], q["options"][3], q["answer"]),
        )
    conn.commit()
    cur.close()


def seed_tips(conn):
    path = os.path.join(DATA_DIR, "tips.json")
    with open(path, "r", encoding="utf-8") as f:
        tips = json.load(f)
    cur = conn.cursor()
    for t in tips:
        cur.execute("INSERT INTO tips (tip_text) VALUES (%s)", (t,))
    conn.commit()
    cur.close()


# ---------------- USER OPERATIONS ----------------

def register_user(full_name, email, password):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cur.fetchone() is not None:
        cur.close()
        conn.close()
        return False, "This account already exists, please Login."
    h, salt = hash_password(password)
    cur.execute(
        """INSERT INTO users (full_name, email, password_hash, salt, role)
           VALUES (%s,%s,%s,%s,%s)""",
        (full_name, email, h, salt, "user"),
    )
    conn.commit()
    cur.close()
    conn.close()
    return True, "Registration successful!"


def login_user(email, password):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row is None:
        return False, "Wrong Email or Password", None
    h, _ = hash_password(password, row["salt"])
    if h != row["password_hash"]:
        return False, "Wrong Email or Password", None
    return True, "Login successful", dict(row)


# ---------------- CHAT HISTORY ----------------

def save_chat(user_id, message, response, intent):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO chat_history (user_id, message, response, intent)
           VALUES (%s,%s,%s,%s)""",
        (user_id, message, response, intent),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_chat_history(user_id, limit=50):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM chat_history WHERE user_id=%s ORDER BY id DESC LIMIT %s",
        (user_id, limit),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return list(reversed(rows))


# ---------------- QUIZ ----------------

def get_all_quiz_questions():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM quiz_questions")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def add_quiz_question(question, options, correct_index):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO quiz_questions
           (question, option_a, option_b, option_c, option_d, correct_index)
           VALUES (%s,%s,%s,%s,%s,%s)""",
        (question, options[0], options[1], options[2], options[3], correct_index),
    )
    conn.commit()
    cur.close()
    conn.close()


def delete_quiz_question(qid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM quiz_questions WHERE id=%s", (qid,))
    conn.commit()
    cur.close()
    conn.close()


def save_quiz_score(user_id, score, total):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO quiz_scores (user_id, score, total) VALUES (%s,%s,%s)",
        (user_id, score, total),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_quiz_scores(user_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM quiz_scores WHERE user_id=%s ORDER BY id DESC", (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ---------------- TIPS ----------------

def get_all_tips():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tips")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def add_tip(text):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO tips (tip_text) VALUES (%s)", (text,))
    conn.commit()
    cur.close()
    conn.close()


def delete_tip(tip_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tips WHERE id=%s", (tip_id,))
    conn.commit()
    cur.close()
    conn.close()


# ---------------- FEEDBACK ----------------

def save_feedback(user_id, message, rating):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO feedback (user_id, message, rating) VALUES (%s,%s,%s)",
        (user_id, message, rating),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_all_feedback():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT feedback.*, users.full_name, users.email FROM feedback
        LEFT JOIN users ON feedback.user_id = users.id
        ORDER BY feedback.id DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ---------------- URL SCANS ----------------

def save_url_scan(user_id, url, verdict, confidence):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO url_scans (user_id, url, verdict, confidence) VALUES (%s,%s,%s,%s)",
        (user_id, url, verdict, confidence),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_url_scan_history(user_id, limit=20):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM url_scans WHERE user_id=%s ORDER BY id DESC LIMIT %s",
        (user_id, limit),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ---------------- ADMIN STATS ----------------

def get_stats():
    conn = get_connection()
    cur = conn.cursor()
    stats = {}
    cur.execute("SELECT COUNT(*) FROM users WHERE role='user'")
    stats["total_users"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM chat_history")
    stats["total_chats"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM quiz_scores")
    stats["total_quiz_attempts"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM url_scans")
    stats["total_url_scans"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM feedback")
    stats["total_feedback"] = cur.fetchone()[0]
    cur.close()
    conn.close()
    return stats
