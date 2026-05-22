import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """
    Configuration settings for BizFlow AI
    Loads from environment variables and credentials file
    """

    # Base paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    PARENT_DIR = BASE_DIR.parent
 
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
    GOOGLE_CLOUD_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY", "")

    # Groq Model Configuration
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.7"))
    GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "2048"))

    # Email Configuration
    EMAIL_USER = os.getenv("EMAIL_USER", "")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
    EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
    EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "465"))

    # Application Settings
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # CORS Settings
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    # Database paths
    DATABASE_DIR = BASE_DIR / "database"
    MANAGERS_FILE = DATABASE_DIR / "managers.json"
    MEETINGS_FILE = DATABASE_DIR / "meetings.json"

    # Credentials file path (in parent directory)
    CREDENTIALS_FILE = PARENT_DIR / "credentials.json"
    TOKEN_FILE = PARENT_DIR / "token.json"

    @classmethod
    def load_google_credentials(cls):
        """Load Google OAuth credentials from credentials.json"""
        try:
            if cls.CREDENTIALS_FILE.exists():
                with open(cls.CREDENTIALS_FILE, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return None

    @classmethod
    def validate_settings(cls):
        """Validate required settings are present"""
        errors = []
        warnings = []

        if not cls.GROQ_API_KEY:
            errors.append("GROQ_API_KEY is not set")

        if not cls.GOOGLE_MAPS_API_KEY or cls.GOOGLE_MAPS_API_KEY == 'your_google_maps_api_key_here':
            warnings.append("GOOGLE_MAPS_API_KEY is not set (system will use fallback coordinates)")

        if not cls.EMAIL_USER:
            warnings.append("EMAIL_USER is not set (email notifications disabled)")

        if not cls.EMAIL_PASSWORD:
            warnings.append("EMAIL_PASSWORD is not set (email notifications disabled)")

        if errors:
            print("❌ Configuration errors:")
            for error in errors:
                print(f"   - {error}")
            print("\nPlease set these in your .env file")

        if warnings:
            print("⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")

        return len(errors) == 0

    @classmethod
    def get_config_summary(cls):
        """Get a summary of current configuration"""
        return {
            "environment": cls.ENVIRONMENT,
            "debug": cls.DEBUG,
            "groq_model": cls.GROQ_MODEL,
            "groq_api_key_set": bool(cls.GROQ_API_KEY),
            "openai_api_key_set": bool(cls.OPENAI_API_KEY),
            "email_configured": bool(cls.EMAIL_USER and cls.EMAIL_PASSWORD),
            "database_dir": str(cls.DATABASE_DIR),
            "credentials_file_exists": cls.CREDENTIALS_FILE.exists()
        }


# Create settings instance
settings = Settings()

# Validate on import (only show warnings, don't fail)
if settings.DEBUG:
    print("[*] BizFlow AI Configuration Loaded")
    config_summary = settings.get_config_summary()
    for key, value in config_summary.items():
        print(f"   {key}: {value}")
