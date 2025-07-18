#!/usr/bin/env python3
"""
Test script for the 2 insights feature
"""

import requests
import json
import time

def test_2_insights():
    """Test the new 2 insights feature with different scenarios"""
    
    base_url = "http://localhost:5001"
    
    # Test scenarios
    test_cases = [
        {
            "name": "South Campus - High Attendance",
            "text": "south had 450 people, 25 new visitors, 8 salvations, 120 youth, 80 kids"
        },
        {
            "name": "Copper Coast - Growing Ministry", 
            "text": "copper coast had 180 people, 12 new people, 5 decisions, 45 youth, 35 kids, 8 connect groups"
        },
        {
            "name": "Paradise - Steady Growth",
            "text": "paradise had 320 people, 15 new visitors, 6 salvations, 90 youth, 60 kids"
        },
        {
            "name": "Salisbury - New Ministry Launch",
            "text": "salisbury had 200 people, 30 new people, 12 decisions, 50 youth, 40 kids, 5 connect groups"
        }
    ]
    
    print("🧪 Testing 2 Insights Feature")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"Input: {test_case['text']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/process_voice",
                json={"text": test_case['text']},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Campus: {data.get('campus', 'unknown')}")
                print(f"📊 Stats: {data.get('stats', {})}")
                
                insights = data.get('insights', [])
                if insights:
                    print(f"💡 Insights ({len(insights)}):")
                    for j, insight in enumerate(insights, 1):
                        print(f"   {j}. {insight}")
                else:
                    print("❌ No insights received")
                    
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        print("-" * 50)
        time.sleep(1)  # Brief pause between tests
    
    print("\n🎉 2 Insights Testing Complete!")
    print("\n💡 Expected Results:")
    print("- Each test should return exactly 2 insights")
    print("- Insights should be short (max 12 words each)")
    print("- Insights should focus on different trends/patterns")
    print("- Frontend should display insights in 2-column layout")

if __name__ == "__main__":
    test_2_insights() 