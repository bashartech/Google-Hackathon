"""
Regenerate Google OAuth2 Token
Run this to create a new token.json from your updated credentials.json
"""

import os
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes for Gmail and Calendar
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar'
]

def regenerate_token():
    """Generate new token.json from credentials.json"""

    base_dir = Path(__file__).parent
    credentials_file = base_dir / "credentials.json"
    token_file = base_dir / "token.json"

    print("=" * 60)
    print("Google OAuth2 Token Regeneration")
    print("=" * 60)

    # Check if credentials.json exists
    if not credentials_file.exists():
        print(f"\n[ERROR] credentials.json not found at: {credentials_file}")
        print("\nPlease ensure credentials.json is in the project root directory")
        return False

    print(f"\n[OK] Found credentials.json")

    # Delete old token if exists
    if token_file.exists():
        print(f"[INFO] Removing old token.json")
        token_file.unlink()

    try:
        print("\n[INFO] Starting OAuth2 flow...")
        print("[INFO] A browser window will open for authentication")
        print("[INFO] Please sign in with your Google account and grant permissions")

        # Run OAuth2 flow
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_file),
            SCOPES
        )

        creds = flow.run_local_server(port=0)

        # Save the credentials
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

        print(f"\n[SUCCESS] token.json created successfully!")
        print(f"[INFO] Token saved to: {token_file}")

        # Verify the token
        print("\n[INFO] Verifying token...")
        if creds.valid:
            print("[SUCCESS] Token is valid and ready to use")
            print("\nScopes granted:")
            for scope in SCOPES:
                print(f"  - {scope}")
            return True
        else:
            print("[WARNING] Token created but may need refresh")
            return True

    except Exception as e:
        print(f"\n[ERROR] Failed to generate token: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure credentials.json is valid")
        print("  2. Check that OAuth2 consent screen is configured")
        print("  3. Verify redirect URIs include http://localhost")
        return False

if __name__ == "__main__":
    success = regenerate_token()

    if success:
        print("\n" + "=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print("1. Restart the backend server")
        print("2. Gmail and Calendar APIs will now work")
        print("3. Test by creating a booking")
        print("\nBackend restart command:")
        print("  cd backend")
        print("  uvicorn main:app --reload --port 8001")
    else:
        print("\n" + "=" * 60)
        print("Token generation failed - please fix the errors above")
        print("=" * 60)
