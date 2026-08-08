import os
from datetime import datetime, timezone
from pathlib import Path

import mysql.connector
from flask import Flask, jsonify, request, render_template, g, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
SITE_DIR = BASE_DIR.parent

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "guardian123"),
    "database": os.environ.get("DB_NAME", "guardian"),
}

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

ALLOWED_ORIGINS = {
    "http://localhost:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5000",
    "https://sinaypradhan.github.io",
}


@app.after_request
def add_cors_headers(resp):
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Vary"] = "Origin"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


def get_db():
    if "db" not in g:
        g.db = mysql.connector.connect(**DB_CONFIG)
        g.db.autocommit = False
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
    )
    cur = db.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS guardian.messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.commit()
    cur.close()
    db.close()


@app.route("/")
def index():
    return send_from_directory(SITE_DIR, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(SITE_DIR, filename)


@app.route("/api/messages", methods=["POST"])
def create_message():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    message = (data.get("message") or "").strip()

    if not name or not email or not message:
        return jsonify({"error": "All fields are required."}), 400

    if "@" not in email or "." not in email:
        return jsonify({"error": "Please enter a valid email address."}), 400

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO messages (name, email, message) VALUES (%s, %s, %s)",
        (name, email, message),
    )
    db.commit()
    new_id = cur.lastrowid
    cur.close()

    return jsonify({"ok": True, "id": new_id}), 201


@app.route("/api/messages", methods=["GET"])
def list_messages():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(
        "SELECT id, name, email, message, created_at FROM messages ORDER BY id DESC"
    )
    rows = cur.fetchall()
    cur.close()
    return jsonify(rows)


@app.route("/admin")
def admin():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(
        "SELECT id, name, email, message, created_at FROM messages ORDER BY id DESC"
    )
    rows = cur.fetchall()
    cur.close()
    return render_template("admin.html", messages=rows)


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
