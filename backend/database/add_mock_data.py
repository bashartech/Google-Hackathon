"""
Add 50+ Mock Data Entries for Complex Testing
Includes diverse providers, bookings, and locations
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database.db_manager_postgres import DatabaseManager
from datetime import datetime, timedelta
import random

db = DatabaseManager()

# Karachi areas
AREAS = [
    "Gulshan-e-Iqbal", "Clifton", "North Nazimabad", "Orangi Town",
    "DHA Phase 5", "Saddar", "Malir", "Korangi", "Lyari",
    "Bahria Town", "Gulistan-e-Johar", "FB Area", "PECHS",
    "Tariq Road", "Shahrah-e-Faisal", "Landhi", "Kemari"
]

# Service types with realistic pricing
SERVICES = [
    ("Plumber", 1500, 3000),
    ("Electrician", 1200, 2500),
    ("AC Repair", 2000, 5000),
    ("Home Cleaning", 1000, 2000),
    ("Carpenter", 1800, 3500),
    ("Painter", 2500, 5000),
    ("Appliance Repair", 1500, 3000),
    ("Pest Control", 2000, 4000),
    ("CCTV Installation", 3000, 6000),
    ("Solar Panel Installation", 5000, 15000),
]

# Provider names
FIRST_NAMES = [
    "Ahmed", "Ali", "Hassan", "Usman", "Bilal", "Kamran", "Faisal", "Imran",
    "Tariq", "Shahid", "Nadeem", "Rashid", "Salman", "Zubair", "Asif"
]

LAST_NAMES = [
    "Khan", "Ahmed", "Ali", "Hussain", "Sheikh", "Malik", "Raza", "Siddiqui",
    "Qureshi", "Ansari", "Butt", "Chaudhry", "Akhtar", "Mirza", "Haider"
]

def generate_phone():
    """Generate Pakistani phone number"""
    return f"0300{random.randint(1000000, 9999999)}"

def generate_email(name):
    """Generate email from name"""
    return f"{name.lower().replace(' ', '.')}@servicelink.pk"

print("=" * 60)
print("Adding 50+ Mock Data Entries")
print("=" * 60)

# 1. Add 30 more providers
print("\n[1/4] Adding 30 providers...")
providers_added = 0

for i in range(30):
    service_type, min_price, max_price = random.choice(SERVICES)
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    name = f"{first_name} {last_name}"
    area = random.choice(AREAS)

    provider_id = f"PRV{str(i + 100).zfill(3)}"
    phone = generate_phone()
    email = generate_email(name)
    rating = round(random.uniform(3.5, 5.0), 1)
    experience = random.randint(2, 15)

    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO service_providers (
                provider_id, name, owner_name, service_type, service_category,
                phone, email, area, city, rating, experience_years,
                verified, emergency_available, total_jobs, reviews_count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (provider_id) DO NOTHING
        """, (
            provider_id, name, name, service_type, service_type,
            phone, email, area, "Karachi", rating, experience,
            True, random.choice([True, False]), random.randint(5, 100), random.randint(10, 200)
        ))

        conn.commit()
        cursor.close()
        conn.close()

        providers_added += 1
        print(f"  [OK] {provider_id}: {name} - {service_type} in {area}")

    except Exception as e:
        print(f"  [FAIL] Failed to add {provider_id}: {e}")

print(f"\nAdded {providers_added} providers")

# 2. Initialize calendar slots for new providers
print("\n[2/4] Initializing calendar slots...")
from utils.calendar_service import CalendarService

calendar_service = CalendarService(db)
slots_initialized = 0

for i in range(30):
    provider_id = f"PRV{str(i + 100).zfill(3)}"
    try:
        calendar_service.initialize_provider_slots(provider_id, days_ahead=30)
        slots_initialized += 1
        print(f"  [OK] Initialized slots for {provider_id}")
    except Exception as e:
        print(f"  [FAIL] Failed for {provider_id}: {e}")

