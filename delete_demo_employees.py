#!/usr/bin/env python3
"""
Script to delete all demo employees from the Urlaubsplaner
"""

import requests
import json

API_URL = "https://time-off-app-2.preview.emergentagent.com/api"

def delete_all_employees():
    """Delete all employees and their vacation entries"""
    print("🗑️  Starting deletion of all demo employees...")
    
    try:
        # Get all employees
        response = requests.get(f"{API_URL}/employees")
        if response.status_code != 200:
            print(f"❌ Failed to get employees: {response.status_code}")
            return
        
        employees = response.json()
        print(f"📊 Found {len(employees)} employees to delete")
        
        if len(employees) == 0:
            print("✅ No employees found - database is already empty")
            return
        
        # Delete each employee (this will also delete their vacation entries)
        deleted_count = 0
        for employee in employees:
            employee_id = employee['id']
            employee_name = employee['name']
            
            delete_response = requests.delete(f"{API_URL}/employees/{employee_id}")
            if delete_response.status_code == 200:
                print(f"✅ Deleted: {employee_name}")
                deleted_count += 1
            else:
                print(f"❌ Failed to delete {employee_name}: {delete_response.status_code}")
        
        print(f"\n🎉 Deletion completed!")
        print(f"📊 Summary:")
        print(f"   - {deleted_count} employees deleted")
        print(f"   - All associated vacation entries automatically deleted")
        
        # Verify deletion
        verify_response = requests.get(f"{API_URL}/employees")
        if verify_response.status_code == 200:
            remaining_employees = verify_response.json()
            print(f"   - {len(remaining_employees)} employees remaining")
            
            # Also check vacation entries
            vacation_response = requests.get(f"{API_URL}/vacation-entries")
            if vacation_response.status_code == 200:
                remaining_vacations = vacation_response.json()
                print(f"   - {len(remaining_vacations)} vacation entries remaining")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    delete_all_employees()