#!/usr/bin/env python3

import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import datetime

# Google Sheets Auth
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

# Initialize Google Sheets client
if os.path.exists("backend/credentials.json"):
    creds = ServiceAccountCredentials.from_json_keyfile_name("backend/credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Stats").sheet1
    print("Google Sheets initialized successfully")
else:
    print("credentials.json not found")
    exit(1)

# Get all rows
rows = sheet.get_all_records()
print(f"Retrieved {len(rows)} total rows from Google Sheets")

# Filter for South campus
south_rows = []
for row in rows:
    row_campus = str(row.get('Campus', '')).strip().lower()
    if row_campus == 'south':
        total_attendance = row.get('Total Attendance', '')
        if total_attendance and str(total_attendance).strip():
            south_rows.append(row)

print(f"\nFound {len(south_rows)} rows for South campus with attendance data")

# Show all South rows with their dates and timestamps
print("\nAll South campus rows with detailed date info:")
for i, row in enumerate(south_rows):
    date_str = row.get('Date', '')
    timestamp_str = row.get('Timestamp', '')
    sunday_date_str = row.get('Sunday Date', '')
    attendance = row.get('Total Attendance', 'N/A')
    print(f"  {i+1}. Date='{date_str}', Timestamp='{timestamp_str}', Sunday Date='{sunday_date_str}', Attendance='{attendance}'")

# Try to parse dates and sort
def get_date_from_row(row):
    # Try all date fields
    date_str = row.get('Date', '') or row.get('Timestamp', '') or row.get('Sunday Date', '')
    if not date_str:
        return datetime.min
    
    try:
        # If it has time information, try to parse the full datetime
        if ' ' in str(date_str) and ':' in str(date_str):
            # Try to parse as full datetime
            try:
                return datetime.strptime(str(date_str), '%Y-%m-%d %H:%M:%S')
            except:
                pass
            try:
                return datetime.strptime(str(date_str), '%Y-%m-%d %H:%M')
            except:
                pass
        
        # Extract just the date part (before any time)
        date_part = str(date_str).split(' ')[0]
        parsed_date = datetime.strptime(date_part, '%Y-%m-%d')
        return parsed_date
    except Exception as e:
        print(f"Failed to parse date '{date_str}': {e}")
        return datetime.min

# Sort by date
south_rows.sort(key=get_date_from_row, reverse=True)

print(f"\nTop 10 South campus rows after sorting:")
for i, row in enumerate(south_rows[:10]):
    date_str = row.get('Date', '')
    timestamp_str = row.get('Timestamp', '')
    sunday_date_str = row.get('Sunday Date', '')
    attendance = row.get('Total Attendance', 'N/A')
    parsed_date = get_date_from_row(row)
    print(f"  {i+1}. Date='{date_str}', Timestamp='{timestamp_str}', Sunday Date='{sunday_date_str}' -> {parsed_date}, Attendance='{attendance}'")

if south_rows:
    most_recent = south_rows[0]
    print(f"\nMost recent row: Date='{most_recent.get('Date', 'N/A')}', Timestamp='{most_recent.get('Timestamp', 'N/A')}', Attendance='{most_recent.get('Total Attendance', 'N/A')}'")
else:
    print("\nNo South campus rows found") 