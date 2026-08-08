"""
config.py
MySQL connection settings for CriptX.

Edit these values to match your MySQL server. Defaults below match a
typical local XAMPP/MySQL install (host=localhost, user=root, no password).
"""

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",          # <-- set your MySQL root/user password here
    "database": "criptx_db",
}

# Set to True to print SQL errors with full detail in the console (useful
# while setting up MySQL for the first time).
DEBUG_SQL = True
