#!/usr/bin/env python3
"""
Test script to verify cross-location comparison includes all stats including tithe
"""

import requests
import json

def test_cross_location_comparison():
    """Test cross-location comparison with comprehensive stats"""
    
    # Test URL
    url = "http://localhost:5002/api/query"
    
    # Test cases for cross-location comparison
    test_cases = [
        {
            "question": "compare south vs barker this year",
            "expected_stats": [
                "Total Attendance", "First Time Visitors", "New People", "New Christians",
                "Rededications", "Youth Attendance", "Youth Salvations", "Youth New People",
                "Kids Attendance", "Kids Leaders", "New Kids", "New Kids Salvations",
                "Connect Groups", "Dream Team", "Tithe", "Baptisms", "Child Dedications",
                "Information Gathered"
            ]
        },
        {
            "question": "south vs paradise vs adelaide in 2025",
            "expected_stats": [
                "Total Attendance", "First Time Visitors", "New People", "New Christians",
                "Rededications", "Youth Attendance", "Youth Salvations", "Youth New People",
                "Kids Attendance", "Kids Leaders", "New Kids", "New Kids Salvations",
                "Connect Groups", "Dream Team", "Tithe", "Baptisms", "Child Dedications",
                "Information Gathered"
            ]
        },
        {
            "question": "compare tithe between south and barker this year",
            "expected_stats": ["Tithe"]
        }
    ]
    
    print("Testing Cross-Location Comparison with Comprehensive Stats")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['question']}")
        print("-" * 40)
        
        try:
            # Send request
            response = requests.post(url, json={"question": test_case['question']})
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('comparison') and data.get('cross_location'):
                    print("✅ Cross-location comparison detected")
                    print(f"📊 Summary: {data.get('summary', 'N/A')}")
                    
                    # Check if data is present
                    if data.get('data'):
                        print(f"📋 Found {len(data['data'])} stat rows")
                        
                        # Check for expected stats
                        found_stats = []
                        for row in data['data']:
                            stat_name = row.get('stat', '')
                            found_stats.append(stat_name)
                            print(f"   - {stat_name}")
                        
                        # Check if tithe is included
                        if 'Tithe' in found_stats:
                            print("✅ Tithe stat found in comparison")
                        else:
                            print("❌ Tithe stat missing from comparison")
                        
                        # Check for other important stats
                        important_stats = ['Total Attendance', 'New Christians', 'Youth Attendance', 'Kids Attendance']
                        missing_stats = [stat for stat in important_stats if stat not in found_stats]
                        
                        if missing_stats:
                            print(f"⚠️  Missing important stats: {missing_stats}")
                        else:
                            print("✅ All important stats present")
                            
                    else:
                        print("❌ No comparison data found")
                        
                else:
                    print("❌ Not detected as cross-location comparison")
                    print(f"Response type: {data.get('comparison', 'N/A')}")
                    
            else:
                print(f"❌ Request failed with status {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Test completed!")

if __name__ == "__main__":
    test_cross_location_comparison() 