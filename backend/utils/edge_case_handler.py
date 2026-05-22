"""
Edge Case Handler for ServiceLink AI
Handles various edge cases in the booking workflow
"""

from datetime import datetime, time
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class EdgeCaseHandler:
    """
    Handles edge cases and exceptional scenarios
    """

    def __init__(self, db_manager, location_service):
        self.db = db_manager
        self.location_service = location_service

    def check_no_providers_available(
        self,
        service_type: str,
        location: str,
        matched_providers: List[Dict]
    ) -> Optional[Dict]:
        """
        Handle case when no providers are found

        Returns:
            Response dict if edge case applies, None otherwise
        """
        if not matched_providers:
            # Suggest nearby areas
            nearby_areas = self._get_nearby_areas(location)

            return {
                "status": "no_providers",
                "message": f"Sorry, no {service_type} providers available in {location}.",
                "suggestions": {
                    "nearby_areas": nearby_areas,
                    "alternative_services": self._get_alternative_services(service_type),
                    "action": "Try searching in nearby areas or contact us to expand service coverage"
                }
            }

        return None

    def check_all_providers_busy(
        self,
        matched_providers: List[Dict],
        requested_date: str
    ) -> Optional[Dict]:
        """
        Handle case when all providers are fully booked

        Returns:
            Response dict if edge case applies, None otherwise
        """
        from utils.calendar_service import CalendarService
        calendar_service = CalendarService(self.db)

        # Check if any provider has availability
        for provider in matched_providers:
            slots = calendar_service.get_available_slots(provider['provider_id'], requested_date)
            if slots:
                return None  # At least one provider available

        # All providers busy - find next available date
        next_available = None
        for provider in matched_providers:
            provider_next = calendar_service.get_next_available_date(provider['provider_id'])
            if provider_next:
                if not next_available or provider_next['date'] < next_available['date']:
                    next_available = provider_next
                    next_available['provider_name'] = provider['name']

        if next_available:
            return {
                "status": "all_busy",
                "message": f"All providers are fully booked on {requested_date}.",
                "next_available": next_available,
                "action": "waitlist",
                "suggestion": f"Next available: {next_available['day_name']}, {next_available['date']} with {next_available['provider_name']}"
            }

        return {
            "status": "all_busy",
            "message": "All providers are fully booked for the next week.",
            "action": "contact_support",
            "suggestion": "Please contact support or try again later"
        }

    def check_service_not_in_city(
        self,
        service_type: str,
        city: str
    ) -> Optional[Dict]:
        """
        Handle case when service is not available in the city

        Returns:
            Response dict if edge case applies, None otherwise
        """
        supported_cities = ['Karachi', 'Islamabad', 'Lahore']

        if city not in supported_cities:
            return {
                "status": "area_not_covered",
                "message": f"We don't operate in {city} yet.",
                "supported_cities": supported_cities,
                "action": "expansion_request",
                "suggestion": "We're expanding soon! Leave your contact info to be notified when we launch in your area."
            }

        return None

    def check_peak_hours_surge(self) -> Optional[Dict]:
        """
        Check if current time is peak hours and apply surge pricing

        Returns:
            Response dict if surge pricing applies, None otherwise
        """
        current_hour = datetime.now().hour

        # Peak hours: 9-11 AM and 5-7 PM
        is_peak = (9 <= current_hour <= 11) or (17 <= current_hour <= 19)

        if is_peak:
            surge_multiplier = 1.3
            return {
                "status": "surge_pricing",
                "message": f"⚡ High demand period. Prices may be {int((surge_multiplier-1)*100)}% higher.",
                "surge_multiplier": surge_multiplier,
                "action": "confirm_surge",
                "suggestion": "Book now or wait for off-peak hours (after 7 PM or before 9 AM) for standard pricing"
            }

        return None

    def check_emergency_availability(
        self,
        urgency: str,
        matched_providers: List[Dict]
    ) -> Optional[Dict]:
        """
        Handle emergency requests when no emergency-ready providers available

        Returns:
            Response dict if edge case applies, None otherwise
        """
        if urgency == "emergency":
            emergency_providers = [p for p in matched_providers if p.get('emergency_available')]

            if not emergency_providers:
                return {
                    "status": "no_emergency_providers",
                    "message": "No emergency-ready providers available right now.",
                    "alternatives": {
                        "regular_providers": len(matched_providers),
                        "estimated_response": "30-60 minutes (non-emergency)",
                        "action": "Book regular provider or wait for emergency provider"
                    }
                }

        return None

    def check_weather_conditions(self, location: str) -> Optional[Dict]:
        """
        Check weather conditions and warn if severe

        Returns:
            Response dict if weather alert applies, None otherwise
        """
        # In production, integrate with weather API
        # For now, return None (no weather issues)
        # Example implementation:
        # weather_status = weather_api.get_current_weather(location)
        # if weather_status == 'severe':
        #     return {
        #         "status": "weather_alert",
        #         "message": "⚠️ Severe weather alert in your area. Service may be delayed.",
        #         "action": "confirm_booking",
        #         "suggestion": "Continue booking with possible delays, or reschedule for better weather"
        #     }

        return None

    def check_minimum_booking_value(
        self,
        service_type: str,
        estimated_cost: str
    ) -> Optional[Dict]:
        """
        Check if booking meets minimum value requirements

        Returns:
            Response dict if minimum not met, None otherwise
        """
        # Extract numeric value from estimated_cost (e.g., "Rs. 1500-2000")
        try:
            import re
            numbers = re.findall(r'\d+', estimated_cost)
            if numbers:
                min_cost = int(numbers[0])

                # Minimum booking value: Rs. 500
                if min_cost < 500:
                    return {
                        "status": "below_minimum",
                        "message": "Minimum booking value is Rs. 500.",
                        "current_estimate": estimated_cost,
                        "action": "add_services",
                        "suggestion": "Consider adding additional services to meet minimum booking value"
                    }
        except:
            pass

        return None

    def _get_nearby_areas(self, location: str) -> List[str]:
        """Get nearby areas for a location"""
        # Simplified mapping - in production, use geolocation
        area_map = {
            'Gulshan': ['DHA', 'Clifton', 'Nazimabad'],
            'DHA': ['Gulshan', 'Clifton', 'Korangi'],
            'Clifton': ['DHA', 'Saddar', 'Gulshan'],
            'F-6': ['F-7', 'G-6', 'G-8'],
            'G-8': ['F-6', 'G-9', 'G-10'],
            'Johar Town': ['DHA Lahore', 'Gulberg', 'Model Town'],
        }

        return area_map.get(location, ['Contact support for area expansion'])

    def _get_alternative_services(self, service_type: str) -> List[str]:
        """Get alternative services"""
        alternatives_map = {
            'AC Repair': ['Electrician', 'Home Cleaning'],
            'Plumbing': ['Electrician', 'Carpenter'],
            'Electrician': ['AC Repair', 'Plumbing'],
            'Home Cleaning': ['Painter', 'Carpenter'],
            'Carpenter': ['Painter', 'Home Cleaning'],
            'Painter': ['Carpenter', 'Home Cleaning'],
        }

        return alternatives_map.get(service_type, [])

    def handle_all_edge_cases(
        self,
        service_type: str,
        location: str,
        city: str,
        urgency: str,
        matched_providers: List[Dict],
        requested_date: str = None
    ) -> Optional[Dict]:
        """
        Check all edge cases and return first applicable one

        Returns:
            Response dict if any edge case applies, None otherwise
        """
        # Check in priority order
        edge_cases = [
            self.check_service_not_in_city(service_type, city),
            self.check_no_providers_available(service_type, location, matched_providers),
            self.check_emergency_availability(urgency, matched_providers) if matched_providers else None,
            self.check_all_providers_busy(matched_providers, requested_date) if matched_providers and requested_date else None,
            self.check_weather_conditions(location),
            self.check_peak_hours_surge(),
        ]

        # Return first applicable edge case
        for edge_case in edge_cases:
            if edge_case:
                logger.info(f"Edge case detected: {edge_case['status']}")
                return edge_case

        return None
