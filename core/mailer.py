import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import Config


def send_otp_email(recipient: str, otp_code: str, username: str) -> bool:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your 2FA Verification Code"
    msg["From"]    = Config.MAIL_SENDER
    msg["To"]      = recipient

    html = f"""
    <html>
      <body style="font-family:Arial,sans-serif;background:#0d0d0d;color:#e0e0e0;padding:40px;">
        <div style="max-width:480px;margin:auto;background:#1a1a1a;border:1px solid #00ff88;
                    border-radius:8px;padding:32px;">
          <h2 style="color:#00ff88;margin-top:0;">S1xSec 2FA System</h2>
          <p>Hey <strong>{username}</strong>,</p>
          <p>Your one-time verification code is:</p>
          <div style="font-size:40px;font-weight:bold;letter-spacing:12px;
                      color:#00ff88;text-align:center;padding:20px 0;">
            {otp_code}
          </div>
          <p style="color:#888;font-size:13px;">
            This code expires in <strong>30 seconds</strong>.<br>
            If you did not request this, ignore this email.
          </p>
        </div>
      </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            server.sendmail(Config.MAIL_SENDER, recipient, msg.as_string())
        return True
    except Exception as e:
        print(f"EMAIL ERROR: {e}")
        return False
