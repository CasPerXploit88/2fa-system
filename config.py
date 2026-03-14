import os
from datetime import timedelta

class Config:
    SECRET_KEY                  = os.environ.get("SECRET_KEY", "change-this-in-production-32chars!")
    DATABASE_PATH               = os.path.join(os.path.dirname(__file__), "database", "users.db")

    # email — set these as environment variables on your machine
    MAIL_SERVER                 = "smtp.gmail.com"
    MAIL_PORT                   = 587
    MAIL_USERNAME               = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD               = os.environ.get("MAIL_PASSWORD", "")
    MAIL_SENDER                 = os.environ.get("MAIL_USERNAME", "")

    # session
    PERMANENT_SESSION_LIFETIME  = timedelta(minutes=30)
    SESSION_COOKIE_HTTPONLY     = True
    SESSION_COOKIE_SAMESITE     = "Lax"

    # rate limiting
    RATELIMIT_DEFAULT           = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URL       = "memory://"

    # otp
    OTP_INTERVAL                = 30    # seconds before OTP expires
    MAX_OTP_ATTEMPTS            = 3
    MAX_LOGIN_ATTEMPTS          = 5
    LOCKOUT_MINUTES             = 15

    # bcrypt
    BCRYPT_ROUNDS               = 12
