"""
Matching Engine for ServiceLink AI
Handles provider matching, ranking, and availability checking
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json

class MatchingEngine:
    """
    Provider matching and ranking engine
    Matches customer requests with best available providers
    """

    def __init__(self, db_manager, location_service):
        self.db = db_manager
        self.location_service = location_service

    def find_matching_providers(
        self,
        service_type: str,
        customer_location: str,
        urgency: str = 'normal',
        max_distance_km: float = 20.0,
        min_rating: float = 4.0
    ) -> List[Dict]:
        """
        Find providers matching service request criteria

        Args:
            service_type: Type of service needed
            customer_location: Customer's address
            urgency: Request urgency level
            max_distance_km: Maximum distance in kilometers
            min_rating: Minimum provider rating

        Returns:
            List of matching providers with ranking scores
        """
        # Get all providers for this service type
        all_providers = self.db.search_providers_by_service(service_type)

        if not all_providers:
            return []

        # Filter by minimum rating
        qualified_providers = [
            p for p in all_providers
            if p.get('rating', 0) >= min_rating and p.get('verified', False)
        ]

        if not qualified_providers:
            return []

        # Find nearby providers and calculate distances
        nearby_providers = self.location_service.find_nearby_providers(
            customer_location,
            qualified_providers,
            max_distance_km
        )

        if not nearby_providers:
            return []

        # Rank providers based on multiple factors
        priority_factors = self._get_priority_factors(urgency)
        ranked_providers = self.location_service.rank_providers(
            nearby_providers,
            customer_location,
            priority_factors
        )

        return ranked_providers

    def _get_priority_factors(self, urgency: str) -> Dict[str, float]:
        """
        Get ranking priority factors based on urgency level

        Args:
            urgency: Request urgency level

        Returns:
            Dict with priority weights
        """
        if urgency == 'emergency':
            # Emergency: prioritize response time and distance
            return {
                'distance': 0.35,
                'rating': 0.20,
                'response_time': 0.40,
                'experience': 0.05
            }
        elif urgency == 'high':
            # High priority: balance between speed and quality
            return {
                'distance': 0.30,
                'rating': 0.35,
                'response_time': 0.25,
                'experience': 0.10
            }
        else:
            # Normal: prioritize quality and experience
            return {
                'distance': 0.25,
                'rating': 0.40,
                'response_time': 0.15,
                'experience': 0.20
            }

    def check_provider_availability(
        self,
        provider_id: str,
        requested_date: str,
        requested_time: str
    ) -> Dict:
        """
        Check if provider is available at requested time

        Args:
            provider_id: Provider ID
            requested_date: Requested date (YYYY-MM-DD)
            requested_time: Requested time (e.g., "10AM", "2PM")

        Returns:
            Dict with availability status and details
        """
        provider = self.db.get_provider_by_id(provider_id)

        if not provider:
            return {
                'available': False,
                'reason': 'Provider not found'
            }

        # Parse requested date
        try:
            date_obj = datetime.strptime(requested_date, '%Y-%m-%d')
            day_name = date_obj.strftime('%A').lower()
        except ValueError:
            return {
                'available': False,
                'reason': 'Invalid date format'
            }

        # Check provider's availability schedule
        availability = provider.get('availability', {})
        day_slots = availability.get(day_name, [])

        if requested_time not in day_slots:
            return {
                'available': False,
                'reason': f'Provider not available on {day_name} at {requested_time}',
                'available_slots': day_slots
            }

        # Check existing bookings for conflicts
        existing_bookings = self.db.get_bookings_by_provider(provider_id)
        for booking in existing_bookings:
            if (booking.get('date') == requested_date and
                booking.get('time') == requested_time and
                booking.get('status') in ['pending', 'confirmed']):
                return {
                    'available': False,
                    'reason': 'Time slot already booked',
                    'available_slots': self._get_available_slots(
                        provider_id, requested_date, day_slots
                    )
                }

        return {
            'available': True,
            'provider': provider,
            'date': requested_date,
            'time': requested_time,
            'day': day_name
        }

    def _get_available_slots(
        self,
        provider_id: str,
        date: str,
        all_slots: List[str]
    ) -> List[str]:
        """
        Get available time slots for a provider on a specific date

        Args:
            provider_id: Provider ID
            date: Date to check (YYYY-MM-DD)
            all_slots: All possible time slots for that day

        Returns:
            List of available time slots
        """
        existing_bookings = self.db.get_bookings_by_provider(provider_id)

        booked_slots = [
            b.get('time') for b in existing_bookings
            if b.get('date') == date and b.get('status') in ['pending', 'confirmed']
        ]

        available_slots = [slot for slot in all_slots if slot not in booked_slots]
        return available_slots

    def suggest_alternative_times(
        self,
        provider_id: str,
        requested_date: str,
        days_ahead: int = 3
    ) -> List[Dict]:
        """
        Suggest alternative available time slots

        Args:
            provider_id: Provider ID
            requested_date: Original requested date
            days_ahead: Number of days to look ahead

        Returns:
            List of alternative time slots
        """
        provider = self.db.get_provider_by_id(provider_id)

        if not provider:
            return []

        alternatives = []
        date_obj = datetime.strptime(requested_date, '%Y-%m-%d')

        for i in range(days_ahead):
            check_date = date_obj + timedelta(days=i)
            check_date_str = check_date.strftime('%Y-%m-%d')
            day_name = check_date.strftime('%A').lower()

            # Get provider's availability for this day
            availability = provider.get('availability', {})
            day_slots = availability.get(day_name, [])

            if not day_slots:
                continue

            # Get available slots
            available_slots = self._get_available_slots(
                provider_id,
                check_date_str,
                day_slots
            )

            for slot in available_slots:
                alternatives.append({
                    'date': check_date_str,
                    'day': day_name.capitalize(),
                    'time': slot,
                    'provider_id': provider_id,
                    'provider_name': provider.get('name')
                })

        return alternatives[:5]  # Return top 5 alternatives

    def suggest_alternative_providers(
        self,
        service_type: str,
        customer_location: str,
        requested_date: str,
        requested_time: str,
        exclude_provider_ids: List[str] = None
    ) -> List[Dict]:
        """
        Suggest alternative providers for the same service

        Args:
            service_type: Type of service
            customer_location: Customer's location
            requested_date: Requested date
            requested_time: Requested time
            exclude_provider_ids: Provider IDs to exclude

        Returns:
            List of alternative providers with availability
        """
        if exclude_provider_ids is None:
            exclude_provider_ids = []

        # Find all matching providers
        all_providers = self.find_matching_providers(
            service_type,
            customer_location
        )

        # Filter out excluded providers
        available_providers = [
            p for p in all_providers
            if p.get('provider_id') not in exclude_provider_ids
        ]

        # Check availability for each provider
        alternatives = []
        for provider in available_providers[:10]:  # Check top 10
            availability = self.check_provider_availability(
                provider.get('provider_id'),
                requested_date,
                requested_time
            )

            if availability.get('available'):
                alternatives.append({
                    'provider': provider,
                    'distance_km': provider.get('distance_km'),
                    'ranking_score': provider.get('ranking_score'),
                    'date': requested_date,
                    'time': requested_time
                })

        return alternatives[:3]  # Return top 3 alternatives

    def calculate_estimated_cost(
        self,
        provider_id: str,
        service_type: str,
        urgency: str = 'normal'
    ) -> Dict:
        """
        Calculate estimated service cost

        Args:
            provider_id: Provider ID
            service_type: Type of service
            urgency: Request urgency

        Returns:
            Dict with cost estimate
        """
        provider = self.db.get_provider_by_id(provider_id)

        if not provider:
            return {'error': 'Provider not found'}

        price_range = provider.get('price_range', 'PKR 0-0')

        # Parse price range (e.g., "PKR 1500-3000")
        try:
            price_parts = price_range.replace('PKR', '').strip().split('-')
            min_price = int(price_parts[0].strip())
            max_price = int(price_parts[1].strip())
            avg_price = (min_price + max_price) / 2
        except (ValueError, IndexError):
            return {'error': 'Invalid price range'}

        # Apply urgency multiplier
        urgency_multipliers = {
            'emergency': 1.5,  # 50% surcharge
            'high': 1.2,       # 20% surcharge
            'normal': 1.0      # No surcharge
        }

        multiplier = urgency_multipliers.get(urgency, 1.0)
        estimated_cost = avg_price * multiplier

        return {
            'provider_id': provider_id,
            'provider_name': provider.get('name'),
            'base_price_range': price_range,
            'urgency': urgency,
            'urgency_multiplier': multiplier,
            'estimated_cost': f"PKR {int(estimated_cost)}",
            'min_cost': f"PKR {int(min_price * multiplier)}",
            'max_cost': f"PKR {int(max_price * multiplier)}"
        }

    def get_provider_statistics(self, provider_id: str) -> Dict:
        """
        Get provider performance statistics

        Args:
            provider_id: Provider ID

        Returns:
            Dict with provider statistics
        """
        provider = self.db.get_provider_by_id(provider_id)

        if not provider:
            return {'error': 'Provider not found'}

        bookings = self.db.get_bookings_by_provider(provider_id)

        completed_bookings = [b for b in bookings if b.get('status') == 'completed']
        cancelled_bookings = [b for b in bookings if b.get('status') == 'cancelled']

        completion_rate = (
            len(completed_bookings) / len(bookings) * 100
            if bookings else 0
        )

        return {
            'provider_id': provider_id,
            'provider_name': provider.get('name'),
            'rating': provider.get('rating'),
            'reviews_count': provider.get('reviews_count'),
            'total_jobs': provider.get('total_jobs'),
            'experience_years': provider.get('experience_years'),
            'total_bookings': len(bookings),
            'completed_bookings': len(completed_bookings),
            'cancelled_bookings': len(cancelled_bookings),
            'completion_rate': round(completion_rate, 2),
            'emergency_available': provider.get('emergency_available'),
            'response_time_minutes': provider.get('response_time_minutes')
        }
