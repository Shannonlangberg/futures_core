#!/usr/bin/env python3
"""
Test script for the new query system
"""

import requests
import json

def test_query_system():
    """Test the new query endpoint with various questions"""
    
    base_url = "http://localhost:5001"
    
    # Test questions
    test_questions = [
        "How many new people has south had this year?",
        "What's the total attendance for south campus?",
        "How many salvations has paradise had?",
        "What's the youth attendance at copper coast?",
        "How many kids have attended at mount barker?",
        "What are the connect groups numbers for victor harbour?",
        "Give me a summary of adelaide city campus"
    ]
    
    print("🔍 Testing Query System")
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
                print(f"📈 Analysis: {data.get('analysis', {})}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_query_system() 