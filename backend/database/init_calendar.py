"""
Initialize calendar system for all providers
Run this once to set up the calendar tables and populate initial slots
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from database.db_manager_postgres import DatabaseManager
from utils.calendar_service import CalendarService
from dotenv import load_dotenv

load_dotenv()


def init_calendar_system():
    """Initialize calendar system"""
    print("=" * 60)
    print("Initializing Calendar System")
    print("=" * 60)

    # Connect to database
    db = DatabaseManager()
    calendar_service = CalendarService(db)

    # Create calendar table
    print("\n[1/3] Creating calendar table...")
    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        # Read and execute schema
        schema_path = Path(__file__).parent / 'calendar_schema.sql'
        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        cursor.execute(schema_sql)
        conn.commit()
        cursor.close()
        conn.close()

        print("✓ Calendar table created successfully")

    except Exception as e:
        print(f"✗ Failed to create calendar table: {e}")
        return

    # Get all providers
    print("\n[2/3] Fetching all providers...")
    try:
        providers = db.get_all_providers()
        print(f"✓ Found {len(providers)} providers")

    except Exception as e:
        print(f"✗ Failed to fetch providers: {e}")
        return

    # Initialize slots for each provider
    print("\n[3/3] Initializing calendar slots for all providers...")
    success_count = 0
    fail_count = 0

    for provider in providers:
        provider_id = provider['provider_id']
        provider_name = provider['name']

        print(f"  - {provider_name} ({provider_id})...", end=" ")

        if calendar_service.initialize_provider_slots(provider_id, days_ahead=30):
            print("✓")
            success_count += 1
        else:
            print("✗")
            fail_count += 1

    print("\n" + "=" * 60)
    print(f"Calendar Initialization Complete")
    print(f"  Success: {success_count} providers")
    print(f"  Failed: {fail_count} providers")
    print("=" * 60)

    # Test availability check
    print("\n[TEST] Checking availability for first provider...")
    if providers:
        test_provider = providers[0]
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')

        slots = calendar_service.get_available_slots(test_provider['provider_id'], today)
        print(f"  Provider: {test_provider['name']}")
        print(f"  Date: {today}")
        print(f"  Available slots: {len(slots)}")
        print(f"  Slots: {', '.join(slots[:5])}{'...' if len(slots) > 5 else ''}")


if __name__ == "__main__":
    init_calendar_system()
