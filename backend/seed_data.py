#!/usr/bin/env python3
"""
Demo data seeder for the Urlaubsplaner
Creates 20 employees and sample vacation entries for testing
"""

import asyncio
import os
from datetime import datetime, date, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uuid

# Load environment
load_dotenv()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Demo employees data
DEMO_EMPLOYEES = [
    {"name": "Anna Schmidt", "email": "anna.schmidt@firma.de", "role": "admin"},
    {"name": "Thomas Müller", "email": "thomas.mueller@firma.de", "role": "admin"},
    {"name": "Sarah Weber", "email": "sarah.weber@firma.de", "role": "employee"},
    {"name": "Michael Bach", "email": "michael.bach@firma.de", "role": "employee"},
    {"name": "Julia Fischer", "email": "julia.fischer@firma.de", "role": "employee"},
    {"name": "David Wagner", "email": "david.wagner@firma.de", "role": "employee"},
    {"name": "Lisa Becker", "email": "lisa.becker@firma.de", "role": "employee"},
    {"name": "Martin Schulz", "email": "martin.schulz@firma.de", "role": "employee"},
    {"name": "Sandra Hoffmann", "email": "sandra.hoffmann@firma.de", "role": "employee"},
    {"name": "Christian Klein", "email": "christian.klein@firma.de", "role": "employee"},
    {"name": "Nina Richter", "email": "nina.richter@firma.de", "role": "employee"},
    {"name": "Stefan Neumann", "email": "stefan.neumann@firma.de", "role": "employee"},
    {"name": "Petra Braun", "email": "petra.braun@firma.de", "role": "employee"},
    {"name": "Andreas Wolf", "email": "andreas.wolf@firma.de", "role": "employee"},
    {"name": "Melanie Krüger", "email": "melanie.krueger@firma.de", "role": "employee"},
    {"name": "Robert Zimmermann", "email": "robert.zimmermann@firma.de", "role": "employee"},
    {"name": "Claudia Hartmann", "email": "claudia.hartmann@firma.de", "role": "employee"},
    {"name": "Jürgen Lange", "email": "juergen.lange@firma.de", "role": "employee"},
    {"name": "Sabine Koch", "email": "sabine.koch@firma.de", "role": "employee"},
    {"name": "Frank Bauer", "email": "frank.bauer@firma.de", "role": "employee"}
]

def calculate_business_days(start_date: date, end_date: date) -> int:
    """Calculate business days between two dates (excluding weekends)"""
    current_date = start_date
    business_days = 0
    
    while current_date <= end_date:
        # 0 = Monday, 6 = Sunday
        if current_date.weekday() < 5:  # Monday to Friday
            business_days += 1
        current_date += timedelta(days=1)
    
    return business_days

async def clear_existing_data():
    """Clear existing employees and vacation entries"""
    print("🗑️  Clearing existing data...")
    await db.employees.delete_many({})
    await db.vacation_entries.delete_many({})
    print("✅ Existing data cleared")

async def create_employees():
    """Create demo employees"""
    print("👥 Creating employees...")
    employees = []
    
    for emp_data in DEMO_EMPLOYEES:
        employee = {
            "id": str(uuid.uuid4()),
            "name": emp_data["name"],
            "email": emp_data["email"],
            "role": emp_data["role"],
            "vacation_days_total": 25,
            "skills": [],
            "created_date": datetime.utcnow()
        }
        employees.append(employee)
    
    await db.employees.insert_many(employees)
    print(f"✅ Created {len(employees)} employees")
    return employees

