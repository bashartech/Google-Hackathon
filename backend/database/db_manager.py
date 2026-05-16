import json
import os
from typing import List, Dict, Optional
from datetime import datetime

class DatabaseManager:
    """
    Database Manager for BizFlow AI
    Handles all JSON database operations for managers and meetings
    """

    def __init__(self):
        self.base_path = os.path.dirname(__file__)
        self.managers_file = os.path.join(self.base_path, "managers.json")
        self.meetings_file = os.path.join(self.base_path, "meetings.json")
        self.employees_file = os.path.join(self.base_path, "employees.json")
        self.service_providers_file = os.path.join(self.base_path, "service_providers.json")
        self.bookings_file = os.path.join(self.base_path, "bookings.json")

    def load_managers(self) -> List[Dict]:
        """Load all managers from JSON database"""
        try:
            with open(self.managers_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def get_manager_by_id(self, manager_id: int) -> Optional[Dict]:
        """Get specific manager by ID"""
        managers = self.load_managers()
        return next((m for m in managers if m['id'] == manager_id), None)

    def get_manager_by_name(self, name: str) -> Optional[Dict]:
        """Get manager by name (case-insensitive partial match)"""
        managers = self.load_managers()
        name_lower = name.lower()

        # Try exact match first
        for manager in managers:
            if manager['name'].lower() == name_lower:
                return manager

        # Try partial match
        for manager in managers:
            if name_lower in manager['name'].lower():
                return manager

        return None

    def get_manager_by_email(self, email: str) -> Optional[Dict]:
        """Get manager by email"""
        managers = self.load_managers()
        return next((m for m in managers if m['email'].lower() == email.lower()), None)

    def search_managers(self, query: str) -> List[Dict]:
        """Search managers by name, role, or department"""
        managers = self.load_managers()
        query_lower = query.lower()

        results = []
        for manager in managers:
            if (query_lower in manager['name'].lower() or
                query_lower in manager['role'].lower() or
                query_lower in manager['department'].lower()):
                results.append(manager)

        return results

    def load_meetings(self) -> List[Dict]:
        """Load all meetings from JSON database"""
        try:
            with open(self.meetings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def save_meeting(self, meeting: Dict) -> Dict:
        """Save a new meeting to database"""
        meetings = self.load_meetings()

        # Generate new ID
        meeting['id'] = len(meetings) + 1
        meeting['created_at'] = datetime.now().isoformat()
        meeting['status'] = meeting.get('status', 'confirmed')

        meetings.append(meeting)

        # Save to file
        with open(self.meetings_file, 'w', encoding='utf-8') as f:
            json.dump(meetings, f, indent=2, ensure_ascii=False)

        return meeting

    def get_meeting(self, meeting_id: int) -> Optional[Dict]:
        """Get specific meeting by ID (alias for get_meeting_by_id)"""
        return self.get_meeting_by_id(meeting_id)

    def update_meeting(self, meeting_id: int, updates: Dict) -> Optional[Dict]:
        """
        Update an existing meeting with new data

        Args:
            meeting_id: ID of meeting to update
            updates: Dictionary of fields to update

        Returns:
            Updated meeting or None if not found
        """
        meetings = self.load_meetings()

        # Find meeting to update
        meeting_index = None
        for i, meeting in enumerate(meetings):
            if meeting['id'] == meeting_id:
                meeting_index = i
                break

        if meeting_index is None:
            return None

        # Update meeting fields
        meetings[meeting_index].update(updates)
        meetings[meeting_index]['updated_at'] = datetime.now().isoformat()

        # Save to file
        with open(self.meetings_file, 'w', encoding='utf-8') as f:
            json.dump(meetings, f, indent=2, ensure_ascii=False)

        return meetings[meeting_index]

    def get_meeting_by_id(self, meeting_id: int) -> Optional[Dict]:
        """Get specific meeting by ID"""
        meetings = self.load_meetings()
        return next((m for m in meetings if m['id'] == meeting_id), None)

    def get_meetings_by_date(self, date: str) -> List[Dict]:
        """Get all meetings for a specific date"""
        meetings = self.load_meetings()
        return [m for m in meetings if m.get('date') == date]

    def get_meetings_by_day(self, day: str) -> List[Dict]:
        """Get all meetings for a specific day of week"""
        meetings = self.load_meetings()
        return [m for m in meetings if m.get('day', '').lower() == day.lower()]

    def check_availability(self, manager_id: int, day: str, time: str) -> bool:
        """
        Check if manager is available at specific time

        Args:
            manager_id: Manager ID
            day: Day of week (e.g., 'monday')
            time: Time slot (e.g., '2PM')

        Returns:
            True if available, False otherwise
        """
        manager = self.get_manager_by_id(manager_id)
        if not manager:
            return False

        availability = manager.get('availability', {}).get(day.lower(), [])
        return time in availability

    def find_common_availability(self, manager_ids: List[int], day: str = None) -> List[Dict]:
        """
        Find common available time slots for multiple managers

        Args:
            manager_ids: List of manager IDs
            day: Optional specific day to check

        Returns:
            List of common time slots
        """
        if not manager_ids:
            return []

        # Get all managers
        managers = [self.get_manager_by_id(mid) for mid in manager_ids]
        managers = [m for m in managers if m is not None]

        if not managers:
            return []

        # Days to check
        days_to_check = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        if day:
            days_to_check = [day.lower()]

        common_slots = []

        for check_day in days_to_check:
            # Get availability for first manager
            first_manager_slots = set(managers[0].get('availability', {}).get(check_day, []))

            # Find intersection with other managers
            for manager in managers[1:]:
                manager_slots = set(manager.get('availability', {}).get(check_day, []))
                first_manager_slots = first_manager_slots.intersection(manager_slots)

            # Add to common slots
            for time_slot in sorted(first_manager_slots):
                common_slots.append({
                    "day": check_day.capitalize(),
                    "time": time_slot,
                    "available_participants": len(managers)
                })

        return common_slots

    def get_all_departments(self) -> List[str]:
        """Get list of all unique departments"""
        managers = self.load_managers()
        departments = set(m['department'] for m in managers)
        return sorted(list(departments))

    def get_managers_by_department(self, department: str) -> List[Dict]:
        """Get all managers in a specific department"""
        managers = self.load_managers()
        return [m for m in managers if m['department'].lower() == department.lower()]

    def get_statistics(self) -> Dict[str, int]:
        """Get database statistics"""
        managers = self.load_managers()
        meetings = self.load_meetings()
        employees = self.load_employees()

        return {
            "total_managers": len(managers),
            "total_meetings": len(meetings),
            "total_employees": len(employees),
            "confirmed_meetings": len([m for m in meetings if m.get('status') == 'confirmed']),
            "active_employees": len([e for e in employees if e.get('status') == 'active'])
        }

    # ============================================================
    # EMPLOYEES MANAGEMENT
    # ============================================================

    def load_employees(self) -> List[Dict]:
        """Load all employees from database"""
        try:
            with open(self.employees_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def get_employee_by_id(self, employee_id: int) -> Optional[Dict]:
        """Get specific employee by ID"""
        employees = self.load_employees()
        return next((e for e in employees if e['id'] == employee_id), None)

    def get_employee_by_name(self, name: str) -> Optional[Dict]:
        """Get employee by name (case-insensitive)"""
        employees = self.load_employees()
        name_lower = name.lower()
        return next((e for e in employees if e['name'].lower() == name_lower), None)

    def get_employee_by_email(self, email: str) -> Optional[Dict]:
        """Get employee by email"""
        employees = self.load_employees()
        return next((e for e in employees if e['email'].lower() == email.lower()), None)

    def get_employees_by_department(self, department: str) -> List[Dict]:
        """Get all employees in a specific department"""
        employees = self.load_employees()
        return [e for e in employees if e.get('department', '').lower() == department.lower()]

    def get_employees_by_manager(self, manager_name: str) -> List[Dict]:
        """Get all employees reporting to a specific manager"""
        employees = self.load_employees()
        return [e for e in employees if e.get('manager', '').lower() == manager_name.lower()]

    def search_employees(self, query: str) -> List[Dict]:
        """Search employees by name, email, role, or department"""
        employees = self.load_employees()
        query_lower = query.lower()

        return [
            e for e in employees
            if query_lower in e.get('name', '').lower()
            or query_lower in e.get('email', '').lower()
            or query_lower in e.get('role', '').lower()
            or query_lower in e.get('department', '').lower()
        ]

    def update_meeting_status(self, meeting_id: int, status: str) -> bool:
        """Update meeting status"""
        meetings = self.load_meetings()

        for meeting in meetings:
            if meeting['id'] == meeting_id:
                meeting['status'] = status
                meeting['updated_at'] = datetime.now().isoformat()

                # Save to file
                with open(self.meetings_file, 'w', encoding='utf-8') as f:
                    json.dump(meetings, f, indent=2, ensure_ascii=False)

                return True

        return False

    def delete_meeting(self, meeting_id: int) -> bool:
        """Delete a meeting"""
        meetings = self.load_meetings()
        original_length = len(meetings)

        meetings = [m for m in meetings if m['id'] != meeting_id]

        if len(meetings) < original_length:
            # Save to file
            with open(self.meetings_file, 'w', encoding='utf-8') as f:
                json.dump(meetings, f, indent=2, ensure_ascii=False)
            return True

        return False

    def get_statistics(self) -> Dict:
        """Get database statistics"""
        managers = self.load_managers()
        meetings = self.load_meetings()

        return {
            "total_managers": len(managers),
            "total_meetings": len(meetings),
            "departments": len(self.get_all_departments()),
            "confirmed_meetings": len([m for m in meetings if m.get('status') == 'confirmed']),
            "pending_meetings": len([m for m in meetings if m.get('status') == 'pending'])
        }

    # ============================================================
    # SERVICE PROVIDERS MANAGEMENT (ServiceLink AI)
    # ============================================================

    def load_service_providers(self) -> Dict:
        """Load all service providers from JSON database"""
        try:
            with open(self.service_providers_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"providers": [], "service_categories": [], "service_types": []}
        except json.JSONDecodeError:
            return {"providers": [], "service_categories": [], "service_types": []}

    def get_provider_by_id(self, provider_id: str) -> Optional[Dict]:
        """Get specific service provider by ID"""
        data = self.load_service_providers()
        providers = data.get('providers', [])
        return next((p for p in providers if p['provider_id'] == provider_id), None)

    def search_providers_by_service(self, service_type: str) -> List[Dict]:
        """Search providers by service type"""
        data = self.load_service_providers()
        providers = data.get('providers', [])
        service_type_lower = service_type.lower()

        return [
            p for p in providers
            if service_type_lower in p.get('service_type', '').lower()
            or service_type_lower in p.get('service_category', '').lower()
            or any(service_type_lower in service.lower() for service in p.get('services_offered', []))
        ]

    def search_providers_by_area(self, area: str) -> List[Dict]:
        """Search providers by area/location"""
        data = self.load_service_providers()
        providers = data.get('providers', [])
        area_lower = area.lower()

        return [
            p for p in providers
            if area_lower in p.get('location', {}).get('area', '').lower()
            or area_lower in p.get('location', {}).get('city', '').lower()
            or area_lower in p.get('location', {}).get('address', '').lower()
        ]

    def get_all_service_types(self) -> List[str]:
        """Get all available service types"""
        data = self.load_service_providers()
        return data.get('service_types', [])

    def get_all_service_categories(self) -> List[str]:
        """Get all service categories"""
        data = self.load_service_providers()
        return data.get('service_categories', [])

    # ============================================================
    # BOOKINGS MANAGEMENT (ServiceLink AI)
    # ============================================================

    def load_bookings(self) -> List[Dict]:
        """Load all bookings from JSON database"""
        try:
            with open(self.bookings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('bookings', [])
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def save_booking(self, booking: Dict) -> Dict:
        """Save a new booking to database"""
        try:
            with open(self.bookings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"bookings": [], "booking_counter": 1}

        bookings = data.get('bookings', [])
        counter = data.get('booking_counter', 1)

        # Generate new booking ID
        booking['booking_id'] = f"BKG{counter:04d}"
        booking['created_at'] = datetime.now().isoformat()
        booking['status'] = booking.get('status', 'pending')

        bookings.append(booking)
        data['bookings'] = bookings
        data['booking_counter'] = counter + 1

        # Save to file
        with open(self.bookings_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return booking

    def get_booking_by_id(self, booking_id: str) -> Optional[Dict]:
        """Get specific booking by ID"""
        bookings = self.load_bookings()
        return next((b for b in bookings if b.get('booking_id') == booking_id), None)

    def update_booking(self, booking_id: str, updates: Dict) -> Optional[Dict]:
        """Update an existing booking"""
        try:
            with open(self.bookings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

        bookings = data.get('bookings', [])

        # Find booking to update
        booking_index = None
        for i, booking in enumerate(bookings):
            if booking.get('booking_id') == booking_id:
                booking_index = i
                break

        if booking_index is None:
            return None

        # Update booking fields
        bookings[booking_index].update(updates)
        bookings[booking_index]['updated_at'] = datetime.now().isoformat()

        data['bookings'] = bookings

        # Save to file
        with open(self.bookings_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return bookings[booking_index]

    def get_bookings_by_customer(self, customer_phone: str) -> List[Dict]:
        """Get all bookings for a specific customer"""
        bookings = self.load_bookings()
        return [b for b in bookings if b.get('customer_phone') == customer_phone]

    def get_bookings_by_provider(self, provider_id: str) -> List[Dict]:
        """Get all bookings for a specific provider"""
        bookings = self.load_bookings()
        return [b for b in bookings if b.get('provider_id') == provider_id]

    def get_bookings_by_status(self, status: str) -> List[Dict]:
        """Get all bookings with specific status"""
        bookings = self.load_bookings()
        return [b for b in bookings if b.get('status', '').lower() == status.lower()]
