
import smtplib
from email.mime.text import MIMEText
from .config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, ALERT_RECIPIENT_EMAIL

def send_email_notification(student_id: str, zone_id: str, timestamp, bunking_score: int):
    """
    Sends an email alert for a confirmed violation.
    
    NOTE: This function uses placeholder credentials from config.py.
    You must update the SMTP settings in school_surveillance/src/config.py
    for this to work.
    """
    if not all([SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, ALERT_RECIPIENT_EMAIL]):
        print("[⚠️] Email alert not sent. SMTP configuration is incomplete in config.py.")
        return

    subject = f"Security Alert: Student Violation Detected"
    body = f"""
    A security violation has been confirmed.

    Details:
    - Student ID: {student_id}
    - Zone ID: {zone_id}
    - Timestamp: {timestamp.strftime('%Y-%m-%d %I:%M:%S %p')}
    - Student's Bunking Score: {bunking_score}

    This is an automated notification.
    """
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_USERNAME
    msg['To'] = ALERT_RECIPIENT_EMAIL

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, [ALERT_RECIPIENT_EMAIL], msg.as_string())
            print(f"[📧] Email alert sent successfully to {ALERT_RECIPIENT_EMAIL}")
    except Exception as e:
        print(f"[❌] Failed to send email alert: {e}")
        print("[ℹ️] Please ensure your SMTP settings in school_surveillance/src/config.py are correct.")