async def create_sample_vacation_entries(employees):
    """Create sample vacation entries"""
    print("📅 Creating sample vacation entries...")
    vacation_entries = []
    
    # Current date and some date ranges
    today = date.today()
    
    # Sample vacation periods for different employees
    sample_vacations = [
        # January 2025
        {"employee_idx": 0, "start": date(2025, 1, 15), "end": date(2025, 1, 19), "type": "URLAUB", "notes": "Winterurlaub"},
        {"employee_idx": 2, "start": date(2025, 1, 22), "end": date(2025, 1, 26), "type": "URLAUB", "notes": "Ski-Urlaub"},
        {"employee_idx": 4, "start": date(2025, 1, 8), "end": date(2025, 1, 10), "type": "KRANKHEIT", "notes": "Grippe"},
        
        # February 2025
        {"employee_idx": 1, "start": date(2025, 2, 10), "end": date(2025, 2, 14), "type": "URLAUB", "notes": "Valentinstag-Woche"},
        {"employee_idx": 3, "start": date(2025, 2, 17), "end": date(2025, 2, 21), "type": "URLAUB", "notes": "Winterferien"},
        {"employee_idx": 5, "start": date(2025, 2, 3), "end": date(2025, 2, 7), "type": "URLAUB", "notes": "Kurzurlaub"},
        
        # March 2025
        {"employee_idx": 6, "start": date(2025, 3, 24), "end": date(2025, 3, 28), "type": "URLAUB", "notes": "Osterurlaub"},
        {"employee_idx": 7, "start": date(2025, 3, 10), "end": date(2025, 3, 14), "type": "URLAUB", "notes": "Frühlingsurlaub"},
        {"employee_idx": 8, "start": date(2025, 3, 5), "end": date(2025, 3, 5), "type": "SONDERURLAUB", "notes": "Umzug"},
        
        # April 2025
        {"employee_idx": 9, "start": date(2025, 4, 14), "end": date(2025, 4, 18), "type": "URLAUB", "notes": "Osterferien"},
        {"employee_idx": 10, "start": date(2025, 4, 21), "end": date(2025, 4, 25), "type": "URLAUB", "notes": "Frühling"},
        {"employee_idx": 11, "start": date(2025, 4, 7), "end": date(2025, 4, 11), "type": "URLAUB", "notes": "Familienzeit"},
        
        # May 2025
        {"employee_idx": 12, "start": date(2025, 5, 5), "end": date(2025, 5, 9), "type": "URLAUB", "notes": "Maifeiertag-Brücke"},
        {"employee_idx": 13, "start": date(2025, 5, 19), "end": date(2025, 5, 23), "type": "URLAUB", "notes": "Pfingsten"},
        {"employee_idx": 14, "start": date(2025, 5, 26), "end": date(2025, 5, 30), "type": "URLAUB", "notes": "Himmelfahrt-Brücke"},
        
        # June 2025 - Multiple people same time (testing 30% rule)
        {"employee_idx": 0, "start": date(2025, 6, 16), "end": date(2025, 6, 20), "type": "URLAUB", "notes": "Sommerurlaub Teil 1"},
        {"employee_idx": 1, "start": date(2025, 6, 16), "end": date(2025, 6, 20), "type": "URLAUB", "notes": "Sommerurlaub Teil 1"},
        {"employee_idx": 2, "start": date(2025, 6, 16), "end": date(2025, 6, 20), "type": "URLAUB", "notes": "Sommerurlaub Teil 1"},
        {"employee_idx": 3, "start": date(2025, 6, 16), "end": date(2025, 6, 20), "type": "URLAUB", "notes": "Sommerurlaub Teil 1"},
        {"employee_idx": 4, "start": date(2025, 6, 16), "end": date(2025, 6, 20), "type": "URLAUB", "notes": "Sommerurlaub Teil 1"},
        {"employee_idx": 5, "start": date(2025, 6, 16), "end": date(2025, 6, 20), "type": "URLAUB", "notes": "Sommerurlaub Teil 1"},
        # This should be exactly 6 people = 30% of 20
        
        # July 2025 - Second wave
        {"employee_idx": 6, "start": date(2025, 7, 14), "end": date(2025, 7, 25), "type": "URLAUB", "notes": "Sommerurlaub Teil 2"},
        {"employee_idx": 7, "start": date(2025, 7, 14), "end": date(2025, 7, 25), "type": "URLAUB", "notes": "Sommerurlaub Teil 2"},
        {"employee_idx": 8, "start": date(2025, 7, 14), "end": date(2025, 7, 25), "type": "URLAUB", "notes": "Sommerurlaub Teil 2"},
        {"employee_idx": 9, "start": date(2025, 7, 21), "end": date(2025, 7, 25), "type": "URLAUB", "notes": "Sommerurlaub kurz"},
        
        # August 2025 - Third wave
        {"employee_idx": 10, "start": date(2025, 8, 4), "end": date(2025, 8, 15), "type": "URLAUB", "notes": "Sommerurlaub Teil 3"},
        {"employee_idx": 11, "start": date(2025, 8, 4), "end": date(2025, 8, 15), "type": "URLAUB", "notes": "Sommerurlaub Teil 3"},
        {"employee_idx": 12, "start": date(2025, 8, 11), "end": date(2025, 8, 22), "type": "URLAUB", "notes": "Sommerurlaub lang"},
        {"employee_idx": 13, "start": date(2025, 8, 18), "end": date(2025, 8, 29), "type": "URLAUB", "notes": "Spätsommer"},
        
        # September 2025
        {"employee_idx": 14, "start": date(2025, 9, 8), "end": date(2025, 9, 12), "type": "URLAUB", "notes": "Herbstanfang"},
        {"employee_idx": 15, "start": date(2025, 9, 15), "end": date(2025, 9, 19), "type": "URLAUB", "notes": "Oktoberfest"},
        {"employee_idx": 16, "start": date(2025, 9, 22), "end": date(2025, 9, 26), "type": "URLAUB", "notes": "Herbstferien"},
        
        # October 2025
        {"employee_idx": 17, "start": date(2025, 10, 6), "end": date(2025, 10, 10), "type": "URLAUB", "notes": "Herbsturlaub"},
        {"employee_idx": 18, "start": date(2025, 10, 20), "end": date(2025, 10, 24), "type": "URLAUB", "notes": "Herbstpause"},
        {"employee_idx": 19, "start": date(2025, 10, 27), "end": date(2025, 10, 31), "type": "URLAUB", "notes": "Halloween-Woche"},
        
        # November 2025
        {"employee_idx": 0, "start": date(2025, 11, 3), "end": date(2025, 11, 7), "type": "URLAUB", "notes": "Herbstferien"},
        {"employee_idx": 2, "start": date(2025, 11, 17), "end": date(2025, 11, 21), "type": "URLAUB", "notes": "Vorweihnachtszeit"},
        
        # December 2025 - Christmas holidays
        {"employee_idx": 1, "start": date(2025, 12, 22), "end": date(2025, 12, 31), "type": "URLAUB", "notes": "Weihnachtsurlaub"},
        {"employee_idx": 3, "start": date(2025, 12, 23), "end": date(2025, 12, 30), "type": "URLAUB", "notes": "Zwischen den Jahren"},
        {"employee_idx": 5, "start": date(2025, 12, 24), "end": date(2025, 12, 31), "type": "URLAUB", "notes": "Weihnachten & Neujahr"},
        {"employee_idx": 7, "start": date(2025, 12, 27), "end": date(2025, 12, 31), "type": "URLAUB", "notes": "Jahresende"},
        
        # Some sick days and special leave scattered throughout
        {"employee_idx": 4, "start": date(2025, 3, 18), "end": date(2025, 3, 19), "type": "KRANKHEIT", "notes": "Erkältung"},
        {"employee_idx": 8, "start": date(2025, 5, 15), "end": date(2025, 5, 15), "type": "SONDERURLAUB", "notes": "Hochzeit Freund"},
        {"employee_idx": 12, "start": date(2025, 7, 3), "end": date(2025, 7, 4), "type": "KRANKHEIT", "notes": "Magenverstimmung"},
        {"employee_idx": 15, "start": date(2025, 9, 29), "end": date(2025, 9, 29), "type": "SONDERURLAUB", "notes": "Arzttermin"},
        {"employee_idx": 18, "start": date(2025, 11, 11), "end": date(2025, 11, 13), "type": "KRANKHEIT", "notes": "Grippe"},
    ]
    
    for vacation in sample_vacations:
        if vacation["employee_idx"] < len(employees):
            employee = employees[vacation["employee_idx"]]
            days_count = calculate_business_days(vacation["start"], vacation["end"])
            
            entry = {
                "id": str(uuid.uuid4()),
                "employee_id": employee["id"],
                "employee_name": employee["name"],
                "start_date": vacation["start"].isoformat(),
                "end_date": vacation["end"].isoformat(), 
                "vacation_type": vacation["type"],
                "notes": vacation["notes"],
                "days_count": days_count,
                "created_date": datetime.utcnow()
            }
            vacation_entries.append(entry)
    
    if vacation_entries:
        await db.vacation_entries.insert_many(vacation_entries)
    
    print(f"✅ Created {len(vacation_entries)} vacation entries")

async def main():
    """Main seeder function"""
    print("🌱 Starting Urlaubsplaner data seeding...")
    
    try:
        # Clear existing data
        await clear_existing_data()
        
        # Create employees
        employees = await create_employees()
        
        # Create vacation entries
        await create_sample_vacation_entries(employees)
        
        print("\n🎉 Data seeding completed successfully!")
        print(f"📊 Summary:")
        print(f"   - {len(employees)} employees created")
        print(f"   - 2 admins: {employees[0]['name']}, {employees[1]['name']}")
        print(f"   - Vacation entries span from January 2025 to December 2025")
        print(f"   - Includes examples of 30% concurrent vacation limit")
        print(f"   - Mixed vacation types: Urlaub, Krankheit, Sonderurlaub")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())