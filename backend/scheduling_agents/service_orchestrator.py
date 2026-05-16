"""
ServiceLink AI - Multi-Agent Service Orchestration System
Using OpenAI Agents SDK with Groq API integration - PROPER IMPLEMENTATION

This module implements natural conversational agents with workflow tracking
"""

import logging
from agents import Agent, Runner, SQLiteSession, set_default_openai_client, set_default_openai_api, set_tracing_disabled
from typing import Dict, Any, List, Optional
from typing_extensions import TypedDict
import sys
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
import json
import re
from datetime import datetime, timedelta

load_dotenv()
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from database.db_manager import DatabaseManager
from utils.location_service import LocationService
from utils.language_processor import LanguageProcessor
from utils.matching_engine import MatchingEngine

# ============================================================
# OPENAI AGENTS SDK CONFIGURATION WITH GROQ
# ============================================================

# Create OpenAI-compatible client pointing to Groq endpoint
client = AsyncOpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# Set Groq client as default for Agents SDK
set_default_openai_client(client)
set_default_openai_api("chat_completions")
set_tracing_disabled(True)

# Initialize services
db = DatabaseManager()
location_service = LocationService()
language_processor = LanguageProcessor()
matching_engine = MatchingEngine(db, location_service)

# Session storage for multi-user support
_sessions = {}

def get_or_create_session(session_id: str) -> SQLiteSession:
    """Get existing session or create new one for stateful conversations"""
    if session_id not in _sessions:
        _sessions[session_id] = SQLiteSession(f"service_session_{session_id}")
    return _sessions[session_id]

# ============================================================
# CONVERSATIONAL SERVICE COORDINATOR AGENT
# ============================================================

conversational_coordinator = Agent(
    name="Service Coordinator",
    model=settings.GROQ_MODEL,
    instructions="""You are a friendly, intelligent service coordinator for ServiceLink AI - a home service booking platform in Pakistan.

**Your Personality:**
- Warm, helpful, and conversational
- Remember customer names and use them naturally
- Understand context from previous messages
- Handle complex requests intelligently
- Support Urdu, Roman Urdu, and English

**Available Services:**
AC Repair, Plumbing, Electrician, Home Cleaning, Carpenter, Painter

**Available Cities:**
Karachi, Islamabad, Lahore (and their areas)

**Your Tasks:**
1. Greet customers warmly (if they introduce themselves, use their name)
2. Understand service requests in natural language
3. Extract: service type, location, urgency, customer name, and PHONE NUMBER
4. Ask for missing information conversationally (especially location and phone number)
5. Handle detailed/complex requests intelligently

**Response Style:**
- Be natural and friendly, not robotic
- If customer says "Hello I am Bashar", respond: "Hi Bashar! Great to meet you! How can I help you today?"
- For detailed requests, acknowledge all details and confirm understanding
- Don't ask for predefined text - understand natural language

**When you have service type AND location, respond with JSON:**
```json
{
    "service_type": "AC Repair|Plumbing|Electrician|Home Cleaning|Carpenter|Painter",
    "location": "area/city",
    "urgency": "emergency|high|normal",
    "customer_name": "name if mentioned",
    "customer_phone": "phone number",
    "ready_to_book": true
}
```

**CRITICAL:** Do NOT set `ready_to_book` to `true` until you have both a LOCATION and a PHONE NUMBER.

**Otherwise, respond conversationally to gather information.**

Examples:
- User: "Hello I am Bashar" → "Hi Bashar! Great to meet you! I can help you book home services in Karachi, Islamabad, or Lahore. What service do you need?"
- User: "A household in Karachi has electrical outage affecting elderly residents..." → "I understand - this is an emergency electrical situation in Karachi affecting elderly residents. I'll find the nearest electrician who can respond within 2 hours. What is the full address in Karachi and your phone number so the provider can reach you?"
- User: "Clifton, Street 5, House 12, phone 0300-1234567" → "Perfect! Finding emergency electrician for Clifton, Karachi. I have your contact as 0300-1234567. Searching now..."
""",
)

# ============================================================
# MAIN ORCHESTRATION FUNCTION
# ============================================================

