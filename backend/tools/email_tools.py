"""
Email Notification Tools for ServiceLink AI
Handles sending email notifications using SMTP
"""

import os
import smtplib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import logging
from config.settings import settings

# Google Auth imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_email_via_gmail_api(to_email: str, subject: str, body_text: str, body_html: str) -> bool:
    """Send email using Gmail API with credentials.json and token.json"""
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    try:
        creds = None
        token_file = settings.TOKEN_FILE
        
        if token_file.exists():
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                logger.warning("Gmail API credentials not valid or missing token.json")
                return False
                
        service = build('gmail', 'v1', credentials=creds)
        
        message = MIMEMultipart('alternative')
        message['to'] = to_email
        message['subject'] = subject
        
        message.attach(MIMEText(body_text, 'plain'))
        message.attach(MIMEText(body_html, 'html'))
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': raw}
        
        service.users().messages().send(userId="me", body=create_message).execute()
        logger.info(f"Email sent via Gmail API to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Gmail API send failed: {e}")
        return False

async def send_booking_confirmation_email(
    to_email: str,
    booking_id: str,
    service_type: str,
    location: str,
    urgency: str,
    customer_contact: str
) -> bool:
    """
    Send booking confirmation email to provider
    Tries Gmail API first, falls back to SMTP
    """
    urgency_text = "🚨 EMERGENCY" if urgency == "emergency" else "⚡ HIGH PRIORITY" if urgency == "high" else "NORMAL"

    subject = f"New Service Booking - {booking_id}"

    text = f"""
New Service Booking - ServiceLink AI

Booking ID: {booking_id}
Service Type: {service_type}
Location: {location}
Urgency: {urgency_text}

Customer Contact: {customer_contact}

Please contact the customer to confirm the appointment time.

---
ServiceLink AI - Home Service Booking Platform
"""

    html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
        <h2 style="color: #3B82F6;">New Service Booking</h2>

        <div style="background-color: #F3F4F6; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p><strong>Booking ID:</strong> {booking_id}</p>
            <p><strong>Service Type:</strong> {service_type}</p>
            <p><strong>Location:</strong> {location}</p>
            <p><strong>Urgency:</strong> <span style="color: {'#DC2626' if urgency == 'emergency' else '#F59E0B' if urgency == 'high' else '#10B981'};">{urgency_text}</span></p>
        </div>

        <p><strong>Customer Contact:</strong> {customer_contact}</p>

        <p style="margin-top: 20px;">Please contact the customer to confirm the appointment time.</p>

        <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
        <p style="font-size: 12px; color: #666;">ServiceLink AI - Home Service Booking Platform</p>
    </div>
</body>
</html>
"""

    # 1. Try Gmail API first (if credentials exist)
    if settings.CREDENTIALS_FILE.exists() or settings.TOKEN_FILE.exists():
        logger.info("Attempting to send via Gmail API...")
        if await send_email_via_gmail_api(to_email, subject, text, html):
            return True

    # 2. Fallback to SMTP
    if not settings.EMAIL_USER or not settings.EMAIL_PASSWORD:
        logger.warning("SMTP not configured and Gmail API failed - skipping notification")
        return False

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.EMAIL_USER
        msg['To'] = to_email
        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))

        with smtplib.SMTP_SSL(settings.EMAIL_SMTP_SERVER, settings.EMAIL_SMTP_PORT) as server:
            server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
            server.send_message(msg)

        logger.info(f"Booking confirmation email sent via SMTP to {to_email}")
        return True

    except Exception as e:
        logger.error(f"SMTP send failed: {e}")
        return False


def get_email_config_status() -> Dict:
    """Get email configuration status"""
    return {
        "configured": bool(settings.EMAIL_USER and settings.EMAIL_PASSWORD),
        "email_user": settings.EMAIL_USER if settings.EMAIL_USER else "Not configured",
        "smtp_server": settings.EMAIL_SMTP_SERVER,
        "smtp_port": settings.EMAIL_SMTP_PORT
    }
