"""
Check Google Calendar API access and scopes
"""
import json
import os
from pathlib import Path
import sys
from config.settings import settings

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def check_google_apis():
    print("=" * 60)
    print("Checking Google API Access")
    print("=" * 60)

    # Check credentials.json
    creds_file = settings.CREDENTIALS_FILE
    if creds_file.exists():
        print("[OK] credentials.json found")
        with open(creds_file, 'r') as f:
            creds = json.load(f)

        # Check if it's OAuth or Service Account
        if 'installed' in creds or 'web' in creds:
            print("[OK] OAuth 2.0 credentials detected")
            client_info = creds.get('installed') or creds.get('web')
            print(f"   Client ID: {client_info.get('client_id', 'N/A')[:50]}...")
        else:
            print("[WARN] Unknown credential type")
    else:
        print(f"[ERROR] credentials.json NOT found at {creds_file}")
        return

    # Check token.json
    token_file = settings.TOKEN_FILE
    if token_file.exists():
        print("[OK] token.json found")
        with open(token_file, 'r') as f:
            token = json.load(f)

        scopes = token.get('scopes', [])
        print(f"\nCurrent Scopes:")
        for scope in scopes:
            print(f"   - {scope}")

        # Check for Calendar API
        has_calendar = any('calendar' in scope.lower() for scope in scopes)
        has_gmail = any('gmail' in scope.lower() or 'mail' in scope.lower() for scope in scopes)

        print(f"\nCalendar API: {'[OK] ENABLED' if has_calendar else '[ERROR] NOT ENABLED'}")
        print(f"Gmail API: {'[OK] ENABLED' if has_gmail else '[ERROR] NOT ENABLED'}")

        if not has_calendar:
            print("\nTo enable Calendar API:")
            print("   1. Go to https://console.cloud.google.com")
            print("   2. Enable 'Google Calendar API'")
            print("   3. Add scope: https://www.googleapis.com/auth/calendar")
            print("   4. Delete token.json and re-authenticate")

        if not has_gmail:
            print("\nTo enable Gmail API:")
            print("   1. Go to https://console.cloud.google.com")
            print("   2. Enable 'Gmail API'")
            print("   3. Add scope: https://www.googleapis.com/auth/gmail.send")
            print("   4. Delete token.json and re-authenticate")

    else:
        print("[ERROR] token.json NOT found")
        print("   Run authentication flow to generate token.json")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_google_apis()