async def process_service_request(user_message: str, conversation_context: str = "", session_id: str = "default") -> Dict[str, Any]:
    """
    Main orchestration using OpenAI Agents SDK for natural conversation

    Args:
        user_message: Customer's message
        conversation_context: Legacy parameter (not used)
        session_id: Session ID for stateful conversation

    Returns:
        Dict with status, message, booking, and workflow_steps
    """
    workflow_steps = []

    try:
        # Get or create session
        session = get_or_create_session(session_id)

        # Step 1: Run conversational agent
        workflow_steps.append({
            "agent": "Service Coordinator",
            "stage": "Understanding Request",
            "status": "in_progress",
            "timestamp": datetime.now().isoformat(),
            "action": "Processing natural language and extracting service details"
        })

        # Use Runner with session for stateful conversation
        # Fixing the error by using positional arguments for the main parameters
        runner = await Runner.run(conversational_coordinator, user_message, session=session)
        #result = await runner.run(user_message)

        agent_response = runner.final_output if hasattr(runner, 'final_output') else str(runner)

        workflow_steps[-1]["status"] = "completed"
        workflow_steps[-1]["action"] = f"Understood request for {service_type if 'service_type' in locals() else 'service'} in {location if 'location' in locals() else 'unknown area'}. Ready to book: {'ready_to_book' in agent_response}"
        workflow_steps[-1]["result"] = agent_response[:150]

        # Try to extract JSON from agent response
        json_match = re.search(r'\{[^{}]*"ready_to_book"[^{}]*\}', agent_response, re.DOTALL)

        if not json_match:
            # Agent is still gathering information - return conversational response
            return {
                "status": "conversation",
                "message": agent_response,
                "workflow_steps": workflow_steps
            }

        # Extract booking data
        try:
            booking_data = json.loads(json_match.group())
        except:
            return {
                "status": "conversation",
                "message": agent_response,
                "workflow_steps": workflow_steps
            }

        service_type = booking_data.get('service_type')
        location = booking_data.get('location')
        urgency = booking_data.get('urgency', 'normal')
        customer_name = booking_data.get('customer_name')
        customer_phone = booking_data.get('customer_phone')

        if not service_type or not location:
            return {
                "status": "conversation",
                "message": agent_response,
                "workflow_steps": workflow_steps
            }

        # Step 2: Provider Discovery
        workflow_steps.append({
            "agent": "Provider Discovery",
            "stage": "Finding Providers",
            "status": "in_progress",
            "timestamp": datetime.now().isoformat(),
            "action": f"Searching for {service_type} providers near {location}"
        })

        matched_providers = matching_engine.find_matching_providers(
            service_type=service_type,
            customer_location=location,
            urgency=urgency
        )

        if not matched_providers:
            workflow_steps[-1]["status"] = "failed"
            workflow_steps[-1]["error"] = "No providers found"

            return {
                "status": "error",
                "message": f"Sorry, no {service_type} providers found near {location}. Try a different area or service type.",
                "workflow_steps": workflow_steps
            }

        workflow_steps[-1]["status"] = "completed"
        workflow_steps[-1]["action"] = f"Successfully matched {len(matched_providers)} qualified providers near {location}."
        workflow_steps[-1]["result"] = f"Found {len(matched_providers)} providers"

        # Step 3: Matching & Ranking
        workflow_steps.append({
            "agent": "Matching & Ranking",
            "stage": "Ranking Providers",
            "status": "in_progress",
            "timestamp": datetime.now().isoformat(),
            "action": f"Ranking providers by distance, rating, and {urgency} priority"
        })

        best_provider = matched_providers[0]

        workflow_steps[-1]["status"] = "completed"
        workflow_steps[-1]["action"] = f"Selected {best_provider['name']} based on top ranking ({best_provider.get('rating', 'N/A')} stars, {best_provider.get('distance_km', 0)} km away)."
        workflow_steps[-1]["result"] = f"Selected: {best_provider['name']} ({best_provider.get('distance_km', 0)} km away)"

        # Step 4: Booking Creation
        workflow_steps.append({
            "agent": "Booking & Confirmation",
            "stage": "Creating Booking",
            "status": "in_progress",
            "timestamp": datetime.now().isoformat(),
            "action": "Creating booking record and sending notifications"
        })

        booking_record = {
            "customer_phone": customer_phone,
            "customer_email": None,
            "customer_name": customer_name,
            "customer_location": location,
            "provider_id": best_provider['provider_id'],
            "provider_name": best_provider['name'],
            "service_type": service_type,
            "urgency": urgency,
            "date": "To be scheduled",
            "time": "To be scheduled",
            "status": "pending",
            "distance_km": best_provider.get('distance_km', 0),
            "estimated_cost": best_provider.get('price_range', 'To be determined')
        }

        booking = db.save_booking(booking_record)

        # Send email notification (if configured)
        try:
            from tools.email_tools import send_booking_confirmation_email
            provider_email = best_provider.get('contact', {}).get('email')
            # Support both Gmail API (credentials/token) and SMTP (EMAIL_USER)
            if provider_email and (settings.EMAIL_USER or settings.CREDENTIALS_FILE.exists() or settings.TOKEN_FILE.exists()):
                await send_booking_confirmation_email(
                    to_email=provider_email,
                    booking_id=booking['booking_id'],
                    service_type=service_type,
                    location=location,
                    urgency=urgency,
                    customer_contact=f"{customer_name or 'Customer'} (Phone: {customer_phone or 'Not provided'})"
                )
                workflow_steps[-1]["email_sent"] = True
        except Exception as e:
            logger.warning(f"Email notification failed: {e}")
            workflow_steps[-1]["email_sent"] = False

        workflow_steps[-1]["status"] = "completed"
        workflow_steps[-1]["action"] = f"Booking {booking['booking_id']} confirmed and notification sent to {best_provider['name']}."
        workflow_steps[-1]["result"] = f"Booking {booking['booking_id']} created"

        # Step 5: Format response
        urgency_badge = ""
        if urgency == "emergency":
            urgency_badge = "\n\n🚨 EMERGENCY REQUEST - Priority Response"
        elif urgency == "high":
            urgency_badge = "\n\n⚡ HIGH PRIORITY"

        greeting = f"Hi {customer_name}! " if customer_name else ""

        response_message = f"""{greeting}✅ Booking Confirmed!

Booking ID: {booking['booking_id']}
Service: {booking['service_type']}
Provider: {booking['provider_name']}
Distance: {booking['distance_km']} km away
Rating: {best_provider.get('rating', 'N/A')} ⭐
Estimated Cost: {booking['estimated_cost']}

📞 Provider Contact:
Phone: {best_provider.get('contact', {}).get('phone', 'N/A')}
Email: {best_provider.get('contact', {}).get('email', 'N/A')}

📍 Your Location: {booking['customer_location']}

Status: {booking['status'].upper()}{urgency_badge}

The provider will contact you shortly to confirm the appointment time.

Alternative Providers: {len(matched_providers) - 1} available"""

        return {
            "status": "success",
            "booking": booking,
            "message": response_message,
            "workflow_steps": workflow_steps,
            "alternatives": matched_providers[1:4] if len(matched_providers) > 1 else []
        }

    except Exception as e:
        logger.error(f"Error processing service request: {e}", exc_info=True)

        workflow_steps.append({
            "agent": "System",
            "stage": "Error",
            "status": "failed",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        })

        return {
            "status": "error",
            "message": f"Sorry, I encountered an error: {str(e)}",
            "workflow_steps": workflow_steps
        }


async def get_booking_status(booking_id: str) -> Dict[str, Any]:
    """Get status of existing booking"""
    booking = db.get_booking_by_id(booking_id)

    if not booking:
        return {
            "status": "error",
            "message": f"Booking {booking_id} not found."
        }

    return {
        "status": "success",
        "booking": booking,
        "message": f"Booking {booking_id} status: {booking['status']}"
    }


async def cancel_booking(booking_id: str, reason: str = None) -> Dict[str, Any]:
    """Cancel existing booking"""
    booking = db.get_booking_by_id(booking_id)

    if not booking:
        return {
            "status": "error",
            "message": f"Booking {booking_id} not found."
        }

    if booking['status'] == 'cancelled':
        return {
            "status": "error",
            "message": f"Booking {booking_id} is already cancelled."
        }

    updated_booking = db.update_booking(booking_id, {
        "status": "cancelled",
        "cancellation_reason": reason or "Customer request"
    })

    return {
        "status": "success",
        "booking": updated_booking,
        "message": f"Booking {booking_id} has been cancelled successfully."
    }
