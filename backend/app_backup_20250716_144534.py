# app.py

print("[DEBUG] Starting import: Flask")
from flask import Flask, request, jsonify, send_from_directory, render_template
print("[DEBUG] Imported Flask")

print("[DEBUG] Starting import: Flask-Cors")
from flask_cors import CORS
print("[DEBUG] Imported Flask-Cors")

print("[DEBUG] Starting import: datetime")
from datetime import datetime, timezone, timedelta
print("[DEBUG] Imported datetime")

print("[DEBUG] Starting import: os")
import os
print("[DEBUG] Imported os")

print("[DEBUG] Starting import: re")
import re
print("[DEBUG] Imported re")

try:
    print("[DEBUG] Starting import: gspread")
    import gspread
    print("[DEBUG] Imported gspread")
except Exception as e:
    print(f"[ERROR] Failed to import gspread: {e}")
    raise

try:
    print("[DEBUG] Starting import: anthropic")
    import anthropic
    print("[DEBUG] Imported anthropic")
except Exception as e:
    print(f"[ERROR] Failed to import anthropic: {e}")
    raise

try:
    print("[DEBUG] Starting import: oauth2client.service_account")
    from oauth2client.service_account import ServiceAccountCredentials
    print("[DEBUG] Imported oauth2client.service_account")
except Exception as e:
    print(f"[ERROR] Failed to import oauth2client.service_account: {e}")
    raise

print("[DEBUG] Starting import: json")
import json
print("[DEBUG] Imported json")

print("[DEBUG] Starting import: typing")
from typing import Dict, List, Optional, Any
print("[DEBUG] Imported typing")

print("[DEBUG] Starting import: logging")
import logging
print("[DEBUG] Imported logging")

try:
    print("[DEBUG] Starting import: dotenv")
    from dotenv import load_dotenv
    print("[DEBUG] Imported dotenv")
except Exception as e:
    print(f"[ERROR] Failed to import dotenv: {e}")
    raise

try:
    print("[DEBUG] Starting import: num2words")
    from num2words import num2words
    print("[DEBUG] Imported num2words")
except ImportError:
    print("[WARNING] num2words not installed, using fallback")
    def num2words(n):
        return str(n)

# Load environment variables from .env file
print("[DEBUG] Loading environment variables from .env")
load_dotenv()
print("[DEBUG] Loaded environment variables from .env")

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("[DEBUG] Starting Google Sheets Auth scope definition")
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
print("[DEBUG] Finished Google Sheets Auth scope definition")

print("[DEBUG] Starting Google Sheets client initialization")
# Initialize Google Sheets client
try:
    if os.path.exists("credentials.json"):
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("Stats").sheet1
        logger.info("Google Sheets initialized successfully")
    else:
        logger.warning("credentials.json not found - Google Sheets functionality disabled")
        sheet = None
except Exception as e:
    logger.error(f"Failed to initialize Google Sheets: {e}")
    sheet = None
print("[DEBUG] Finished Google Sheets client initialization")

print("[DEBUG] Starting Claude setup")
# Claude setup
try:
    from anthropic import Client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        claude = Client(api_key=api_key)
        logger.info("Claude initialized successfully (Client)")
        print("[DEBUG] Claude initialized successfully (Client)")
    else:
        logger.warning("ANTHROPIC_API_KEY not found in environment variables")
        print("[WARNING] ANTHROPIC_API_KEY not found in environment variables")
        claude = None
except Exception as e:
    logger.error(f"Failed to initialize Claude: {e}")
    print(f"[ERROR] Failed to initialize Claude: {e}")
    claude = None
print("[DEBUG] Finished Claude setup")

print("[DEBUG] Starting ElevenLabs setup")
# ElevenLabs setup
try:
    import requests
    elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
    elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Default voice ID
    if elevenlabs_api_key:
        logger.info("ElevenLabs API key found")
        print("[DEBUG] ElevenLabs API key found")
    else:
        logger.warning("ELEVENLABS_API_KEY not found - will use browser TTS")
        print("[WARNING] ELEVENLABS_API_KEY not found - will use browser TTS")
except Exception as e:
    logger.error(f"Failed to initialize ElevenLabs: {e}")
    print(f"[ERROR] Failed to initialize ElevenLabs: {e}")
    elevenlabs_api_key = None
print("[DEBUG] Finished ElevenLabs setup")

print("[DEBUG] Starting memory storage setup")
# Memory storage for conversational history
conversation_memory_file = "data/conversation_memory.json"
print("[DEBUG] Finished memory storage setup")

# Restore missing memory functions

