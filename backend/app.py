import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request, render_template, g, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
SITE_DIR = BASE_DIR.parent
DB_PATH = BASE_DIR / "messages.db"

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
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )
    db.commit()
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
    cur = db.execute(
        "INSERT INTO messages (name, email, message, created_at) VALUES (?, ?, ?, ?)",
        (name, email, message, datetime.now(timezone.utc).isoformat()),
    )
    db.commit()

    return jsonify({"ok": True, "id": cur.lastrowid}), 201


@app.route("/api/messages", methods=["GET"])
def list_messages():
    db = get_db()
    rows = db.execute(
        "SELECT id, name, email, message, created_at FROM messages ORDER BY id DESC"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/admin")
def admin():
    db = get_db()
    rows = db.execute(
        "SELECT id, name, email, message, created_at FROM messages ORDER BY id DESC"
    ).fetchall()
    return render_template("admin.html", messages=[dict(r) for r in rows])


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
