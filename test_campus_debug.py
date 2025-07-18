#!/usr/bin/env python3
"""
Test script to debug campus detection
"""

import requests
import json

def test_campus_detection():
    """Test campus detection with various inputs"""
    
    test_cases = [
        "south had 400 people, 5 nc, 7 np, 20 yout, 5 kids and 3 connects",
        "South campus had 145 people today, 8 new visitors, 3 salvations",
        "south campus attendance was 132 people",
        "South had 128 people, 6 new visitors"
    ]
    
    print("🧪 Testing Campus Detection")
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
    print("🚀 Campus Detection Debug Test")
    print("Make sure the server is running on http://localhost:5001")
    print()
    
    test_campus_detection() 