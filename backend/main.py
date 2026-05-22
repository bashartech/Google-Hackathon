"""
BizFlow AI - FastAPI Backend
Main application with REST API endpoints
"""
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models.schemas import (
    ScheduleRequest,
    ScheduleResponse,
    ManagersResponse,
    MeetingsResponse,
    HealthResponse,
    ErrorResponse,
    Manager,
    Meeting
)
from scheduling_agents.agent_system import process_scheduling_request
from scheduling_agents.service_orchestrator import (
    process_service_request,
    get_booking_status,
    cancel_booking
)
from database.db_manager_postgres import DatabaseManager
from config.settings import settings
from tools.email_tools import get_email_config_status
from utils.session_manager import session_manager
from datetime import datetime
import logging
import uvicorn

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="BizFlow AI - Agentic Scheduling System",
    description="Multi-agent autonomous business scheduling automation using OpenAI Agents SDK with Gemini API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database manager
db = DatabaseManager()


# ============================================================
# Exception Handlers
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            detail=exc.detail,
            status_code=exc.status_code,
            timestamp=datetime.now().isoformat()
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            detail="Internal server error",
            status_code=500,
            timestamp=datetime.now().isoformat()
        ).model_dump()
    )


# ============================================================
# API Endpoints
# ============================================================

@app.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Returns service status and configuration
    """
    try:
        # Get configuration status
        email_config = get_email_config_status()
        db_stats = db.get_statistics()

        return HealthResponse(
            service="BizFlow AI",
            status="running",
            version="1.0.0",
            timestamp=datetime.now().isoformat(),
            configuration={
                "groq_api_configured": bool(settings.GROQ_API_KEY),
                "email_configured": email_config["configured"],
                "database_stats": db_stats,
                "environment": settings.ENVIRONMENT,
                "debug": settings.DEBUG
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )


@app.post("/api/schedule", response_model=ScheduleResponse)
async def schedule_meeting(request: ScheduleRequest):
    """
    Main scheduling endpoint
    Processes natural language scheduling requests through multi-agent system
    Supports stateful conversations with session management

    Args:
        request: ScheduleRequest with natural language message and optional session_id

    Returns:
        ScheduleResponse with workflow results and session_id
    """
    try:
        logger.info(f"Processing scheduling request: {request.message}")

        # Validate Groq API key
        if not settings.GROQ_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="Groq API key not configured. Please set GROQ_API_KEY in .env file"
            )

        # Get or create session
        session_id = request.session_id or session_manager.create_session()
        session = session_manager.get_session(session_id)

        # Add user message to history
        session.add_message("user", request.message)

        # Get conversation context
        conversation_context = session.get_context_string()

        # Process request through agent system with context
        result = await process_scheduling_request(
            request.message,
            conversation_history=conversation_context
        )

        # Add assistant response to history
        session.add_message("assistant", result["final_output"], {
            "workflow_steps": result.get("workflow_steps", [])
        })

        logger.info(f"Scheduling request completed with status: {result['status']}")

        return ScheduleResponse(
            status=result["status"],
            final_output=result["final_output"],
            workflow_complete=result["workflow_complete"],
            session_id=session_id,
            workflow_steps=result.get("workflow_steps", []),
            error=result.get("error")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing scheduling request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process scheduling request: {str(e)}"
        )


@app.get("/api/managers", response_model=ManagersResponse)
async def get_managers():
    """
    Get all managers and their availability

    Returns:
        ManagersResponse with list of all managers
    """
    try:
        managers = db.load_managers()
        return ManagersResponse(
            managers=managers,
            total=len(managers)
        )
    except Exception as e:
        logger.error(f"Error fetching managers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch managers: {str(e)}"
        )


@app.get("/api/employees")
async def get_employees(
    department: Optional[str] = None,
    manager: Optional[str] = None,
    search: Optional[str] = None
):
    """
    Get all employees with optional filtering

    Args:
        department: Filter by department
        manager: Filter by manager name
        search: Search query for name, email, role, or department

    Returns:
        List of employees
    """
    try:
        if search:
            employees = db.search_employees(search)
        elif department:
            employees = db.get_employees_by_department(department)
        elif manager:
            employees = db.get_employees_by_manager(manager)
        else:
            employees = db.load_employees()

        return {
            "employees": employees,
            "total": len(employees)
        }
    except Exception as e:
        logger.error(f"Error fetching employees: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch employees: {str(e)}"
        )


@app.get("/api/employees/{employee_id}")
async def get_employee(employee_id: int):
    """
    Get specific employee by ID

    Args:
        employee_id: Employee ID

    Returns:
        Employee details
    """
    try:
        employee = db.get_employee_by_id(employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        return employee
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching employee: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch employee: {str(e)}"
        )


@app.get("/api/managers", response_model=ManagersResponse)
async def get_managers():
    """
    Get all managers and their availability

    Returns:
        ManagersResponse with list of all managers
    """
    try:
        managers = db.load_managers()

        # Convert to Pydantic models
        manager_models = [Manager(**manager) for manager in managers]

        return ManagersResponse(
            managers=manager_models,
            total=len(manager_models)
        )

    except Exception as e:
        logger.error(f"Error fetching managers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch managers: {str(e)}"
        )


@app.get("/api/managers/{manager_id}")
async def get_manager(manager_id: int):
    """
    Get specific manager by ID

    Args:
        manager_id: Manager ID

    Returns:
        Manager details
    """
    try:
        manager = db.get_manager_by_id(manager_id)

        if not manager:
            raise HTTPException(
                status_code=404,
                detail=f"Manager with ID {manager_id} not found"
            )

        return Manager(**manager)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching manager {manager_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch manager: {str(e)}"
        )


@app.get("/api/meetings", response_model=MeetingsResponse)
async def get_meetings():
    """
    Get all scheduled meetings

    Returns:
        MeetingsResponse with list of all meetings
    """
    try:
        meetings = db.load_meetings()

        # Convert to Pydantic models
        meeting_models = [Meeting(**meeting) for meeting in meetings]

        return MeetingsResponse(
            meetings=meeting_models,
            total=len(meeting_models)
        )

    except Exception as e:
        logger.error(f"Error fetching meetings: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch meetings: {str(e)}"
        )


@app.get("/api/meetings/{meeting_id}")
async def get_meeting(meeting_id: int):
    """
    Get specific meeting by ID

    Args:
        meeting_id: Meeting ID

    Returns:
        Meeting details
    """
    try:
        meeting = db.get_meeting_by_id(meeting_id)

        if not meeting:
            raise HTTPException(
                status_code=404,
                detail=f"Meeting with ID {meeting_id} not found"
            )

        return Meeting(**meeting)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching meeting {meeting_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch meeting: {str(e)}"
        )


@app.get("/api/statistics")
async def get_statistics():
    """
    Get database statistics

    Returns:
        Statistics about managers and meetings
    """
    try:
        stats = db.get_statistics()
        return stats

    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch statistics: {str(e)}"
        )


@app.get("/api/departments")
async def get_departments():
    """
    Get all unique departments

    Returns:
        List of department names
    """
    try:
        departments = db.get_all_departments()
        return {"departments": departments, "total": len(departments)}

    except Exception as e:
        logger.error(f"Error fetching departments: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch departments: {str(e)}"
        )


@app.get("/api/config")
async def get_config():
    """
    Get current configuration status (for debugging)

    Returns:
        Configuration details
    """
    try:
        config_summary = settings.get_config_summary()
        email_config = get_email_config_status()

        return {
            "application": config_summary,
            "email": email_config
        }

    except Exception as e:
        logger.error(f"Error fetching config: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch config: {str(e)}"
        )


# ============================================================
# ServiceLink AI Endpoints (Home Service Booking)
# ============================================================

@app.post("/api/service-request")
async def create_service_request(request: ScheduleRequest):
    """
    Main service booking endpoint for ServiceLink AI
    Processes natural language service requests in multiple languages (Urdu, Roman Urdu, English)
    Supports stateful conversations with session management

    Args:
        request: ScheduleRequest with natural language message and optional session_id

    Returns:
        Service booking response with provider details and session_id
    """
    try:
        logger.info(f"Processing service request: {request.message}")

        # Validate Groq API key
        if not settings.GROQ_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="Groq API key not configured"
            )

        # Google Maps is optional - will use fallback coordinates if not configured
        if not settings.GOOGLE_MAPS_API_KEY or settings.GOOGLE_MAPS_API_KEY == 'your_google_maps_api_key_here':
            logger.warning("Google Maps API not configured - using fallback coordinates")

        # Get or create session for conversation memory
        session_id = request.session_id or session_manager.create_session()

        # Process service request through orchestrator with OpenAI Agents SDK session
        # The SDK handles conversation memory automatically via SQLiteSession
        from scheduling_agents.service_orchestrator import process_service_request
        result = await process_service_request(
            user_message=request.message,
            conversation_context="",  # Not used anymore - SDK handles memory
            session_id=session_id
        )

        return {
            "status": result["status"],
            "message": result["message"],
            "session_id": session_id,
            "booking": result.get("booking"),
            "workflow_steps": result.get("workflow_steps", []),
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing service request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process service request: {str(e)}"
        )


@app.get("/api/bookings/{booking_id}")
async def get_booking(booking_id: str):
    """
    Get booking status by ID

    Args:
        booking_id: Booking ID (e.g., BKG0001)

    Returns:
        Booking details and status
    """
    try:
        result = await get_booking_status(booking_id)

        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching booking: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch booking: {str(e)}"
        )


@app.delete("/api/bookings/{booking_id}")
async def delete_booking(booking_id: str, reason: Optional[str] = None):
    """
    Cancel booking by ID

    Args:
        booking_id: Booking ID
        reason: Optional cancellation reason

    Returns:
        Cancellation confirmation
    """
    try:
        result = await cancel_booking(booking_id, reason)

        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling booking: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel booking: {str(e)}"
        )


@app.patch("/api/bookings/{booking_id}/status")
async def update_booking_status(booking_id: str, status_data: dict):
    """Update booking status and sync with Google Calendar"""
    try:
        new_status = status_data.get("status")
        if not new_status:
            raise HTTPException(status_code=400, detail="Status is required")

        # Get old booking for comparison
        old_booking = db.get_booking_by_id(booking_id)
        if not old_booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        # Update booking status
        updated_booking = db.update_booking(booking_id, {"status": new_status})

        # Sync with Google Calendar if event ID exists
        try:
            from utils.google_calendar_service import GoogleCalendarService
            google_calendar = GoogleCalendarService()

            if updated_booking.get('google_calendar_event_id') and google_calendar.check_availability():
                google_calendar.update_booking_event(
                    event_id=updated_booking['google_calendar_event_id'],
                    new_status=new_status,
                    additional_notes=f"Status updated from {old_booking['status']} to {new_status}"
                )
                logger.info(f"Synced status update to Google Calendar for booking {booking_id}")
        except Exception as e:
            logger.warning(f"Failed to sync status update to Google Calendar: {e}")

        # Send status update email
        try:
            from utils.reminder_service import ReminderService
            reminder_service = ReminderService()

            if updated_booking.get('customer_email'):
                reminder_service.send_status_update(
                    to_email=updated_booking['customer_email'],
                    booking_id=booking_id,
                    old_status=old_booking['status'],
                    new_status=new_status,
                    service_type=updated_booking['service_type'],
                    customer_name=updated_booking.get('customer_name')
                )
        except Exception as e:
            logger.warning(f"Failed to send status update email: {e}")

        return {"status": "success", "booking": updated_booking}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating booking status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/providers")
async def get_providers(service_type: Optional[str] = None, city: Optional[str] = None):
    """
    Get all providers or filter by service type and city
    """
    try:
        providers = db.get_all_providers()

        # Filter by service type if provided
        if service_type:
            providers = [p for p in providers if p.get('service_type') == service_type]

        # Filter by city if provided
        if city:
            providers = [p for p in providers if p.get('location', {}).get('city') == city]

        return {
            "status": "success",
            "count": len(providers),
            "providers": providers
        }
    except Exception as e:
        logger.error(f"Error fetching providers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/providers/{provider_id}/availability")
async def get_provider_availability(provider_id: str, date: str):
    """
    Get available time slots for a provider on a specific date

    Args:
        provider_id: Provider ID (e.g., PRV001)
        date: Date in YYYY-MM-DD format

    Returns:
        List of available time slots
    """
    try:
        from utils.calendar_service import CalendarService
        calendar_service = CalendarService(db)

        slots = calendar_service.get_available_slots(provider_id, date)

        return {
            "status": "success",
            "provider_id": provider_id,
            "date": date,
            "available_slots": slots,
            "count": len(slots)
        }
    except Exception as e:
        logger.error(f"Error fetching availability: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/providers/{provider_id}/next-available")
async def get_next_available_date(provider_id: str, days_to_check: int = 7):
    """
    Find the next available date with open slots for a provider

    Args:
        provider_id: Provider ID
        days_to_check: Number of days to check ahead (default 7)

    Returns:
        Next available date with slots
    """
    try:
        from utils.calendar_service import CalendarService
        calendar_service = CalendarService(db)

        next_available = calendar_service.get_next_available_date(provider_id, days_to_check)

        if next_available:
            return {
                "status": "success",
                "provider_id": provider_id,
                "next_available": next_available
            }
        else:
            return {
                "status": "no_availability",
                "provider_id": provider_id,
                "message": f"No availability in next {days_to_check} days"
            }
    except Exception as e:
        logger.error(f"Error finding next available date: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/providers/{provider_id}/schedule")
async def get_provider_schedule(provider_id: str, start_date: str, end_date: str):
    """
    Get provider's schedule for a date range

    Args:
        provider_id: Provider ID
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        Provider's schedule with booked and available slots
    """
    try:
        from utils.calendar_service import CalendarService
        calendar_service = CalendarService(db)

        schedule = calendar_service.get_provider_schedule(provider_id, start_date, end_date)

        return {
            "status": "success",
            "provider_id": provider_id,
            "start_date": start_date,
            "end_date": end_date,
            "schedule": schedule
        }
    except Exception as e:
        logger.error(f"Error fetching schedule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bookings")
async def get_all_bookings(status: Optional[str] = None, limit: Optional[int] = 50):
    """
    Get all bookings or filter by status
    """
    try:
        bookings = db.get_all_bookings()

        # Filter by status if provided
        if status:
            bookings = [b for b in bookings if b.get('status') == status]

        # Limit results
        bookings = bookings[:limit]

        return {
            "status": "success",
            "count": len(bookings),
            "bookings": bookings
        }
    except Exception as e:
        logger.error(f"Error fetching bookings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """
    Get dashboard statistics
    """
    try:
        bookings = db.get_all_bookings()
        providers = db.get_all_providers()

        # Calculate stats
        total_bookings = len(bookings)
        active_bookings = len([b for b in bookings if b.get('status') in ['pending', 'confirmed', 'in_progress']])
        completed_bookings = len([b for b in bookings if b.get('status') == 'completed'])
        total_providers = len(providers)

        # Service type breakdown
        service_breakdown = {}
        for booking in bookings:
            service = booking.get('service_type', 'Unknown')
            service_breakdown[service] = service_breakdown.get(service, 0) + 1

        # City breakdown
        city_breakdown = {}
        for booking in bookings:
            location = booking.get('customer_location', '')
            # Extract city from location string
            if 'Karachi' in location:
                city = 'Karachi'
            elif 'Islamabad' in location:
                city = 'Islamabad'
            elif 'Lahore' in location:
                city = 'Lahore'
            else:
                city = 'Other'
            city_breakdown[city] = city_breakdown.get(city, 0) + 1

        return {
            "status": "success",
            "stats": {
                "total_bookings": total_bookings,
                "active_bookings": active_bookings,
                "completed_bookings": completed_bookings,
                "total_providers": total_providers,
                "service_breakdown": service_breakdown,
                "city_breakdown": city_breakdown
            }
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/bookings/{booking_id}/status")
async def update_booking_status(
    booking_id: str,
    status: str,
    notes: Optional[str] = None
):
    """
    Update booking status

    Args:
        booking_id: Booking ID
        status: New status (pending, confirmed, in_progress, completed, cancelled)
        notes: Optional notes about the status change

    Returns:
        Updated booking details
    """
    try:
        # Validate status
        valid_statuses = ['pending', 'confirmed', 'in_progress', 'completed', 'cancelled']
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )

        # Get existing booking
        booking = db.get_booking_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")

        # Update booking
        updates = {
            "status": status,
            "status_updated_at": datetime.now().isoformat()
        }
        if notes:
            updates["status_notes"] = notes

        updated_booking = db.update_booking(booking_id, updates)

        return {
            "status": "success",
            "message": f"Booking {booking_id} status updated to {status}",
            "booking": updated_booking
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating booking status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update booking status: {str(e)}"
        )


@app.get("/api/providers")
async def get_providers(
    service_type: Optional[str] = None,
    area: Optional[str] = None
):
    """
    Get all service providers with optional filtering

    Args:
        service_type: Filter by service type (AC Repair, Plumbing, etc.)
        area: Filter by area/location

    Returns:
        List of service providers
    """
    try:
        data = db.load_service_providers()
        providers = data.get('providers', [])

        # Apply filters
        if service_type:
            providers = db.search_providers_by_service(service_type)

        if area:
            providers = db.search_providers_by_area(area)

        return {
            "providers": providers,
            "total": len(providers),
            "service_types": data.get('service_types', []),
            "service_categories": data.get('service_categories', [])
        }

    except Exception as e:
        logger.error(f"Error fetching providers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch providers: {str(e)}"
        )


@app.get("/api/providers/{provider_id}")
async def get_provider(provider_id: str):
    """
    Get specific provider by ID

    Args:
        provider_id: Provider ID (e.g., PRV001)

    Returns:
        Provider details
    """
    try:
        provider = db.get_provider_by_id(provider_id)

        if not provider:
            raise HTTPException(
                status_code=404,
                detail=f"Provider {provider_id} not found"
            )

        return provider

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching provider: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch provider: {str(e)}"
        )


@app.get("/api/service-types")
async def get_service_types():
    """
    Get all available service types

    Returns:
        List of service types and categories
    """
    try:
        data = db.load_service_providers()

        return {
            "service_types": data.get('service_types', []),
            "service_categories": data.get('service_categories', [])
        }

    except Exception as e:
        logger.error(f"Error fetching service types: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch service types: {str(e)}"
        )


@app.get("/api/bookings")
async def get_all_bookings(
    status: Optional[str] = None,
    customer_phone: Optional[str] = None,
    provider_id: Optional[str] = None
):
    """
    Get all bookings with optional filtering

    Args:
        status: Filter by status (pending, confirmed, completed, cancelled)
        customer_phone: Filter by customer phone
        provider_id: Filter by provider ID

    Returns:
        List of bookings
    """
    try:
        if status:
            bookings = db.get_bookings_by_status(status)
        elif customer_phone:
            bookings = db.get_bookings_by_customer(customer_phone)
        elif provider_id:
            bookings = db.get_bookings_by_provider(provider_id)
        else:
            bookings = db.load_bookings()

        return {
            "bookings": bookings,
            "total": len(bookings)
        }

    except Exception as e:
        logger.error(f"Error fetching bookings: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch bookings: {str(e)}"
        )


# ============================================================
# Smart Scheduling Endpoints
# ============================================================

@app.get("/api/scheduling/best-times")
async def get_best_booking_times(service_type: str, area: str):
    """
    Get optimal booking times based on demand patterns

    Args:
        service_type: Type of service
        area: Area/location

    Returns:
        List of recommended booking times with discounts
    """
    try:
        from utils.smart_scheduler import SmartScheduler
        scheduler = SmartScheduler(db)

        best_times = scheduler.suggest_best_time(service_type, area)

        return {
            "status": "success",
            "service_type": service_type,
            "area": area,
            "recommendations": best_times
        }

    except Exception as e:
        logger.error(f"Error getting best times: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/scheduling/insights")
async def get_scheduling_insights(service_type: str, area: str):
    """
    Get comprehensive scheduling insights

    Args:
        service_type: Type of service
        area: Area/location

    Returns:
        Detailed scheduling insights and recommendations
    """
    try:
        from utils.smart_scheduler import SmartScheduler
        scheduler = SmartScheduler(db)

        insights = scheduler.get_scheduling_insights(service_type, area)

        return {
            "status": "success",
            "service_type": service_type,
            "area": area,
            "insights": insights
        }

    except Exception as e:
        logger.error(f"Error getting scheduling insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/scheduling/peak-hours")
async def get_peak_hours_info():
    """
    Get current peak hours information and surge pricing

    Returns:
        Peak hours status and pricing info
    """
    try:
        from utils.smart_scheduler import SmartScheduler
        scheduler = SmartScheduler(db)

        peak_info = scheduler.get_peak_hours_info()

        return {
            "status": "success",
            "peak_info": peak_info
        }

    except Exception as e:
        logger.error(f"Error getting peak hours info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Provider Acceptance Workflow Endpoints
# ============================================================

@app.post("/api/provider/respond/{booking_id}")
async def provider_respond_to_booking(booking_id: str, response_data: dict):
    """
    Provider accepts or rejects a booking request

    Args:
        booking_id: Booking ID
        response_data: {"response": "accepted" or "rejected", "provider_id": "...", "reason": "..." (optional)}

    Returns:
        Response status and next steps
    """
    try:
        from utils.provider_acceptance_service import ProviderAcceptanceService
        acceptance_service = ProviderAcceptanceService(db)

        response = response_data.get("response")
        provider_id = response_data.get("provider_id")
        reason = response_data.get("reason")

        if not response or not provider_id:
            raise HTTPException(status_code=400, detail="Response and provider_id are required")

        if response == "accepted":
            result = acceptance_service.provider_accept_booking(booking_id, provider_id)
        elif response == "rejected":
            result = acceptance_service.provider_reject_booking(booking_id, provider_id, reason)
        else:
            raise HTTPException(status_code=400, detail="Response must be 'accepted' or 'rejected'")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing provider response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/provider/{provider_id}/stats")
async def get_provider_stats(provider_id: str):
    """
    Get provider's acceptance/rejection statistics

    Args:
        provider_id: Provider ID

    Returns:
        Provider statistics including acceptance rate and response time
    """
    try:
        from utils.provider_acceptance_service import ProviderAcceptanceService
        acceptance_service = ProviderAcceptanceService(db)

        stats = acceptance_service.get_provider_response_stats(provider_id)

        return {
            "status": "success",
            "provider_id": provider_id,
            "stats": stats
        }

    except Exception as e:
        logger.error(f"Error fetching provider stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/provider/initialize-acceptance-system")
async def initialize_provider_acceptance_system():
    """
    Initialize provider acceptance system (create tables)
    """
    try:
        from utils.provider_acceptance_service import ProviderAcceptanceService
        acceptance_service = ProviderAcceptanceService(db)

        success = acceptance_service.create_provider_response_table()

        if success:
            return {
                "status": "success",
                "message": "Provider acceptance system initialized successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to initialize system")

    except Exception as e:
        logger.error(f"Error initializing provider acceptance system: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Startup and Shutdown Events
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("=" * 60)
    logger.info("BizFlow AI - Agentic Scheduling System")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info(f"Groq API Configured: {bool(settings.GROQ_API_KEY)}")
    logger.info(f"Gmail API Configured: {settings.CREDENTIALS_FILE.exists()}")

    # Validate settings
    if settings.DEBUG:
        settings.validate_settings()

    logger.info("Application started successfully")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Application shutting down...")


# ============================================================
# Main Entry Point
# ============================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG,
        log_level="info"
    )
