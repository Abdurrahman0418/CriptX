-- ============================================================
-- CriptX - AI-Powered Cybersecurity Awareness Chatbot
-- MySQL Database Schema
-- ============================================================
-- HOW TO USE:
--   1. Open MySQL Workbench / phpMyAdmin / the mysql CLI.
--   2. Run this entire file. It will create the `criptx_db`
--      database and all required tables.
--   3. Update `config.py` in the project with your MySQL
--      host/user/password if they differ from the defaults
--      (default assumes XAMPP/local MySQL: host=localhost,
--      user=root, password="").
--
-- CLI usage:
--   mysql -u root -p < mysql_schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS criptx_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE criptx_db;

-- ---------------- USERS ----------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(64) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------- CHAT HISTORY ----------------
CREATE TABLE IF NOT EXISTS chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    message TEXT,
    response TEXT,
    intent VARCHAR(100),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------- QUIZ QUESTIONS ----------------
CREATE TABLE IF NOT EXISTS quiz_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT,
    option_a VARCHAR(255),
    option_b VARCHAR(255),
    option_c VARCHAR(255),
    option_d VARCHAR(255),
    correct_index TINYINT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------- QUIZ SCORES ----------------
CREATE TABLE IF NOT EXISTS quiz_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    score INT,
    total INT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------- TIPS ----------------
CREATE TABLE IF NOT EXISTS tips (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tip_text TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------- FEEDBACK ----------------
CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    message TEXT,
    rating TINYINT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------- URL SCANS ----------------
CREATE TABLE IF NOT EXISTS url_scans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    url TEXT,
    verdict VARCHAR(100),
    confidence FLOAT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------- DEFAULT ADMIN ACCOUNT ----------------
-- The default admin account (admin@criptx.com / Admin@123) is created
-- automatically by the Python app the first time you run `python main.py`,
-- because its password hash uses a randomly generated per-account salt
-- (SHA-256(salt + password)) that must be computed at seed-time, not
-- hardcoded here. No manual insert is needed — just run the app once
-- after importing this schema.
