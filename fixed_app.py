"""
Meridian Trust - SECURE (Fixed) Version
----------------------------------------
CodeAlpha Cyber Security Internship - Task 3 (remediated code).

Every vulnerability found in the original app.py has been fixed here.
Fictional bank, for educational use only.

Setup:
    pip install flask
    python fixed_app.py
"""

import os
import re
import sqlite3
from html import escape

from flask import Flask, request, redirect, send_from_directory, abort
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# FIX 3: secret comes from an environment variable, never hardcoded
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

DB_NAME = "users_secure.db"
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,30}$")


def get_db():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE,
                        password_hash TEXT)""")
    conn.commit()
    conn.close()


PAGE_SHELL = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} - Meridian Trust</title>
<style>
  :root {{
    --deep: #0F2E2A;
    --deep-2: #163F39;
    --gold: #C9A227;
    --paper: #FAF9F6;
    --ink: #1C2320;
    --muted: #5B6B66;
    --line: #DDE3DF;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: Georgia, "Times New Roman", serif;
    background: var(--paper);
    color: var(--ink);
  }}
  header.topbar {{
    background: var(--deep);
    color: #fff;
    padding: 18px 40px;
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .mark {{
    width: 34px; height: 34px;
    border-radius: 50%;
    background: var(--gold);
    display: flex; align-items: center; justify-content: center;
    color: var(--deep); font-weight: bold; font-size: 17px;
    font-family: Georgia, serif;
  }}
  .brand {{
    font-size: 20px;
    letter-spacing: 0.3px;
  }}
  main {{
    min-height: calc(100vh - 72px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
  }}
  .card {{
    background: #fff;
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 40px 44px;
    width: 100%;
    max-width: 420px;
    box-shadow: 0 12px 30px rgba(15,46,42,0.08);
  }}
  .card h1 {{
    margin: 0 0 6px;
    font-size: 26px;
    color: var(--deep);
  }}
  .card p.sub {{
    margin: 0 0 28px;
    color: var(--muted);
    font-family: Calibri, Arial, sans-serif;
    font-size: 14px;
  }}
  label {{
    display: block;
    font-family: Calibri, Arial, sans-serif;
    font-size: 13px;
    color: var(--deep-2);
    margin-bottom: 6px;
    margin-top: 18px;
  }}
  input {{
    width: 100%;
    padding: 11px 12px;
    border: 1px solid var(--line);
    border-radius: 6px;
    font-size: 15px;
    font-family: Calibri, Arial, sans-serif;
  }}
  input:focus {{
    outline: none;
    border-color: var(--deep-2);
  }}
  button {{
    width: 100%;
    margin-top: 26px;
    padding: 12px;
    background: var(--deep);
    color: #fff;
    border: none;
    border-radius: 6px;
    font-size: 15px;
    font-family: Calibri, Arial, sans-serif;
    cursor: pointer;
  }}
  button:hover {{ background: var(--deep-2); }}
  .switch {{
    margin-top: 22px;
    text-align: center;
    font-family: Calibri, Arial, sans-serif;
    font-size: 13.5px;
    color: var(--muted);
  }}
  .switch a {{ color: var(--deep-2); text-decoration: none; font-weight: bold; }}
  .result-card {{ text-align: center; }}
  .result-card .badge {{
    width: 56px; height: 56px; border-radius: 50%;
    background: var(--gold); color: var(--deep);
    display: flex; align-items: center; justify-content: center;
    font-size: 26px; margin: 0 auto 18px;
  }}
  .balance {{
    font-size: 34px; color: var(--deep); margin: 4px 0 2px;
  }}
  .balance-label {{
    font-family: Calibri, Arial, sans-serif;
    font-size: 12.5px; color: var(--muted);
    letter-spacing: 0.5px;
  }}
  .error {{
    color: #9A2B2B;
    font-family: Calibri, Arial, sans-serif;
    font-size: 14px;
    background: #FBEAEA;
    border: 1px solid #EFC9C9;
    padding: 12px 14px;
    border-radius: 6px;
    margin-top: 18px;
  }}
</style>
</head>
<body>
<header class="topbar">
  <div class="mark">M</div>
  <div class="brand">Meridian Trust</div>
</header>
<main>
  <div class="card {card_class}">
    {content}
  </div>
</main>
</body>
</html>
"""

def render_page(title, content, card_class=""):
    return PAGE_SHELL.format(title=title, content=content, card_class=card_class)


FORM = """
    <h1>{heading}</h1>
    <p class="sub">{sub}</p>
    {error}
    <form method="post">
        <label>Username</label>
        <input name="username" autocomplete="off" maxlength="30">
        <label>Password</label>
        <input name="password" type="password" maxlength="128">
        <button type="submit">{button}</button>
    </form>
    <div class="switch">{switch}</div>
"""


@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # FIX: input validation
        if not USERNAME_RE.match(username):
            error = '<div class="error">Username must be 3-30 letters, numbers or underscores.</div>'
        elif len(password) < 8:
            error = '<div class="error">Password must be at least 8 characters.</div>'
        else:
            conn = get_db()
            try:
                # FIX 1: parameterized query + FIX 4: hashed password
                conn.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                conn.commit()
                return redirect("/login")
            except sqlite3.IntegrityError:
                error = '<div class="error">That username is already taken.</div>'
            finally:
                conn.close()

    return render_page("Open an account", FORM.format(
        heading="Open an account", sub="Join Meridian Trust in under a minute.",
        error=error, button="Create account",
        switch='Already with us? <a href="/login">Sign in</a>'))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        conn = get_db()
        # FIX 1: parameterized query
        row = conn.execute(
            "SELECT password_hash FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        # FIX 4: compare against the stored hash
        if row and check_password_hash(row[0], password):
            # FIX 2: escape user-controlled data before putting it in HTML
            content = (
                '<div class="badge">&#10003;</div>'
                '<h1 style="text-align:center;">Welcome back, ' + escape(username) + '</h1>'
                '<p class="sub" style="text-align:center;">Your account overview</p>'
                '<p class="balance-label" style="text-align:center;">AVAILABLE BALANCE</p>'
                '<p class="balance" style="text-align:center;">$12,480.55</p>'
            )
            return render_page("Account overview", content, card_class="result-card")
        error = '<div class="error">Incorrect username or password.</div>'

    return render_page("Sign in", FORM.format(
        heading="Sign in", sub="Access your Meridian Trust account.",
        error=error, button="Sign in",
        switch='New here? <a href="/register">Open an account</a>'))


@app.route("/profile-pic")
def profile_pic():
    filename = request.args.get("file", "")
    # FIX 6: only allow simple filenames from the uploads folder (blocks ../ traversal)
    if not re.match(r"^[A-Za-z0-9_.-]+$", filename) or ".." in filename:
        abort(400)
    if not os.path.isfile(os.path.join(UPLOAD_DIR, filename)):
        # FIX 5: generic error, no internal details leaked
        return render_page("Document unavailable",
                           '<h1>Document unavailable</h1><div class="error">We could not find that file.</div>'), 404
    return send_from_directory(UPLOAD_DIR, filename)


if __name__ == "__main__":
    init_db()
    # FIX 7: debug off, bound to localhost only
    app.run(debug=False, host="127.0.0.1")
