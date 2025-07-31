#!/usr/bin/env python3
"""
Test script for internal cross-location comparison functions
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Mock the current_user for testing
class MockUser:
    def __init__(self):
        self.is_authenticated = True
        self.role = 'senior_leader'
        self.campus = 'all_campuses'
    
    def has_permission(self, permission_type, campus=None):
        if permission_type == 'cross_location_comparison':
            return True
        return True

# Mock the current_user
import app
app.current_user = MockUser()

def test_cross_location_detection():
    """Test the cross-location comparison detection function"""
    
    test_cases = [
        {
            "question": "compare south vs barker this year",
            "expected_campuses": ["south", "mount_barker"],
            "description": "Basic cross-location comparison"
        },
        {
            "question": "how many np did south have compared to barker this year",
            "expected_campuses": ["south", "mount_barker"],
            "description": "Specific stat comparison"
        },
        {
            "question": "south vs paradise in 2024",
            "expected_campuses": ["south", "paradise"],
            "description": "Different campuses and year"
        },
        {
            "question": "compare adelaide and salisbury",
            "expected_campuses": ["adelaide_city", "salisbury"],
            "description": "Using 'and' keyword"
        }
    ]
    
    print("Testing Cross-Location Comparison Detection")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Question: {test_case['question']}")
        
        try:
            # Test the detection function
            is_cross_location, campuses, year, specific_stat = app.detect_cross_location_comparison(test_case['question'])
            
            print(f"Detection result: {is_cross_location}")
            print(f"Detected campuses: {campuses}")
            print(f"Year: {year}")
            print(f"Specific stat: {specific_stat}")
            
            if is_cross_location:
                print("✅ Cross-location comparison detected!")
                
                # Check if expected campuses were detected
                expected_campuses = set(test_case['expected_campuses'])
                detected_campuses = set(campuses)
                
                if expected_campuses.issubset(detected_campuses):
                    print("✅ Expected campuses detected!")
                else:
                    print(f"❌ Expected campuses {expected_campuses} not all detected. Got: {detected_campuses}")
            else:
                print("❌ Cross-location comparison not detected")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_cross_location_detection() 