"""
Legacy agent system for meeting scheduling requests.
This module provides backward compatibility for the original Business Automation system.
"""

from typing import Dict, Any
from datetime import datetime
import json


async def process_scheduling_request(
    user_message: str,
    user_email: str = None,
    conversation_context: str = ""
) -> Dict[str, Any]:
    """
    Process a meeting scheduling request.

    This is a legacy function maintained for backward compatibility.
    For new service booking requests, use service_orchestrator.process_service_request()

    Args:
        user_message: The user's scheduling request
        user_email: Optional user email for notifications
        conversation_context: Previous conversation context

    Returns:
        Dict containing scheduling response and metadata
    """

    return {
        "status": "success",
        "message": "This endpoint is for legacy meeting scheduling. Please use the service booking endpoint for ServiceLink AI.",
        "data": {
            "request_type": "meeting_scheduling",
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "note": "Legacy system - use /api/service-request for ServiceLink AI"
        },
        "workflow_steps": []
    }


def extract_meeting_details(user_message: str) -> Dict[str, Any]:
    """
    Extract meeting details from user message.
    Legacy function for meeting scheduler.
    """
    return {
        "extracted": False,
        "message": "Legacy meeting scheduler - use ServiceLink AI for service bookings"
    }