def load_conversation_memory() -> Dict[str, Any]:
    """Load conversation memory from file"""
    try:
        if os.path.exists(conversation_memory_file):
            with open(conversation_memory_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load conversation memory: {e}")
    return {}

def save_conversation_memory(memory: Dict[str, Any]):
    """Save conversation memory to file"""
    try:
        os.makedirs(os.path.dirname(conversation_memory_file), exist_ok=True)
        with open(conversation_memory_file, 'w') as f:
            json.dump(memory, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save conversation memory: {e}")

print("[DEBUG] Creating Flask app instance")
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
print("[DEBUG] Flask app instance created and CORS enabled")

# Enhanced regex patterns for parsing stats with better context awareness
patterns = {
    # Match numbers with various contexts for attendance
    "total_attendance": r"(\d+)\s+(?:people|attendance|total|had|got|there were)",
    "new_people": r"(\d+)\s+(?:new(?:\s+people|visitors?|guests?)?|np)",
    "new_christians": r"(\d+)\s+(?:salvations|new\s+christians|decisions|baptisms?|nc)",
    "youth_attendance": r"(\d+)\s+(?:youth(?:\s+group|\s+ministry)?|teens?|yout)",
    "kids_total": r"(\d+)\s+(?:kids|children|kids\s+ministry|nursery)",
    "connect_groups": r"(\d+)\s+(?:connect\s+groups?|small\s+groups?|connects?|life\s+groups?)",
    "tithe_amount": r"\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\s+(?:tithe|offering|giving|in\s+tithe)",
    "volunteers": r"(\d+)\s+(?:volunteers?|team\s+members?|servers?)"
}

# Campus detection patterns
campus_patterns = {
    "paradise": r"(?:paradise)",
    "adelaide_city": r"(?:adelaide\s+city)",
    "salisbury": r"(?:salisbury)",
    "south": r"(?:south\s+campus|southside|south)",
    "clare_valley": r"(?:clare\s+valley)",
    "mount_barker": r"(?:mount\s+barker)",
    "victor_harbour": r"(?:victor\s+harbour)",
    "copper_coast": r"(?:copper\s+coast)",
    "north": r"(?:north\s+campus|northside)",
    "east": r"(?:east\s+campus|eastside)",
    "west": r"(?:west\s+campus|westside)",
    "online": r"(?:online|virtual|stream)"
}

def detect_campus(text: str) -> Optional[str]:
    """Detect campus from voice input with improved patterns and confidence scoring"""
    text_lower = text.lower()
    logger.info(f"Detecting campus from text: '{text}'")
    
    # Enhanced campus detection patterns with confidence scoring
    campus_keywords = {
        "south": [r"\bsouth\b", r"\bsouth\s+campus\b", "southampton", "for south", "at south", "south campus"],
        "north": [r"\bnorth\b", r"\bnorth\s+campus\b", "for north", "at north", "north campus"],
        "east": [r"\beast\b", r"\beast\s+campus\b", "for east", "at east", "east campus"],
        "west": [r"\bwest\b", r"\bwest\s+campus\b", "for west", "at west", "west campus"],
        "paradise": [r"\bparadise\b", r"\bparadise\s+campus\b", "main campus", "for paradise", "at paradise"],
        "adelaide_city": [r"adelaide\s+city", r"\bcity\s+campus\b", r"\bcity\b", "for adelaide", "at adelaide"],
        "salisbury": [r"\bsalisbury\b", r"\bsalisbury\s+campus\b", "for salisbury", "at salisbury"],
        "clare_valley": [r"clare\s+valley", r"\bclare\b", "for clare", "at clare"],
        "mount_barker": [r"mount\s+barker", r"\bbarker\b", "for mount barker", "at mount barker"],
        "victor_harbour": [r"victor\s+harbour", r"\bvictor\b", "for victor", "at victor"],
        "copper_coast": [r"copper\s+coast", r"\bcopper\b", "for copper", "at copper"]
    }
    
    # Check for campus keywords using regex for word boundaries with confidence scoring
    best_match = None
    best_confidence = 0
    
    for campus, patterns in campus_keywords.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                # Calculate confidence based on pattern specificity
                confidence = len(pattern.split())  # More specific patterns get higher confidence
                if confidence > best_confidence:
                    best_match = campus
                    best_confidence = confidence
                    logger.info(f"Found campus '{campus}' using pattern '{pattern}' with confidence {confidence}")
    
    if best_match:
        return best_match
    
    # Fallback to original patterns
    for campus, pattern in campus_patterns.items():
        if re.search(pattern, text_lower):
            logger.info(f"Found campus '{campus}' using fallback pattern '{pattern}'")
            return campus
    
    logger.info("No campus detected, returning None")
    return None  # no campus detected

def extract_stats_with_context(text: str, campus: str) -> Dict[str, Any]:
    """Extract stats with enhanced context awareness and mutually exclusive patterns"""
    result = {
        "Campus": campus,
        "Timestamp": datetime.now(timezone.utc).isoformat(),
        "Raw_Text": text
    }
    # Only extract a stat if its context matches, do not fallback to first number
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Convert to string for Google Sheets compatibility
            result[key.replace("_", " ").title()] = str(match.group(1))
            logger.info(f"Extracted {key}: {match.group(1)}")
    # No fallback for total_attendance: only extract if context matches
    return result

def generate_encouragement_with_memory(text: str, campus: str, memory: Dict[str, Any]) -> List[str]:
    """Generate conversational responses using Claude with conversation memory"""
    if not claude:
        return ["Thanks for logging those stats!", "Keep up the great work!"]
    
    # Build context from memory with better formatting
    campus_history = memory.get(campus, [])
    recent_stats = campus_history[-3:] if campus_history else []
    
    context = ""
    if recent_stats:
        context = f"\n\nRecent stats from {campus} campus:\n"
        for i, stat in enumerate(recent_stats, 1):
            raw_text = stat.get('Raw_Text', '')
            timestamp = stat.get('Timestamp', '')
            if timestamp:
                # Extract just the date part
                try:
                    date_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    date_str = date_obj.strftime("%B %d")
                except:
                    date_str = "recently"
            else:
                date_str = "recently"
            context += f"{i}. {date_str}: {raw_text}\n"
    
    # Check if this is a request to log stats vs actual stats vs a query
    text_lower = text.lower()
    is_request = any(word in text_lower for word in ['log', 'record', 'enter', 'add', 'can we', 'how to', 'stats', 'google stats', 'want to', 'help me', 'assist'])
    is_query = any(word in text_lower for word in [
        'how many', 'what is', 'average', 'last week', 'this week', 'total', 'count', 'query', 'data', 'has had', 'had this year', 'had this month',
        'compare', 'comparison', 'vs', 'versus', 'between', 'year over year',
        'review', 'annual review', 'mid year review', 'mid-year review', 'report', 'summary', 'dashboard', 'snapshot', 'full report', 'overview', 'recap', 'stats summary', 'stat summary', 'stat report', 'stat overview', 'stat recap'
    ])
    
    if is_query:
        prompt = f"""You are a helpful church AI assistant. A leader from the {campus} campus is asking for data:
"{text}"

{context}

Respond naturally as a helpful assistant. Tell them you'll look up that information for them. Be conversational and friendly. Keep it under 15 words. Examples:
- "I'll look that up for you right away!"
- "Let me check the data for {campus} campus."
- "I'll find that information for you."""
    elif is_request:
        prompt = f"""You are a friendly, helpful church AI assistant. A leader from the {campus} campus is asking:
"{text}"

{context}

Respond naturally as a helpful assistant. If they want to log stats, guide them conversationally. Be encouraging and friendly. Keep it under 20 words. 

Guide them to log new stats. Examples:
- "Perfect! I'm ready to record today's stats for {campus} campus. What were your numbers?"
- "Great! Let's log today's stats for {campus} campus. How many people attended?"
- "Absolutely! I'm here to help log stats for {campus} campus. What numbers do you have?"
- "Ready to log stats for {campus} campus! What numbers do you have today?"""
    else:
        prompt = f"""You are a church insights assistant. A leader from the {campus} campus submitted:
"{text}"

{context}

Generate EXACTLY 2 short insights (max 12 words each). Focus on different trends, patterns, or observations. Be encouraging but factual. Format as:
1. [First insight]
2. [Second insight]"""

    try:
        response = claude.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=80,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response.content[0].text.strip() if hasattr(response.content[0], 'text') else str(response.content[0])
        
        if is_request:
            # For requests, return a single helpful response
            return [response_text]
        else:
            # Parse the response to extract exactly 2 insights
            lines = response_text.split('\n')
            insights = []
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('1.') and not line.startswith('2.'):
                    insights.append(line)
            
            # Ensure we have exactly 2 insights
            if len(insights) >= 2:
                return insights[:2]
            elif len(insights) == 1:
                return [insights[0], "Great progress this week!"]
            else:
                return ["Thanks for logging those stats!", "Keep up the great work!"]
            
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        if is_request:
            return [f"Sure! I'd love to help log stats for {campus} campus. Just tell me the numbers!", "What were your attendance numbers today?"]
        else:
            return ["Thanks for logging those stats!", "Keep up the great work!"]

# Update: allow generate_audio_with_elevenlabs to accept a filename for saving audio

def generate_audio_with_elevenlabs(text: str, filename: Optional[str] = None) -> Optional[str]:
    """Generate audio using ElevenLabs API, optionally saving to a specific filename"""
    if not elevenlabs_api_key:
        return None
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{elevenlabs_voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": elevenlabs_api_key
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            os.makedirs("temp_audio", exist_ok=True)
            if filename:
                audio_filename = filename
            else:
                audio_filename = f"temp_audio/response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            with open(audio_filename, "wb") as f:
                f.write(response.content)
            logger.info(f"Generated audio file: {audio_filename}")
            return f"/{audio_filename}" if filename else f"/temp_audio/{os.path.basename(audio_filename)}"
        else:
            logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Failed to generate audio with ElevenLabs: {e}")
        return None

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

def parse_date_range(question: str) -> tuple:
    """Parse date range from question text"""
    question_lower = question.lower()
    current_year = datetime.now().year
    
    # Extract year from question (look for 4-digit years like 2024, 2023, etc.)
    import re
    year_match = re.search(r'\b(20\d{2})\b', question)
    target_year = int(year_match.group(1)) if year_match else current_year
    
    # YTD (Year to Date) detection
    if any(phrase in question_lower for phrase in ['ytd', 'year to date', 'this year', 'so far this year']):
        start_date = datetime(target_year, 1, 1)
        end_date = datetime.now() if target_year == current_year else datetime(target_year, 12, 31)
        return start_date, end_date, f"year to date ({target_year})"
    
    # Month range detection
    months = {
        'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
        'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7,
        'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'october': 10, 'oct': 10,
        'november': 11, 'nov': 11, 'december': 12, 'dec': 12
    }
    
    # Look for "from X to Y" or "X to Y" patterns
    for month_name, month_num in months.items():
        if month_name in question_lower:
            # Check for "from X to Y" pattern
            if f"from {month_name}" in question_lower:
                for end_month_name, end_month_num in months.items():
                    if f"to {end_month_name}" in question_lower:
                        start_date = datetime(target_year, month_num, 1)
                        if end_month_num == 12:
                            end_date = datetime(target_year, end_month_num, 31)
                        else:
                            end_date = datetime(target_year, end_month_num + 1, 1) - timedelta(days=1)
                        return start_date, end_date, f"{month_name.title()} to {end_month_name.title()} {target_year}"
            
            # Check for "X to Y" pattern (without "from")
            for end_month_name, end_month_num in months.items():
                if f"{month_name} to {end_month_name}" in question_lower:
                    start_date = datetime(target_year, month_num, 1)
                    if end_month_num == 12:
                        end_date = datetime(target_year, end_month_num, 31)
                    else:
                        end_date = datetime(target_year, end_month_num + 1, 1) - timedelta(days=1)
                    return start_date, end_date, f"{month_name.title()} to {end_month_name.title()} {target_year}"
    
    # Single month detection
    for month_name, month_num in months.items():
        if month_name in question_lower:
            start_date = datetime(target_year, month_num, 1)
            if month_num == 12:
                end_date = datetime(target_year, month_num, 31)
            else:
                end_date = datetime(target_year, month_num + 1, 1) - timedelta(days=1)
            return start_date, end_date, f"{month_name.title()} {target_year}"
    
    # No date range found
    return None, None, None

def detect_comparison_request(question: str) -> tuple:
    """Detect if this is a comparison request and extract years to compare"""
    question_lower = question.lower()
    current_year = datetime.now().year
    
    # Look for comparison keywords
    comparison_keywords = ['compare', 'comparison', 'vs', 'versus', 'against', 'side by side', 'year over year']
    is_comparison = any(keyword in question_lower for keyword in comparison_keywords)
    
    if not is_comparison:
        return False, [], None
    
    # Extract all years mentioned in the question
    import re
    years = re.findall(r'\b(20\d{2})\b', question)
    
    if len(years) >= 2:
        # Multiple years found, use them for comparison
        return True, [int(year) for year in years], "comparison"
    elif len(years) == 1:
        # One year found, compare with previous year
        year1 = int(years[0])
        year2 = year1 - 1
        return True, [year1, year2], "comparison"
    else:
        # No years found, compare current year with previous year
        return True, [current_year, current_year - 1], "comparison"
    
    return False, [], None

def extract_stat_from_row(entry, stat_type):
    # If entry is a dict, use flexible field name matching
    if isinstance(entry, dict):
        stat_fields = {
            'attendance': ["Total Attendance", "Attendance", "attendance", "total_attendance"],
            'new_people': ["New People", "NewPeople", "new_people"],
            'new_christians': ["New Christians", "Souls", "new_christians"],
            'youth': ["Youth Attendance", "Youth", "youth_attendance"],
            'kids': ["Kids Total", "Kids", "kids_total"],
            'connect_groups': ["Connect Groups", "ConnectGroups", "connect_groups"],
            'dream_team': ["Volunteers", "volunteers", "Dream Team", "dream_team"]
        }
        for field in stat_fields.get(stat_type, []):
            val = entry.get(field)
            if val not in (None, ""):
                try:
                    return int(str(val).replace(",", "").strip())
                except Exception:
                    continue
        return 0
    # If entry is a list or tuple, use positional mapping
    elif isinstance(entry, (list, tuple)):
        # Detect format: if 3rd column is a date, it's standard; if 2nd column is campus, it's link-logged
        def is_date(val):
            try:
                if not val or not isinstance(val, str):
                    return False
                parts = val.split("-")
                return len(parts) >= 3 and len(parts[0]) == 4
            except Exception:
                return False
        # Standard: [Timestamp, Date, Campus, ...]
        if len(entry) >= 12 and is_date(entry[1]):
            mapping = {
                'attendance': 3,
                'new_people': 4,
                'new_christians': 5,
                'youth': 6,
                'kids': 9,
                'connect_groups': 11,
                'dream_team': None  # Not present
            }
        # Link-logged: [Timestamp, Campus, Attendance, ...]
        elif len(entry) >= 8 and not is_date(entry[1]):
            mapping = {
                'attendance': 2,
                'new_people': 3,
                'new_christians': 4,
                'youth': 5,
                'kids': 6,
                'connect_groups': 7,
                'dream_team': None  # Not present
            }
        else:
            return 0
        idx = mapping.get(stat_type)
        if idx is not None and idx < len(entry):
            val = entry[idx]
            if val not in (None, ""):
                try:
                    return int(str(val).replace(",", "").strip())
                except Exception:
                    return 0
        return 0
    return 0

def calculate_stats_for_year_range(rows: List[dict], campus: str, start_year: int, end_year: Optional[int] = None) -> dict:
    """Calculate stats for a specific year range"""
    if end_year is None:
        end_year = start_year
    
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    
    # Normalize campus name for comparison
    campus_normalized = normalize_campus(campus)
    filtered_rows = []
    unique_campuses = set()
    
    for row in rows:
        row_campus = normalize_campus(row.get("Campus") or row.get("campus") or "")
        unique_campuses.add(row_campus)
        if row_campus == campus_normalized or campus_normalized in row_campus:
            print(f"MATCHED ROW for {campus}: {row}")  # DEBUG: Show matched rows
            # Apply date filtering
            try:
                timestamp_str = row.get("Timestamp", "")
                if timestamp_str:
                    # Handle different timestamp formats
                    if "T" in timestamp_str:
                        row_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    else:
                        row_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    # Check if row date is within the specified range
                    if start_date <= row_date <= end_date:
                        filtered_rows.append(row)
                else:
                    # If no timestamp, include the row (fallback)
                    filtered_rows.append(row)
            except Exception as e:
                logger.warning(f"Could not parse timestamp for row: {e}")
                filtered_rows.append(row)
    print(f"[DEBUG] Unique campuses in data: {sorted(unique_campuses)}")
    # Calculate stats
    total_attendance = 0
    total_new_people = 0
    total_new_christians = 0
    total_youth = 0
    total_kids = 0
    total_connect_groups = 0
    entry_count = 0
    
    # Track values for average calculation
    attendance_values = []
    new_people_values = []
    new_christians_values = []
    youth_values = []
    kids_values = []
    connect_groups_values = []
    
    for entry in filtered_rows:
        if isinstance(entry, (dict, list, tuple)):
            attendance_val = extract_stat_from_row(entry, 'attendance')
            new_people_val = extract_stat_from_row(entry, 'new_people')
            new_christians_val = extract_stat_from_row(entry, 'new_christians')
            youth_val = extract_stat_from_row(entry, 'youth')
            kids_val = extract_stat_from_row(entry, 'kids')
            connect_groups_val = extract_stat_from_row(entry, 'connect_groups')
            # Only count entries with at least one stat
            if any([attendance_val, new_people_val, new_christians_val, youth_val, kids_val, connect_groups_val]):
                entry_count += 1
            
            # Add to totals
            total_attendance += attendance_val
            total_new_people += new_people_val
            total_new_christians += new_christians_val
            total_youth += youth_val
            total_kids += kids_val
            total_connect_groups += connect_groups_val
            
            # Add to lists for averages (only if > 0)
            if attendance_val > 0:
                attendance_values.append(attendance_val)
            if new_people_val > 0:
                new_people_values.append(new_people_val)
            if new_christians_val > 0:
                new_christians_values.append(new_christians_val)
            if youth_val > 0:
                youth_values.append(youth_val)
            if kids_val > 0:
                kids_values.append(kids_val)
            if connect_groups_val > 0:
                connect_groups_values.append(connect_groups_val)
    
    # Calculate averages
    avg_attendance = sum(attendance_values) / len(attendance_values) if attendance_values else 0
    avg_new_people = sum(new_people_values) / len(new_people_values) if new_people_values else 0
    avg_new_christians = sum(new_christians_values) / len(new_christians_values) if new_christians_values else 0
    avg_youth = sum(youth_values) / len(youth_values) if youth_values else 0
    avg_kids = sum(kids_values) / len(kids_values) if kids_values else 0
    avg_connect_groups = sum(connect_groups_values) / len(connect_groups_values) if connect_groups_values else 0
    
    return {
        "year": start_year,
        "total_entries": entry_count,
        "total_attendance": total_attendance,
        "total_new_people": total_new_people,
        "total_new_christians": total_new_christians,
        "total_youth": total_youth,
        "total_kids": total_kids,
        "total_connect_groups": total_connect_groups,
        "averages": {
            "attendance": round(avg_attendance, 1),
            "new_people": round(avg_new_people, 1),
            "new_christians": round(avg_new_christians, 1),
            "youth": round(avg_youth, 1),
            "kids": round(avg_kids, 1),
            "connect_groups": round(avg_connect_groups, 1)
        }
    }

def query_data_internal(data: Dict[str, Any]) -> Dict[str, Any]:
    """Internal function to query data (same logic as /api/query endpoint)"""
    question = str(data.get("question", "")).strip()
    if not question:
        return {"error": "Missing question"}

    # Extract campus from question using the same detection logic
    campus = detect_campus(question)
    
    if not campus:
        return {"error": "No campus specified in question. Please mention a campus name like 'South', 'Salisbury', etc."}

    # --- Move review intent check here ---
    if is_review_intent(question):
        # Try to extract campus and years
        campus = detect_campus(question) or campus or "main"
        # Extract years (default to current year only, unless user asks for multiple years)
        import re
        years = re.findall(r'\b(20\d{2})\b', question)
        if len(years) == 0:
            # Default to current year only
            years = [datetime.now().year]
        elif len(years) == 1:
            # User specified one year, use that
            years = [int(y) for y in years]
        else:
            # User specified multiple years, use all of them
            years = [int(y) for y in years]
        report = generate_full_stat_report(campus, years)
        return report
    # --- End review intent check ---

    # Check if this is a comparison request
    is_comparison, comparison_years, comparison_type = detect_comparison_request(question)
    
    if is_comparison:
        # Handle comparison request
        return handle_comparison_request(question, campus, comparison_years)
    
    # Parse date range from question
    start_date, end_date, date_range_desc = parse_date_range(question)

    # Try to use Google Sheets if available
    rows = []
    if sheet:
        try:
            rows = sheet.get_all_records()
        except Exception as e:
            logger.error(f"Failed to get stats from Google Sheets: {e}")
            rows = []

    # If no rows from Sheets, fallback to memory
    if not rows:
        memory = load_conversation_memory()
        campus_history = memory.get("session_stats", {}).get(campus, [])
        if not campus_history:
            campus_capitalized = campus.title()
            campus_history = memory.get("session_stats", {}).get(campus_capitalized, [])
            if campus_history:
                campus = campus_capitalized
        # Convert memory format to rows-like dicts for uniformity
        rows = campus_history

    # Normalize campus name for comparison and apply date filtering
    campus_lower = campus.lower()
    filtered_rows = []
    for row in rows:
        row_campus = normalize_campus(row.get("Campus") or row.get("campus") or "")
        campus_normalized = normalize_campus(campus)
        if row_campus == campus_normalized or campus_normalized in row_campus:
            print(f"MATCHED ROW for {campus}: {row}")  # DEBUG: Show matched rows
            # Apply date filtering
            try:
                timestamp_str = row.get("Timestamp", "")
                if timestamp_str:
                    # Handle different timestamp formats
                    if "T" in timestamp_str:
                        row_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    else:
                        row_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    # Only include if row_date is valid and in range
                    if row_date is not None and start_date <= row_date <= end_date:
                        filtered_rows.append(row)
                # If no timestamp, skip the row (do not include as fallback)
            except Exception as e:
                logger.warning(f"Could not parse timestamp for row: {e}")
                # Skip row if timestamp is unparseable
        else:
            print(f"NO MATCH for {campus}: row campus was '{row_campus}'")  # DEBUG: Show non-matches

    # Analyze the question and extract relevant data
    question_lower = question.lower()
    response_data = {
        "question": question,
        "campus": display_campus_name(campus),
        "date_range": date_range_desc,
        "analysis": {},
        "answer": ""
    }

    # Calculate totals and averages for different metrics
    total_attendance = 0
    total_new_people = 0
    total_new_christians = 0
    total_youth = 0
    total_kids = 0
    total_connect_groups = 0
    entry_count = 0

    # Track values for average calculation
    attendance_values = []
    new_people_values = []
    new_christians_values = []
    youth_values = []
    kids_values = []
    connect_groups_values = []

    for entry in filtered_rows:
        if isinstance(entry, (dict, list, tuple)):
            attendance_val = extract_stat_from_row(entry, 'attendance')
            new_people_val = extract_stat_from_row(entry, 'new_people')
            new_christians_val = extract_stat_from_row(entry, 'new_christians')
            youth_val = extract_stat_from_row(entry, 'youth')
            kids_val = extract_stat_from_row(entry, 'kids')
            connect_groups_val = extract_stat_from_row(entry, 'connect_groups')

            # Only count entries with at least one stat
            if any([attendance_val, new_people_val, new_christians_val, youth_val, kids_val, connect_groups_val]):
                entry_count += 1

            # Add to totals
            total_attendance += attendance_val
            total_new_people += new_people_val
            total_new_christians += new_christians_val
            total_youth += youth_val
            total_kids += kids_val
            total_connect_groups += connect_groups_val

            # Add to lists for averages (only if > 0)
            if attendance_val > 0:
                attendance_values.append(attendance_val)
            if new_people_val > 0:
                new_people_values.append(new_people_val)
            if new_christians_val > 0:
                new_christians_values.append(new_christians_val)
            if youth_val > 0:
                youth_values.append(youth_val)
            if kids_val > 0:
                kids_values.append(kids_val)
            if connect_groups_val > 0:
                connect_groups_values.append(connect_groups_val)

    # Calculate averages
    avg_attendance = sum(attendance_values) / len(attendance_values) if attendance_values else 0
    avg_new_people = sum(new_people_values) / len(new_people_values) if new_people_values else 0
    avg_new_christians = sum(new_christians_values) / len(new_christians_values) if new_christians_values else 0
    avg_youth = sum(youth_values) / len(youth_values) if youth_values else 0
    avg_kids = sum(kids_values) / len(kids_values) if kids_values else 0
    avg_connect_groups = sum(connect_groups_values) / len(connect_groups_values) if connect_groups_values else 0

    response_data["analysis"] = {
        "total_entries": entry_count,
        "total_attendance": total_attendance,
        "total_new_people": total_new_people,
        "total_new_christians": total_new_christians,
        "total_youth": total_youth,
        "total_kids": total_kids,
        "total_connect_groups": total_connect_groups,
        "averages": {
            "attendance": round(avg_attendance, 1),
            "new_people": round(avg_new_people, 1),
            "new_christians": round(avg_new_christians, 1),
            "youth": round(avg_youth, 1),
            "kids": round(avg_kids, 1),
            "connect_groups": round(avg_connect_groups, 1)
        }
    }

    # Generate conversational answer based on question type
    date_suffix = f" for {date_range_desc}" if date_range_desc else ""
    
    if "average" in question_lower or "avg" in question_lower:
        if "youth" in question_lower:
            avg_youth_rounded = int(round(avg_youth))
            response_data["answer"] = f"{display_campus_name(campus)} campus had an average of {avg_youth_rounded} youth each week{date_suffix}."
        elif "attendance" in question_lower or "people" in question_lower:
            avg_attendance_rounded = int(round(avg_attendance))
            response_data["answer"] = f"{display_campus_name(campus)} campus had an average of {avg_attendance_rounded} people each week{date_suffix}."
        elif "new people" in question_lower or "new visitors" in question_lower:
            avg_new_people_rounded = int(round(avg_new_people))
            response_data["answer"] = f"{display_campus_name(campus)} campus had an average of {avg_new_people_rounded} new visitors each week{date_suffix}."
        elif "salvations" in question_lower or "new christians" in question_lower:
            avg_new_christians_rounded = int(round(avg_new_christians))
            response_data["answer"] = f"{display_campus_name(campus)} campus had an average of {avg_new_christians_rounded} salvations each week{date_suffix}."
        elif "kids" in question_lower or "children" in question_lower:
            avg_kids_rounded = int(round(avg_kids))
            response_data["answer"] = f"{display_campus_name(campus)} campus had an average of {avg_kids_rounded} kids each week{date_suffix}."
        elif "connect groups" in question_lower:
            avg_connect_groups_rounded = int(round(avg_connect_groups))
            response_data["answer"] = f"{display_campus_name(campus)} campus had an average of {avg_connect_groups_rounded} connect groups each week{date_suffix}."
        else:
            avg_attendance_rounded = int(round(avg_attendance))
            response_data["answer"] = f"{display_campus_name(campus)} campus had an average of {avg_attendance_rounded} people each week{date_suffix}."
    elif "new people" in question_lower or "new visitors" in question_lower or "np" in question_lower:
        response_data["answer"] = f"{display_campus_name(campus)} campus has had {total_new_people} total new visitors{date_suffix}."
    elif "attendance" in question_lower or "people" in question_lower:
        response_data["answer"] = f"{display_campus_name(campus)} campus has had {total_attendance} total people{date_suffix}."
    elif "salvations" in question_lower or "new christians" in question_lower or "nc" in question_lower:
        response_data["answer"] = f"{display_campus_name(campus)} campus has had {total_new_christians} total salvations{date_suffix}."
    elif "youth" in question_lower:
        response_data["answer"] = f"{display_campus_name(campus)} campus has had {total_youth} total youth{date_suffix}."
    elif "kids" in question_lower or "children" in question_lower:
        response_data["answer"] = f"{display_campus_name(campus)} campus has had {total_kids} total kids{date_suffix}."
    elif "connect groups" in question_lower or "small groups" in question_lower:
        response_data["answer"] = f"{display_campus_name(campus)} campus has had {total_connect_groups} total connect groups{date_suffix}."
    else:
        response_data["answer"] = f"{display_campus_name(campus)} campus has had {total_attendance} total people, {total_new_people} new visitors, and {total_new_christians} salvations{date_suffix}."

    return response_data

def is_review_intent(question: str) -> bool:
    review_keywords = [
        'review', 'annual review', 'anual review', 'mid year review', 'mid-year review', 'report', 'summary', 'dashboard', 'snapshot', 'full report', 'overview', 'recap',
        'stats summary', 'stat summary', 'stat report', 'stat overview', 'stat recap',
        'year in review', 'yearly review', 'yearly report', 'year-end review', 'year end review', 'end of year report', 'end of year review',
        'give me a review', 'give me an annual review', 'can i get a review', 'can i get an annual review', 'show me a review', 'show me an annual review',
        'show me the annual report', 'show me the report', 'show me the summary', 'show me the dashboard', 'show me the stats summary',
        'generate a report', 'generate an annual report', 'generate a summary', 'generate an annual summary',
        'full stats', 'all stats', 'all statistics', 'all numbers', 'all data', 'all metrics',
        'recap of the year', 'recap for the year', 'recap', 'stat recap', 'stats recap',
        'big picture', 'big picture stats', 'big picture summary', 'big picture report',
        'comprehensive report', 'comprehensive review', 'comprehensive summary',
        'church report', 'church review', 'church summary',
        'midyear review', 'midyear report', 'mid year report', 'mid-year report',
        'annual stats', 'annual statistics', 'annual numbers', 'annual data',
        'give me a summary', 'can i get a summary', 'show me a summary',
        'give me a dashboard', 'can i get a dashboard', 'show me a dashboard',
        'give me a snapshot', 'can i get a snapshot', 'show me a snapshot',
        'give me an overview', 'can i get an overview', 'show me an overview',
        'give me a full report', 'can i get a full report', 'show me a full report',
        'give me a full review', 'can i get a full review', 'show me a full review',
        'give me a full summary', 'can i get a full summary', 'show me a full summary',
        'give me a stat report', 'can i get a stat report', 'show me a stat report',
        'give me a stat summary', 'can i get a stat summary', 'show me a stat summary',
        'give me a stat overview', 'can i get a stat overview', 'show me a stat overview',
        'give me a stat recap', 'can i get a stat recap', 'show me a stat recap',
        'give me a stats summary', 'can i get a stats summary', 'show me a stats summary',
        'give me a stats overview', 'can i get a stats overview', 'show me a stats overview',
        'give me a stats recap', 'can i get a stats recap', 'show me a stats recap',
        'give me an annual stats', 'can i get annual stats', 'show me annual stats',
        'give me an annual statistics', 'can i get annual statistics', 'show me annual statistics',
        'give me an annual numbers', 'can i get annual numbers', 'show me annual numbers',
        'give me an annual data', 'can i get annual data', 'show me annual data',
        'give me an annual summary', 'can i get annual summary', 'show me annual summary',
        'give me an annual report', 'can i get annual report', 'show me annual report',
        'give me an annual review', 'can i get annual review', 'show me annual review',
        'give me an anual review', 'can i get an anual review', 'show me an anual review',
        'give me an anual report', 'can i get an anual report', 'show me an anual report',
        'give me an anual summary', 'can i get an anual summary', 'show me an anual summary',
        'give me an anual stats', 'can i get an anual stats', 'show me an anual stats',
        'give me an anual statistics', 'can i get an anual statistics', 'show me an anual statistics',
        'give me an anual numbers', 'can i get an anual numbers', 'show me an anual numbers',
        'give me an anual data', 'can i get an anual data', 'show me an anual data',
        'mid year', 'mid-year', 'midyear', 'mid year review', 'mid-year review', 'midyear review',
        'mid year report', 'mid-year report', 'midyear report',
        'mid year summary', 'mid-year summary', 'midyear summary',
        'mid year stats', 'mid-year stats', 'midyear stats',
        'mid year statistics', 'mid-year statistics', 'midyear statistics',
        'mid year numbers', 'mid-year numbers', 'midyear numbers',
        'mid year data', 'mid-year data', 'midyear data',
        'mid year recap', 'mid-year recap', 'midyear recap',
        'mid year overview', 'mid-year overview', 'midyear overview',
        'mid year dashboard', 'mid-year dashboard', 'midyear dashboard',
        'mid year snapshot', 'mid-year snapshot', 'midyear snapshot',
        'mid year full report', 'mid-year full report', 'midyear full report',
        'mid year full review', 'mid-year full review', 'midyear full review',
        'mid year full summary', 'mid-year full summary', 'midyear full summary',
        'mid year stat report', 'mid-year stat report', 'midyear stat report',
        'mid year stat summary', 'mid-year stat summary', 'midyear stat summary',
        'mid year stat overview', 'mid-year stat overview', 'midyear stat overview',
        'mid year stat recap', 'mid-year stat recap', 'midyear stat recap',
        'mid year stats summary', 'mid-year stats summary', 'midyear stats summary',
        'mid year stats overview', 'mid-year stats overview', 'midyear stats overview',
        'mid year stats recap', 'mid-year stats recap', 'midyear stats recap',
    ]
    q = question.lower()
    return any(phrase in q for phrase in review_keywords)

def generate_full_stat_report(campus: str, years: list) -> dict:
    # List of all stat types to include
    stat_types = [
        ('attendance', 'Total Attendance', 'attendance'),
        ('new_people', 'New People', 'new_people'),
        ('new_christians', 'New Christians', 'new_christians'),
        ('youth', 'Youth Attendance', 'youth'),
        ('kids', 'Kids Total', 'kids'),
        ('connect_groups', 'Connect Groups', 'connect_groups'),
        ('dream_team', 'Volunteers', 'volunteers'),
    ]
    results = []
    for year in years:
        # Get all rows for the campus and year using the robust function
        rows = []
        if sheet:
            try:
                rows = sheet.get_all_records()
            except Exception as e:
                logger.error(f"Failed to get stats from Google Sheets: {e}")
                rows = []
        if not rows:
            memory = load_conversation_memory()
            campus_history = memory.get("session_stats", {}).get(campus, [])
            if not campus_history:
                campus_capitalized = campus.title()
                campus_history = memory.get("session_stats", {}).get(campus_capitalized, [])
                if campus_history:
                    campus = campus_capitalized
            rows = campus_history
        # Use the robust function to get all stats for the year
        year_stats = calculate_stats_for_year_range(rows, campus, year)
        for stat_type, stat_label, avg_key in stat_types:
            # Map stat_type to the correct key in year_stats
            if stat_type == 'attendance':
                total = year_stats.get('total_attendance', 0)
                avg = year_stats.get('averages', {}).get('attendance', 0)
                count = year_stats.get('total_entries', 0)
            elif stat_type == 'new_people':
                total = year_stats.get('total_new_people', 0)
                avg = year_stats.get('averages', {}).get('new_people', 0)
                count = year_stats.get('total_entries', 0)
            elif stat_type == 'new_christians':
                total = year_stats.get('total_new_christians', 0)
                avg = year_stats.get('averages', {}).get('new_christians', 0)
                count = year_stats.get('total_entries', 0)
            elif stat_type == 'youth':
                total = year_stats.get('total_youth', 0)
                avg = year_stats.get('averages', {}).get('youth', 0)
                count = year_stats.get('total_entries', 0)
            elif stat_type == 'kids':
                total = year_stats.get('total_kids', 0)
                avg = year_stats.get('averages', {}).get('kids', 0)
                count = year_stats.get('total_entries', 0)
            elif stat_type == 'connect_groups':
                total = year_stats.get('total_connect_groups', 0)
                avg = year_stats.get('averages', {}).get('connect_groups', 0)
                count = year_stats.get('total_entries', 0)
            elif stat_type == 'dream_team':
                # Volunteers/dream_team is not in calculate_stats_for_year_range, so extract manually
                # Try to sum from filtered rows
                filtered_rows = []
                campus_normalized = normalize_campus(campus)
                start_date = datetime(year, 1, 1)
                end_date = datetime(year, 12, 31)
                for row in rows:
                    row_campus = normalize_campus(row.get("Campus") or row.get("campus") or "")
                    if row_campus == campus_normalized or campus_normalized in row_campus:
                        timestamp_str = row.get("Timestamp", "")
                        if timestamp_str:
                            try:
                                if "T" in timestamp_str:
                                    row_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                else:
                                    row_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                                if start_date <= row_date <= end_date:
                                    filtered_rows.append(row)
                            except Exception:
                                filtered_rows.append(row)
                        else:
                            filtered_rows.append(row)
                total = 0
                avg = 0
                count = 0
                values = []
                for entry in filtered_rows:
                    def safe_int(val):
                        try:
                            return int(str(val).replace(",", "").strip()) if str(val).strip() else 0
                        except Exception:
                            return 0
                    val = safe_int(entry.get("Volunteers") or entry.get("volunteers"))
                    if val > 0:
                        values.append(val)
                        total += val
                        count += 1
                if count > 0:
                    avg = total / count
            else:
                total = 0
                avg = 0
                count = 0
            results.append({
                "stat": stat_type,
                "label": stat_label,
                "year": year,
                "campus": display_campus_name(campus),
                "total": total,
                "average": round(avg, 1),
                "count": count
            })
    # Generate a spoken summary that matches the report data
    spoken_summary = generate_spoken_report_summary(results, campus, years)
    return {
        "report": results,
        "text": spoken_summary
    }

def generate_spoken_report_summary(results: list, campus: str, years: list) -> str:
    """Generate a simple, friendly response for annual/mid-year reviews"""
    campus_display = display_campus_name(campus)
    if not results:
        return f"No data found for {campus_display} campus."
    
    # Default to "annual review" unless it's clearly mid-year
    current_year = datetime.now().year
    current_month = datetime.now().month
    is_mid_year = any(year == current_year for year in years) and current_month <= 6  # Only call it mid-year if we're in first half
    
    if len(years) == 1:
        year_str = str(years[0])
        if is_mid_year:
            return f"Here's your mid-year review for {campus_display} campus in {year_str}."
        else:
            return f"Here's your annual review for {campus_display} campus in {year_str}."
    else:
        years_str = ", ".join(str(year) for year in sorted(years))
        return f"Here's your annual review for {campus_display} campus covering {years_str}."
    # After generating the summary string, replace large numbers with their word equivalents
    import re
    def replace_large_numbers(text):
        def repl(match):
            n = int(match.group(0).replace(',', ''))
            if n >= 1000:
                return num2words(n, to='number').replace('-', ' ')
            return match.group(0)
        return re.sub(r'\b\d{1,3}(?:,\d{3})+|\b\d{4,}\b', repl, text)
    summary = ... # existing summary generation logic
    summary = replace_large_numbers(summary)
    return summary

def handle_comparison_request(question: str, campus: str, years: List[int]) -> Dict[str, Any]:
    """Handles comparison requests (e.g., "compare 2023 to 2022") and generates a comparison response."""
    start_year, end_year = years
    
    # Get rows data (same logic as query_data_internal)
    rows = []
    if sheet:
        try:
            rows = sheet.get_all_records()
        except Exception as e:
            logger.error(f"Failed to get stats from Google Sheets: {e}")
            rows = []

    # If no rows from Sheets, fallback to memory
    if not rows:
        memory = load_conversation_memory()
        campus_history = memory.get("session_stats", {}).get(campus, [])
        if not campus_history:
            campus_capitalized = campus.title()
            campus_history = memory.get("session_stats", {}).get(campus_capitalized, [])
            if campus_history:
                campus = campus_capitalized
        # Convert memory format to rows-like dicts for uniformity
        rows = campus_history
    
    # Calculate stats for both years
    start_year_stats = calculate_stats_for_year_range(rows, campus, start_year)
    end_year_stats = calculate_stats_for_year_range(rows, campus, end_year)
    
    # Detect which stat the user is asking about
    question_lower = question.lower()
    stat_type = "attendance"  # default
    
    # Detect if user wants total vs average
    want_total = any(word in question_lower for word in ['total', 'sum', 'all', 'entire', 'whole', 'cumulative', 'grand total', 'overall', 'combined', 'aggregate', 'in total', 'for the year', 'so far', 'to date', 'ytd', 'this year', 'last year'])
    want_average = any(word in question_lower for word in ['average', 'avg', 'mean', 'per week', 'weekly', 'on average', 'week to week', 'typical', 'median', 'usual', 'normally', 'week average', 'weekly average'])
    
    # Default to average if neither is specified
    use_total = want_total and not want_average
    use_average = want_average or (not want_total and not want_average)
    
    # Expanded stat keyword detection
    if any(word in question_lower for word in [
        'np', 'nps', "np's", 'new person', 'new people', 'newcomer', 'newcomers', 'visitor', 'visitors', 'first timer', 'first timers', 'guest', 'guests']):
        stat_type = "new_people"
        stat_name = "new people"
        stat_key = "total_new_people"
        avg_key = "new_people"
    elif any(word in question_lower for word in [
        'nc', 'ncs', "nc's", 'new christian', 'new christians', 'salvation', 'salvations', 'decision', 'decisions', 'commitment', 'commitments', 'response', 'responses']):
        stat_type = "new_christians"
        stat_name = "salvations"
        stat_key = "total_new_christians"
        avg_key = "new_christians"
    elif any(word in question_lower for word in [
        'youth', 'youths', 'teen', 'teens', 'teenager', 'teenagers', 'high school', 'highschool', 'youth group', 'youth ministry']):
        stat_type = "youth"
        stat_name = "youth"
        stat_key = "total_youth"
        avg_key = "youth"
    elif any(word in question_lower for word in [
        'kid', 'kids', 'child', 'children', 'primary', 'primary school', 'kids church', 'kids ministry', "children's", "children's ministry"]):
        stat_type = "kids"
        stat_name = "kids"
        stat_key = "total_kids"
        avg_key = "kids"
    elif any(word in question_lower for word in [
        'cg', 'cgs', "cg's", 'connect group', 'connect groups', 'small group', 'small groups', 'group', 'groups', 'life group', 'life groups', 'community group', 'community groups']):
        stat_type = "connect_groups"
        stat_name = "connect groups"
        stat_key = "total_connect_groups"
        avg_key = "connect_groups"
    elif any(word in question_lower for word in [
        'dt', 'dream team', 'team', 'teams', 'volunteer', 'volunteers', 'serve team', 'serving team', 'helper', 'helpers', 'roster', 'rostered']):
        stat_type = "dream_team"
        stat_name = "dream team"
        stat_key = "volunteers"
        avg_key = "volunteers"
    else:
        # Default to attendance
        stat_type = "attendance"
        stat_name = "attendance"
        stat_key = "total_attendance"
        avg_key = "attendance"
    
    # Get the values for the specific stat
    start_year_value = start_year_stats[stat_key]
    end_year_value = end_year_stats[stat_key]
    start_year_avg = start_year_stats["averages"][avg_key]
    end_year_avg = end_year_stats["averages"][avg_key]
    
    # Calculate percentage change based on what user wants
    if use_total:
        base_value = start_year_value
        compare_value = end_year_value
        if base_value == 0:
            percentage_change = 0
        else:
            percentage_change = ((compare_value - base_value) / base_value) * 100
    else:  # use_average
        base_value = start_year_avg
        compare_value = end_year_avg
        if base_value == 0:
            percentage_change = 0
        else:
            percentage_change = ((compare_value - base_value) / base_value) * 100
    
    # Determine if it's an increase or decrease
    change_direction = "increase" if percentage_change > 0 else "decrease"
    if percentage_change == 0:
        change_direction = "no change"
    
    # Generate conversational response based on stat type and total vs average
    if stat_type == "attendance":
        if use_total:
            response_text = f"{display_campus_name(campus)} campus had a total of {start_year_value} people in {start_year}, and a total of {end_year_value} people in {end_year}. This represents a {change_direction} of {abs(round(percentage_change))}% in total attendance from {start_year} to {end_year}."
        else:
            response_text = f"{display_campus_name(campus)} campus had an average of {round(start_year_avg)} people per week in {start_year}, and an average of {round(end_year_avg)} people per week in {end_year}. This represents a {change_direction} of {abs(round(percentage_change))}% in attendance from {start_year} to {end_year}."
    elif stat_type == "new_people":
        if use_total:
            response_text = f"{display_campus_name(campus)} campus had a total of {start_year_value} new visitors in {start_year}, and a total of {end_year_value} new visitors in {end_year}. This represents a {change_direction} of {abs(round(percentage_change))}% in total new visitors from {start_year} to {end_year}."
        else:
            response_text = f"{display_campus_name(campus)} campus had an average of {round(start_year_avg)} new visitors per week in {start_year}, and an average of {round(end_year_avg)} new visitors per week in {end_year}. This represents a {change_direction} of {abs(round(percentage_change))}% in new visitors from {start_year} to {end_year}."
    elif stat_type == "new_christians":
        if use_total:
            response_text = f"{display_campus_name(campus)} campus had a total of {start_year_value} salvations in {start_year}, and a total of {end_year_value} salvations in {end_year}. This represents a {change_direction} of {abs(round(percentage_change))}% in total salvations from {start_year} to {end_year}."
        else:
            response_text = f"{display_campus_name(campus)} campus had an average of {round(start_year_avg)} salvations per week in {start_year}, and an average of {round(end_year_avg)} salvations per week in {end_year}. This represents a {change_direction} of {abs(round(percentage_change))}% in salvations from {start_year} to {end_year}."
    elif stat_type == "youth":
        if use_total:
            response_text = f"{display_campus_name(campus)} campus had a total of {start_year_value} youth in {start_year}, and a total of {end_year_value} youth in {end_year}. This represents a {change_direction} of {abs(round(percentage_change))}% in total youth attendance from {start_year} to {end_year}."
        else:
            response_text = f"{display_campus_name(campus)} campus had an average of {round(start_year_avg)} youth per week in {start_year}, and an average of {round(end_year_avg)} youth per week in {end_year}. This represents a {change_direction} of {abs(round(percentage_change))}% in youth attendance from {start_year} to {end_year}."
    elif stat_type == "kids":
        if use_total:
            response_text = f"{display_campus_name(campus)} campus had a total of {start_year_value} kids in {start_year}, and a total of {end_year_value} kids in {end_year}. This represents a {change_direction} of {abs(round(percentage_change))}% in total kids attendance from {start_year} to {end_year}."
        else:
            response_text = f"{display_campus_name(campus)} campus had an average of {round(start_year_avg)} kids per week in {start_year}, and an average of {round(end_year_avg)} kids per week in {end_year}. This represents a {change_direction} of {abs(round(percentage_change))}% in kids attendance from {start_year} to {end_year}."
    elif stat_type == "connect_groups":
        if use_total:
            response_text = f"{display_campus_name(campus)} campus had a total of {start_year_value} connect groups in {start_year}, and a total of {end_year_value} connect groups in {end_year}. This represents a {change_direction} of {abs(round(percentage_change))}% in total connect groups from {start_year} to {end_year}."
        else:
            response_text = f"{display_campus_name(campus)} campus had an average of {round(start_year_avg)} connect groups per week in {start_year}, and an average of {round(end_year_avg)} connect groups per week in {end_year}. This represents a {change_direction} of {abs(round(percentage_change))}% in connect groups from {start_year} to {end_year}."
    elif stat_type == "dream_team":
        if use_total:
            response_text = f"{display_campus_name(campus)} campus had a total of {start_year_value} volunteers in {start_year}, and a total of {end_year_value} volunteers in {end_year}. This represents a {change_direction} of {abs(round(percentage_change))}% in total volunteers from {start_year} to {end_year}."
        else:
            response_text = f"{display_campus_name(campus)} campus had an average of {round(start_year_avg)} volunteers per week in {start_year}, and an average of {round(end_year_avg)} volunteers per week in {end_year}. This represents a {change_direction} of {abs(round(percentage_change))}% in volunteers from {start_year} to {end_year}."
    
    # Format the response
    response_data = {
        "question": question,
        "campus": display_campus_name(campus),
        "date_range": f"{start_year} to {end_year}",
        "stat_type": stat_type,
        "analysis": {
            "total_entries": start_year_stats["total_entries"] + end_year_stats["total_entries"],
            "total_attendance": start_year_stats["total_attendance"] + end_year_stats["total_attendance"],
            "total_new_people": start_year_stats["total_new_people"] + end_year_stats["total_new_people"],
            "total_new_christians": start_year_stats["total_new_christians"] + end_year_stats["total_new_christians"],
            "total_youth": start_year_stats["total_youth"] + end_year_stats["total_youth"],
            "total_kids": start_year_stats["total_kids"] + end_year_stats["total_kids"],
            "total_connect_groups": start_year_stats["total_connect_groups"] + end_year_stats["total_connect_groups"],
            "averages": {
                "attendance": round(start_year_stats["averages"]["attendance"] + end_year_stats["averages"]["attendance"], 1),
                "new_people": round(start_year_stats["averages"]["new_people"] + end_year_stats["averages"]["new_people"], 1),
                "new_christians": round(start_year_stats["averages"]["new_christians"] + end_year_stats["averages"]["new_christians"], 1),
                "youth": round(start_year_stats["averages"]["youth"] + end_year_stats["averages"]["youth"], 1),
                "kids": round(start_year_stats["averages"]["kids"] + end_year_stats["averages"]["kids"], 1),
                "connect_groups": round(start_year_stats["averages"]["connect_groups"] + end_year_stats["averages"]["connect_groups"], 1)
            }
        },
        "answer": response_text
    }

    return response_data

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    if app.static_folder:
        return send_from_directory(app.static_folder, filename)
    return jsonify({"error": "Static folder not configured"}), 404

@app.route('/temp_audio/<path:filename>')
def serve_audio(filename):
    """Serve generated audio files"""
    return send_from_directory('temp_audio', filename)

@app.route('/query')
def serve_query():
    return render_template('query.html')

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "ok",
        "sheets_connected": sheet is not None,
        "claude_connected": claude is not None,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.route('/api/session')
def session_info():
    return jsonify({
        "user": "guest",
        "campus": "unknown",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.route('/api/stats')
def get_stats():
    if not sheet:
        return jsonify({"error": "Google Sheets not connected"}), 500
    try:
        campus_filter = request.args.get('campus', '').strip()
        rows = sheet.get_all_records()
        logger.info(f"Retrieved {len(rows)} total rows from Google Sheets")
        # Load any link-logged rows from memory (if you store them)
        # If you have a function to get link-logged rows, add them to rows here
        # rows += get_link_logged_rows()
        if not rows:
            logger.warning("No rows found in Google Sheets")
            return jsonify({"stats": [], "encouragements": []})
        # Filter by campus if specified
        if campus_filter:
            filtered_rows = []
            for row in rows:
                row_campus = str(row.get('Campus', '')).strip().lower()
                if row_campus == campus_filter.lower():
                    total_attendance = row.get('Total Attendance', '')
                    if total_attendance and str(total_attendance).strip():
                        filtered_rows.append(row)
            # Sort by timestamp (first column) for both dict and list/tuple rows
            def get_row_timestamp(row):
                import re
                from datetime import datetime
                ts = ''
                if isinstance(row, dict):
                    ts = row.get('Timestamp', '') or row.get('Date', '')
                elif isinstance(row, (list, tuple)):
                    ts = row[0] if len(row) > 0 else ''
                # Try to parse as datetime
                try:
                    # Accept both 'YYYY-MM-DD HH:MM:SS' and 'YYYY-MM-DD' formats
                    match = re.match(r'(\d{4}-\d{2}-\d{2})(?:[ T](\d{2}:\d{2}:\d{2}))?', ts)
                    if match:
                        date_part = match.group(1)
                        time_part = match.group(2) or '00:00:00'
                        return datetime.strptime(f'{date_part} {time_part}', '%Y-%m-%d %H:%M:%S')
                except Exception:
                    pass
                return datetime.min
            filtered_rows.sort(key=get_row_timestamp, reverse=True)
            most_recent = filtered_rows[0] if filtered_rows else {}
            stats_for_frontend = {
                'Total Attendance': most_recent.get('Total Attendance', 0) if isinstance(most_recent, dict) else 0,
                'total_attendance': most_recent.get('Total Attendance', 0) if isinstance(most_recent, dict) else 0,
                'New People': most_recent.get('New People', 0) if isinstance(most_recent, dict) else 0,
                'new_people': most_recent.get('New People', 0) if isinstance(most_recent, dict) else 0,
                'New Christians': most_recent.get('New Christians', 0) if isinstance(most_recent, dict) else 0,
                'new_christians': most_recent.get('New Christians', 0) if isinstance(most_recent, dict) else 0,
                'Youth Attendance': most_recent.get('Youth Attendance', 0) if isinstance(most_recent, dict) else 0,
                'youth_attendance': most_recent.get('Youth Attendance', 0) if isinstance(most_recent, dict) else 0,
                'Kids Total': most_recent.get('Kids Total', 0) if isinstance(most_recent, dict) else 0,
                'kids_total': most_recent.get('Kids Total', 0) if isinstance(most_recent, dict) else 0,
                'Connect Groups': most_recent.get('Connect Groups', 0) if isinstance(most_recent, dict) else 0,
                'connect_groups': most_recent.get('Connect Groups', 0) if isinstance(most_recent, dict) else 0
            }
            encouragements = []
            encouragement = most_recent.get("Encouragement", "") if isinstance(most_recent, dict) else ''
            if encouragement:
                if " | " in encouragement:
                    encouragements.extend(encouragement.split(" | "))
                else:
                    encouragements.append(encouragement)
            logger.info(f"Returning stats for {campus_filter}: {stats_for_frontend}")
            return jsonify({
                "stats": stats_for_frontend,
                "encouragements": encouragements
            })
        else:
            # No campus filter - return the 5 most recent rows overall
            def get_row_timestamp(row):
                import re
                from datetime import datetime
                ts = ''
                if isinstance(row, dict):
                    ts = row.get('Timestamp', '') or row.get('Date', '')
                elif isinstance(row, (list, tuple)):
                    ts = row[0] if len(row) > 0 else ''
                try:
                    match = re.match(r'(\d{4}-\d{2}-\d{2})(?:[ T](\d{2}:\d{2}:\d{2}))?', ts)
                    if match:
                        date_part = match.group(1)
                        time_part = match.group(2) or '00:00:00'
                        return datetime.strptime(f'{date_part} {time_part}', '%Y-%m-%d %H:%M:%S')
                except Exception:
                    pass
                return datetime.min
            valid_rows = [row for row in rows if (row.get('Total Attendance', '') if isinstance(row, dict) else False) and str(row.get('Total Attendance', '') if isinstance(row, dict) else '').strip()]
            valid_rows.sort(key=get_row_timestamp, reverse=True)
            recent_stats = valid_rows[:5] if valid_rows else []
            stats_for_frontend = []
            for row in recent_stats:
                stats_for_frontend.append({
                    'Total Attendance': row.get('Total Attendance', 0) if isinstance(row, dict) else 0,
                    'total_attendance': row.get('Total Attendance', 0) if isinstance(row, dict) else 0,
                    'New People': row.get('New People', 0) if isinstance(row, dict) else 0,
                    'new_people': row.get('New People', 0) if isinstance(row, dict) else 0,
                    'New Christians': row.get('New Christians', 0) if isinstance(row, dict) else 0,
                    'new_christians': row.get('New Christians', 0) if isinstance(row, dict) else 0,
                    'Youth Attendance': row.get('Youth Attendance', 0) if isinstance(row, dict) else 0,
                    'youth_attendance': row.get('Youth Attendance', 0) if isinstance(row, dict) else 0,
                    'Kids Total': row.get('Kids Total', 0) if isinstance(row, dict) else 0,
                    'kids_total': row.get('Kids Total', 0) if isinstance(row, dict) else 0,
                    'Connect Groups': row.get('Connect Groups', 0) if isinstance(row, dict) else 0,
                    'connect_groups': row.get('Connect Groups', 0) if isinstance(row, dict) else 0
                })
            encouragements = []
            for row in recent_stats:
                encouragement = row.get("Encouragement", "") if isinstance(row, dict) else ''
                if encouragement:
                    if " | " in encouragement:
                        encouragements.extend(encouragement.split(" | "))
                    else:
                        encouragements.append(encouragement)
            logger.info(f"Returning {len(recent_stats)} stats overall (no campus filter)")
            return jsonify({
                "stats": stats_for_frontend,
                "encouragements": encouragements
            })
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return jsonify({"error": "Failed to retrieve stats"}), 500

@app.route('/api/process_voice', methods=['POST'])
def process_voice():
    if not request.is_json:
        return jsonify({"error": "Expected JSON request"}), 400

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Missing or invalid JSON body"}), 400

    text = str(data.get("text", "")).strip()
    campus = str(data.get("campus", "")).strip()

    if not text:
        return jsonify({"error": "Missing text"}), 400

    # Always detect campus from text first, then fall back to provided campus
    detected_campus = detect_campus(text)
    if detected_campus:  # If we detected a specific campus
        campus = detected_campus
        logger.info(f"Detected campus from text: {campus}")
    elif campus and campus.lower() not in ['none', 'null', '']:
        logger.info(f"Using provided campus: {campus}")
    else:
        campus = None  # No campus detected - will prompt user
    
    logger.info(f"Final campus: {campus}")

    # Load conversation memory
    memory = load_conversation_memory()
    
    # Check if this is a query request vs stat logging
    text_lower = text.lower()
    is_query = any(word in text_lower for word in [
        'how many', 'what is', 'average', 'last week', 'this week', 'total', 'count', 'query', 'data', 'has had', 'had this year', 'had this month',
        'compare', 'comparison', 'vs', 'versus', 'between', 'year over year',
        'review', 'annual review', 'mid year review', 'mid-year review', 'report', 'summary', 'dashboard', 'snapshot', 'full report', 'overview', 'recap', 'stats summary', 'stat summary', 'stat report', 'stat overview', 'stat recap',
        'annual', 'mid year', 'mid-year', 'midyear'
    ])
    
    # Handle case where no campus is detected
    if campus is None or campus == "None" or campus == "null":
        # Return a response asking for campus selection with more helpful guidance
        return jsonify({
            "text": "I'd be happy to help you log stats! Which campus would you like to log stats for? You can say something like 'Salisbury campus', 'South campus', or just 'Salisbury' or 'South'.",
            "campus": None,
            "stats": {},
            "missing_stats": [],
            "suggestions": ["Try saying: 'Salisbury campus', 'South campus', 'Paradise campus', 'Adelaide City campus'"],
            "insights": ["Please select a campus first"]
        })
    
    # If this is a query, redirect to query endpoint
    if is_query:
        # Call the query endpoint internally
        query_data = {"question": text}
        query_response = query_data_internal(query_data)
        
        # Format response for frontend
        if "error" in query_response:
            response_text = query_response["error"]
        else:
            # Use the actual report text if available, otherwise fallback
            response_text = query_response.get("text", query_response.get("answer", "I couldn't find that information."))
        
        # Generate audio with ElevenLabs if available
        audio_url = None
        if elevenlabs_api_key:
            audio_url = generate_audio_with_elevenlabs(response_text)
        
        # Format response for frontend - preserve all query fields
        response = {
            "text": response_text,
            "campus": display_campus_name(campus),
            "stats": {},
            "missing_stats": [],
            "suggestions": [],
            "insights": [response_text],
            "audio_url": audio_url
        }
        
        # Preserve all query fields from query_response
        if "report" in query_response:
            response["report"] = query_response["report"]
        if "analysis" in query_response:
            response["analysis"] = query_response["analysis"]
        if "question" in query_response:
            response["question"] = query_response["question"]
        if "answer" in query_response:
            response["answer"] = query_response["answer"]
        
        return jsonify(response)
    
    # Extract stats with enhanced context
    result = extract_stats_with_context(text, campus)
    
    # Generate insights with memory
    insights = generate_encouragement_with_memory(text, campus, memory)
    
    # Detect missing stats
    missing_stats = detect_missing_stats(text, campus)
    
    # Update memory
    if campus not in memory:
        memory[campus] = []
    memory[campus].append(result)
    save_conversation_memory(memory)

    # Log to Google Sheet if available
    if sheet:
        try:
            now = datetime.now(timezone.utc)
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            date = now.strftime("%Y-%m-%d")
            
            # Create row in exact column order: A=Timestamp, B=Date, C=Campus, D=Total Attendance, E=New People, F=New Christians, G=Youth Attendance, H=New Youth, I=New Youth Christians, J=Kids Total, K=New Kids, L=Connect Groups, M=Encouragement
            row = [
                timestamp,  # A - Timestamp
                date,  # B - Date
                result.get("Campus", display_campus_name(campus)),  # C - Campus
                result.get("Total Attendance", ""),  # D - Total Attendance
                result.get("New People", ""),  # E - New People
                result.get("New Christians", ""),  # F - New Christians
                result.get("Youth Attendance", ""),  # G - Youth Attendance
                result.get("New Youth", ""),  # H - New Youth
                result.get("New Youth Christians", ""),  # I - New Youth Christians
                result.get("Kids Total", ""),  # J - Kids Total
                result.get("New Kids", ""),  # K - New Kids
                result.get("Connect Groups", ""),  # L - Connect Groups
                insights[0] if insights else ""  # M - Encouragement
            ]
            sheet.append_row(row)
        except Exception as e:
            logger.error(f"Failed to log to Google Sheets: {e}")

    # Always return campus and stats in a way the frontend expects
    # Convert result to frontend-expected format
    frontend_stats = {}
    for key, value in result.items():
        if key in ["Total Attendance", "New People", "New Christians", "Youth Attendance", "Kids Total", "Connect Groups", "Tithe Amount", "Volunteers"]:
            # Convert to frontend expected keys
            frontend_key = key.lower().replace(" ", "_")
            if value and str(value).strip():
                frontend_stats[frontend_key] = value
                logger.info(f"✅ Converting {key} -> {frontend_key} = {value}")
            else:
                logger.info(f"❌ Skipping {key} -> {frontend_key} (empty value: {value})")
        else:
            logger.info(f"⚠️ Skipping unknown key: {key}")
    
    # Debug logging
    logger.info(f"Extracted stats: {result}")
    logger.info(f"Frontend stats: {frontend_stats}")
    
    # Generate response text
    response_text = insights[0] if insights else "Thanks for logging those stats!"
    
    # Generate audio with ElevenLabs if available
    audio_url = None
    if elevenlabs_api_key:
        audio_url = generate_audio_with_elevenlabs(response_text)
    
    return jsonify({
        "text": response_text,
        "campus": display_campus_name(campus),
        "stats": frontend_stats,
        "missing_stats": missing_stats,
        "suggestions": missing_stats,
        "insights": insights,
        "audio_url": audio_url
    })

@app.route('/api/memory/<campus>')
def get_campus_memory(campus: str):
    """Get conversation memory for a specific campus"""
    memory = load_conversation_memory()
    campus_history = memory.get(campus, [])
    return jsonify({
        "campus": campus,
        "history": campus_history[-10:],  # Last 10 entries
        "total_entries": len(campus_history)
    })

@app.route('/api/campuses')
def get_campuses():
    """Get list of available campuses"""
    return jsonify({
        "campuses": list(campus_patterns.keys()),
        "default": "main"
    })

@app.route('/api/query', methods=['POST'])
def query_data():
    """Query historical data and answer questions about stats"""
    if not request.is_json:
        return jsonify({"error": "Expected JSON request"}), 400

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Missing or invalid JSON body"}), 400

    # Use the internal function that has review intent handling
    result = query_data_internal(data)
    
    # If there's an error, return it
    if "error" in result:
        return jsonify(result), 400
    
    # If there's a report, return it with the report structure
    if "report" in result:
        return jsonify(result)
    
    # Otherwise, return the normal response
    return jsonify(result)

@app.route('/api/bulk_review', methods=['POST'])
def bulk_review():
    """Parse multi-line review text and return a structured report of all detected stats"""
    if not request.is_json:
        return jsonify({"error": "Expected JSON request"}), 400
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Missing or invalid JSON body"}), 400
    text = str(data.get("text", "")).strip()
    if not text:
        return jsonify({"error": "Missing text"}), 400

    # Split text into lines and try to detect stat/campus/year for each block
    import re
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    campus = None
    # Try to detect campus from the header or any line
    for line in lines:
        detected = detect_campus(line)
        if detected:
            campus = detected
            break
    if not campus:
        campus = "main"  # fallback
    campus_normalized = normalize_campus(campus)

    # Define stat label to stat type mapping (expand as needed)
    stat_map = {
        'souls': 'new_christians',
        'attendance': 'attendance',
        'new people': 'new_people',
        'cg': 'connect_groups', 'cgs': 'connect_groups', 'connect groups': 'connect_groups',
        'dt': 'dream_team', 'dream team': 'dream_team', 'team': 'dream_team',
        'yth': 'youth', 'youth': 'youth',
        'kids': 'kids',
    }
    # For each stat block, look for lines like 'Total Souls:', 'Average Attendance:', etc.
    results = []
    for i, line in enumerate(lines):
        # Try to match stat label
        stat_label_match = re.match(r'(total|average)?\s*([a-zA-Z\u2019\'\s]+):', line, re.IGNORECASE)
        if stat_label_match:
            intent = stat_label_match.group(1) or ''
            stat_label = stat_label_match.group(2).strip().lower()
            # Map to stat type
            stat_type = None
            for key, value in stat_map.items():
                if key in stat_label:
                    stat_type = value
                    break
            if not stat_type:
                continue  # skip unknown stat
            # Look ahead for year lines (e.g., '2025 YTD:', '2024 YTD:')
            year_lines = []
            for j in range(i+1, min(i+5, len(lines))):
                year_match = re.match(r'(20\d{2})\s*(ytd)?', lines[j], re.IGNORECASE)
                if year_match:
                    year = int(year_match.group(1))
                    ytd = bool(year_match.group(2))
                    year_lines.append((year, ytd))
            # For each year, run the stat query
            for year, ytd in year_lines:
                # Use the same stat/campus/year detection logic as comparison
                # For YTD, use Jan 1 to now; else, use full year
                if ytd:
                    start_date = datetime(year, 1, 1)
                    end_date = datetime.now() if year == datetime.now().year else datetime(year, 12, 31)
                else:
                    start_date = datetime(year, 1, 1)
                    end_date = datetime(year, 12, 31)
                # Get rows data
                rows = []
                if sheet:
                    try:
                        rows = sheet.get_all_records()
                    except Exception as e:
                        logger.error(f"Failed to get stats from Google Sheets: {e}")
                        rows = []
                if not rows:
                    memory = load_conversation_memory()
                    # Try all possible normalizations for the campus key
                    session_stats = memory.get("session_stats", {})
                    campus_history = session_stats.get(campus, [])
                    if not campus_history:
                        campus_capitalized = campus.title()
                        campus_history = session_stats.get(campus_capitalized, [])
                    if not campus_history:
                        for k in session_stats:
                            if normalize_campus(k) == campus_normalized:
                                campus_history = session_stats[k]
                                break
                    if campus_history:
                        campus = campus_capitalized
                    rows = campus_history
                # Filter rows by date
                filtered_rows = []
                unique_campuses = set()
                for row in rows:
                    row_campus = normalize_campus(row.get("Campus") or row.get("campus") or "")
                    unique_campuses.add(row_campus)
                    if row_campus == campus_normalized or campus_normalized in row_campus:
                        timestamp_str = row.get("Timestamp", "")
                        if timestamp_str:
                            try:
                                if "T" in timestamp_str:
                                    row_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                else:
                                    row_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                                if start_date <= row_date <= end_date:
                                    filtered_rows.append(row)
                            except Exception:
                                filtered_rows.append(row)
                        else:
                            filtered_rows.append(row)
                print(f"[DEBUG] Unique campuses in data: {sorted(unique_campuses)}")
                # Calculate stat value
                total = 0
                avg = 0
                count = 0
                values = []
                for entry in filtered_rows:
                    def safe_int(val):
                        try:
                            return int(str(val).replace(",", "").strip()) if str(val).strip() else 0
                        except Exception:
                            return 0
                    if stat_type == "attendance":
                        val = safe_int(entry.get("Total Attendance") or entry.get("total_attendance"))
                    elif stat_type == "new_people":
                        val = safe_int(entry.get("New People") or entry.get("new_people"))
                    elif stat_type == "new_christians":
                        val = safe_int(entry.get("New Christians") or entry.get("new_christians"))
                    elif stat_type == "youth":
                        val = safe_int(entry.get("Youth Attendance") or entry.get("youth_attendance"))
                    elif stat_type == "kids":
                        val = safe_int(entry.get("Kids Total") or entry.get("kids_total"))
                    elif stat_type == "connect_groups":
                        val = safe_int(entry.get("Connect Groups") or entry.get("connect_groups"))
                    elif stat_type == "dream_team":
                        val = safe_int(entry.get("Volunteers") or entry.get("volunteers"))
                    else:
                        val = 0
                    print(f"[DEBUG] Stat: {stat_type}, Value: {val}, Entry: {entry}")
                    if val > 0:
                        values.append(val)
                        total += val
                        count += 1
                if count > 0:
                    avg = total / count
                results.append({
                    "stat": stat_type,
                    "intent": intent.strip().lower() or "total",
                    "year": year,
                    "ytd": ytd,
                    "campus": display_campus_name(campus),
                    "total": total,
                    "average": round(avg, 1),
                    "count": count
                })
    return jsonify({"results": results})

@app.route('/api/test')
def test_route():
    """Test route to verify Flask is working"""
    logger.info("Test route called")
    return jsonify({"message": "Test route working"})

# Update greeting_audio endpoint to use the correct filename
@app.route('/api/greeting_audio')
def greeting_audio():
    """Generate and serve the greeting audio using ElevenLabs, cache for reuse."""
    logger.info("Greeting audio endpoint called")
    greeting_text = "Connected to Futures Link, how can I help you today?"
    audio_filename = "temp_audio/greeting_elevenlabs.mp3"
    try:
        if not os.path.exists(audio_filename):
            logger.info("Greeting audio file does not exist, generating with ElevenLabs...")
            audio_url = generate_audio_with_elevenlabs(greeting_text, filename=audio_filename)
            if not audio_url or not os.path.exists(audio_filename):
                logger.error("Failed to generate greeting audio file with ElevenLabs.")
                return jsonify({"error": "Failed to generate greeting audio file."}), 500
            logger.info(f"Greeting audio file generated: {audio_filename}")
        else:
            logger.info(f"Greeting audio file already exists: {audio_filename}")
        logger.info(f"Serving greeting audio file: {audio_filename}")
        return send_from_directory('temp_audio', 'greeting_elevenlabs.mp3')
    except Exception as e:
        logger.error(f"Error in greeting_audio route: {e}")
        return jsonify({"error": str(e)}), 500

# Update demo_status to use the correct filename for greeting audio
@app.route('/api/demo_status')
def demo_status():
    """Check all services for demo readiness"""
    status = {
        "backend": "running",
        "claude": claude is not None,
        "elevenlabs": elevenlabs_api_key is not None,
        "google_sheets": sheet is not None,
        "greeting_audio": "ready",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    try:
        greeting_text = "Connected to Futures Link, how can I help you today?"
        audio_filename = "temp_audio/greeting_elevenlabs.mp3"
        if not os.path.exists(audio_filename):
            if elevenlabs_api_key:
                audio_url = generate_audio_with_elevenlabs(greeting_text, filename=audio_filename)
                status["greeting_audio"] = "generated" if audio_url else "failed"
            else:
                status["greeting_audio"] = "no_elevenlabs_key"
        else:
            status["greeting_audio"] = "cached"
    except Exception as e:
        status["greeting_audio"] = f"error: {str(e)}"
    return jsonify(status)

def normalize_campus(name):
    return str(name).strip().lower().replace("_", " ")

# Add this helper near the top of the file (after imports)
def display_campus_name(name):
    return str(name).replace('_', ' ').title()

if __name__ == '__main__':
    print("Starting app.py")
    print("App running on: http://localhost:5001")
    app.run(debug=False, port=5001)