print(f"\nInitialized calendar for {slots_initialized} providers")

# 3. Add 30 bookings with various statuses
print("\n[3/4] Adding 30 bookings...")
bookings_added = 0

STATUSES = ["pending", "confirmed", "in_progress", "completed", "cancelled"]
CUSTOMER_NAMES = [
    "Ayesha Khan", "Fatima Ali", "Sara Ahmed", "Zainab Hassan",
    "Hira Sheikh", "Maryam Malik", "Nida Raza", "Sana Qureshi"
]

for i in range(30):
    booking_id = f"BKG{str(i + 100).zfill(4)}"

    # Random date in the past 30 days or next 7 days
    days_offset = random.randint(-30, 7)
    booking_date = (datetime.now() + timedelta(days=days_offset)).date()

    service_type, min_price, max_price = random.choice(SERVICES)
    provider_id = f"PRV{str(random.randint(1, 130)).zfill(3)}"
    customer_name = random.choice(CUSTOMER_NAMES)
    customer_phone = generate_phone()
    customer_location = random.choice(AREAS)
    status = random.choice(STATUSES)

    # Random time slot
    time_slots = ['09:00', '10:00', '11:00', '12:00', '14:00', '15:00', '16:00', '17:00', '18:00']
    booking_time = random.choice(time_slots)

    price = random.randint(min_price, max_price)

    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO bookings (
                booking_id, customer_name, customer_phone, customer_location,
                service_type, provider_id, booking_date, booking_time,
                status, total_price, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (booking_id) DO NOTHING
        """, (
            booking_id, customer_name, customer_phone, customer_location,
            service_type, provider_id, booking_date, booking_time,
            status, price, datetime.now() - timedelta(days=abs(days_offset))
        ))

        conn.commit()
        cursor.close()
        conn.close()

        bookings_added += 1
        print(f"  [OK] {booking_id}: {service_type} on {booking_date} at {booking_time} - {status}")

    except Exception as e:
        print(f"  [FAIL] Failed to add {booking_id}: {e}")

print(f"\nAdded {bookings_added} bookings")

# 4. Add provider responses
print("\n[4/4] Adding provider responses...")
responses_added = 0

for i in range(20):
    booking_id = f"BKG{str(random.randint(1, 130)).zfill(4)}"
    provider_id = f"PRV{str(random.randint(1, 130)).zfill(3)}"

    response = random.choice(["accepted", "rejected"])
    reason = None
    if response == "rejected":
        reasons = [
            "Already booked",
            "Too far from my location",
            "Not available at that time",
            "Service type mismatch"
        ]
        reason = random.choice(reasons)

    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO provider_responses (
                booking_id, provider_id, response, reason, responded_at
            ) VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            booking_id, provider_id, response, reason, datetime.now()
        ))

        conn.commit()
        cursor.close()
        conn.close()

        responses_added += 1
        print(f"  [OK] {provider_id} {response} {booking_id}")

    except Exception as e:
        print(f"  [FAIL] Failed: {e}")

print(f"\nAdded {responses_added} provider responses")

# Summary
print("\n" + "=" * 60)
print("Mock Data Summary")
print("=" * 60)

try:
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM providers")
    total_providers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM provider_calendar")
    total_slots = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM provider_responses")
    total_responses = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    print(f"\nTotal Providers: {total_providers}")
    print(f"Total Bookings: {total_bookings}")
    print(f"Total Calendar Slots: {total_slots}")
    print(f"Total Provider Responses: {total_responses}")

    print("\n[SUCCESS] Mock data added successfully!")
    print("\nYou can now test complex scenarios like:")
    print("  - Multi-service bookings across different areas")
    print("  - Schedule optimization with travel time")
    print("  - Provider availability in various locations")
    print("  - Peak hour demand analysis")

except Exception as e:
    print(f"\n[ERROR] Error getting summary: {e}")

print("\n" + "=" * 60)
