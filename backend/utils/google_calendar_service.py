"""
Google Calendar Integration Service
Syncs provider schedules with Google Calendar
Uses credentials.json and token.json (same as Gmail API)
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path
import logging
from config.settings import settings

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """
    Integrates with Google Calendar API to sync provider schedules
    """

    def __init__(self):
        self.creds = self._get_credentials()
        self.service = build('calendar', 'v3', credentials=self.creds) if self.creds else None

    def _get_credentials(self):
        """Get Google Calendar API credentials from token.json"""
        try:
            token_path = settings.TOKEN_FILE

            if not token_path.exists():
                logger.error(f"token.json not found at {token_path}")
                return None

            creds = Credentials.from_authorized_user_file(str(token_path))

            # Refresh if expired
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())

            # Check if Calendar scope is present
            if creds and creds.scopes:
                has_calendar = any('calendar' in scope.lower() for scope in creds.scopes)
                if not has_calendar:
                    logger.warning("Calendar API scope not found in token.json")
                    return None

            return creds

        except Exception as e:
            logger.error(f"Failed to load Calendar credentials: {e}")
            return None

    def create_booking_event(
        self,
        booking_id: str,
        service_type: str,
        provider_name: str,
        customer_name: str,
        customer_phone: str,
        customer_location: str,
        date: str,
        time_slot: str,
        duration_minutes: int = 60
    ) -> Optional[str]:
        """
        Create a Google Calendar event for a booking

        Args:
            booking_id: Booking ID
            service_type: Type of service
            provider_name: Provider name
            customer_name: Customer name
            customer_phone: Customer phone
            customer_location: Customer location
            date: Date in YYYY-MM-DD format
            time_slot: Time slot (e.g., '09:00')
            duration_minutes: Duration in minutes (default 60)

        Returns:
            Event ID if successful, None otherwise
        """
        if not self.service:
            logger.warning("Google Calendar API not configured")
            return None

        try:
            # Parse date and time
            start_datetime = datetime.strptime(f"{date} {time_slot}", "%Y-%m-%d %H:%M")
            end_datetime = start_datetime + timedelta(minutes=duration_minutes)

            # Create event
            event = {
                'summary': f'{service_type} - {customer_name}',
                'location': customer_location,
                'description': f"""
ServiceLink AI Booking

Booking ID: {booking_id}
Service: {service_type}
Provider: {provider_name}
Customer: {customer_name}
Phone: {customer_phone}
Location: {customer_location}

Status: Confirmed
                """.strip(),
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'Asia/Karachi',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'Asia/Karachi',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
                'colorId': '9',  # Blue color for service bookings
            }

            # Insert event
            event_result = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()

            logger.info(f"Created Google Calendar event: {event_result.get('id')}")
            return event_result.get('id')

        except Exception as e:
            logger.error(f"Failed to create calendar event: {e}")
            return None

    def update_booking_event(
        self,
        event_id: str,
        new_status: str,
        additional_notes: str = None
    ) -> bool:
        """
        Update a Google Calendar event (e.g., when status changes)

        Args:
            event_id: Google Calendar event ID
            new_status: New booking status
            additional_notes: Additional notes to append

        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            return False

        try:
            # Get existing event
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()

            # Update description with new status
            current_description = event.get('description', '')
            updated_description = current_description.replace(
                'Status: Confirmed',
                f'Status: {new_status.upper()}'
            )

            if additional_notes:
                updated_description += f"\n\nNotes: {additional_notes}"

            event['description'] = updated_description

            # Change color based on status
            status_colors = {
                'confirmed': '9',    # Blue
                'in_progress': '5',  # Yellow
                'completed': '10',   # Green
                'cancelled': '11',   # Red
            }
            event['colorId'] = status_colors.get(new_status, '9')

            # Update event
            self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()

            logger.info(f"Updated Google Calendar event: {event_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update calendar event: {e}")
            return False

    def delete_booking_event(self, event_id: str) -> bool:
        """
        Delete a Google Calendar event (e.g., when booking is cancelled)

        Args:
            event_id: Google Calendar event ID

        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            return False

        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()

            logger.info(f"Deleted Google Calendar event: {event_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete calendar event: {e}")
            return False

    def get_busy_times(self, date: str) -> List[Dict]:
        """
        Get busy times from Google Calendar for a specific date

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            List of busy time slots
        """
        if not self.service:
            return []

        try:
            # Parse date
            start_datetime = datetime.strptime(date, "%Y-%m-%d")
            end_datetime = start_datetime + timedelta(days=1)

            # Query free/busy
            body = {
                "timeMin": start_datetime.isoformat() + 'Z',
                "timeMax": end_datetime.isoformat() + 'Z',
                "items": [{"id": "primary"}]
            }

            events_result = self.service.freebusy().query(body=body).execute()
            busy_times = events_result['calendars']['primary']['busy']

            return busy_times

        except Exception as e:
            logger.error(f"Failed to get busy times: {e}")
            return []

    def check_availability(self) -> bool:
        """
        Check if Google Calendar API is available and working

        Returns:
            True if available, False otherwise
        """
        if not self.service:
            return False

        try:
            # Try to access calendar
            self.service.calendarList().list().execute()
            return True
        except Exception as e:
            logger.error(f"Google Calendar API not available: {e}")
            return False
