#!/usr/bin/env python3
"""
Test script for cross-location comparison functionality
"""

import requests
import json

def test_cross_location_comparison():
    """Test the cross-location comparison functionality"""
    
    # Test cases
    test_cases = [
        {
            "question": "compare south vs barker this year",
            "description": "Basic cross-location comparison"
        },
        {
            "question": "how many np did south have compared to barker this year",
            "description": "Specific stat comparison"
        },
        {
            "question": "south vs paradise in 2024",
            "description": "Different campuses and year"
        }
    ]
    
    base_url = "http://localhost:5002"
    
    print("Testing Cross-Location Comparison Functionality")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Question: {test_case['question']}")
        
        try:
            # Test the query endpoint
            response = requests.post(
                f"{base_url}/api/query",
                json={
                    "question": test_case['question'],
                    "campus": "all_campuses"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Status: {response.status_code}")
                print(f"Response keys: {list(data.keys())}")
                
                if data.get('comparison') and data.get('cross_location'):
                    print("✅ Cross-location comparison detected!")
                    print(f"Campus data: {data.get('data', [])}")
                else:
                    print("❌ Cross-location comparison not detected")
                    print(f"Response: {data.get('text', 'No text')}")
            else:
                print(f"❌ Failed! Status: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_cross_location_comparison() 