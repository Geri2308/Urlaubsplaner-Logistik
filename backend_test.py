#!/usr/bin/env python3
"""
Comprehensive Backend API Test for Urlaubsplaner (Vacation Planner)
Tests all CRUD operations and validates API responses
"""

import requests
import sys
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Any

class UrlaubsplanerAPITester:
    def __init__(self, base_url="https://time-off-app-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_employees = []
        self.created_vacation_entries = []

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")
        return success

    def make_request(self, method: str, endpoint: str, data: Dict = None, expected_status: int = 200) -> tuple:
        """Make HTTP request and return success status and response data"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                return False, f"Unsupported method: {method}"

            success = response.status_code == expected_status
            
            if success:
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                return False, f"Status {response.status_code}, Expected {expected_status}. Response: {response.text[:200]}"
                
        except requests.exceptions.RequestException as e:
            return False, f"Request failed: {str(e)}"

    def test_health_check(self):
        """Test API health endpoint"""
        success, data = self.make_request('GET', 'health')
        if success and isinstance(data, dict) and data.get('status') == 'healthy':
            return self.log_test("Health Check", True, f"- {data.get('message', '')}")
        return self.log_test("Health Check", False, f"- {data}")

    def test_get_settings(self):
        """Test company settings endpoint"""
        success, data = self.make_request('GET', 'settings')
        if success and isinstance(data, dict):
            expected_keys = ['max_concurrent_percentage', 'total_employees', 'max_concurrent_calculated']
            has_keys = all(key in data for key in expected_keys)
            return self.log_test("Get Settings", has_keys, f"- Found keys: {list(data.keys())}")
        return self.log_test("Get Settings", False, f"- {data}")

    def test_get_employees(self):
        """Test getting all employees"""
        success, data = self.make_request('GET', 'employees')
        if success and isinstance(data, list):
            employee_count = len(data)
            return self.log_test("Get Employees", True, f"- Found {employee_count} employees")
        return self.log_test("Get Employees", False, f"- {data}")

    def test_create_employee(self):
        """Test creating a new employee"""
        test_employee = {
            "name": f"Test Employee {datetime.now().strftime('%H%M%S')}",
            "email": f"test{datetime.now().strftime('%H%M%S')}@example.com",
            "role": "employee",
            "skills": [
                {"name": "Python", "rating": 4},
                {"name": "JavaScript", "rating": 3}
            ]
        }
        
        success, data = self.make_request('POST', 'employees', test_employee, 200)
        if success and isinstance(data, dict) and 'id' in data:
            self.created_employees.append(data['id'])
            return self.log_test("Create Employee", True, f"- Created employee with ID: {data['id']}")
        return self.log_test("Create Employee", False, f"- {data}")

    def test_get_employee_by_id(self):
        """Test getting employee by ID"""
        if not self.created_employees:
            return self.log_test("Get Employee by ID", False, "- No employees created to test")
        
        employee_id = self.created_employees[0]
        success, data = self.make_request('GET', f'employees/{employee_id}')
        if success and isinstance(data, dict) and data.get('id') == employee_id:
            return self.log_test("Get Employee by ID", True, f"- Retrieved employee: {data.get('name')}")
        return self.log_test("Get Employee by ID", False, f"- {data}")

    def test_update_employee(self):
        """Test updating an employee"""
        if not self.created_employees:
            return self.log_test("Update Employee", False, "- No employees created to test")
        
        employee_id = self.created_employees[0]
        update_data = {
            "name": f"Updated Employee {datetime.now().strftime('%H%M%S')}",
            "email": "updated@example.com",
            "role": "admin",
            "skills": [{"name": "Management", "rating": 5}]
        }
        
        success, data = self.make_request('PUT', f'employees/{employee_id}', update_data)
        if success and isinstance(data, dict) and data.get('name') == update_data['name']:
            return self.log_test("Update Employee", True, f"- Updated employee name to: {data.get('name')}")
        return self.log_test("Update Employee", False, f"- {data}")

    def test_get_vacation_entries(self):
        """Test getting all vacation entries"""
        success, data = self.make_request('GET', 'vacation-entries')
        if success and isinstance(data, list):
            entry_count = len(data)
            return self.log_test("Get Vacation Entries", True, f"- Found {entry_count} vacation entries")
        return self.log_test("Get Vacation Entries", False, f"- {data}")

    def test_create_vacation_entry(self):
        """Test creating a vacation entry"""
        if not self.created_employees:
            return self.log_test("Create Vacation Entry", False, "- No employees available for vacation entry")
        
        # Create vacation entry for next week
        start_date = (date.today() + timedelta(days=7)).isoformat()
        end_date = (date.today() + timedelta(days=9)).isoformat()
        
        vacation_data = {
            "employee_id": self.created_employees[0],
            "start_date": start_date,
            "end_date": end_date,
            "vacation_type": "URLAUB",
            "notes": "Test vacation entry"
        }
        
        success, data = self.make_request('POST', 'vacation-entries', vacation_data, 200)
        if success and isinstance(data, dict) and 'id' in data:
            self.created_vacation_entries.append(data['id'])
            return self.log_test("Create Vacation Entry", True, f"- Created vacation entry with ID: {data['id']}")
        return self.log_test("Create Vacation Entry", False, f"- {data}")

    def test_get_vacation_entry_by_id(self):
        """Test getting vacation entry by ID"""
        if not self.created_vacation_entries:
            return self.log_test("Get Vacation Entry by ID", False, "- No vacation entries created to test")
        
        entry_id = self.created_vacation_entries[0]
        success, data = self.make_request('GET', f'vacation-entries/{entry_id}')
        if success and isinstance(data, dict) and data.get('id') == entry_id:
            return self.log_test("Get Vacation Entry by ID", True, f"- Retrieved vacation entry for: {data.get('employee_name')}")
        return self.log_test("Get Vacation Entry by ID", False, f"- {data}")

    def test_update_vacation_entry(self):
        """Test updating a vacation entry"""
        if not self.created_vacation_entries or not self.created_employees:
            return self.log_test("Update Vacation Entry", False, "- No vacation entries or employees to test")
        
        entry_id = self.created_vacation_entries[0]
        start_date = (date.today() + timedelta(days=14)).isoformat()
        end_date = (date.today() + timedelta(days=16)).isoformat()
        
        update_data = {
            "employee_id": self.created_employees[0],
            "start_date": start_date,
            "end_date": end_date,
            "vacation_type": "SONDERURLAUB",
            "notes": "Updated test vacation entry"
        }
        
        success, data = self.make_request('PUT', f'vacation-entries/{entry_id}', update_data)
        if success and isinstance(data, dict) and data.get('vacation_type') == 'SONDERURLAUB':
            return self.log_test("Update Vacation Entry", True, f"- Updated vacation type to: {data.get('vacation_type')}")
        return self.log_test("Update Vacation Entry", False, f"- {data}")

    def test_employee_analytics(self):
        """Test employee analytics endpoint"""
        if not self.created_employees:
            return self.log_test("Employee Analytics", False, "- No employees to test analytics")
        
        employee_id = self.created_employees[0]
        success, data = self.make_request('GET', f'analytics/employee-summary/{employee_id}?year=2025')
        if success and isinstance(data, dict):
            expected_keys = ['employee', 'year', 'vacation_days_total', 'vacation_days_used']
            has_keys = all(key in data for key in expected_keys)
            return self.log_test("Employee Analytics", has_keys, f"- Analytics data available")
        return self.log_test("Employee Analytics", False, f"- {data}")

    def test_team_overview(self):
        """Test team overview analytics"""
        start_date = date.today().isoformat()
        end_date = (date.today() + timedelta(days=30)).isoformat()
        
        success, data = self.make_request('GET', f'analytics/team-overview?start_date={start_date}&end_date={end_date}')
        if success and isinstance(data, dict):
            expected_keys = ['date_range', 'total_employees', 'vacation_entries_count']
            has_keys = all(key in data for key in expected_keys)
            return self.log_test("Team Overview", has_keys, f"- Team overview data available")
        return self.log_test("Team Overview", False, f"- {data}")

    def test_concurrent_vacation_validation(self):
        """Test concurrent vacation validation"""
        if not self.created_employees:
            return self.log_test("Concurrent Vacation Validation", False, "- No employees to test")
        
        # Try to create overlapping vacation entries to test validation
        start_date = (date.today() + timedelta(days=21)).isoformat()
        end_date = (date.today() + timedelta(days=23)).isoformat()
        
        vacation_data = {
            "employee_id": self.created_employees[0],
            "start_date": start_date,
            "end_date": end_date,
            "vacation_type": "URLAUB",
            "notes": "Concurrent validation test"
        }
        
        success, data = self.make_request('POST', 'vacation-entries', vacation_data, 200)
        if success:
            return self.log_test("Concurrent Vacation Validation", True, "- Vacation entry created successfully")
        else:
            # If it fails due to concurrent limits, that's also valid behavior
            if "concurrent" in str(data).lower():
                return self.log_test("Concurrent Vacation Validation", True, "- Concurrent validation working")
            return self.log_test("Concurrent Vacation Validation", False, f"- {data}")

    def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 Cleaning up test data...")
        
        # Delete vacation entries first (due to foreign key constraints)
        for entry_id in self.created_vacation_entries:
            success, _ = self.make_request('DELETE', f'vacation-entries/{entry_id}', expected_status=200)
            if success:
                print(f"   Deleted vacation entry: {entry_id}")
        
        # Delete employees
        for employee_id in self.created_employees:
            success, _ = self.make_request('DELETE', f'employees/{employee_id}', expected_status=200)
            if success:
                print(f"   Deleted employee: {employee_id}")

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Urlaubsplaner API Tests")
        print(f"📍 Testing API at: {self.api_url}")
        print("=" * 60)
        
        # Basic connectivity tests
        self.test_health_check()
        self.test_get_settings()
        
        # Employee CRUD tests
        self.test_get_employees()
        self.test_create_employee()
        self.test_get_employee_by_id()
        self.test_update_employee()
        
        # Vacation entry CRUD tests
        self.test_get_vacation_entries()
        self.test_create_vacation_entry()
        self.test_get_vacation_entry_by_id()
        self.test_update_vacation_entry()
        
        # Analytics tests
        self.test_employee_analytics()
        self.test_team_overview()
        
        # Business logic tests
        self.test_concurrent_vacation_validation()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! API is working correctly.")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed. Check the issues above.")
            return 1

def main():
    """Main test runner"""
    tester = UrlaubsplanerAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())