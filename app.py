
"""
Meridian Trust — Intentionally Vulnerable Demo Banking App
-------------------------------------------------------------
CodeAlpha Cyber Security Internship — Task 3 practice material.
 
"Meridian Trust" is a FICTIONAL bank created only to give this security
review a realistic, professional look. It is not affiliated with any
real financial institution.
 
This app is deliberately INSECURE. It contains several real, common
vulnerabilities planted on purpose so they can be found, documented,
and fixed as part of a Secure Coding Review. Do not deploy this
anywhere public — local learning use only.
 
Setup:
    pip install flask
    python app.py
Then visit http://127.0.0.1:5000/register
"""
 
from flask import Flask, request, render_template_string, redirect
import sqlite3
 
app = Flask(__name__)
 
# --- Bug hint area: look closely at how this app handles secrets, ---
# --- user input, passwords, errors, and file access. ---
 
SECRET_KEY = "sk_live_supersecret12345"  # <-- something looks off here
 
DB_NAME = "users.db"
 
 
def get_db():
    conn = sqlite3.connect(DB_NAME)
    return conn
 
 
def init_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT,
                        password TEXT)""")
    conn.commit()
    conn.close()
 
 
# ---------------------------------------------------------------------
# Shared page shell — professional banking look for every page
# ---------------------------------------------------------------------
 
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
 
 
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
 
        conn = get_db()
        # Bug hint: how is this query being built?
        query = "INSERT INTO users (username, password) VALUES ('%s', '%s')" % (username, password)
        conn.execute(query)
        conn.commit()
        conn.close()
        return redirect("/login")
 
    content = """
        <h1>Open an account</h1>
        <p class="sub">Join Meridian Trust in under a minute.</p>
        <form method="post">
            <label>Username</label>
            <input name="username" autocomplete="off">
            <label>Password</label>
            <input name="password" type="password">
            <button type="submit">Create account</button>
        </form>
        <div class="switch">Already with us? <a href="/login">Sign in</a></div>
    """
    return render_page("Open an account", content)
 
 
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
 
        conn = get_db()
        # Bug hint: same pattern as register — think about what a user
        # could type INTO the username or password field.
        query = "SELECT * FROM users WHERE username = '%s' AND password = '%s'" % (username, password)
        cursor = conn.execute(query)
        user = cursor.fetchone()
        conn.close()
 
        if user:
            # Bug hint: what does this page do with "username" below?
            content = """
                <div class="badge">&#10003;</div>
                <h1 style="text-align:center;">Welcome back, """ + username + """</h1>
                <p class="sub" style="text-align:center;">Your account overview</p>
                <p class="balance-label" style="text-align:center;">AVAILABLE BALANCE</p>
                <p class="balance" style="text-align:center;">$12,480.55</p>
            """
            return render_page("Account overview", content, card_class="result-card")
        else:
            content = """
                <h1>Sign in</h1>
                <p class="sub">Access your Meridian Trust account.</p>
                <div class="error">Incorrect username or password.</div>
                <form method="post">
                    <label>Username</label>
                    <input name="username" autocomplete="off">
                    <label>Password</label>
                    <input name="password" type="text">
                    <button type="submit">Sign in</button>
                </form>
                <div class="switch">New here? <a href="/register">Open an account</a></div>
            """
            return render_page("Sign in", content)
 
    content = """
        <h1>Sign in</h1>
        <p class="sub">Access your Meridian Trust account.</p>
        <form method="post">
            <label>Username</label>
            <input name="username" autocomplete="off">
            <label>Password</label>
            <input name="password" type="text">
            <button type="submit">Sign in</button>
        </form>
        <div class="switch">New here? <a href="/register">Open an account</a></div>
    """
    return render_page("Sign in", content)
 
 
@app.route("/profile-pic", methods=["GET"])
def profile_pic():
    # Bug hint: this takes a filename straight from the URL...
    filename = request.args.get("file")
    try:
        with open(f"uploads/{filename}", "rb") as f:
            return f.read()
    except Exception as e:
        # Bug hint: what does this expose to the user on failure?
        content = f"""
            <h1>Document unavailable</h1>
            <div class="error">Error loading file: {e}</div>
        """
        return render_page("Document unavailable", content)
 
 
if __name__ == "__main__":
    init_db()
    # Bug hint: is this safe to leave on?
    app.run(debug=True, host="0.0.0.0")
 