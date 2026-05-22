"""
Reminder System for ServiceLink AI
Uses Gmail API (not SMTP) with credentials.json and token.json
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional
import os
from pathlib import Path
import logging
from config.settings import settings

logger = logging.getLogger(__name__)


class ReminderService:
    """
    Handles automated reminders and follow-ups using Gmail API
    """

    def __init__(self):
        self.creds = self._get_credentials()
        self.service = build('gmail', 'v1', credentials=self.creds) if self.creds else None

    def _get_credentials(self):
        """Get Gmail API credentials from token.json"""
        try:
            token_path = settings.TOKEN_FILE

            if not token_path.exists():
                logger.error(f"token.json not found at {token_path}")
                return None

            creds = Credentials.from_authorized_user_file(str(token_path))

            # Refresh if expired
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Save refreshed token
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())

            return creds

        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            return None

    def _send_email_via_gmail_api(self, to_email: str, subject: str, html_body: str) -> bool:
        """Send email using Gmail API"""
        if not self.service:
            logger.warning("Gmail API not configured")
            return False

        try:
            message = MIMEText(html_body, 'html')
            message['to'] = to_email
            message['subject'] = subject

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            send_message = {'raw': raw_message}

            self.service.users().messages().send(userId='me', body=send_message).execute()
            logger.info(f"Email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def send_reminder_email(
        self,
        to_email: str,
        booking_id: str,
        service_type: str,
        scheduled_time: str,
        provider_name: str,
        customer_name: str = None
    ) -> bool:
        """Send reminder email 1 hour before appointment"""

        greeting = f"Hi {customer_name}!" if customer_name else "Hello!"

        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
              <h2 style="color: #0ea5e9;">Service Reminder</h2>

              <p>{greeting}</p>

              <p>This is a friendly reminder that your <strong>{service_type}</strong> service is scheduled in <strong>1 hour</strong>.</p>

              <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #0ea5e9;">Booking Details</h3>
                <p><strong>Booking ID:</strong> {booking_id}</p>
                <p><strong>Service:</strong> {service_type}</p>
                <p><strong>Provider:</strong> {provider_name}</p>
                <p><strong>Scheduled Time:</strong> {scheduled_time}</p>
              </div>

              <p style="color: #666; font-size: 14px;">
                Please ensure someone is available at the location to receive the service provider.
              </p>

              <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">

              <p style="color: #999; font-size: 12px;">
                This is an automated reminder from ServiceLink AI.
              </p>
            </div>
          </body>
        </html>
        """

        return self._send_email_via_gmail_api(
            to_email=to_email,
            subject=f"Reminder: {service_type} Service in 1 Hour",
            html_body=html
        )

    def send_completion_request(
        self,
        to_email: str,
        booking_id: str,
        service_type: str,
        provider_name: str,
        customer_name: str = None
    ) -> bool:
        """Send completion confirmation request after service"""

        greeting = f"Hi {customer_name}!" if customer_name else "Hello!"

        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
              <h2 style="color: #10b981;">Service Completed</h2>

              <p>{greeting}</p>

              <p>We hope your <strong>{service_type}</strong> service was completed successfully!</p>

              <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #10b981;">Booking Details</h3>
                <p><strong>Booking ID:</strong> {booking_id}</p>
                <p><strong>Service:</strong> {service_type}</p>
                <p><strong>Provider:</strong> {provider_name}</p>
              </div>

              <div style="background-color: #fef3c7; padding: 15px; border-radius: 8px; border-left: 4px solid #f59e0b;">
                <p style="margin: 0;"><strong>Rate Your Experience</strong></p>
                <p style="margin: 10px 0 0 0; font-size: 14px;">
                  Your feedback helps us improve our service quality.
                </p>
              </div>

              <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">

              <p style="color: #999; font-size: 12px;">
                Thank you for using ServiceLink AI!
              </p>
            </div>
          </body>
        </html>
        """

        return self._send_email_via_gmail_api(
            to_email=to_email,
            subject=f"Service Completed - Please Confirm",
            html_body=html
        )

    def send_status_update(
        self,
        to_email: str,
        booking_id: str,
        old_status: str,
        new_status: str,
        service_type: str,
        customer_name: str = None
    ) -> bool:
        """Send status update notification"""

        greeting = f"Hi {customer_name}!" if customer_name else "Hello!"

        status_emoji = {
            'pending': 'Pending',
            'confirmed': 'Confirmed',
            'in_progress': 'In Progress',
            'completed': 'Completed',
            'cancelled': 'Cancelled'
        }

        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
              <h2 style="color: #0ea5e9;">Status Update</h2>

              <p>{greeting}</p>

              <p>Your booking status has been updated:</p>

              <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <p><strong>Booking ID:</strong> {booking_id}</p>
                <p><strong>Service:</strong> {service_type}</p>
                <p style="margin-top: 15px;">
                  <span style="color: #999; text-decoration: line-through;">{status_emoji.get(old_status, old_status).title()}</span>
                  →
                  <span style="color: #0ea5e9; font-weight: bold;">{status_emoji.get(new_status, new_status).title()}</span>
                </p>
              </div>

              <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">

              <p style="color: #999; font-size: 12px;">
                This is an automated notification from ServiceLink AI.
              </p>
            </div>
          </body>
        </html>
        """

        return self._send_email_via_gmail_api(
            to_email=to_email,
            subject=f"Booking Status Updated: {new_status.title()}",
            html_body=html
        )
