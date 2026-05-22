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
from database.db_manager_postgres import DatabaseManager
from utils.location_service import LocationService
from utils.language_processor import LanguageProcessor
from utils.matching_engine import MatchingEngine
from utils.calendar_service import CalendarService
from utils.google_calendar_service import GoogleCalendarService
from utils.edge_case_handler import EdgeCaseHandler

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
calendar_service = CalendarService(db)
google_calendar_service = GoogleCalendarService()
edge_case_handler = EdgeCaseHandler(db, location_service)

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

**CRITICAL WORKFLOW - FOLLOW THIS ORDER:**
1. Greet customers warmly (if they introduce themselves, use their name)
2. Ask what service they need (if not mentioned)
3. Ask for their location/area (if not mentioned)
4. **IMPORTANT:** Once you have service type AND location, respond with a CHECK_AVAILABILITY JSON to verify providers exist
5. ONLY after confirming availability, ask for phone number
6. Ask for preferred date (today, tomorrow, or specific date)
7. Once you have phone number AND date preference, respond with BOOK_SERVICE JSON

**CRITICAL: NEVER SHOW JSON TO USERS**
- When you need to check availability or book a service, respond ONLY with the JSON
- Do NOT add any conversational text before or after the JSON
- Do NOT explain what the JSON does
- The JSON is for the system to process, not for the user to see
- After the system processes the JSON, it will generate a user-friendly response

**Response Style:**
- Be natural and friendly, not robotic
- If customer says "Hello I am Bashar", respond: "Hi Bashar! Great to meet you! How can I help you today?"
- For detailed requests, acknowledge all details and confirm understanding
- Don't ask for predefined text - understand natural language
- **NEVER promise service availability before checking the database**
- **NEVER show JSON, code, or technical details to users**

**When you have service type AND location (but NO phone yet), respond ONLY with:**
```json
{
    "action": "CHECK_AVAILABILITY",
    "service_type": "AC Repair|Plumbing|Electrician|Home Cleaning|Carpenter|Painter",
    "location": "area/city",
    "urgency": "emergency|high|normal",
    "customer_name": "name if mentioned"
}
```

**When availability is confirmed AND you have phone number AND date preference, respond ONLY with:**
```json
{
    "action": "BOOK_SERVICE",
    "service_type": "AC Repair|Plumbing|Electrician|Home Cleaning|Carpenter|Painter",
    "location": "area/city",
    "urgency": "emergency|high|normal",
    "customer_name": "name if mentioned",
    "customer_phone": "phone number",
    "preferred_date": "today|tomorrow|YYYY-MM-DD",
    "preferred_time": "morning|afternoon|evening|HH:MM (optional)",
    "ready_to_book": true
}
```

**For multiple services on the same day:**
- Book them ONE AT A TIME
- After first service is booked, ask: "Would you like to book another service?"
- Then repeat the process for the next service

**Otherwise, respond conversationally to gather information.**

