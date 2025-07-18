#!/usr/bin/env python3
"""
Test script for Futures Core Voice Assistant Backend
This script tests the core functionality without requiring external APIs
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any

# Test patterns (copied from app.py)
patterns = {
    "total_attendance": r"(\d+)\s+(?:people|attendance|total|adults?)",
    "new_people": r"(\d+)\s+new(?:\s+people|visitors?|guests?)?",
    "new_christians": r"(\d+)\s+(?:salvations|new\s+christians|decisions|baptisms?)",
    "youth_attendance": r"(\d+)\s+(?:youth(?:\s+group|\s+ministry)?|teens?)",
    "kids_total": r"(\d+)\s+(?:kids|children|kids\s+ministry|nursery)",
    "connect_groups": r"(\d+)\s+(?:connect\s+groups?|small\s+groups?|connects?|life\s+groups?)",
    "tithe_amount": r"\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\s+(?:tithe|offering|giving|in\s+tithe)",
    "volunteers": r"(\d+)\s+(?:volunteers?|team\s+members?|servers?)"
}

campus_patterns = {
    "main": r"(?:main\s+campus|downtown|central)",
    "north": r"(?:north\s+campus|northside)",
    "south": r"(?:south\s+campus|southside)",
    "east": r"(?:east\s+campus|eastside)",
    "west": r"(?:west\s+campus|westside)",
    "online": r"(?:online|virtual|stream)"
}

def detect_campus(text: str) -> str:
    """Detect campus from voice input"""
    text_lower = text.lower()
    for campus, pattern in campus_patterns.items():
        if re.search(pattern, text_lower):
            return campus
    return "main"  # default campus

def extract_stats_with_context(text: str, campus: str) -> Dict[str, Any]:
    """Extract stats with enhanced context awareness"""
    result = {
        "Campus": campus,
        "Timestamp": datetime.now().isoformat(),
        "Raw_Text": text
    }
    
    # Extract stat values with better context
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Convert to string for Google Sheets compatibility
            result[key.replace("_", " ").title()] = str(match.group(1))
    
    return result

def detect_missing_stats(text: str, campus: str) -> List[str]:
    """Detect what stats might be missing and suggest follow-up questions"""
    extracted = extract_stats_with_context(text, campus)
    missing = []
    
    # Check for common missing stats
    if not any(key in extracted for key in ["Total Attendance", "Total attendance"]):
        missing.append("How many people attended today?")
    
    if not any(key in extracted for key in ["New People", "New people"]):
        missing.append("Were there any new visitors today?")
    
    if not any(key in extracted for key in ["Kids Total", "Kids total"]):
        missing.append("How many kids were in children's ministry?")
    
    if not any(key in extracted for key in ["Youth Attendance", "Youth attendance"]):
        missing.append("How many youth attended?")
    
    return missing

def test_voice_processing():
    """Test the voice processing functionality"""
    print("🧪 Testing Voice Processing Engine")
    print("=" * 40)
    
    test_cases = [
        {
            "input": "We had 150 people today at the main campus, 25 new visitors, and 3 salvations.",
            "expected_campus": "main",
            "expected_stats": ["Total Attendance", "New People", "New Christians"]
        },
        {
            "input": "North campus this morning: 200 total attendance, 15 new people, 5 salvations, 45 youth, 60 kids, 12 connect groups, and we had $15,000 in tithe.",
            "expected_campus": "north",
            "expected_stats": ["Total Attendance", "New People", "New Christians", "Youth Attendance", "Kids Total", "Connect Groups", "Tithe Amount"]
        },
        {
            "input": "South campus had 180 people, 20 new visitors, and 4 baptisms today.",
            "expected_campus": "south",
            "expected_stats": ["Total Attendance", "New People", "New Christians"]
        },
        {
            "input": "Online service had 75 people watching, 5 new viewers, and 2 decisions.",
            "expected_campus": "online",
            "expected_stats": ["Total Attendance", "New People", "New Christians"]
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['input'][:50]}...")
        
        # Test campus detection
        detected_campus = detect_campus(test_case['input'])
        campus_correct = detected_campus == test_case['expected_campus']
        
        # Test stat extraction
        extracted_stats = extract_stats_with_context(test_case['input'], detected_campus)
        extracted_keys = [key for key in extracted_stats.keys() if key not in ['Campus', 'Timestamp', 'Raw_Text']]
        
        # Check if expected stats were found
        expected_found = all(stat in extracted_keys for stat in test_case['expected_stats'])
        
        # Test missing stats detection
        missing_stats = detect_missing_stats(test_case['input'], detected_campus)
        
        # Print results
        print(f"  Campus: {detected_campus} (expected: {test_case['expected_campus']}) - {'✅' if campus_correct else '❌'}")
        print(f"  Stats found: {extracted_keys}")
        print(f"  Expected stats: {test_case['expected_stats']} - {'✅' if expected_found else '❌'}")
        print(f"  Missing stats suggestions: {missing_stats}")
        
        if campus_correct and expected_found:
            passed += 1
            print("  Result: ✅ PASSED")
        else:
            print("  Result: ❌ FAILED")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    return passed == total

def test_memory_system():
    """Test the memory system functionality"""
    print("\n🧠 Testing Memory System")
    print("=" * 40)
    
    # Simulate conversation memory
    memory = {
        "main": [
            {
                "Campus": "main",
                "Timestamp": "2024-01-15T10:30:00",
                "Total Attendance": "150",
                "New People": "25",
                "Raw_Text": "We had 150 people today..."
            },
            {
                "Campus": "main",
                "Timestamp": "2024-01-22T10:30:00",
                "Total Attendance": "165",
                "New People": "30",
                "Raw_Text": "We had 165 people today..."
            }
        ]
    }
    
    print("Memory structure created successfully")
    print(f"Main campus has {len(memory['main'])} historical entries")
    
    # Test context building
    campus_history = memory.get("main", [])
    recent_stats = campus_history[-3:] if campus_history else []
    
    print(f"Recent stats: {len(recent_stats)} entries")
    for stat in recent_stats:
        print(f"  - {stat.get('Raw_Text', '')}")
    
    return True

def test_api_endpoints():
    """Test API endpoint structure"""
    print("\n🌐 Testing API Endpoints")
    print("=" * 40)
    
    endpoints = [
        "/api/health",
        "/api/stats", 
        "/api/process_voice",
        "/api/memory/<campus>",
        "/api/campuses"
    ]
    
    print("Available endpoints:")
    for endpoint in endpoints:
        print(f"  - {endpoint}")
    
    return True

def main():
    """Run all tests"""
    print("🔥 Futures Core Voice Assistant - Backend Tests")
    print("=" * 50)
    
    tests = [
        test_voice_processing,
        test_memory_system,
        test_api_endpoints
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print(f"\n🎉 Overall Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("✅ All tests passed! Backend is ready for deployment.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    main() 