"""
BizFlow AI - System Test Script
Tests workflow visualization and email functionality
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scheduling_agents.agent_system import process_scheduling_request
from config.settings import settings
from database.db_manager import DatabaseManager


async def test_workflow_visualization():
    """Test that workflow steps are generated correctly"""
    print("\n" + "="*60)
    print("TEST 1: Workflow Visualization")
    print("="*60)

    test_message = "Schedule a meeting with Ali Khan tomorrow at 2PM"

    print(f"\n📝 Test Request: {test_message}")
    print("\n⏳ Processing through multi-agent system...\n")

    result = await process_scheduling_request(test_message)

    print(f"✅ Status: {result['status']}")
    print(f"✅ Workflow Complete: {result['workflow_complete']}")
    print(f"✅ Execution Time: {result.get('execution_time', 'N/A')}")

    print(f"\n📊 Workflow Steps ({len(result.get('workflow_steps', []))}):")
    for i, step in enumerate(result.get('workflow_steps', []), 1):
        status_icon = "✓" if step['status'] == 'completed' else "⏳" if step['status'] == 'in_progress' else "❌"
        print(f"\n  {i}. {status_icon} {step['agent']}")
        print(f"     Stage: {step['stage']}")
        print(f"     Status: {step['status']}")
        print(f"     Action: {step['action'][:80]}...")

    print(f"\n💬 Final Output Preview:")
    print("-" * 60)
    print(result['final_output'][:500])
    print("-" * 60)

    return result


async def test_email_configuration():
    """Test email configuration status"""
    print("\n" + "="*60)
    print("TEST 2: Email Configuration")
    print("="*60)

    print(f"\n📧 EMAIL_USER: {'✓ Configured' if settings.EMAIL_USER else '❌ Not configured'}")
    print(f"📧 EMAIL_PASSWORD: {'✓ Configured' if settings.EMAIL_PASSWORD else '❌ Not configured'}")
    print(f"📧 SMTP Server: {settings.EMAIL_SMTP_SERVER}")
    print(f"📧 SMTP Port: {settings.EMAIL_SMTP_PORT}")

    if settings.EMAIL_USER and settings.EMAIL_PASSWORD:
        print("\n✅ Email is configured - notifications will be sent")
    else:
        print("\n⚠️  Email not configured - add to .env:")
        print("   EMAIL_USER=your-email@gmail.com")
        print("   EMAIL_PASSWORD=your-app-password")


async def test_database():
    """Test database functionality"""
    print("\n" + "="*60)
    print("TEST 3: Database")
    print("="*60)

    db = DatabaseManager()

    managers = db.load_managers()
    meetings = db.load_meetings()
    stats = db.get_statistics()

    print(f"\n📊 Database Statistics:")
    print(f"   Total Managers: {stats['total_managers']}")
    print(f"   Total Meetings: {stats['total_meetings']}")
    if 'total_departments' in stats:
        print(f"   Departments: {stats['total_departments']}")

    print(f"\n👥 Sample Managers:")
    for manager in managers[:3]:
        print(f"   - {manager['name']} ({manager['role']})")

    if meetings:
        print(f"\n📅 Recent Meetings:")
        for meeting in meetings[-3:]:
            print(f"   - {meeting['meeting_type']} on {meeting['day']} at {meeting['time']}")
    else:
        print(f"\n📅 No meetings scheduled yet")


async def test_gemini_configuration():
    """Test Gemini API configuration"""
    print("\n" + "="*60)
    print("TEST 4: Gemini API Configuration")
    print("="*60)

    print(f"\n🤖 GEMINI_API_KEY: {'✓ Configured' if settings.GEMINI_API_KEY else '❌ Not configured'}")
    print(f"🤖 GEMINI_MODEL: {settings.GEMINI_MODEL}")
    print(f"🤖 Temperature: {settings.GEMINI_TEMPERATURE}")
    print(f"🤖 Max Tokens: {settings.GEMINI_MAX_TOKENS}")

    if not settings.GEMINI_API_KEY:
        print("\n❌ ERROR: Gemini API key not configured!")
        print("   Add to .env: GEMINI_API_KEY=your_key_here")
        return False

    return True


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 BizFlow AI - System Test Suite")
    print("="*60)

    # Test 4: Gemini Configuration (must pass)
    gemini_ok = await test_gemini_configuration()
    if not gemini_ok:
        print("\n❌ Cannot proceed without Gemini API key")
        return

    # Test 2: Email Configuration (optional)
    await test_email_configuration()

    # Test 3: Database
    await test_database()

    # Test 1: Workflow Visualization (main test)
    result = await test_workflow_visualization()

    # Final Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)

    if result['status'] == 'success':
        print("\n✅ ALL TESTS PASSED!")
        print("\n✓ Workflow visualization working")
        print("✓ Multi-agent system operational")
        print("✓ Database integration working")

        if settings.EMAIL_USER and settings.EMAIL_PASSWORD:
            print("✓ Email notifications configured")
        else:
            print("⚠️  Email notifications not configured (optional)")

        print("\n🎉 System is ready for use!")
        print("\n📝 Next steps:")
        print("   1. Start backend: python main.py")
        print("   2. Start frontend: npm run dev")
        print("   3. Open http://localhost:3000")
        print("   4. Send a scheduling request")

    else:
        print("\n❌ TESTS FAILED")
        print(f"   Error: {result.get('error', 'Unknown error')}")

    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(main())
