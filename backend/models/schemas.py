"""
Pydantic Models for BizFlow AI API
Request and Response schemas
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============================================================
# Request Models
# ============================================================

class ScheduleRequest(BaseModel):
    """Request model for scheduling endpoint"""
    message: str = Field(
        ...,
        description="Natural language scheduling request",
        min_length=1,
        examples=["Schedule a product review meeting with Ali Khan and Sarah Ahmed tomorrow at 2PM"]
    )
    session_id: Optional[str] = Field(
        None,
        description="Session ID for conversation continuity. If not provided, a new session will be created."
    )


# ============================================================
# Response Models
# ============================================================

class WorkflowStep(BaseModel):
    """Workflow step model"""
    agent: str = Field(..., description="Agent name")
    stage: str = Field(..., description="Stage description")
    status: str = Field(..., description="Status: in_progress, completed, failed")
    timestamp: str = Field(..., description="ISO timestamp")
    action: str = Field(..., description="Action description")
    error: Optional[str] = Field(None, description="Error message if failed")


class ScheduleResponse(BaseModel):
    """Response model for scheduling endpoint"""
    status: str = Field(..., description="Status of the request (success/error/conversational)")
    final_output: str = Field(..., description="Final output message from the agent system")
    workflow_complete: bool = Field(..., description="Whether the workflow completed successfully")
    session_id: str = Field(..., description="Session ID for conversation continuity")
    workflow_steps: Optional[List[WorkflowStep]] = Field(None, description="Workflow steps executed")
    error: Optional[str] = Field(None, description="Error message if status is error")


class Manager(BaseModel):
    """Manager model"""
    id: int
    name: str
    email: EmailStr
    role: str
    department: str
    availability: Dict[str, List[str]]
    timezone: str


class ManagersResponse(BaseModel):
    """Response model for managers endpoint"""
    managers: List[Manager]
    total: int


class Meeting(BaseModel):
    """Meeting model"""
    id: int
    meeting_type: str
    participants: List[str]
    participant_emails: List[EmailStr]
    day: str
    time: str
    status: str
    priority: Optional[str] = Field(None, description="Priority level: emergency, urgent, high, medium, low")
    priority_reasoning: Optional[str] = Field(None, description="Explanation for priority level")
    reasoning: Optional[str] = None
    created_at: str


class MeetingsResponse(BaseModel):
    """Response model for meetings endpoint"""
    meetings: List[Meeting]
    total: int


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    service: str
    status: str
    version: str
    timestamp: str
    configuration: Dict[str, Any]


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str
    status_code: int
    timestamp: str
