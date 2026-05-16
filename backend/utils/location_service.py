"""
Location Service for ServiceLink AI
Handles location-based provider matching with optional Google Maps API
Falls back to extensive mock coordinates for Karachi, Islamabad, Lahore
"""

import googlemaps
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class LocationService:
    """
    Location service with optional Google Maps API integration
    Falls back to extensive mock coordinates for major Pakistani cities
    """

    def __init__(self):
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        self.gmaps_available = False
        self.cache = {}  # Simple in-memory cache for geocoded addresses

        # Try to initialize Google Maps API (optional)
        if self.api_key and self.api_key != 'your_google_maps_api_key_here':
            try:
                self.gmaps = googlemaps.Client(key=self.api_key)
                # Test the API with a simple request
                test_result = self.gmaps.geocode("Islamabad, Pakistan")
                if test_result:
                    self.gmaps_available = True
                    logger.info("✅ Google Maps API initialized successfully")
                else:
                    logger.warning("⚠️ Google Maps API test failed - using mock data")
                    self.gmaps = None
            except Exception as e:
                logger.warning(f"⚠️ Google Maps API error: {str(e)[:100]}")
                logger.info("⚠️ Using mock location data for Karachi, Islamabad, Lahore")
                self.gmaps = None
        else:
            logger.info("⚠️ Google Maps API not configured - using mock location data")
            self.gmaps = None

    def geocode_location(self, address: str) -> Optional[Dict]:
        """
        Convert address to coordinates using Google Maps Geocoding API
        Falls back to mock coordinates if API unavailable

        Args:
            address: Full address string or area name

        Returns:
            Dict with lat, lng, formatted_address
        """
        # Check cache first
        if address in self.cache:
            return self.cache[address]

        # If Google Maps available, use real API
        if self.gmaps_available:
            try:
                geocode_result = self.gmaps.geocode(address)

                if not geocode_result:
                    logger.warning(f"No geocoding results for '{address}', using fallback")
                    return self._get_fallback_coordinates(address)

                location = geocode_result[0]['geometry']['location']
                formatted_address = geocode_result[0]['formatted_address']

                result = {
                    'lat': location['lat'],
                    'lng': location['lng'],
                    'formatted_address': formatted_address
                }

                # Cache the result
                self.cache[address] = result
                return result

            except googlemaps.exceptions.ApiError as e:
                logger.error(f"Google Maps API Error: {str(e)[:100]}")
                return self._get_fallback_coordinates(address)
            except Exception as e:
                logger.error(f"Geocoding error: {str(e)[:100]}")
                return self._get_fallback_coordinates(address)

        # FALLBACK MODE: Use mock coordinates
        return self._get_fallback_coordinates(address)

    def _get_fallback_coordinates(self, address: str) -> Optional[Dict]:
        """
        Fallback method: Returns mock coordinates for major Pakistani cities
        Extensive coverage for Karachi, Islamabad, and Lahore
        """
        # Mock coordinates for Karachi, Islamabad, Lahore areas
        area_coords = {
            # KARACHI - Major areas
            'karachi': {'lat': 24.8607, 'lng': 67.0011, 'city': 'Karachi'},
            'clifton': {'lat': 24.8138, 'lng': 67.0299, 'city': 'Karachi'},
            'defence': {'lat': 24.8059, 'lng': 67.0761, 'city': 'Karachi'},
            'dha': {'lat': 24.8059, 'lng': 67.0761, 'city': 'Karachi'},
            'gulshan': {'lat': 24.9207, 'lng': 67.0824, 'city': 'Karachi'},
            'gulshan-e-iqbal': {'lat': 24.9207, 'lng': 67.0824, 'city': 'Karachi'},
            'north nazimabad': {'lat': 24.9260, 'lng': 67.0333, 'city': 'Karachi'},
            'nazimabad': {'lat': 24.9260, 'lng': 67.0333, 'city': 'Karachi'},
            'saddar': {'lat': 24.8546, 'lng': 67.0271, 'city': 'Karachi'},
            'malir': {'lat': 24.8943, 'lng': 67.2060, 'city': 'Karachi'},
            'korangi': {'lat': 24.8418, 'lng': 67.1157, 'city': 'Karachi'},
            'landhi': {'lat': 24.8481, 'lng': 67.1929, 'city': 'Karachi'},
            'shah faisal': {'lat': 24.8897, 'lng': 67.1329, 'city': 'Karachi'},
            'bahadurabad': {'lat': 24.8774, 'lng': 67.0697, 'city': 'Karachi'},
            'tariq road': {'lat': 24.8700, 'lng': 67.0600, 'city': 'Karachi'},
            'pechs': {'lat': 24.8700, 'lng': 67.0650, 'city': 'Karachi'},
            'fb area': {'lat': 24.8900, 'lng': 67.0700, 'city': 'Karachi'},
            'north karachi': {'lat': 24.9800, 'lng': 67.0500, 'city': 'Karachi'},
            'surjani town': {'lat': 25.0400, 'lng': 67.0800, 'city': 'Karachi'},
            'bahria town karachi': {'lat': 24.9200, 'lng': 67.2000, 'city': 'Karachi'},

            # ISLAMABAD - All sectors
            'islamabad': {'lat': 33.6844, 'lng': 73.0479, 'city': 'Islamabad'},
            'blue area': {'lat': 33.7181, 'lng': 73.0776, 'city': 'Islamabad'},
            'f-6': {'lat': 33.7294, 'lng': 73.0551, 'city': 'Islamabad'},
            'f-7': {'lat': 33.7215, 'lng': 73.0433, 'city': 'Islamabad'},
            'f-8': {'lat': 33.7098, 'lng': 73.0551, 'city': 'Islamabad'},
            'f-10': {'lat': 33.7098, 'lng': 73.0279, 'city': 'Islamabad'},
            'f-11': {'lat': 33.6973, 'lng': 73.0279, 'city': 'Islamabad'},
            'g-6': {'lat': 33.7181, 'lng': 73.0669, 'city': 'Islamabad'},
            'g-7': {'lat': 33.7098, 'lng': 73.0669, 'city': 'Islamabad'},
            'g-8': {'lat': 33.6973, 'lng': 73.0669, 'city': 'Islamabad'},
            'g-9': {'lat': 33.6844, 'lng': 73.0669, 'city': 'Islamabad'},
            'g-10': {'lat': 33.7098, 'lng': 73.0515, 'city': 'Islamabad'},
            'g-11': {'lat': 33.6973, 'lng': 73.0515, 'city': 'Islamabad'},
            'g-13': {'lat': 33.6844, 'lng': 73.0479, 'city': 'Islamabad'},
            'g-14': {'lat': 33.6715, 'lng': 73.0479, 'city': 'Islamabad'},
            'i-8': {'lat': 33.6688, 'lng': 73.0746, 'city': 'Islamabad'},
            'i-9': {'lat': 33.6593, 'lng': 73.0746, 'city': 'Islamabad'},
            'i-10': {'lat': 33.6498, 'lng': 73.0746, 'city': 'Islamabad'},
            'i-11': {'lat': 33.6403, 'lng': 73.0746, 'city': 'Islamabad'},
            'i-14': {'lat': 33.6215, 'lng': 73.0746, 'city': 'Islamabad'},
            'bahria town': {'lat': 33.5651, 'lng': 73.1350, 'city': 'Islamabad'},
            'dha islamabad': {'lat': 33.5800, 'lng': 73.1200, 'city': 'Islamabad'},
            'pwd': {'lat': 33.7050, 'lng': 73.0900, 'city': 'Islamabad'},

            # LAHORE - Major areas
            'lahore': {'lat': 31.5204, 'lng': 74.3587, 'city': 'Lahore'},
            'gulberg': {'lat': 31.5080, 'lng': 74.3436, 'city': 'Lahore'},
            'model town': {'lat': 31.4814, 'lng': 74.3160, 'city': 'Lahore'},
            'johar town': {'lat': 31.4697, 'lng': 74.2728, 'city': 'Lahore'},
            'dha lahore': {'lat': 31.4697, 'lng': 74.4097, 'city': 'Lahore'},
            'cantt': {'lat': 31.5656, 'lng': 74.3242, 'city': 'Lahore'},
            'mall road': {'lat': 31.5656, 'lng': 74.3242, 'city': 'Lahore'},
            'faisal town': {'lat': 31.4315, 'lng': 74.2572, 'city': 'Lahore'},
            'iqbal town': {'lat': 31.5080, 'lng': 74.2900, 'city': 'Lahore'},
            'garden town': {'lat': 31.4900, 'lng': 74.3200, 'city': 'Lahore'},
            'township': {'lat': 31.4500, 'lng': 74.3200, 'city': 'Lahore'},
            'wapda town': {'lat': 31.4200, 'lng': 74.2600, 'city': 'Lahore'},
            'bahria town lahore': {'lat': 31.3400, 'lng': 74.1900, 'city': 'Lahore'},
            'allama iqbal town': {'lat': 31.5200, 'lng': 74.2900, 'city': 'Lahore'},
            'shadman': {'lat': 31.5500, 'lng': 74.3100, 'city': 'Lahore'},
            'liberty': {'lat': 31.5100, 'lng': 74.3500, 'city': 'Lahore'},
            'mm alam road': {'lat': 31.5100, 'lng': 74.3500, 'city': 'Lahore'},
        }

        # Extract area from address
        address_lower = address.lower()
        for area, coords in area_coords.items():
            if area in address_lower:
                result = {
                    'lat': coords['lat'],
                    'lng': coords['lng'],
                    'formatted_address': f"{address}, {coords['city']}, Pakistan"
                }
                self.cache[address] = result
                return result

        # Default to Islamabad if no area found
        result = {
            'lat': 33.6844,
            'lng': 73.0479,
            'formatted_address': f"{address}, Islamabad, Pakistan"
        }
        self.cache[address] = result
        return result

    def calculate_distance(self, origin: str, destination: str) -> Optional[Dict]:
        """
        Calculate distance and duration between two addresses
        Uses Google Maps Distance Matrix API if available, otherwise Haversine formula

        Args:
            origin: Origin address
            destination: Destination address

        Returns:
            Dict with distance_km, distance_text, duration_minutes, duration_text
        """
        # If Google Maps available, use real API
        if self.gmaps_available:
            try:
                distance_result = self.gmaps.distance_matrix(
                    origins=[origin],
                    destinations=[destination],
                    mode="driving",
                    units="metric"
                )

                if distance_result['status'] != 'OK':
                    logger.warning(f"Distance Matrix API status: {distance_result['status']}, using fallback")
                    return self._calculate_haversine_distance(origin, destination)

                element = distance_result['rows'][0]['elements'][0]

                if element['status'] != 'OK':
                    logger.warning(f"Distance calculation status: {element['status']}, using fallback")
                    return self._calculate_haversine_distance(origin, destination)

                distance_meters = element['distance']['value']
                distance_text = element['distance']['text']
                duration_seconds = element['duration']['value']
                duration_text = element['duration']['text']

                return {
                    'distance_km': round(distance_meters / 1000, 2),
                    'distance_text': distance_text,
                    'duration_minutes': round(duration_seconds / 60, 1),
                    'duration_text': duration_text
                }

            except Exception as e:
                logger.error(f"Distance calculation error: {str(e)[:100]}, using fallback")
                return self._calculate_haversine_distance(origin, destination)

        # FALLBACK: Use Haversine formula
        return self._calculate_haversine_distance(origin, destination)

    def _calculate_haversine_distance(self, origin: str, destination: str) -> Optional[Dict]:
        """
        Calculate distance using Haversine formula (straight-line distance)
        """
        from math import radians, sin, cos, sqrt, atan2

        # Get coordinates for both locations
        origin_coords = self.geocode_location(origin)
        dest_coords = self.geocode_location(destination)

        if not origin_coords or not dest_coords:
            return None

        # Haversine formula
        R = 6371  # Earth's radius in kilometers

        lat1 = radians(origin_coords['lat'])
        lon1 = radians(origin_coords['lng'])
        lat2 = radians(dest_coords['lat'])
        lon2 = radians(dest_coords['lng'])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance_km = R * c

        # Estimate duration (assuming 30 km/h average speed in city)
        duration_minutes = (distance_km / 30) * 60

        return {
            'distance_km': round(distance_km, 2),
            'distance_text': f"{round(distance_km, 1)} km",
            'duration_minutes': round(duration_minutes, 1),
            'duration_text': f"{round(duration_minutes)} mins"
        }

    def calculate_distance_haversine(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        Fallback method when Distance Matrix API is not needed

        Args:
            lat1, lng1: Origin coordinates
            lat2, lng2: Destination coordinates

        Returns:
            Distance in kilometers
        """
        from math import radians, sin, cos, sqrt, atan2

        R = 6371  # Earth's radius in kilometers

        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lng = radians(lng2 - lng1)

        a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lng / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return round(distance, 2)

    def find_nearby_providers(
        self,
        customer_address: str,
        providers: List[Dict],
        max_distance_km: float = 20.0
    ) -> List[Dict]:
        """
        Find providers near customer location and rank by distance

        Args:
            customer_address: Customer's address
            providers: List of provider dictionaries with location data
            max_distance_km: Maximum distance in kilometers (default 20km)

        Returns:
            List of providers with distance info, sorted by distance
        """
        # Geocode customer address
        customer_location = self.geocode_location(customer_address)

        if not customer_location:
            print(f"❌ Failed to geocode customer address: {customer_address}")
            return []

        customer_lat = customer_location['lat']
        customer_lng = customer_location['lng']

        nearby_providers = []

        for provider in providers:
            provider_address = provider.get('location', {}).get('address')

            if not provider_address:
                continue

            # Geocode provider address
            provider_location = self.geocode_location(provider_address)

            if not provider_location:
                print(f"⚠️ Failed to geocode provider address: {provider_address}")
                continue

            provider_lat = provider_location['lat']
            provider_lng = provider_location['lng']

            # Calculate distance using Haversine formula
            distance_km = self.calculate_distance_haversine(
                customer_lat, customer_lng,
                provider_lat, provider_lng
            )

            # Filter by max distance
            if distance_km <= max_distance_km:
                provider_with_distance = provider.copy()
                provider_with_distance['distance_km'] = distance_km
                provider_with_distance['coordinates'] = {
                    'lat': provider_lat,
                    'lng': provider_lng
                }
                nearby_providers.append(provider_with_distance)

        # Sort by distance (closest first)
        nearby_providers.sort(key=lambda p: p['distance_km'])

        return nearby_providers

    def rank_providers(
        self,
        providers: List[Dict],
        customer_address: str,
        priority_factors: Dict = None
    ) -> List[Dict]:
        """
        Rank providers based on multiple factors:
        - Distance (40% weight)
        - Rating (30% weight)
        - Response time (20% weight)
        - Experience (10% weight)

        Args:
            providers: List of providers with distance info
            customer_address: Customer's address (for distance calculation)
            priority_factors: Optional custom weights for ranking

        Returns:
            List of providers sorted by ranking score
        """
        if not priority_factors:
            priority_factors = {
                'distance': 0.40,
                'rating': 0.30,
                'response_time': 0.20,
                'experience': 0.10
            }

        # Find nearby providers first
        providers_with_distance = self.find_nearby_providers(customer_address, providers)

        if not providers_with_distance:
            return []

        # Calculate ranking scores
        for provider in providers_with_distance:
            # Distance score (inverse - closer is better)
            max_distance = max(p['distance_km'] for p in providers_with_distance)
            distance_score = (1 - (provider['distance_km'] / max_distance)) * 100 if max_distance > 0 else 100

            # Rating score (out of 5, convert to 100)
            rating_score = (provider.get('rating', 0) / 5.0) * 100

            # Response time score (inverse - faster is better)
            max_response_time = max(p.get('response_time_minutes', 60) for p in providers_with_distance)
            response_time_score = (1 - (provider.get('response_time_minutes', 60) / max_response_time)) * 100 if max_response_time > 0 else 100

            # Experience score (years)
            max_experience = max(p.get('experience_years', 1) for p in providers_with_distance)
            experience_score = (provider.get('experience_years', 0) / max_experience) * 100 if max_experience > 0 else 0

            # Calculate weighted total score
            total_score = (
                distance_score * priority_factors['distance'] +
                rating_score * priority_factors['rating'] +
                response_time_score * priority_factors['response_time'] +
                experience_score * priority_factors['experience']
            )

            provider['ranking_score'] = round(total_score, 2)
            provider['score_breakdown'] = {
                'distance_score': round(distance_score, 2),
                'rating_score': round(rating_score, 2),
                'response_time_score': round(response_time_score, 2),
                'experience_score': round(experience_score, 2)
            }

        # Sort by ranking score (highest first)
        providers_with_distance.sort(key=lambda p: p['ranking_score'], reverse=True)

        return providers_with_distance

    def validate_address(self, address: str) -> bool:
        """
        Validate if an address can be geocoded

        Args:
            address: Address string to validate

        Returns:
            True if address is valid, False otherwise
        """
        result = self.geocode_location(address)
        return result is not None

    def get_travel_time(self, origin: str, destination: str) -> Optional[int]:
        """
        Get estimated travel time in minutes between two addresses

        Args:
            origin: Origin address
            destination: Destination address

        Returns:
            Travel time in minutes or None if calculation fails
        """
        distance_info = self.calculate_distance(origin, destination)

        if distance_info:
            return distance_info['duration_minutes']

        return None
