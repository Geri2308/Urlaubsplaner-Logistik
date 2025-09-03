#!/usr/bin/env python3
"""
Specific test to verify the employee count bug fix
Tests that all 16 employees are returned and checks for the specific names mentioned
"""

import requests
import sys

def test_employee_count_fix():
    """Test the specific employee count fix"""
    base_url = "https://time-off-app-2.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    # Expected employee names from the bug report
    expected_employees = [
        "Alexander Knoll", "Benjamin Winter", "Bernhard Sager", "Claudiu Rosza", 
        "Denis Constantin", "Gabriela Ackerl", "Gerhard Pailer", "Gerhard Schmidt", 
        "Marcel Zengerer", "Mario Pregartner", "Markus Strahlhofer", "Nicole Prack", 
        "Norbert Kreil", "Peter Koch", "Richard Tavaszi", "Sabrina Würtinger"
    ]
    
    print("🔍 Testing Employee Count Bug Fix")
    print("=" * 50)
    
    try:
        # Get all employees
        response = requests.get(f"{api_url}/employees", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ API request failed with status {response.status_code}")
            return False
        
        employees = response.json()
        
        print(f"📊 Total employees returned: {len(employees)}")
        print(f"📋 Expected employees: {len(expected_employees)}")
        
        # Check if we have 16 employees
        if len(employees) != 16:
            print(f"❌ FAILED: Expected 16 employees, got {len(employees)}")
            return False
        
        print("✅ SUCCESS: All 16 employees are returned by the API")
        
        # Get employee names
        employee_names = [emp['name'] for emp in employees]
        print("\n👥 Current employees in database:")
        for i, name in enumerate(sorted(employee_names), 1):
            print(f"   {i:2d}. {name}")
        
        # Check for expected names
        print(f"\n🔍 Checking for expected employee names...")
        found_expected = []
        missing_expected = []
        
        for expected_name in expected_employees:
            if expected_name in employee_names:
                found_expected.append(expected_name)
            else:
                missing_expected.append(expected_name)
        
        print(f"✅ Found {len(found_expected)} of {len(expected_employees)} expected employees:")
        for name in found_expected:
            print(f"   ✓ {name}")
        
        if missing_expected:
            print(f"\n⚠️  Missing {len(missing_expected)} expected employees:")
            for name in missing_expected:
                print(f"   ✗ {name}")
        
        # Additional employees not in expected list
        additional_employees = [name for name in employee_names if name not in expected_employees]
        if additional_employees:
            print(f"\n📝 Additional employees (not in expected list):")
            for name in additional_employees:
                print(f"   + {name}")
        
        print("\n" + "=" * 50)
        print("🎯 BUG FIX VERIFICATION RESULTS:")
        print(f"   • API returns {len(employees)} employees (✅ Fixed from 11)")
        print(f"   • Found {len(found_expected)}/{len(expected_employees)} expected names")
        print(f"   • Backend cursor limit fix is working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

def main():
    """Main test runner"""
    success = test_employee_count_fix()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())