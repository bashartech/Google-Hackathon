"""
PostgreSQL Database Manager for ServiceLink AI
Replaces JSON file operations with Neon DB (PostgreSQL) queries
"""

import psycopg2
from psycopg2.extras import RealDictCursor, Json
from typing import List, Dict, Optional
from datetime import datetime
import os
import json
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    """
    Database Manager for ServiceLink AI
    Handles all PostgreSQL database operations for providers and bookings
    """

    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL not found in environment variables")

    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)

    # ============================================================
    # SERVICE PROVIDERS MANAGEMENT
    # ============================================================

    def get_all_providers(self) -> List[Dict]:
        """Get all service providers"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                provider_id, name, owner_name, service_type, service_category,
                address, area, city, rating, reviews_count, total_jobs,
                price_range, experience_years, verified, phone, whatsapp, email,
                languages, services_offered, emergency_available, response_time_minutes,
                availability, created_at, updated_at
            FROM service_providers
            ORDER BY rating DESC, total_jobs DESC
        """)

        providers = []
        for row in cursor.fetchall():
            provider = dict(row)
            # Parse JSON fields
            provider['languages'] = json.loads(provider['languages']) if provider['languages'] else []
            provider['services_offered'] = json.loads(provider['services_offered']) if provider['services_offered'] else []
            # Restructure for compatibility
            provider['location'] = {
                'address': provider.pop('address'),
                'area': provider.pop('area'),
                'city': provider.pop('city')
            }
            provider['contact'] = {
                'phone': provider.pop('phone'),
                'whatsapp': provider.pop('whatsapp'),
                'email': provider.pop('email')
            }
            providers.append(provider)

        cursor.close()
        conn.close()
        return providers

    def get_provider_by_id(self, provider_id: str) -> Optional[Dict]:
        """Get specific service provider by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM service_providers WHERE provider_id = %s
        """, (provider_id,))

        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            return None

        provider = dict(row)
        provider['languages'] = json.loads(provider['languages']) if provider['languages'] else []
        provider['services_offered'] = json.loads(provider['services_offered']) if provider['services_offered'] else []
        provider['location'] = {
            'address': provider.pop('address'),
            'area': provider.pop('area'),
            'city': provider.pop('city')
        }
        provider['contact'] = {
            'phone': provider.pop('phone'),
            'whatsapp': provider.pop('whatsapp'),
            'email': provider.pop('email')
        }
        return provider

    def search_providers_by_service(self, service_type: str) -> List[Dict]:
        """Search providers by service type"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM service_providers
            WHERE LOWER(service_type) LIKE LOWER(%s)
            OR LOWER(service_category) LIKE LOWER(%s)
            ORDER BY rating DESC, total_jobs DESC
        """, (f"%{service_type}%", f"%{service_type}%"))

        providers = []
        for row in cursor.fetchall():
            provider = dict(row)
            provider['languages'] = json.loads(provider['languages']) if provider['languages'] else []
            provider['services_offered'] = json.loads(provider['services_offered']) if provider['services_offered'] else []
            provider['location'] = {
                'address': provider.pop('address'),
                'area': provider.pop('area'),
                'city': provider.pop('city')
            }
            provider['contact'] = {
                'phone': provider.pop('phone'),
                'whatsapp': provider.pop('whatsapp'),
                'email': provider.pop('email')
            }
            providers.append(provider)

        cursor.close()
        conn.close()
        return providers

    def search_providers_by_area(self, area: str) -> List[Dict]:
        """Search providers by area/location"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM service_providers
            WHERE LOWER(area) LIKE LOWER(%s)
            OR LOWER(city) LIKE LOWER(%s)
            ORDER BY rating DESC, total_jobs DESC
        """, (f"%{area}%", f"%{area}%"))

        providers = []
        for row in cursor.fetchall():
            provider = dict(row)
            provider['languages'] = json.loads(provider['languages']) if provider['languages'] else []
            provider['services_offered'] = json.loads(provider['services_offered']) if provider['services_offered'] else []
            provider['location'] = {
                'address': provider.pop('address'),
                'area': provider.pop('area'),
                'city': provider.pop('city')
            }
            provider['contact'] = {
                'phone': provider.pop('phone'),
                'whatsapp': provider.pop('whatsapp'),
                'email': provider.pop('email')
            }
            providers.append(provider)

        cursor.close()
        conn.close()
        return providers

    def get_all_service_types(self) -> List[str]:
        """Get all available service types"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT service_type FROM service_providers
            ORDER BY service_type
        """)

        service_types = [row['service_type'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return service_types

    def get_all_service_categories(self) -> List[str]:
        """Get all service categories"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT service_category FROM service_providers
            ORDER BY service_category
        """)

        categories = [row['service_category'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return categories

    # ============================================================
    # BOOKINGS MANAGEMENT
    # ============================================================

    def get_all_bookings(self) -> List[Dict]:
        """Get all bookings"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM bookings
            ORDER BY created_at DESC
        """)

        bookings = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return bookings

    def save_booking(self, booking: Dict) -> Dict:
        """Save a new booking to database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Generate booking ID
        cursor.execute("SELECT COUNT(*) as count FROM bookings")
        count = cursor.fetchone()['count']
        booking_id = f"BKG{count + 1:04d}"

        insert_sql = """
        INSERT INTO bookings (
            booking_id, customer_phone, customer_email, customer_name,
            customer_location, provider_id, provider_name, service_type,
            urgency, date, time, status, distance_km, estimated_cost
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING *
        """

        cursor.execute(insert_sql, (
            booking_id,
            booking.get('customer_phone'),
            booking.get('customer_email'),
            booking.get('customer_name'),
            booking.get('customer_location'),
            booking.get('provider_id'),
            booking.get('provider_name'),
            booking.get('service_type'),
            booking.get('urgency', 'normal'),
            booking.get('date'),
            booking.get('time'),
            booking.get('status', 'pending'),
            booking.get('distance_km'),
            booking.get('estimated_cost')
        ))

        new_booking = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        conn.close()

        return new_booking

    def get_booking_by_id(self, booking_id: str) -> Optional[Dict]:
        """Get specific booking by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM bookings WHERE booking_id = %s
        """, (booking_id,))

        row = cursor.fetchone()
        cursor.close()
        conn.close()

        return dict(row) if row else None

    def update_booking(self, booking_id: str, updates: Dict) -> Optional[Dict]:
        """Update an existing booking"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Build dynamic UPDATE query
        set_clauses = []
        values = []

        for key, value in updates.items():
            set_clauses.append(f"{key} = %s")
            values.append(value)

        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values.append(booking_id)

        update_sql = f"""
        UPDATE bookings
        SET {', '.join(set_clauses)}
        WHERE booking_id = %s
        RETURNING *
        """

        cursor.execute(update_sql, values)
        row = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        return dict(row) if row else None

    def get_bookings_by_customer(self, customer_phone: str) -> List[Dict]:
        """Get all bookings for a specific customer"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM bookings
            WHERE customer_phone = %s
            ORDER BY created_at DESC
        """, (customer_phone,))

        bookings = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return bookings

    def get_bookings_by_provider(self, provider_id: str) -> List[Dict]:
        """Get all bookings for a specific provider"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM bookings
            WHERE provider_id = %s
            ORDER BY created_at DESC
        """, (provider_id,))

        bookings = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return bookings

    def get_bookings_by_status(self, status: str) -> List[Dict]:
        """Get all bookings with specific status"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM bookings
            WHERE LOWER(status) = LOWER(%s)
            ORDER BY created_at DESC
        """, (status,))

        bookings = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return bookings

    def get_statistics(self) -> Dict:
        """Get database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()

        stats = {}

        # Total providers
        cursor.execute("SELECT COUNT(*) as count FROM service_providers")
        stats['total_providers'] = cursor.fetchone()['count']

        # Total bookings
        cursor.execute("SELECT COUNT(*) as count FROM bookings")
        stats['total_bookings'] = cursor.fetchone()['count']

        # Bookings by status
        cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE status = 'pending'")
        stats['pending_bookings'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE status = 'confirmed'")
        stats['confirmed_bookings'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE status = 'completed'")
        stats['completed_bookings'] = cursor.fetchone()['count']

        cursor.close()
        conn.close()

        return stats

    # Legacy methods for backward compatibility
    def load_service_providers(self) -> Dict:
        """Load all service providers (legacy compatibility)"""
        providers = self.get_all_providers()
        service_types = self.get_all_service_types()
        categories = self.get_all_service_categories()

        return {
            "providers": providers,
            "service_types": service_types,
            "service_categories": categories
        }

    def load_bookings(self) -> List[Dict]:
        """Load all bookings (legacy compatibility)"""
        return self.get_all_bookings()
