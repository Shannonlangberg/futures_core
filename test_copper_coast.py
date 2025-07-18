#!/usr/bin/env python3
"""
Test script specifically for Copper Coast campus detection
"""

import requests
import json

def test_copper_coast():
    """Test Copper Coast campus detection"""
    
    test_cases = [
        "copper coast had 403 people",
        "Copper Coast had 150 people, 5 new visitors",
        "copper coast campus had 200 people",
        "Copper Coast attendance was 180 people"
    ]
    
    print("🧪 Testing Copper Coast Campus Detection")
    print("=" * 50)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n📊 Test {i}: {test_text}")
        
        try:
            response = requests.post(
                'http://localhost:5001/api/process_voice',
                json={
                    "text": test_text,
                    "campus": ""  # Let it auto-detect
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response received")
                print(f"   Campus: '{data.get('campus', 'N/A')}'")
                print(f"   Stats: {data.get('stats', {})}")
                print(f"   Text: {data.get('text', 'N/A')[:100]}...")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Copper Coast Campus Detection Test")
    print("Make sure the server is running on http://localhost:5001")
    print()
    
    test_copper_coast() 