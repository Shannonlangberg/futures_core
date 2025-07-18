#!/usr/bin/env python3
"""
Test script for the new average calculation feature
"""

import requests
import json

def test_averages():
    """Test the new average calculation feature"""
    
    base_url = "http://localhost:5001"
    
    # Test questions focusing on averages
    test_questions = [
        "What's the average youth attendance at south campus?",
        "What's the average attendance at paradise campus?",
        "What's the average new people at copper coast?",
        "What's the average kids attendance at mount barker?",
        "What's the average connect groups at victor harbour?",
        "What's the average new christians at adelaide city?",
        "Give me all the averages for south campus"
    ]
    
    print("📊 Testing Average Calculations")
    print("=" * 50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        
        try:
            response = requests.post(
                f"{base_url}/api/query",
                json={"question": question},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Campus: {data.get('campus', 'unknown')}")
                print(f"📊 Answer: {data.get('answer', 'No answer')}")
                
                # Show averages if available
                analysis = data.get('analysis', {})
                averages = analysis.get('averages', {})
                if averages:
                    print(f"📈 Averages: {averages}")
                    
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_averages() 