from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
from core import database as db
from core.auth import register_user, validate_login
from core.otp import generate_otp, verify_otp, generate_session_token
from core.mailer import send_otp_email
import sys, os

sys.path.insert(0, os.path.dirname(__file__))

app = Flask(__name__)
app.config.from_object(Config)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

db.init_db()


# ── helpers ───────────────────────────────────────────────────────────────────

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ── routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username", "").strip()
    email    = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not all([username, email, password]):
        return render_template("register.html", error="All fields are required.")

    if len(password) < 8:
        return render_template("register.html", error="Password must be at least 8 characters.")

    result = register_user(username, email, password)

    if not result["success"]:
        return render_template("register.html", error=result["message"])

    return redirect(url_for("login", registered="1"))


@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if request.method == "GET":
        registered = request.args.get("registered")
        return render_template("login.html", registered=registered)

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    result = validate_login(username, password)

    if not result["success"]:
        return render_template("login.html", error=result["message"])

    user  = result["user"]
    otp   = generate_otp(user["otp_secret"])
    token = generate_session_token()

    db.create_otp_session(user["id"], token)

    sent = send_otp_email(user["email"], otp, user["username"])
    if not sent:
        return render_template("login.html", error="Failed to send OTP email. Check your mail config.")

    session["otp_token"]  = token
    session["pending_uid"] = user["id"]

    return redirect(url_for("verify"))


@app.route("/verify", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def verify():
    if "otp_token" not in session:
        return redirect(url_for("login"))

    token = session["otp_token"]

    if request.method == "GET":
        return render_template("verify.html", interval=Config.OTP_INTERVAL)

    code = request.form.get("otp", "").strip()

    if not code.isdigit() or len(code) != 6:
        return render_template("verify.html", error="Enter a valid 6-digit code.", interval=Config.OTP_INTERVAL)

    otp_session = db.fetch_otp_session(token)

    if not otp_session:
        session.clear()
        return redirect(url_for("login", error="Session expired. Please login again."))

    if otp_session["attempts"] >= Config.MAX_OTP_ATTEMPTS:
        db.invalidate_otp_session(token)
        session.clear()
        return render_template("login.html", error="Too many incorrect OTP attempts. Please login again.")

    user = db.fetch_user_by_id(session["pending_uid"])

    if not verify_otp(user["otp_secret"], code):
        db.increment_otp_attempts(token)
        remaining = Config.MAX_OTP_ATTEMPTS - otp_session["attempts"] - 1
        return render_template("verify.html", error=f"Incorrect code. {remaining} attempt(s) remaining.", interval=Config.OTP_INTERVAL)

    db.invalidate_otp_session(token)
    session.pop("otp_token", None)
    session.pop("pending_uid", None)
    session["user_id"]   = user["id"]
    session["username"]  = user["username"]
    session.permanent    = True

    return redirect(url_for("dashboard"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session["username"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.errorhandler(429)
def rate_limit_handler(e):
    return render_template("error.html", message="Too many requests. Please slow down."), 429


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", message="Page not found."), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
