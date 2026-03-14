import bcrypt
from datetime import datetime, timedelta
from config import Config
from core import database as db


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(
        plain.encode(), bcrypt.gensalt(rounds=Config.BCRYPT_ROUNDS)
    ).decode()


def check_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def is_locked(user) -> bool:
    if user["locked_until"] is None:
        return False
    locked_until = datetime.fromisoformat(user["locked_until"])
    if datetime.utcnow() < locked_until:
        return True
    db.reset_login_attempts(user["id"])
    return False


def register_user(username: str, email: str, password: str) -> dict:
    from core.otp import generate_secret

    if db.fetch_user_by_username(username):
        return {"success": False, "message": "Username already exists."}

    hashed   = hash_password(password)
    secret   = generate_secret()

    try:
        db.insert_user(username, email, hashed, secret)
        return {"success": True}
    except Exception:
        return {"success": False, "message": "Email already registered."}


def validate_login(username: str, password: str) -> dict:
    user = db.fetch_user_by_username(username)

    if not user:
        return {"success": False, "message": "Invalid credentials."}

    if is_locked(user):
        return {"success": False, "message": f"Account locked. Try again in {Config.LOCKOUT_MINUTES} minutes."}

    if not check_password(password, user["password_hash"]):
        db.increment_login_attempts(user["id"])
        remaining = Config.MAX_LOGIN_ATTEMPTS - user["login_attempts"] - 1

        if remaining <= 0:
            until = (datetime.utcnow() + timedelta(minutes=Config.LOCKOUT_MINUTES)).isoformat()
            db.lock_user(user["id"], until)
            return {"success": False, "message": f"Too many attempts. Account locked for {Config.LOCKOUT_MINUTES} minutes."}

        return {"success": False, "message": f"Invalid credentials. {remaining} attempt(s) remaining."}

    db.reset_login_attempts(user["id"])
    return {"success": True, "user": user}
