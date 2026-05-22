"""
Smart Scheduling Service
Analyzes demand patterns and suggests optimal booking times
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SmartScheduler:
    """
    Provides intelligent scheduling recommendations based on demand patterns
    """

    def __init__(self, db_manager):
        self.db = db_manager

    def analyze_demand_patterns(self, service_type: str, area: str) -> List[Dict]:
        """
        Analyze historical booking data to find low-demand periods

        Args:
            service_type: Type of service
            area: Area/location

        Returns:
            List of time slots with demand levels
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    EXTRACT(HOUR FROM created_at) as hour,
                    EXTRACT(DOW FROM created_at) as day_of_week,
                    COUNT(*) as booking_count
                FROM bookings
                WHERE service_type = %s AND customer_location LIKE %s
                GROUP BY hour, day_of_week
                ORDER BY booking_count ASC
            """, (service_type, f"%{area}%"))

            low_demand_slots = cursor.fetchall()
            cursor.close()
            conn.close()

            return [
                {
                    'hour': int(row['hour']),
                    'day_of_week': int(row['day_of_week']),
                    'booking_count': row['booking_count']
                }
                for row in low_demand_slots
            ]

        except Exception as e:
            logger.error(f"Failed to analyze demand patterns: {e}")
            return []

    def suggest_best_time(self, service_type: str, area: str) -> List[Dict]:
        """
        Suggest best times to book based on demand and pricing

        Returns:
            List of suggested time slots with reasons
        """
        try:
            low_demand = self.analyze_demand_patterns(service_type, area)

            if not low_demand:
                # Default suggestions if no historical data
                return [
                    {
                        "day": "Tuesday",
                        "time": "10:00 AM",
                        "demand_level": "Low",
                        "discount": "15%",
                        "reason": "Off-peak hours - faster service, lower prices"
                    },
                    {
                        "day": "Wednesday",
                        "time": "2:00 PM",
                        "demand_level": "Low",
                        "discount": "15%",
                        "reason": "Mid-week afternoon - minimal wait time"
                    },
                    {
                        "day": "Thursday",
                        "time": "11:00 AM",
                        "demand_level": "Low",
                        "discount": "10%",
                        "reason": "Late morning - good availability"
                    }
                ]

            suggestions = []
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

            for slot in low_demand[:3]:  # Top 3 best times
                day_name = day_names[int(slot['day_of_week'])]
                hour = int(slot['hour'])
                time_str = f"{hour}:00"

                # Calculate discount based on demand
                booking_count = slot['booking_count']
                if booking_count < 5:
                    discount = "20%"
                    demand_level = "Very Low"
                elif booking_count < 10:
                    discount = "15%"
                    demand_level = "Low"
                else:
                    discount = "10%"
                    demand_level = "Moderate"

                suggestions.append({
                    "day": day_name,
                    "time": time_str,
                    "demand_level": demand_level,
                    "discount": discount,
                    "reason": f"Off-peak hours - {demand_level.lower()} demand, faster service"
                })

            return suggestions

        except Exception as e:
            logger.error(f"Failed to suggest best time: {e}")
            return []

    def get_peak_hours_info(self) -> Dict:
        """
        Get information about peak hours

        Returns:
            Dict with peak hours and surge pricing info
        """
        current_hour = datetime.now().hour

        # Peak hours: 9-11 AM and 5-7 PM
        is_peak = (9 <= current_hour <= 11) or (17 <= current_hour <= 19)

        if is_peak:
            return {
                "is_peak": True,
                "surge_multiplier": 1.3,
                "message": "⚡ High demand period. Prices may be 30% higher.",
                "off_peak_hours": ["12:00 PM - 4:00 PM", "8:00 PM - 8:00 AM"]
            }
        else:
            return {
                "is_peak": False,
                "surge_multiplier": 1.0,
                "message": "✓ Off-peak hours. Standard pricing applies.",
                "next_peak": "5:00 PM - 7:00 PM" if current_hour < 17 else "9:00 AM - 11:00 AM (tomorrow)"
            }

    def calculate_optimal_booking_time(
        self,
        service_type: str,
        area: str,
        urgency: str
    ) -> Dict:
        """
        Calculate the optimal booking time considering all factors

        Returns:
            Dict with optimal time and reasoning
        """
        if urgency == "emergency":
            return {
                "recommended_time": "Immediate",
                "reason": "Emergency service - book now for fastest response",
                "estimated_wait": "15-30 minutes"
            }

        best_times = self.suggest_best_time(service_type, area)
        peak_info = self.get_peak_hours_info()

        if best_times:
            optimal = best_times[0]
            return {
                "recommended_time": f"{optimal['day']} at {optimal['time']}",
                "reason": optimal['reason'],
                "discount": optimal['discount'],
                "demand_level": optimal['demand_level'],
                "alternatives": best_times[1:3],
                "peak_info": peak_info
            }

        return {
            "recommended_time": "Flexible",
            "reason": "Book anytime - consistent availability",
            "peak_info": peak_info
        }

    def get_scheduling_insights(
        self,
        service_type: str,
        area: str
    ) -> Dict:
        """
        Get comprehensive scheduling insights

        Returns:
            Dict with insights and recommendations
        """
        try:
            best_times = self.suggest_best_time(service_type, area)
            peak_info = self.get_peak_hours_info()

            # Get average wait times by hour
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    EXTRACT(HOUR FROM created_at) as hour,
                    AVG(EXTRACT(EPOCH FROM (updated_at - created_at))/60) as avg_wait_minutes
                FROM bookings
                WHERE service_type = %s AND customer_location LIKE %s
                AND status = 'completed'
                GROUP BY hour
                ORDER BY avg_wait_minutes ASC
            """, (service_type, f"%{area}%"))

            wait_times = cursor.fetchall()
            cursor.close()
            conn.close()

            fastest_hours = [
                {
                    "hour": f"{int(row['hour'])}:00",
                    "avg_wait_minutes": round(row['avg_wait_minutes'], 1)
                }
                for row in wait_times[:3]
            ] if wait_times else []

            return {
                "best_times": best_times,
                "peak_info": peak_info,
                "fastest_service_hours": fastest_hours,
                "recommendation": best_times[0] if best_times else None
            }

        except Exception as e:
            logger.error(f"Failed to get scheduling insights: {e}")
            return {}
