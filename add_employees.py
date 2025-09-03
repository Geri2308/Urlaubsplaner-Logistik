#!/usr/bin/env python3
"""
Script to add the 16 specific employees to the Urlaubsplaner
"""

import requests
import json

API_URL = "https://time-off-app-2.preview.emergentagent.com/api"

# List of employees to add
EMPLOYEES = [
    "Gerhard Pailer",
    "Mario Pregartner", 
    "Marcel Zengerer",
    "Sabrina Würtinger",
    "Alexander Knoll",
    "Gerhard Schmidt",
    "Claudiu Rosza",
    "Richard Tavaszi",
    "Bernhard Sager",
    "Benjamin Winter",
    "Gabriela Ackerl",
    "Markus Strahlhofer",
    "Norbert Kreil",
    "Nicole Prack",
    "Denis Constantin",
    "Peter Koch"
]

def generate_email(name):
    """Generate email address from name"""
    # Convert name to lowercase and replace spaces with dots
    email_name = name.lower().replace(" ", ".")
    # Handle special characters
    email_name = email_name.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return f"{email_name}@firma.at"

def add_employees():
    """Add all employees to the system"""
    print("👥 Starting to add employees...")
    
    added_count = 0
    failed_count = 0
    
    for name in EMPLOYEES:
        employee_data = {
            "name": name,
            "email": generate_email(name),
            "role": "employee",
            "skills": []
        }
        
        try:
            response = requests.post(f"{API_URL}/employees", json=employee_data)
            if response.status_code == 200:
                print(f"✅ Added: {name} ({employee_data['email']})")
                added_count += 1
            else:
                print(f"❌ Failed to add {name}: {response.status_code} - {response.text[:100]}")
                failed_count += 1
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error adding {name}: {e}")
            failed_count += 1
        except Exception as e:
            print(f"❌ Error adding {name}: {e}")
            failed_count += 1
    
    print(f"\n🎉 Employee creation completed!")
    print(f"📊 Summary:")
    print(f"   - {added_count} employees successfully added")
    print(f"   - {failed_count} employees failed")
    print(f"   - Total attempted: {len(EMPLOYEES)}")
    
    # Verify by getting all employees
    try:
        response = requests.get(f"{API_URL}/employees")
        if response.status_code == 200:
            employees = response.json()
            print(f"   - {len(employees)} total employees now in database")
            
            # Show the added employees
            print(f"\n📋 Current employees in system:")
            for emp in sorted(employees, key=lambda x: x['name']):
                role_icon = "👑" if emp['role'] == 'admin' else "👤"
                print(f"   {role_icon} {emp['name']} ({emp['role']})")
                
    except Exception as e:
        print(f"❌ Error verifying employees: {e}")

if __name__ == "__main__":
    add_employees()