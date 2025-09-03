from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, date
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Urlaubsplaner API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class VacationType(str, Enum):
    URLAUB = "URLAUB"
    KRANKHEIT = "KRANKHEIT"
    SONDERURLAUB = "SONDERURLAUB"

class UserRole(str, Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"
    LEIHARBEITER = "leiharbeiter"

# Data Models
class Skill(BaseModel):
    name: str
    rating: int = Field(ge=1, le=5)  # 1-5 stars

class Employee(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: Optional[str] = ""
    role: UserRole = UserRole.EMPLOYEE
    vacation_days_total: int = 25
    skills: List[Skill] = Field(default_factory=list)
    created_date: datetime = Field(default_factory=datetime.utcnow)

class EmployeeCreate(BaseModel):
    name: str
    email: Optional[str] = ""
    role: UserRole = UserRole.EMPLOYEE
    skills: List[Skill] = Field(default_factory=list)

class VacationEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    employee_name: str  # For easier frontend display
    start_date: date
    end_date: date
    vacation_type: VacationType
    notes: Optional[str] = ""
    days_count: int  # Calculated field
    created_date: datetime = Field(default_factory=datetime.utcnow)

class VacationEntryCreate(BaseModel):
    employee_id: str
    start_date: date
    end_date: date
    vacation_type: VacationType
    notes: Optional[str] = ""

class CompanySettings(BaseModel):
    max_concurrent_percentage: int = 30  # 30% of total employees
    max_concurrent_fixed: Optional[int] = None  # Fixed number instead of percentage

# Helper Functions
def calculate_business_days(start_date: date, end_date: date) -> int:
    """Calculate business days between two dates (excluding weekends)"""
    from datetime import timedelta
    
    current_date = start_date
    business_days = 0
    
    while current_date <= end_date:
        # 0 = Monday, 6 = Sunday
        if current_date.weekday() < 5:  # Monday to Friday
            business_days += 1
        current_date += timedelta(days=1)
    
    return business_days

async def get_employee_by_id(employee_id: str) -> Optional[Employee]:
    """Get employee by ID"""
    employee_data = await db.employees.find_one({"id": employee_id})
    if employee_data:
        return Employee(**employee_data)
    return None

async def check_concurrent_vacations(start_date: date, end_date: date, exclude_entry_id: Optional[str] = None) -> dict:
    """Check if adding this vacation would exceed the concurrent limit"""
    from datetime import timedelta
    
    # Convert dates to ISO format for MongoDB query
    start_date_str = start_date.isoformat()
    end_date_str = end_date.isoformat()
    
    # Get all vacation entries that overlap with the requested dates
    overlap_query = {
        "start_date": {"$lte": end_date_str},
        "end_date": {"$gte": start_date_str},
        "vacation_type": VacationType.URLAUB  # Only count actual vacation days
    }
    
    if exclude_entry_id:
        overlap_query["id"] = {"$ne": exclude_entry_id}
    
    overlapping_vacations = await db.vacation_entries.find(overlap_query).to_list(1000)
    
    # Get total number of employees
    total_employees = await db.employees.count_documents({})
    
    # Check each day in the range
    current_date = start_date
    max_concurrent_day = None
    max_concurrent_count = 0
    
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Only check business days
            daily_count = 0
            for vacation in overlapping_vacations:
                # Handle both string and date objects for compatibility
                if isinstance(vacation["start_date"], str):
                    vacation_start = datetime.strptime(vacation["start_date"], "%Y-%m-%d").date()
                else:
                    vacation_start = vacation["start_date"]
                    
                if isinstance(vacation["end_date"], str):
                    vacation_end = datetime.strptime(vacation["end_date"], "%Y-%m-%d").date()
                else:
                    vacation_end = vacation["end_date"]
                    
                if vacation_start <= current_date <= vacation_end:
                    daily_count += 1
            
            # Add 1 for the new vacation we're checking
            daily_count += 1
            
            if daily_count > max_concurrent_count:
                max_concurrent_count = daily_count
                max_concurrent_day = current_date
        
        current_date += timedelta(days=1)
    
    settings = CompanySettings()
    
    # Calculate max allowed based on settings
    if settings.max_concurrent_fixed:
        max_allowed = settings.max_concurrent_fixed
    elif total_employees > 0:
        max_allowed = max(1, int((settings.max_concurrent_percentage / 100) * total_employees))
    else:
        max_allowed = 1  # Fallback for empty company
    
    percentage = round((max_concurrent_count / max(total_employees, 1)) * 100, 1) if total_employees > 0 else 0
    
    return {
        "is_valid": max_concurrent_count <= max_allowed,
        "max_concurrent_count": max_concurrent_count,
        "max_allowed": max_allowed,
        "max_concurrent_day": max_concurrent_day,
        "percentage": percentage,
        "total_employees": total_employees
    }

# API Endpoints

# Employee Management
@api_router.post("/employees", response_model=Employee)
async def create_employee(employee_data: EmployeeCreate):
    """Create a new employee"""
    employee = Employee(**employee_data.dict())
    await db.employees.insert_one(employee.dict())
    return employee

@api_router.get("/employees", response_model=List[Employee])
async def get_employees():
    """Get all employees"""
    employees = await db.employees.find().to_list(1000)
    return [Employee(**emp) for emp in employees]

@api_router.get("/employees/{employee_id}", response_model=Employee)
async def get_employee(employee_id: str):
    """Get employee by ID"""
    employee = await get_employee_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@api_router.put("/employees/{employee_id}", response_model=Employee)
async def update_employee(employee_id: str, employee_data: EmployeeCreate):
    """Update employee"""
    existing_employee = await get_employee_by_id(employee_id)
    if not existing_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    updated_employee = Employee(
        id=employee_id,
        **employee_data.dict(),
        created_date=existing_employee.created_date
    )
    
    await db.employees.replace_one({"id": employee_id}, updated_employee.dict())
    return updated_employee

@api_router.delete("/employees/{employee_id}")
async def delete_employee(employee_id: str):
    """Delete employee and all their vacation entries"""
    employee = await get_employee_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Delete all vacation entries for this employee
    await db.vacation_entries.delete_many({"employee_id": employee_id})
    
    # Delete the employee
    await db.employees.delete_one({"id": employee_id})
    
    return {"message": "Employee and all vacation entries deleted successfully"}

# Vacation Entry Management
@api_router.post("/vacation-entries", response_model=VacationEntry)
async def create_vacation_entry(vacation_data: VacationEntryCreate):
    """Create a new vacation entry"""
    # Validate employee exists
    employee = await get_employee_by_id(vacation_data.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Validate date range
    if vacation_data.start_date > vacation_data.end_date:
        raise HTTPException(status_code=400, detail="Start date must be before or equal to end date")
    
    # Calculate business days
    days_count = calculate_business_days(vacation_data.start_date, vacation_data.end_date)
    
    # Check concurrent vacation limits (only for actual vacations, not sick days)
    if vacation_data.vacation_type == VacationType.URLAUB:
        concurrent_check = await check_concurrent_vacations(vacation_data.start_date, vacation_data.end_date)
        if not concurrent_check["is_valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Too many concurrent vacations. Maximum {concurrent_check['max_allowed']} people ({concurrent_check['percentage']}%) can be on vacation simultaneously. Peak day: {concurrent_check['max_concurrent_day']} with {concurrent_check['max_concurrent_count']} people."
            )
    
    # Create vacation entry - convert dates to strings for MongoDB
    vacation_dict = vacation_data.dict()
    vacation_dict['start_date'] = vacation_dict['start_date'].isoformat()
    vacation_dict['end_date'] = vacation_dict['end_date'].isoformat()
    
    vacation_entry = VacationEntry(
        **vacation_dict,
        employee_name=employee.name,
        days_count=days_count
    )
    
    # Convert the entire dict for MongoDB (dates already converted above)
    entry_dict = vacation_entry.dict()
    entry_dict['start_date'] = vacation_dict['start_date']  # Keep as string
    entry_dict['end_date'] = vacation_dict['end_date']      # Keep as string
    
    await db.vacation_entries.insert_one(entry_dict)
    return vacation_entry

@api_router.get("/vacation-entries", response_model=List[VacationEntry])
async def get_vacation_entries(
    employee_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    vacation_type: Optional[VacationType] = None
):
    """Get vacation entries with optional filters"""
    query = {}
    
    if employee_id:
        query["employee_id"] = employee_id
    if start_date:
        query["end_date"] = {"$gte": start_date}
    if end_date:
        if "start_date" not in query:
            query["start_date"] = {}
        query["start_date"]["$lte"] = end_date
    if vacation_type:
        query["vacation_type"] = vacation_type
    
    vacation_entries = await db.vacation_entries.find(query).sort("start_date", 1).to_list(1000)
    return [VacationEntry(**entry) for entry in vacation_entries]

@api_router.get("/vacation-entries/{entry_id}", response_model=VacationEntry)
async def get_vacation_entry(entry_id: str):
    """Get vacation entry by ID"""
    entry_data = await db.vacation_entries.find_one({"id": entry_id})
    if not entry_data:
        raise HTTPException(status_code=404, detail="Vacation entry not found")
    return VacationEntry(**entry_data)

@api_router.put("/vacation-entries/{entry_id}", response_model=VacationEntry)
async def update_vacation_entry(entry_id: str, vacation_data: VacationEntryCreate):
    """Update vacation entry"""
    # Check if entry exists
    existing_entry_data = await db.vacation_entries.find_one({"id": entry_id})
    if not existing_entry_data:
        raise HTTPException(status_code=404, detail="Vacation entry not found")
    
    existing_entry = VacationEntry(**existing_entry_data)
    
    # Validate employee exists
    employee = await get_employee_by_id(vacation_data.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Validate date range
    if vacation_data.start_date > vacation_data.end_date:
        raise HTTPException(status_code=400, detail="Start date must be before or equal to end date")
    
    # Calculate business days
    days_count = calculate_business_days(vacation_data.start_date, vacation_data.end_date)
    
    # Check concurrent vacation limits (exclude current entry from check)
    if vacation_data.vacation_type == VacationType.URLAUB:
        concurrent_check = await check_concurrent_vacations(
            vacation_data.start_date, 
            vacation_data.end_date, 
            exclude_entry_id=entry_id
        )
        if not concurrent_check["is_valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Too many concurrent vacations. Maximum {concurrent_check['max_allowed']} people can be on vacation simultaneously."
            )
    
    # Update vacation entry - convert dates to strings for MongoDB  
    vacation_dict = vacation_data.dict()
    vacation_dict['start_date'] = vacation_dict['start_date'].isoformat()
    vacation_dict['end_date'] = vacation_dict['end_date'].isoformat()
    
    updated_entry = VacationEntry(
        id=entry_id,
        **vacation_dict,
        employee_name=employee.name,
        days_count=days_count,
        created_date=existing_entry.created_date
    )
    
    # Convert for MongoDB storage
    entry_dict = updated_entry.dict()
    entry_dict['start_date'] = vacation_dict['start_date']  # Keep as string
    entry_dict['end_date'] = vacation_dict['end_date']      # Keep as string
    
    await db.vacation_entries.replace_one({"id": entry_id}, entry_dict)
    return updated_entry

@api_router.delete("/vacation-entries/{entry_id}")
async def delete_vacation_entry(entry_id: str):
    """Delete vacation entry"""
    entry_data = await db.vacation_entries.find_one({"id": entry_id})
    if not entry_data:
        raise HTTPException(status_code=404, detail="Vacation entry not found")
    
    await db.vacation_entries.delete_one({"id": entry_id})
    return {"message": "Vacation entry deleted successfully"}

# Analytics & Reporting
@api_router.get("/analytics/employee-summary/{employee_id}")
async def get_employee_vacation_summary(employee_id: str, year: int = 2025):
    """Get vacation summary for a specific employee and year"""
    employee = await get_employee_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Get vacation entries for the year
    start_of_year = date(year, 1, 1)
    end_of_year = date(year, 12, 31)
    
    vacation_entries = await db.vacation_entries.find({
        "employee_id": employee_id,
        "start_date": {"$gte": start_of_year},
        "end_date": {"$lte": end_of_year}
    }).to_list(1000)
    
    # Calculate totals by type
    urlaub_days = sum(entry["days_count"] for entry in vacation_entries if entry["vacation_type"] == VacationType.URLAUB)
    krankheit_days = sum(entry["days_count"] for entry in vacation_entries if entry["vacation_type"] == VacationType.KRANKHEIT)
    sonderurlaub_days = sum(entry["days_count"] for entry in vacation_entries if entry["vacation_type"] == VacationType.SONDERURLAUB)
    
    return {
        "employee": employee,
        "year": year,
        "vacation_days_total": employee.vacation_days_total,
        "vacation_days_used": urlaub_days,
        "vacation_days_remaining": employee.vacation_days_total - urlaub_days,
        "sick_days": krankheit_days,
        "special_leave_days": sonderurlaub_days,
        "total_days_off": urlaub_days + krankheit_days + sonderurlaub_days,
        "vacation_entries": [VacationEntry(**entry) for entry in vacation_entries]
    }

@api_router.get("/analytics/employee-sick-days/{employee_id}")
async def get_employee_sick_days(employee_id: str, year: int = 2025):
    """Get sick days for a specific employee and year"""
    # Get vacation entries for the year that are sick days
    start_of_year = date(year, 1, 1)
    end_of_year = date(year, 12, 31)
    
    sick_entries = await db.vacation_entries.find({
        "employee_id": employee_id,
        "vacation_type": VacationType.KRANKHEIT,
        "start_date": {"$gte": start_of_year.isoformat()},
        "end_date": {"$lte": end_of_year.isoformat()}
    }).to_list(1000)
    
    total_sick_days = sum(entry["days_count"] for entry in sick_entries)
    
    return {
        "employee_id": employee_id,
        "year": year,
        "sick_days": total_sick_days,
        "sick_entries_count": len(sick_entries)
    }

@api_router.get("/analytics/team-overview")
async def get_team_overview(start_date: date, end_date: date):
    """Get team vacation overview for a date range"""
    # Get all vacation entries in the date range
    vacation_entries = await db.vacation_entries.find({
        "start_date": {"$lte": end_date},
        "end_date": {"$gte": start_date}
    }).to_list(1000)
    
    # Get all employees
    employees = await db.employees.find().to_list(1000)
    
    # Check concurrent vacations for the date range
    concurrent_check = await check_concurrent_vacations(start_date, end_date)
    
    return {
        "date_range": {"start_date": start_date, "end_date": end_date},
        "total_employees": len(employees),
        "vacation_entries_count": len(vacation_entries),
        "concurrent_analysis": concurrent_check,
        "vacation_entries": [VacationEntry(**entry) for entry in vacation_entries]
    }

@api_router.get("/settings")
async def get_company_settings():
    """Get company settings with current employee count"""
    total_employees = await db.employees.count_documents({})
    settings = CompanySettings()
    
    return {
        "max_concurrent_percentage": settings.max_concurrent_percentage,
        "max_concurrent_fixed": settings.max_concurrent_fixed,
        "total_employees": total_employees,
        "max_concurrent_calculated": settings.max_concurrent_fixed or max(1, int((settings.max_concurrent_percentage / 100) * total_employees))
    }

# Health check
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Urlaubsplaner API is running"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()