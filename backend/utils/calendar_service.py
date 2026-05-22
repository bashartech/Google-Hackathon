"""
Calendar Service for ServiceLink AI
Database-based calendar system (no Google Calendar API)
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class CalendarService:
    """
    Manages provider availability and booking slots using database
    """

    def __init__(self, db_manager):
        self.db = db_manager

    def initialize_provider_slots(self, provider_id: str, days_ahead: int = 30):
        """
        Initialize time slots for a provider for the next N days
        Time slots: 9:00, 10:00, 11:00, 12:00, 14:00, 15:00, 16:00, 17:00, 18:00
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            time_slots = ['09:00', '10:00', '11:00', '12:00', '14:00', '15:00', '16:00', '17:00', '18:00']

            for day in range(days_ahead):
                date = (datetime.now() + timedelta(days=day)).date()

                for time_slot in time_slots:
                    cursor.execute("""
                        INSERT INTO provider_calendar (provider_id, date, time_slot, is_booked)
                        VALUES (%s, %s, %s, FALSE)
                        ON CONFLICT DO NOTHING
                    """, (provider_id, date, time_slot))

            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"Initialized calendar slots for provider {provider_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize calendar slots: {e}")
            return False

    def get_available_slots(self, provider_id: str, date: str) -> List[str]:
        """
        Get available time slots for a provider on a specific date

        Args:
            provider_id: Provider ID
            date: Date in YYYY-MM-DD format

        Returns:
            List of available time slots (e.g., ['09:00', '10:00', '14:00'])
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT time_slot FROM provider_calendar
                WHERE provider_id = %s AND date = %s AND is_booked = FALSE
                ORDER BY time_slot
            """, (provider_id, date))

            slots = [row['time_slot'] for row in cursor.fetchall()]
            cursor.close()
            conn.close()

            return slots

        except Exception as e:
            logger.error(f"Failed to get available slots: {e}")
            return []

    def get_next_available_date(self, provider_id: str, days_to_check: int = 7) -> Optional[Dict]:
        """
        Find the next date with available slots for a provider

        Returns:
            Dict with 'date' and 'slots' or None if no availability
        """
        try:
            for day in range(days_to_check):
                date = (datetime.now() + timedelta(days=day)).date()
                slots = self.get_available_slots(provider_id, str(date))

                if slots:
                    return {
                        'date': str(date),
                        'slots': slots,
                        'day_name': date.strftime('%A')
                    }

            return None

        except Exception as e:
            logger.error(f"Failed to find next available date: {e}")
            return None

    def book_slot(self, provider_id: str, date: str, time_slot: str, booking_id: str) -> bool:
        """
        Mark a time slot as booked

        Args:
            provider_id: Provider ID
            date: Date in YYYY-MM-DD format
            time_slot: Time slot (e.g., '09:00')
            booking_id: Booking ID to associate with this slot

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Check if slot is available
            cursor.execute("""
                SELECT is_booked FROM provider_calendar
                WHERE provider_id = %s AND date = %s AND time_slot = %s
            """, (provider_id, date, time_slot))

            result = cursor.fetchone()

            if not result:
                logger.warning(f"Slot not found: {provider_id}, {date}, {time_slot}")
                cursor.close()
                conn.close()
                return False

            if result['is_booked']:  # Already booked
                logger.warning(f"Slot already booked: {provider_id}, {date}, {time_slot}")
                cursor.close()
                conn.close()
                return False

            # Book the slot
            cursor.execute("""
                UPDATE provider_calendar
                SET is_booked = TRUE, booking_id = %s, updated_at = NOW()
                WHERE provider_id = %s AND date = %s AND time_slot = %s
            """, (booking_id, provider_id, date, time_slot))

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"Booked slot: {provider_id}, {date}, {time_slot} for booking {booking_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to book slot: {e}")
            return False

    def cancel_booking(self, booking_id: str) -> bool:
        """
        Cancel a booking and free up the time slot

        Args:
            booking_id: Booking ID to cancel

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE provider_calendar
                SET is_booked = FALSE, booking_id = NULL, updated_at = NOW()
                WHERE booking_id = %s
            """, (booking_id,))

            conn.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            conn.close()

            if rows_affected > 0:
                logger.info(f"Cancelled booking {booking_id}")
                return True
            else:
                logger.warning(f"No slots found for booking {booking_id}")
                return False

        except Exception as e:
            logger.error(f"Failed to cancel booking: {e}")
            return False

    def get_provider_schedule(self, provider_id: str, start_date: str, end_date: str) -> List[Dict]:
        """
        Get provider's schedule for a date range

        Returns:
            List of dicts with date, time_slot, is_booked, booking_id
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT date, time_slot, is_booked, booking_id
                FROM provider_calendar
                WHERE provider_id = %s AND date BETWEEN %s AND %s
                ORDER BY date, time_slot
            """, (provider_id, start_date, end_date))

            schedule = []
            for row in cursor.fetchall():
                schedule.append({
                    'date': str(row['date']),
                    'time_slot': row['time_slot'],
                    'is_booked': row['is_booked'],
                    'booking_id': row['booking_id']
                })

            cursor.close()
            conn.close()

            return schedule

        except Exception as e:
            logger.error(f"Failed to get provider schedule: {e}")
            return []

    def check_availability_for_providers(self, provider_ids: List[str], date: str) -> Dict[str, List[str]]:
        """
        Check availability for multiple providers on a specific date

        Returns:
            Dict mapping provider_id to list of available slots
        """
        availability = {}

        for provider_id in provider_ids:
            slots = self.get_available_slots(provider_id, date)
            availability[provider_id] = slots

        return availability
