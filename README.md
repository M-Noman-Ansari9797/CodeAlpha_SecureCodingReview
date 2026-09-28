# CodeAlpha_SecureCodingReview

Secure Coding Review of a deliberately vulnerable Python (Flask) banking demo app, completed for the **CodeAlpha Cyber Security Internship (Task 3)**.

"Meridian Trust" is a **fictional bank** created for this review. It is not affiliated with any real institution.

## Scope

| Item | Detail |
|------|--------|
| Language / Framework | Python 3 / Flask, SQLite |
| Application reviewed | `app.py` (login, registration, file viewer) |
| Method | Manual code review + live exploitation on localhost |
| Result | 7 vulnerabilities found and fixed in `fixed_app.py` |

## Repository Files

| File | Description |
|------|-------------|
| `app.py` | Original vulnerable version (for review) |
| `fixed_app.py` | Secure, remediated version |
| `screenshots/` | Evidence of each vulnerability |

## Findings Summary

| # | Vulnerability | Location | Severity |
|---|---------------|----------|----------|
| 1 | SQL Injection | `login()`, `register()` | Critical |
| 2 | Cross-Site Scripting (XSS) | `login()` welcome message | High |
| 3 | Hardcoded secret key | `SECRET_KEY` | High |
| 4 | Plaintext password storage | `users` table | Critical |
| 5 | Verbose error disclosure | `profile_pic()` | Medium |
| 6 | Path traversal / no filename validation | `profile_pic()` | High |
| 7 | Insecure server config (`debug=True`, `host=0.0.0.0`) | `app.run()` | High |

## Detailed Findings

### 1. SQL Injection (Critical)
**Where:** `login()` and `register()`
**Issue:** User input is pasted directly into SQL strings using `%` formatting.
```python
query = "SELECT * FROM users WHERE username = '%s' AND password = '%s'" % (username, password)
```
**Impact:** Entering `' OR '1'='1` as the username logs an attacker in without a valid password. In a real bank this could expose every account.
**Evidence:** `screenshots/03_sql_injection.png`
**Fix:** Parameterized queries.
```python
conn.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
```

### 2. Cross-Site Scripting (High)
**Where:** `login()` welcome page
**Issue:** The username is concatenated into HTML without escaping.
**Impact:** An attacker can run JavaScript in a victim's browser (session theft, fake forms).
**Fix:** Escape output with `html.escape(username)`.

### 3. Hardcoded Secret Key (High)
**Where:** `SECRET_KEY = "sk_live_supersecret12345"`
**Impact:** Anyone with access to the code (e.g. a public repo) can forge sessions or use the credential.
**Evidence:** `screenshots/05_code_secret.png`
**Fix:** Load secrets from environment variables: `os.environ.get("SECRET_KEY")`.

### 4. Plaintext Password Storage (Critical)
**Where:** `users` table, `password TEXT`
**Impact:** If the database leaks, every password is instantly exposed, and users often reuse passwords elsewhere.
**Fix:** Hash with `generate_password_hash()` and verify with `check_password_hash()`.

### 5. Verbose Error Disclosure (Medium)
**Where:** `profile_pic()` returns the raw exception text.
**Impact:** Leaks internal file paths and system details that help attackers plan further attacks.
**Evidence:** `screenshots/04_error_disclosure.png`
**Fix:** Return a generic message; log details server-side only.

### 6. Path Traversal (High)
**Where:** `open(f"uploads/{filename}")`
**Impact:** A request such as `?file=../app.py` could read files outside the uploads folder.
**Fix:** Allow-list filename characters, reject `..`, and serve with `send_from_directory`.

### 7. Insecure Server Configuration (High)
**Where:** `app.run(debug=True, host="0.0.0.0")`
**Impact:** Debug mode exposes an interactive debugger and stack traces; `0.0.0.0` exposes the app to the whole network.
**Evidence:** `screenshots/06_debug_config.png`
**Fix:** `app.run(debug=False, host="127.0.0.1")`.

## Additional Hardening Added in `fixed_app.py`
- Input validation on username (3-30 letters/numbers/underscore) and minimum password length
- `UNIQUE` constraint on usernames
- Generic login error message (does not reveal which field was wrong)

## Tools & Method
- Manual line-by-line review, tracing every place user input reaches a query, page, or file path
- Live exploitation on `127.0.0.1` to confirm each finding
- Recommended next step: run `bandit -r .` (Python static analyzer) as an automated second check

## Key Lessons
- Never trust user input: validate it, and separate data from code (parameterized queries)
- Escape output before placing it in HTML
- Never store plaintext passwords or commit secrets to code
- Fail safely: generic errors for users, detailed logs for developers
- Development settings (debug mode) must never reach production

## How to Run
```bash
pip install flask
python app.py          # vulnerable version
python fixed_app.py    # secure version
```

## Disclaimer
Educational use only. The vulnerable app must never be deployed publicly, and these techniques must only be used on systems you own or have permission to test.

## Acknowledgements
Built as part of the **CodeAlpha Cyber Security Internship**, Task 3: Secure Coding Review. [www.codealpha.tech](https://www.codealpha.tech)
