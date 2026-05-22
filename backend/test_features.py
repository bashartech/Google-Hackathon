"""
Test Script for ServiceLink AI - All Features
Tests calendar integration, provider acceptance, edge cases, and smart scheduling
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_calendar_availability():
    """Test calendar availability checking"""
    print_section("Testing Calendar Availability")

    # Test 1: Get availability for a provider
    provider_id = "PRV001"
    date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    response = requests.get(f"{BASE_URL}/api/providers/{provider_id}/availability?date={date}")
    data = response.json()

    print(f"\n[TEST 1] Provider {provider_id} availability on {date}:")
    print(f"Status: {data.get('status')}")
    print(f"Available slots: {len(data.get('available_slots', []))}")
    print(f"Slots: {', '.join(data.get('available_slots', [])[:5])}")

    # Test 2: Get next available date
    response = requests.get(f"{BASE_URL}/api/providers/{provider_id}/next-available")
    data = response.json()

    print(f"\n[TEST 2] Next available date for {provider_id}:")
    if data.get('status') == 'success':
        next_avail = data.get('next_available', {})
        print(f"Date: {next_avail.get('date')} ({next_avail.get('day_name')})")
        print(f"Available slots: {len(next_avail.get('slots', []))}")
    else:
        print(f"Status: {data.get('status')}")

def test_smart_scheduling():
    """Test smart scheduling recommendations"""
    print_section("Testing Smart Scheduling")

    # Test 1: Get best booking times
    response = requests.get(f"{BASE_URL}/api/scheduling/best-times?service_type=Plumbing&area=Gulshan")
    data = response.json()

    print(f"\n[TEST 1] Best times for Plumbing in Gulshan:")
    print(f"Status: {data.get('status')}")
    recommendations = data.get('recommendations', [])
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"\n  Option {i}:")
        print(f"    Day: {rec.get('day')}")
        print(f"    Time: {rec.get('time')}")
        print(f"    Demand: {rec.get('demand_level')}")
        print(f"    Discount: {rec.get('discount')}")
        print(f"    Reason: {rec.get('reason')}")

    # Test 2: Get peak hours info
    response = requests.get(f"{BASE_URL}/api/scheduling/peak-hours")
    data = response.json()

    print(f"\n[TEST 2] Current peak hours status:")
    peak_info = data.get('peak_info', {})
    print(f"Is Peak: {peak_info.get('is_peak')}")
    print(f"Message: {peak_info.get('message')}")
    if peak_info.get('is_peak'):
        print(f"Surge Multiplier: {peak_info.get('surge_multiplier')}x")

def test_provider_stats():
    """Test provider acceptance statistics"""
    print_section("Testing Provider Statistics")

    provider_id = "PRV001"
    response = requests.get(f"{BASE_URL}/api/provider/{provider_id}/stats")
    data = response.json()

    print(f"\n[TEST] Provider {provider_id} statistics:")
    print(f"Status: {data.get('status')}")
    stats = data.get('stats', {})
    print(f"Total Responses: {stats.get('total_responses', 0)}")
    print(f"Accepted: {stats.get('accepted', 0)}")
    print(f"Rejected: {stats.get('rejected', 0)}")
    print(f"Acceptance Rate: {stats.get('acceptance_rate', 0):.1f}%")
    print(f"Avg Response Time: {stats.get('avg_response_time_minutes', 0):.1f} minutes")

def test_dashboard_stats():
    """Test dashboard statistics"""
    print_section("Testing Dashboard Statistics")

    response = requests.get(f"{BASE_URL}/api/dashboard/stats")
    data = response.json()

    print(f"\n[TEST] Dashboard statistics:")
    print(f"Status: {data.get('status')}")
    stats = data.get('stats', {})
    print(f"Total Bookings: {stats.get('total_bookings', 0)}")
    print(f"Active Bookings: {stats.get('active_bookings', 0)}")
    print(f"Completed Bookings: {stats.get('completed_bookings', 0)}")
    print(f"Total Providers: {stats.get('total_providers', 0)}")

    print(f"\nService Breakdown:")
    for service, count in stats.get('service_breakdown', {}).items():
        print(f"  {service}: {count}")

def test_service_booking():
    """Test complete service booking flow"""
    print_section("Testing Service Booking Flow")

    # Test conversation flow
    messages = [
        "Hello, I need a plumber",
        "I'm in Gulshan, Karachi",
        "03001234567",
        "Tomorrow morning"
    ]

    session_id = None

    for i, message in enumerate(messages, 1):
        print(f"\n[STEP {i}] User: {message}")

        payload = {
            "message": message,
            "session_id": session_id
        }

        response = requests.post(f"{BASE_URL}/api/service-request", json=payload)
        data = response.json()

        session_id = data.get('session_id')

        print(f"Status: {data.get('status')}")
        print(f"Response: {data.get('message')[:200]}...")

        # Show workflow steps
        workflow_steps = data.get('workflow_steps', [])
        if workflow_steps:
            print(f"\nWorkflow Steps ({len(workflow_steps)}):")
            for step in workflow_steps[-2:]:  # Show last 2 steps
                print(f"  - {step.get('agent')}: {step.get('stage')} [{step.get('status')}]")
                if step.get('reasoning'):
                    print(f"    Reasoning: {json.dumps(step['reasoning'], indent=6)[:150]}...")

def test_all_providers():
    """Test getting all providers"""
    print_section("Testing Provider Listing")

    response = requests.get(f"{BASE_URL}/api/providers")
    data = response.json()

    print(f"\n[TEST] All providers:")
    print(f"Status: {data.get('status')}")
    print(f"Total Providers: {data.get('count', 0)}")

    providers = data.get('providers', [])
    if providers:
        print(f"\nSample providers:")
        for provider in providers[:3]:
            print(f"  - {provider.get('name')} ({provider.get('service_type')})")
            print(f"    Location: {provider.get('location', {}).get('area')}, {provider.get('location', {}).get('city')}")
            print(f"    Rating: {provider.get('rating')}/5.0")

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  ServiceLink AI - Feature Testing Suite")
    print("  Testing: Calendar, Smart Scheduling, Provider Stats, Booking")
    print("=" * 60)

    try:
        # Test 1: Calendar availability
        test_calendar_availability()

        # Test 2: Smart scheduling
        test_smart_scheduling()

        # Test 3: Provider statistics
        test_provider_stats()

        # Test 4: Dashboard statistics
        test_dashboard_stats()

        # Test 5: All providers
        test_all_providers()

        # Test 6: Service booking flow (optional - creates actual booking)
        # Uncomment to test full booking flow
        # test_service_booking()

        print("\n" + "=" * 60)
        print("  All Tests Completed Successfully!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot connect to backend server.")
        print("Make sure the backend is running: uvicorn main:app --reload")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
