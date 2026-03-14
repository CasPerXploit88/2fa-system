import pyotp
import base64
import os


def generate_secret() -> str:
    return pyotp.random_base32()


def generate_otp(secret: str) -> str:
    totp = pyotp.TOTP(secret, interval=30)
    return totp.now()


def verify_otp(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret, interval=30)
    return totp.verify(code, valid_window=1)


def generate_session_token() -> str:
    return base64.urlsafe_b64encode(os.urandom(32)).decode()
