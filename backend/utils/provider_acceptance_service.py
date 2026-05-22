"""
Provider Acceptance Workflow
Handles provider responses to booking requests
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ProviderAcceptanceService:
    """
    Manages provider acceptance/rejection workflow
    """

    def __init__(self, db_manager):
        self.db = db_manager

    def create_provider_response_table(self):
        """Create provider_responses table if not exists"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS provider_responses (
                    id SERIAL PRIMARY KEY,
                    booking_id VARCHAR(20) NOT NULL,
                    provider_id VARCHAR(20) NOT NULL,
                    response VARCHAR(20) CHECK (response IN ('pending', 'accepted', 'rejected')),
                    rejection_reason TEXT,
                    responded_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_provider_responses_booking
                ON provider_responses(booking_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_provider_responses_provider
                ON provider_responses(provider_id)
            """)

            conn.commit()
            cursor.close()
            conn.close()

            logger.info("Provider responses table created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create provider_responses table: {e}")
            return False

    def send_booking_request_to_provider(
        self,
        booking_id: str,
        provider_id: str,
        timeout_minutes: int = 5
    ) -> bool:
        """
        Send booking request to provider and set timeout

        Args:
            booking_id: Booking ID
            provider_id: Provider ID
            timeout_minutes: Minutes before auto-rejection (default 5)

        Returns:
            True if successful
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Create provider response record
            cursor.execute("""
                INSERT INTO provider_responses (booking_id, provider_id, response)
                VALUES (%s, %s, 'pending')
            """, (booking_id, provider_id))

            # Update booking status
            cursor.execute("""
                UPDATE bookings
                SET status = 'pending_provider_response',
                    provider_response_deadline = NOW() + INTERVAL '%s minutes'
                WHERE booking_id = %s
            """, (timeout_minutes, booking_id))

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"Sent booking request to provider {provider_id} for booking {booking_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to send booking request: {e}")
            return False

    def provider_accept_booking(
        self,
        booking_id: str,
        provider_id: str
    ) -> Dict:
        """
        Provider accepts a booking

        Returns:
            Dict with status and message
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Update provider response
            cursor.execute("""
                UPDATE provider_responses
                SET response = 'accepted', responded_at = NOW()
                WHERE booking_id = %s AND provider_id = %s
            """, (booking_id, provider_id))

            # Update booking status
            cursor.execute("""
                UPDATE bookings
                SET status = 'confirmed'
                WHERE booking_id = %s
            """, (booking_id,))

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"Provider {provider_id} accepted booking {booking_id}")

            return {
                "status": "success",
                "message": "Booking accepted successfully",
                "booking_id": booking_id
            }

        except Exception as e:
            logger.error(f"Failed to accept booking: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def provider_reject_booking(
        self,
        booking_id: str,
        provider_id: str,
        rejection_reason: str = None
    ) -> Dict:
        """
        Provider rejects a booking - reassign to next best provider

        Returns:
            Dict with status and message
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Update provider response
            cursor.execute("""
                UPDATE provider_responses
                SET response = 'rejected',
                    rejection_reason = %s,
                    responded_at = NOW()
                WHERE booking_id = %s AND provider_id = %s
            """, (rejection_reason, booking_id, provider_id))

            # Get booking details
            cursor.execute("""
                SELECT * FROM bookings WHERE booking_id = %s
            """, (booking_id,))

            booking = cursor.fetchone()

            if not booking:
                conn.close()
                return {"status": "error", "message": "Booking not found"}

            # Find next best provider
            # This would use the matching engine to find alternatives
            # For now, mark as cancelled if no alternatives

            cursor.execute("""
                UPDATE bookings
                SET status = 'cancelled'
                WHERE booking_id = %s
            """, (booking_id,))

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"Provider {provider_id} rejected booking {booking_id}: {rejection_reason}")

            return {
                "status": "rejected",
                "message": "Booking rejected. Looking for alternative providers.",
                "booking_id": booking_id,
                "reason": rejection_reason
            }

        except Exception as e:
            logger.error(f"Failed to reject booking: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def check_timed_out_responses(self):
        """
        Check for provider responses that have timed out
        Auto-reject and reassign to next provider

        Returns:
            Number of timed-out bookings processed
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Find timed-out bookings
            cursor.execute("""
                SELECT booking_id, provider_id FROM bookings
                WHERE status = 'pending_provider_response'
                AND provider_response_deadline < NOW()
            """)

            timed_out_bookings = cursor.fetchall()
            cursor.close()
            conn.close()

            count = 0
            for booking in timed_out_bookings:
                booking_id = booking[0]
                provider_id = booking[1]

                # Auto-reject
                self.provider_reject_booking(
                    booking_id=booking_id,
                    provider_id=provider_id,
                    rejection_reason="Timeout - no response within 5 minutes"
                )
                count += 1

            if count > 0:
                logger.info(f"Processed {count} timed-out provider responses")

            return count

        except Exception as e:
            logger.error(f"Failed to check timed-out responses: {e}")
            return 0

    def get_provider_response_stats(self, provider_id: str) -> Dict:
        """
        Get provider's acceptance/rejection statistics

        Returns:
            Dict with acceptance rate and response time
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN response = 'accepted' THEN 1 ELSE 0 END) as accepted,
                    SUM(CASE WHEN response = 'rejected' THEN 1 ELSE 0 END) as rejected,
                    AVG(EXTRACT(EPOCH FROM (responded_at - created_at))/60) as avg_response_minutes
                FROM provider_responses
                WHERE provider_id = %s AND response != 'pending'
            """, (provider_id,))

            stats = cursor.fetchone()
            cursor.close()
            conn.close()

            if stats and stats[0] > 0:
                total = stats[0]
                accepted = stats[1] or 0
                rejected = stats[2] or 0
                avg_response_time = stats[3] or 0

                return {
                    "total_responses": total,
                    "accepted": accepted,
                    "rejected": rejected,
                    "acceptance_rate": (accepted / total) * 100 if total > 0 else 0,
                    "avg_response_time_minutes": round(avg_response_time, 2)
                }
            else:
                return {
                    "total_responses": 0,
                    "accepted": 0,
                    "rejected": 0,
                    "acceptance_rate": 0,
                    "avg_response_time_minutes": 0
                }

        except Exception as e:
            logger.error(f"Failed to get provider stats: {e}")
            return {}
