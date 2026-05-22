"""
Migration script to load JSON data into Neon DB (PostgreSQL)
Run this once to migrate from JSON files to PostgreSQL database
"""

import json
import os
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv
from schema import CREATE_TABLES_SQL, DROP_TABLES_SQL

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def get_connection():
    """Get database connection"""
    return psycopg2.connect(DATABASE_URL)

def create_tables(conn):
    """Create database tables"""
    print("Creating tables...")
    cursor = conn.cursor()
    cursor.execute(CREATE_TABLES_SQL)
    conn.commit()
    cursor.close()
    print("✅ Tables created successfully")

def drop_tables(conn):
    """Drop all tables (use with caution!)"""
    print("Dropping existing tables...")
    cursor = conn.cursor()
    cursor.execute(DROP_TABLES_SQL)
    conn.commit()
    cursor.close()
    print("✅ Tables dropped")

def migrate_providers(conn):
    """Migrate service providers from JSON to PostgreSQL"""
    print("\nMigrating service providers...")

    # Load JSON data
    json_file = os.path.join(os.path.dirname(__file__), 'service_providers.json')
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    providers = data.get('providers', [])
    cursor = conn.cursor()

    insert_sql = """
    INSERT INTO service_providers (
        provider_id, name, owner_name, service_type, service_category,
        address, area, city, rating, reviews_count, total_jobs,
        price_range, experience_years, verified, phone, whatsapp, email,
        languages, services_offered, emergency_available, response_time_minutes,
        availability
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    ) ON CONFLICT (provider_id) DO UPDATE SET
        name = EXCLUDED.name,
        owner_name = EXCLUDED.owner_name,
        service_type = EXCLUDED.service_type,
        rating = EXCLUDED.rating,
        updated_at = CURRENT_TIMESTAMP
    """

    count = 0
    for provider in providers:
        location = provider.get('location', {})
        contact = provider.get('contact', {})

        cursor.execute(insert_sql, (
            provider.get('provider_id'),
            provider.get('name'),
            provider.get('owner_name'),
            provider.get('service_type'),
            provider.get('service_category'),
            location.get('address'),
            location.get('area'),
            location.get('city'),
            provider.get('rating'),
            provider.get('reviews_count'),
            provider.get('total_jobs'),
            provider.get('price_range'),
            provider.get('experience_years'),
            provider.get('verified', True),
            contact.get('phone'),
            contact.get('whatsapp'),
            contact.get('email'),
            json.dumps(provider.get('languages', [])),
            json.dumps(provider.get('services_offered', [])),
            provider.get('emergency_available', False),
            provider.get('response_time_minutes'),
            Json(provider.get('availability', {}))
        ))
        count += 1

    conn.commit()
    cursor.close()
    print(f"✅ Migrated {count} service providers")

def migrate_bookings(conn):
    """Migrate bookings from JSON to PostgreSQL"""
    print("\nMigrating bookings...")

    # Load JSON data
    json_file = os.path.join(os.path.dirname(__file__), 'bookings.json')

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("⚠️  No bookings.json file found, skipping bookings migration")
        return

    bookings = data.get('bookings', [])

    if not bookings:
        print("⚠️  No bookings to migrate")
        return

    cursor = conn.cursor()

    insert_sql = """
    INSERT INTO bookings (
        booking_id, customer_phone, customer_email, customer_name,
        customer_location, provider_id, provider_name, service_type,
        urgency, date, time, status, distance_km, estimated_cost,
        cancellation_reason
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    ) ON CONFLICT (booking_id) DO UPDATE SET
        status = EXCLUDED.status,
        updated_at = CURRENT_TIMESTAMP
    """

    count = 0
    for booking in bookings:
        cursor.execute(insert_sql, (
            booking.get('booking_id'),
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
            booking.get('estimated_cost'),
            booking.get('cancellation_reason')
        ))
        count += 1

    conn.commit()
    cursor.close()
    print(f"✅ Migrated {count} bookings")

def verify_migration(conn):
    """Verify migration was successful"""
    print("\nVerifying migration...")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM service_providers")
    provider_count = cursor.fetchone()[0]
    print(f"✅ Service Providers in DB: {provider_count}")

    cursor.execute("SELECT COUNT(*) FROM bookings")
    booking_count = cursor.fetchone()[0]
    print(f"✅ Bookings in DB: {booking_count}")

    cursor.close()

def main():
    """Main migration function"""
    print("=" * 60)
    print("ServiceLink AI - Database Migration to Neon DB")
    print("=" * 60)

    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL not found in .env file")
        return

    try:
        # Connect to database
        print(f"\nConnecting to Neon DB...")
        conn = get_connection()
        print("✅ Connected successfully")

        # Ask user if they want to drop existing tables
        response = input("\n⚠️  Drop existing tables? (yes/no): ").strip().lower()
        if response == 'yes':
            drop_tables(conn)

        # Create tables
        create_tables(conn)

        # Migrate data
        migrate_providers(conn)
        migrate_bookings(conn)

        # Verify
        verify_migration(conn)

        # Close connection
        conn.close()

        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
