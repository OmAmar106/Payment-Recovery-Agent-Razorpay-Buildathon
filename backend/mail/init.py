import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

def send_reachout_email(data, result):
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    recipient = data['payload']['payment']['entity']['email']

    message = MIMEMultipart("alternative")
    message["From"] = smtp_user
    message["To"] = recipient
    message["Subject"] = "Payment Failure @ Razorpay"

    message.attach(MIMEText(result.get("message", "Payment failed."), "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.set_debuglevel(1)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        response = server.send_message(message)


def send_mail(data, result):
    send_reachout_email(data, result)