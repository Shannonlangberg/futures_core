#!/usr/bin/env python3
"""
Test Script for South Campus - Futures Link Assistant
Tests the voice/text processing with realistic church attendance data
"""

import requests
import json
import time

# Test data for South campus
test_cases = [
    {
        "name": "Basic South Campus Stats",
        "text": "South campus had 145 people today, 8 new visitors, 3 salvations, 25 youth, 35 kids, 12 connect groups",
        "expected_campus": "south"
    },
    {
        "name": "South Campus with Tithe",
        "text": "South campus attendance was 132 people, 5 new visitors, 2 salvations, 22 youth group, 28 kids ministry, 10 connect groups, $8,450 in tithe",
        "expected_campus": "south"
    },
    {
        "name": "South Campus Volunteers",
        "text": "South campus had 128 people, 6 new visitors, 1 salvation, 20 youth, 30 kids, 11 connect groups, 45 volunteers",
        "expected_campus": "south"
    },
    {
        "name": "South Campus Minimal",
        "text": "South campus 115 people, 3 new visitors",
        "expected_campus": "south"
    },
    {
        "name": "South Campus with Youth Focus",
        "text": "South campus youth ministry had 28 students, total attendance 140 people, 7 new visitors, 2 salvations",
        "expected_campus": "south"
    }
]

def test_voice_processing():
    """Test the voice/text processing endpoint"""
    base_url = "http://localhost:5001"
    
    print("🧪 Testing South Campus Stats Processing")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📊 Test {i}: {test_case['name']}")
        print(f"Input: {test_case['text']}")
        
        try:
            # Send request to the API
            response = requests.post(
                f"{base_url}/api/process_voice",
                json={
                    "text": test_case['text'],
                    "campus": "south"
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success!")
                print(f"Campus: {data.get('campus', 'N/A')}")
                print(f"Response: {data.get('text', 'N/A')}")
                print(f"Stats: {data.get('stats', {})}")
                
                # Check if campus was detected correctly
                if data.get('campus') == test_case['expected_campus']:
                    print(f"✅ Campus detection: {data.get('campus')}")
                else:
                    print(f"❌ Campus detection failed: expected {test_case['expected_campus']}, got {data.get('campus')}")
                
                # Check if stats were extracted
                stats = data.get('stats', {})
                if stats:
                    print(f"✅ Stats extracted: {len(stats)} values")
                    for key, value in stats.items():
                        print(f"   {key}: {value}")
                else:
                    print("❌ No stats extracted")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection error - make sure the server is running on http://localhost:5001")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Small delay between tests
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

def test_health_check():
    """Test the health endpoint"""
    print("\n🏥 Testing Health Check")
    try:
        response = requests.get("http://localhost:5001/api/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Health check passed")
            print(f"   Sheets connected: {health.get('sheets_connected')}")
            print(f"   Claude connected: {health.get('claude_connected')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

if __name__ == "__main__":
    print("🚀 Futures Link Assistant - South Campus Test Script")
    print("Make sure the server is running on http://localhost:5001")
    print()
    
    # Test health first
    test_health_check()
    
    # Test voice processing
    test_voice_processing()
    
    print("\n💡 Tips:")
    print("- Check the browser at http://localhost:5001 to see the UI")
    print("- Look at the server logs for detailed debugging info")
    print("- The stats should appear in the frontend cards after processing") 