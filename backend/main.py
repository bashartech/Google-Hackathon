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
from database.db_manager import DatabaseManager
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


@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """
    Get dashboard statistics

    Returns:
        Dashboard statistics including counts and summaries
    """
    try:
        stats = db.get_statistics()
        managers = db.load_managers()
        meetings = db.load_meetings()
        employees = db.load_employees()

        # Calculate additional stats
        departments = set()
        for manager in managers:
            departments.add(manager.get('department', 'Unknown'))
        for employee in employees:
            departments.add(employee.get('department', 'Unknown'))

        # Recent meetings (last 5)
        recent_meetings = sorted(
            meetings,
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )[:5]

        # Meetings by status
        meetings_by_status = {
            "confirmed": len([m for m in meetings if m.get('status') == 'confirmed']),
            "pending": len([m for m in meetings if m.get('status') == 'pending']),
            "cancelled": len([m for m in meetings if m.get('status') == 'cancelled'])
        }

        # Employees by department
        employees_by_dept = {}
        for employee in employees:
            dept = employee.get('department', 'Unknown')
            employees_by_dept[dept] = employees_by_dept.get(dept, 0) + 1

        return {
            "overview": {
                "total_managers": stats.get('total_managers', 0),
                "total_employees": stats.get('total_employees', 0),
                "total_meetings": stats.get('total_meetings', 0),
                "total_departments": len(departments),
                "active_employees": stats.get('active_employees', 0),
                "confirmed_meetings": stats.get('confirmed_meetings', 0)
            },
            "meetings_by_status": meetings_by_status,
            "employees_by_department": employees_by_dept,
            "recent_meetings": recent_meetings,
            "departments": sorted(list(departments))
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch dashboard stats: {str(e)}"
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
