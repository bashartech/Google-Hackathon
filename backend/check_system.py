"""
Debug Script - Check ServiceLink AI Setup
Run this to verify all systems are working
"""

import sys
from pathlib import Path
from config.settings import settings

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("ServiceLink AI - System Check")
print("=" * 60)

# Check 1: Python packages
print("\n[1/6] Checking Python packages...")
required_packages = [
    ('fastapi', 'fastapi'),
    ('uvicorn', 'uvicorn'),
    ('psycopg2', 'psycopg2'),
    ('agents', 'agents'),
    ('openai', 'openai'),
    ('google-auth', 'google.auth'),
    ('google-auth-oauthlib', 'google_auth_oauthlib'),
    ('googleapiclient', 'googleapiclient'),
    ('apscheduler', 'apscheduler')
]

missing_packages = []
for display_name, import_name in required_packages:
    try:
        __import__(import_name)
        print(f"  ✓ {display_name}")
    except ImportError:
        print(f"  ✗ {display_name} - MISSING")
        missing_packages.append(display_name)

if missing_packages:
    print(f"\n  ERROR: Missing packages: {', '.join(missing_packages)}")
    print(f"  Run: pip install {' '.join(missing_packages)}")
else:
    print("  All packages installed!")

# Check 2: Database connection
print("\n[2/6] Checking database connection...")
try:
    from database.db_manager_postgres import DatabaseManager
    db = DatabaseManager()
    providers = db.get_all_providers()
    print(f"  ✓ Database connected")
    print(f"  ✓ Found {len(providers)} providers")
except Exception as e:
    print(f"  ✗ Database error: {e}")

# Check 3: Calendar table
print("\n[3/6] Checking calendar table...")
try:
    from database.db_manager_postgres import DatabaseManager
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM provider_calendar")
    count = cursor.fetchone()['count']

    cursor.close()
    conn.close()

    if count > 0:
        print(f"  ✓ Calendar table exists with {count} slots")
    else:
        print(f"  ✗ Calendar table is EMPTY")
        print(f"  Run: python database/init_calendar.py")
except Exception as e:
    print(f"  ✗ Calendar table error: {e}")
    print(f"  Run: python database/init_calendar.py")

# Check 4: Google Calendar credentials
print("\n[4/6] Checking Google Calendar credentials...")
if settings.CREDENTIALS_FILE.exists():
    print(f"  ✓ credentials.json found at {settings.CREDENTIALS_FILE}")
else:
    print(f"  ✗ credentials.json NOT found at {settings.CREDENTIALS_FILE}")

if settings.TOKEN_FILE.exists():
    print(f"  ✓ token.json found at {settings.TOKEN_FILE}")
else:
    print(f"  ✗ token.json NOT found at {settings.TOKEN_FILE}")

# Check 5: Provider acceptance table
print("\n[5/6] Checking provider acceptance table...")
try:
    from database.db_manager_postgres import DatabaseManager
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM provider_responses")
    count = cursor.fetchone()['count']

    cursor.close()
    conn.close()

    print(f"  ✓ Provider responses table exists with {count} records")
except Exception as e:
    print(f"  ✗ Provider responses table error: {e}")
    print(f"  Run initialization command")

# Check 6: Service orchestrator imports
print("\n[6/6] Checking service orchestrator...")
try:
    from scheduling_agents.service_orchestrator import (
        calendar_service,
        google_calendar_service,
        edge_case_handler
    )
    print(f"  ✓ Calendar service imported")
    print(f"  ✓ Google Calendar service imported")
    print(f"  ✓ Edge case handler imported")
except Exception as e:
    print(f"  ✗ Import error: {e}")

print("\n" + "=" * 60)
print("System Check Complete")
print("=" * 60)