Examples:
- User: "Hello I am Bashar" → "Hi Bashar! Great to meet you! How can I help you today?"
- User: "I need plumbing service" → "Sure! I can help you with plumbing. Which area are you located in?"
- User: "I am in Gulshan, Karachi" → Return ONLY the CHECK_AVAILABILITY JSON (no other text)
- After system confirms availability → "Great news! We have plumbers available in Gulshan. What's your phone number so they can reach you?"
- User provides phone and date → Return ONLY the BOOK_SERVICE JSON (no other text)
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
        workflow_steps[-1]["action"] = "Processed customer request and extracted information"

        # Try to extract JSON from agent response
        json_match = re.search(r'\{[^{}]*"action"[^{}]*\}', agent_response, re.DOTALL)

        if not json_match:
            # Agent is still gathering information - return conversational response
            return {
                "status": "conversation",
                "message": agent_response,
                "workflow_steps": workflow_steps
            }

        # Extract action data
        try:
            action_data = json.loads(json_match.group())
        except:
            return {
                "status": "conversation",
                "message": agent_response,
                "workflow_steps": workflow_steps
            }

        action = action_data.get('action')
        service_type = action_data.get('service_type')
        location = action_data.get('location')
        urgency = action_data.get('urgency', 'normal')
        customer_name = action_data.get('customer_name')
        customer_phone = action_data.get('customer_phone')

        # Handle CHECK_AVAILABILITY action
        if action == "CHECK_AVAILABILITY":
            if not service_type or not location:
                return {
                    "status": "conversation",
                    "message": agent_response,
                    "workflow_steps": workflow_steps
                }

            # Step 2: Check Provider Availability
            workflow_steps.append({
                "agent": "Provider Discovery",
                "stage": "Checking Availability",
                "status": "in_progress",
                "timestamp": datetime.now().isoformat(),
                "action": f"Checking if {service_type} providers are available near {location}"
            })

            matched_providers = matching_engine.find_matching_providers(
                service_type=service_type,
                customer_location=location,
                urgency=urgency
            )

            if not matched_providers:
                workflow_steps[-1]["status"] = "failed"
                workflow_steps[-1]["error"] = "No providers found"

                greeting = f"Hi {customer_name}! " if customer_name else ""
                return {
                    "status": "conversation",
                    "message": f"{greeting}I'm sorry, but we don't have {service_type} providers available in {location} right now. Would you like to try a different area or service type?",
                    "workflow_steps": workflow_steps
                }

            workflow_steps[-1]["status"] = "completed"
            workflow_steps[-1]["action"] = f"Found {len(matched_providers)} {service_type} providers available in {location}"

            # Check calendar availability for top providers
            workflow_steps.append({
                "agent": "Calendar Service",
                "stage": "Checking Time Slots",
                "status": "in_progress",
                "timestamp": datetime.now().isoformat(),
                "action": "Checking available time slots for providers"
            })

            today = datetime.now().strftime('%Y-%m-%d')
            provider_ids = [p['provider_id'] for p in matched_providers[:3]]  # Check top 3
            availability_map = calendar_service.check_availability_for_providers(provider_ids, today)

            available_count = sum(1 for slots in availability_map.values() if slots)

            workflow_steps[-1]["status"] = "completed"
            workflow_steps[-1]["action"] = f"{available_count} providers have available time slots today"

            greeting = f"Hi {customer_name}! " if customer_name else ""
            return {
                "status": "conversation",
                "message": f"{greeting}Great news! We have {len(matched_providers)} {service_type} providers available in {location}. What's your phone number so they can reach you to schedule the service?",
                "workflow_steps": workflow_steps
            }

        # Handle BOOK_SERVICE action
        if action == "BOOK_SERVICE" and action_data.get('ready_to_book'):
            if not service_type or not location or not customer_phone:
                return {
                    "status": "conversation",
                    "message": agent_response,
                    "workflow_steps": workflow_steps
                }

            # Parse date preference
            preferred_date = action_data.get('preferred_date', 'today')
            preferred_time = action_data.get('preferred_time', 'morning')

            if preferred_date == 'today':
                booking_date = datetime.now().strftime('%Y-%m-%d')
            elif preferred_date == 'tomorrow':
                booking_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            else:
                booking_date = preferred_date  # Assume YYYY-MM-DD format

            # Step 2: Provider Discovery (for booking)
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
                "action": f"Ranking providers by distance, rating, and {urgency} priority",
                "reasoning": {
                    "algorithm": "Multi-factor weighted scoring",
                    "urgency_level": urgency,
                    "providers_analyzed": len(matched_providers),
                    "ranking_factors": ["distance", "rating", "response_time", "experience"]
                }
            })

            best_provider = matched_providers[0]

            # Enhanced reasoning for top provider selection
            ranking_details = {
                "top_provider": {
                    "name": best_provider['name'],
                    "provider_id": best_provider['provider_id'],
                    "scores": {
                        "distance": f"{best_provider.get('distance_km', 0)} km",
                        "rating": f"{best_provider.get('rating', 'N/A')}/5.0",
                        "experience": f"{best_provider.get('experience_years', 'N/A')} years",
                        "response_time": best_provider.get('response_time', 'N/A')
                    },
                    "why_selected": f"Highest overall score based on {urgency} priority weights"
                },
                "alternatives": [
                    {
                        "name": p['name'],
                        "distance": f"{p.get('distance_km', 0)} km",
                        "rating": f"{p.get('rating', 'N/A')}/5.0"
                    }
                    for p in matched_providers[1:3]
                ] if len(matched_providers) > 1 else []
            }

            workflow_steps[-1]["status"] = "completed"
            workflow_steps[-1]["action"] = f"Selected {best_provider['name']} based on top ranking ({best_provider.get('rating', 'N/A')} stars, {best_provider.get('distance_km', 0)} km away)."
            workflow_steps[-1]["result"] = f"Selected: {best_provider['name']} ({best_provider.get('distance_km', 0)} km away)"
            workflow_steps[-1]["reasoning"]["ranking_details"] = ranking_details

            # Step 3.5: Check and book calendar slot
            workflow_steps.append({
                "agent": "Calendar Service",
                "stage": "Booking Time Slot",
                "status": "in_progress",
                "timestamp": datetime.now().isoformat(),
                "action": f"Finding available time slot for {booking_date}"
            })

            available_slots = calendar_service.get_available_slots(best_provider['provider_id'], booking_date)

            if not available_slots:
                # Try next available date
                next_available = calendar_service.get_next_available_date(best_provider['provider_id'])
                if next_available:
                    workflow_steps[-1]["status"] = "completed"
                    workflow_steps[-1]["action"] = f"Provider fully booked on {booking_date}, found availability on {next_available['date']}"

                    return {
                        "status": "conversation",
                        "message": f"The provider is fully booked on {booking_date}. Next available date is {next_available['day_name']}, {next_available['date']}. Available times: {', '.join(next_available['slots'][:3])}. Would you like to book for that date instead?",
                        "workflow_steps": workflow_steps
                    }
                else:
                    workflow_steps[-1]["status"] = "failed"
                    workflow_steps[-1]["error"] = "No availability in next 7 days"

                    return {
                        "status": "error",
                        "message": f"Sorry, {best_provider['name']} is fully booked for the next week. Would you like to try a different provider?",
                        "workflow_steps": workflow_steps
                    }

            # Select time slot based on preference
            if preferred_time == 'morning':
                selected_slot = next((s for s in available_slots if s < '12:00'), available_slots[0])
            elif preferred_time == 'afternoon':
                selected_slot = next((s for s in available_slots if '12:00' <= s < '17:00'), available_slots[0])
            elif preferred_time == 'evening':
                selected_slot = next((s for s in available_slots if s >= '17:00'), available_slots[0])
            else:
                # Try to match specific time or use first available
                selected_slot = preferred_time if preferred_time in available_slots else available_slots[0]

            workflow_steps[-1]["status"] = "completed"
            workflow_steps[-1]["action"] = f"Selected time slot: {selected_slot} on {booking_date}"

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
                "date": booking_date,
                "time": selected_slot,
                "status": "pending",
                "distance_km": best_provider.get('distance_km', 0),
                "estimated_cost": best_provider.get('price_range', 'To be determined')
            }

            booking = db.save_booking(booking_record)

            # Book the calendar slot in database
            calendar_service.book_slot(
                provider_id=best_provider['provider_id'],
                date=booking_date,
                time_slot=selected_slot,
                booking_id=booking['booking_id']
            )

            # Sync with Google Calendar (if available)
            try:
                if google_calendar_service.check_availability():
                    google_event_id = google_calendar_service.create_booking_event(
                        booking_id=booking['booking_id'],
                        service_type=service_type,
                        provider_name=best_provider['name'],
                        customer_name=customer_name or 'Customer',
                        customer_phone=customer_phone,
                        customer_location=location,
                        date=booking_date,
                        time_slot=selected_slot,
                        duration_minutes=60
                    )

                    if google_event_id:
                        # Update booking with Google Calendar event ID
                        db.update_booking(booking['booking_id'], {
                            'google_calendar_event_id': google_event_id
                        })
                        booking['google_calendar_event_id'] = google_event_id
                        workflow_steps[-1]["google_calendar_synced"] = True
                        logger.info(f"Synced booking {booking['booking_id']} to Google Calendar: {google_event_id}")
                else:
                    workflow_steps[-1]["google_calendar_synced"] = False
                    logger.info("Google Calendar not available, using database calendar only")
            except Exception as e:
                logger.warning(f"Failed to sync with Google Calendar: {e}")
                workflow_steps[-1]["google_calendar_synced"] = False

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
📅 Scheduled: {booking_date} at {selected_slot}
Distance: {booking['distance_km']} km away
Rating: {best_provider.get('rating', 'N/A')} ⭐
Estimated Cost: {booking['estimated_cost']}

📞 Provider Contact:
Phone: {best_provider.get('contact', {}).get('phone', 'N/A')}
Email: {best_provider.get('contact', {}).get('email', 'N/A')}

📍 Your Location: {booking['customer_location']}

Status: {booking['status'].upper()}{urgency_badge}

The provider will contact you shortly to confirm the appointment.

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
