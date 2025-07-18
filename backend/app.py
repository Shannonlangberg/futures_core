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

def safe_int(val: Any) -> int:
    """Safely convert a value to int, returning 0 on failure."""
    try:
        return int(str(val).replace(",", "").strip()) if str(val).strip() else 0
    except Exception:
        return 0

def get_row_timestamp(row: Any) -> datetime:
    """Extract and parse a timestamp from a row (dict or tuple). Returns datetime.min on failure."""
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
    """Detect campus from text with support for cross-campus queries"""
    text_lower = text.lower()
    
    # Check for cross-campus indicators first
    cross_campus_indicators = [
        'futures church', 'all campuses', 'all campus', 'every campus', 'across futures', 
        'church wide', 'churchwide', 'whole church', 'entire church', 'all locations',
        'across all', 'all sites', 'every site', 'church total', 'total church'
    ]
    
    for indicator in cross_campus_indicators:
        if indicator in text_lower:
            return "all_campuses"
    
    # Individual campus detection (existing logic)
    campus_keywords = {
        'south': ['south', 'south campus'],
        'paradise': ['paradise', 'paradise campus'],
        'salisbury': ['salisbury', 'salisbury campus'],
        'mount barker': ['mount barker', 'mount barker campus', 'mt barker', 'mt barker campus'],
        'adelaide city': ['adelaide city', 'adelaide city campus', 'city campus'],
        'victor harbour': ['victor harbour', 'victor harbour campus', 'victor harbor', 'victor harbor campus'],
        'clare valley': ['clare valley', 'clare valley campus'],
        'copper coast': ['copper coast', 'copper coast campus']
    }
    
    for campus, keywords in campus_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                return campus
    
    # If no specific campus is mentioned, default to all campuses for church-wide queries
    # Check if this looks like a church-wide stat query
    church_wide_indicators = [
        'how many', 'what is', "what's", 'give me', 'tell me', 'what was', 'how much',
        'total', 'average', 'church', 'this weekend', 'this week', 'this month', 'this year'
    ]
    
    has_church_wide_query = any(indicator in text_lower for indicator in church_wide_indicators)
    
    if has_church_wide_query:
        return "all_campuses"
    
    return None

def get_all_campuses_data(rows: list, start_date: datetime, end_date: datetime) -> list:
    """Get data from all campuses within the date range"""
    all_campus_data = []
    
    for row in rows:
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
                    all_campus_data.append(row)
            else:
                # If no timestamp, include the row (fallback)
                all_campus_data.append(row)
        except Exception as e:
            logger.warning(f"Could not parse timestamp for row: {e}")
            all_campus_data.append(row)
    
    return all_campus_data

def generate_cross_campus_insights(question: str, analysis_data: dict, filtered_rows: list) -> str:
    """Generate intelligent AI insights for cross-campus data"""
    if not claude:
        return "I'd be happy to analyze your church-wide data, but I need to connect to my AI assistant first."
    
    # Prepare data summary for Claude
    data_summary = f"""
Here's what I found for Futures Church ({analysis_data.get('date_range', 'recent data')}):

Church-wide numbers:
- {analysis_data.get('total_attendance', 0):,} total attendance
- {analysis_data.get('total_new_people', 0):,} new people
- {analysis_data.get('total_new_christians', 0):,} new christians
- {analysis_data.get('total_youth', 0):,} youth
- {analysis_data.get('total_kids', 0):,} kids
- {analysis_data.get('total_connect_groups', 0):,} connect groups

Weekly averages across all campuses:
- {analysis_data.get('averages', {}).get('attendance', 0):.1f} people per week
- {analysis_data.get('averages', {}).get('new_people', 0):.1f} new people per week
- {analysis_data.get('averages', {}).get('new_christians', 0):.1f} new christians per week
- {analysis_data.get('averages', {}).get('youth', 0):.1f} youth per week
- {analysis_data.get('averages', {}).get('kids', 0):.1f} kids per week
- {analysis_data.get('averages', {}).get('connect_groups', 0):.1f} connect groups per week
"""

    # Add recent data points for trend analysis
    if filtered_rows:
        recent_data = "Recent weeks across all campuses:\n"
        for i, row in enumerate(filtered_rows[-5:], 1):  # Last 5 entries
            if isinstance(row, dict):
                date = row.get('Date', row.get('Timestamp', 'Unknown'))
                campus = row.get('Campus', 'Unknown')
                attendance = row.get('Total Attendance', 0)
                new_people = row.get('New People', 0)
                new_christians = row.get('New Christians', 0)
                recent_data += f"{i}. {date} ({campus}): {attendance} people, {new_people} new, {new_christians} christians\n"
        data_summary += f"\n{recent_data}"

    # Create intelligent prompt for cross-campus analysis
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['trend', 'trends', 'pattern', 'growth', 'improve', 'attention', 'working']):
        prompt = f"""You're a friendly church growth expert. A leader from Futures Church is asking: "{question}"

{data_summary}

Give them warm, encouraging insights about their church-wide data. Focus on:
- What trends you see across all their campuses
- How the whole church is performing
- What areas are doing well or need attention across campuses
- Simple suggestions that could help the entire church

Be conversational and encouraging. Use their data to back up your insights. Keep it under 120 words and make it feel like a friendly conversation about their whole church."""
    
    elif any(word in question_lower for word in ['compare', 'vs', 'versus', 'against', 'difference']):
        prompt = f"""You're a helpful church data friend. A leader from Futures Church is asking: "{question}"

{data_summary}

Give them friendly analysis of their church-wide data. Focus on:
- How their overall numbers stack up
- What patterns you notice across campuses
- What the data tells us about their church-wide progress
- What might be influencing their results

Be encouraging and use their specific numbers. Keep it under 120 words and sound like you're chatting about their whole church."""
    
    else:
        prompt = f"""You're a helpful church assistant. A leader from Futures Church is asking: "{question}"

{data_summary}

Give them friendly, helpful insights about their church-wide data. Focus on:
- What they're really asking about
- What their church-wide data shows
- How this info can help their whole church
- What positive things you notice across all campuses

Be warm and specific. Use their data to give meaningful insights about Futures Church as a whole. Keep it under 120 words and sound conversational."""

    try:
        response = claude.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response.content[0].text.strip() if hasattr(response.content[0], 'text') else str(response.content[0])
        return response_text
        
    except Exception as e:
        logger.error(f"Claude API error in generate_cross_campus_insights: {e}")
        return f"I'd be happy to analyze your church-wide data for Futures Church, but I'm having trouble connecting to my AI assistant right now. The data shows {analysis_data.get('total_attendance', 0)} total attendance across all campuses with an average of {analysis_data.get('averages', {}).get('attendance', 0):.1f} people per week."

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
        'review', 'annual review', 'mid year review', 'mid-year review', 'report', 'summary', 'dashboard', 'snapshot', 'full report', 'overview', 'recap', 'stats summary', 'stat summary', 'stat report', 'stat overview', 'stat recap',
        'annual', 'mid year', 'mid-year', 'midyear'
    ]) or any(word in text_lower for word in ['20', 'q1', 'q2', 'q3', 'q4', 'quarter 1', 'quarter 2', 'quarter 3', 'quarter 4', 'first quarter', 'second quarter', 'third quarter', 'fourth quarter'])
    
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
    
    # No date range found - default to recent data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # Default to last 30 days
    return start_date, end_date, "recent data"

def detect_comparison_request(question: str) -> tuple:
    """Detect if this is a comparison request and extract years/periods to compare"""
    question_lower = question.lower()
    current_year = datetime.now().year
    import re
    
    # Look for comparison keywords - expanded list
    comparison_keywords = [
        'compare', 'comparison', 'vs', 'versus', 'against', 'side by side', 'year over year',
        'between', 'difference', 'compared to', 'compared with', 'relative to',
        'q1 vs', 'q2 vs', 'q3 vs', 'q4 vs', 'quarter 1 vs', 'quarter 2 vs', 'quarter 3 vs', 'quarter 4 vs',
        'first quarter vs', 'second quarter vs', 'third quarter vs', 'fourth quarter vs',
        'mid-year vs', 'mid year vs', 'midyear vs'
    ]
    is_comparison = any(keyword in question_lower for keyword in comparison_keywords)
    logger.info(f"[COMPARE DEBUG] Question: '{question}' -> Lower: '{question_lower}'")
    logger.info(f"[COMPARE DEBUG] Comparison keywords found: {[kw for kw in comparison_keywords if kw in question_lower]}")
    logger.info(f"[COMPARE DEBUG] Is comparison: {is_comparison}")
    if not is_comparison:
        return False, [], None, None
    
    # Detect mid-year comparison
    if 'mid-year' in question_lower or 'mid year' in question_lower or 'midyear' in question_lower:
        years = re.findall(r'\b(20\d{2})\b', question)
        if len(years) >= 2:
            return True, [int(years[0]), int(years[1])], 'mid_year', None
        elif len(years) == 1:
            y = int(years[0])
            return True, [y-1, y], 'mid_year', None
        else:
            return True, [current_year-1, current_year], 'mid_year', None

    # Detect quarterly comparison (Q1, Q2, Q3, Q4) - improved detection
    quarter = None
    quarter_patterns = [
        (r'\bq1\b', 1), (r'\bq2\b', 2), (r'\bq3\b', 3), (r'\bq4\b', 4),
        (r'\bquarter 1\b', 1), (r'\bquarter 2\b', 2), (r'\bquarter 3\b', 3), (r'\bquarter 4\b', 4),
        (r'\bfirst quarter\b', 1), (r'\bsecond quarter\b', 2), (r'\bthird quarter\b', 3), (r'\bfourth quarter\b', 4)
    ]
    
    for pattern, q in quarter_patterns:
        if re.search(pattern, question_lower):
            quarter = q
            break
    
    if quarter:
        years = re.findall(r'\b(20\d{2})\b', question)
        if len(years) >= 2:
            return True, [int(years[0]), int(years[1])], 'quarterly', quarter
        elif len(years) == 1:
            y = int(years[0])
            return True, [y-1, y], 'quarterly', quarter
        else:
            return True, [current_year-1, current_year], 'quarterly', quarter

    # Default: annual comparison
    years = re.findall(r'\b(20\d{2})\b', question)
    if len(years) >= 2:
        return True, [int(year) for year in years], 'annual', None
    elif len(years) == 1:
        y = int(years[0])
        return True, [y-1, y], 'annual', None
    else:
        return True, [current_year-1, current_year], 'annual', None

# Handler for mid-year and quarterly comparisons

def query_data_internal(data: Dict[str, Any]) -> Dict[str, Any]:
    """Internal function to query data (same logic as /api/query endpoint)"""
    question = str(data.get("question", "")).strip()
    if not question:
        return {"error": "Missing question"}

    # Lowercase for matching
    question_lower = question.lower()
    # If any weekend review phrase is present, handle campus-specific or cross-campus weekend review
    if any(phrase in question_lower for phrase in WEEKEND_REVIEW_PHRASES):
        campus = detect_campus(question)
        if campus and campus != "all_campuses":
            # Generate campus-specific weekend review (last 7 days)
            start_date = datetime.now() - timedelta(days=7)
            end_date = datetime.now()
            # Get rows from Google Sheets or memory
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
                rows = campus_history
            # Filter rows for campus and date range
            campus_normalized = normalize_campus(campus)
            filtered_rows = []
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
                            continue
            # Calculate stats (reuse your existing logic)
            analysis_data = calculate_stats_for_year_range(filtered_rows, campus, start_date.year)
            summary = (
                f"{display_campus_name(campus)} Weekend Review\n"
                f"Total Attendance: {analysis_data.get('total_attendance', 0):,}\n"
                f"New People: {analysis_data.get('total_new_people', 0):,}\n"
                f"New Christians: {analysis_data.get('total_new_christians', 0):,}\n"
                f"Youth: {analysis_data.get('total_youth', 0):,}\n"
                f"Kids: {analysis_data.get('total_kids', 0):,}\n"
                f"Connect Groups: {analysis_data.get('total_connect_groups', 0):,}"
            )
            # Build report array for modal table
            report = [
                {"label": "Total Attendance", "total": analysis_data.get("total_attendance", 0), "average": analysis_data.get("averages", {}).get("attendance", 0), "count": analysis_data.get("total_entries", 0), "year": start_date.year},
                {"label": "New People", "total": analysis_data.get("total_new_people", 0), "average": analysis_data.get("averages", {}).get("new_people", 0), "count": analysis_data.get("total_entries", 0), "year": start_date.year},
                {"label": "New Christians", "total": analysis_data.get("total_new_christians", 0), "average": analysis_data.get("averages", {}).get("new_christians", 0), "count": analysis_data.get("total_entries", 0), "year": start_date.year},
                {"label": "Youth", "total": analysis_data.get("total_youth", 0), "average": analysis_data.get("averages", {}).get("youth", 0), "count": analysis_data.get("total_entries", 0), "year": start_date.year},
                {"label": "Kids", "total": analysis_data.get("total_kids", 0), "average": analysis_data.get("averages", {}).get("kids", 0), "count": analysis_data.get("total_entries", 0), "year": start_date.year},
                {"label": "Connect Groups", "total": analysis_data.get("total_connect_groups", 0), "average": analysis_data.get("averages", {}).get("connect_groups", 0), "count": analysis_data.get("total_entries", 0), "year": start_date.year},
            ]
            return {
                "question": question,
                "campus": display_campus_name(campus),
                "date_range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "summary": summary,
                "stats": analysis_data,
                "report": report,
                "text": summary,
                "popup": True
            }
        else:
            # No campus detected, do cross-campus as before
            report = generate_cross_campus_report('weekly', "")
            stats = report.get('stats', {})
            summary = (
                f"Futures Church Weekend Review\n"
                f"Total Attendance: {stats.get('attendance', {}).get('total', 0):,}\n"
                f"Average Attendance: {stats.get('attendance', {}).get('average', 0):,.1f}\n"
                f"New People: {stats.get('new_people', {}).get('total', 0):,}\n"
                f"New Christians: {stats.get('new_christians', {}).get('total', 0):,}\n"
                f"Youth: {stats.get('youth', {}).get('total', 0):,}\n"
                f"Kids: {stats.get('kids', {}).get('total', 0):,}\n"
                f"Connect Groups: {stats.get('connect_groups', {}).get('total', 0):,}"
            )
            return {
                "question": question,
                "campus": "Futures Church (All Campuses)",
                "date_range": report.get('date_range', ''),
                "summary": summary,
                "stats": stats,
                "report": report,  # Add report property for frontend popup detection
                "text": summary,
                "popup": True
            }
    # ... rest of the function unchanged ...

def generate_ai_insights(question: str, campus: str, analysis_data: dict, filtered_rows: list) -> str:
    """Generate intelligent AI insights using Claude based on the data and question"""
    if not claude:
        return "I'd be happy to analyze your data, but I need to connect to my AI assistant first."
    
    # Prepare data summary for Claude
    data_summary = f"""
Here's what I found for {display_campus_name(campus)} campus ({analysis_data.get('date_range', 'recent data')}):

Their numbers:
- {analysis_data.get('total_attendance', 0):,} total attendance
- {analysis_data.get('total_new_people', 0):,} new people
- {analysis_data.get('total_new_christians', 0):,} new christians
- {analysis_data.get('total_youth', 0):,} youth
- {analysis_data.get('total_kids', 0):,} kids
- {analysis_data.get('total_connect_groups', 0):,} connect groups

Weekly averages:
- {analysis_data.get('averages', {}).get('attendance', 0):.1f} people per week
- {analysis_data.get('averages', {}).get('new_people', 0):.1f} new people per week
- {analysis_data.get('averages', {}).get('new_christians', 0):.1f} new christians per week
- {analysis_data.get('averages', {}).get('youth', 0):.1f} youth per week
- {analysis_data.get('averages', {}).get('kids', 0):.1f} kids per week
- {analysis_data.get('averages', {}).get('connect_groups', 0):.1f} connect groups per week
"""

    # Add recent data points for trend analysis
    if filtered_rows:
        recent_data = "Recent weeks:\n"
        for i, row in enumerate(filtered_rows[-5:], 1):  # Last 5 entries
            if isinstance(row, dict):
                date = row.get('Date', row.get('Timestamp', 'Unknown'))
                attendance = row.get('Total Attendance', 0)
                new_people = row.get('New People', 0)
                new_christians = row.get('New Christians', 0)
                recent_data += f"{i}. {date}: {attendance} people, {new_people} new, {new_christians} christians\n"
        data_summary += f"\n{recent_data}"

    # Create intelligent prompt based on question type
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['trend', 'trends', 'pattern', 'growth', 'improve', 'attention', 'working']):
        prompt = f"""You're a friendly church growth expert. A leader from {display_campus_name(campus)} campus is asking: "{question}"

{data_summary}

Give them warm, encouraging insights about their data. Focus on:
- What trends you see in their numbers
- How their campus is performing overall
- What areas are doing well or need attention
- Simple suggestions that could help

Be conversational and encouraging. Use their data to back up your insights. Keep it under 120 words and make it feel like a friendly conversation."""
    
    elif any(word in question_lower for word in ['compare', 'vs', 'versus', 'against', 'difference']):
        prompt = f"""You're a helpful church data friend. A leader from {display_campus_name(campus)} campus is asking: "{question}"

{data_summary}

Give them friendly analysis of their data. Focus on:
- How their numbers stack up
- What patterns you notice
- What the data tells us about their progress
- What might be influencing their results

Be encouraging and use their specific numbers. Keep it under 120 words and sound like you're chatting with a friend."""
    
    elif any(word in question_lower for word in ['how', 'what', 'why', 'analysis', 'insight']):
        prompt = f"""You're a helpful church assistant. A leader from {display_campus_name(campus)} campus is asking: "{question}"

{data_summary}

Give them friendly, helpful insights. Focus on:
- What they're really asking about
- What their data shows
- How this info can help them
- What positive things you notice

Be warm and specific. Use their data to give meaningful insights. Keep it under 120 words and sound conversational."""
    
    else:
        prompt = f"""You're a helpful church assistant. A leader from {display_campus_name(campus)} campus is asking: "{question}"

{data_summary}

Give them friendly, helpful insights. Focus on:
- What they're really asking about
- What their data shows
- How this info can help them
- What positive things you notice

Be warm and specific. Use their data to give meaningful insights. Keep it under 120 words and sound conversational."""

    try:
        response = claude.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response.content[0].text.strip() if hasattr(response.content[0], 'text') else str(response.content[0])
        return response_text
        
    except Exception as e:
        logger.error(f"Claude API error in generate_ai_insights: {e}")
        return f"I'd be happy to analyze your data for {display_campus_name(campus)} campus, but I'm having trouble connecting to my AI assistant right now. The data shows {analysis_data.get('total_attendance', 0)} total attendance with an average of {analysis_data.get('averages', {}).get('attendance', 0):.1f} people per week."

def detect_review_type(question: str) -> tuple:
    """Detect the type of review requested and extract relevant parameters"""
    import re
    q = question.lower()
    
    # Quarterly review detection (Q1, Q2, Q3, Q4)
    quarterly_patterns = [
        r'\bq1\b', r'\bq2\b', r'\bq3\b', r'\bq4\b',
        r'\bquarter 1\b', r'\bquarter 2\b', r'\bquarter 3\b', r'\bquarter 4\b',
        r'\bfirst quarter\b', r'\bsecond quarter\b', r'\bthird quarter\b', r'\bfourth quarter\b',
        r'\bq1 review\b', r'\bq2 review\b', r'\bq3 review\b', r'\bq4 review\b',
        r'\bquarterly review\b', r'\bquarter review\b'
    ]
    
    for pattern in quarterly_patterns:
        if re.search(pattern, q):
            # Extract quarter number
            if 'q1' in q or 'quarter 1' in q or 'first quarter' in q:
                quarter = 1
            elif 'q2' in q or 'quarter 2' in q or 'second quarter' in q:
                quarter = 2
            elif 'q3' in q or 'quarter 3' in q or 'third quarter' in q:
                quarter = 3
            elif 'q4' in q or 'quarter 4' in q or 'fourth quarter' in q:
                quarter = 4
            else:
                quarter = 1  # Default to Q1
            
            # Extract year
            import re
            years = re.findall(r'\b(20\d{2})\b', question)
            year = int(years[0]) if years else datetime.now().year
            
            return "quarterly", quarter, year
    
    # Mid-year review detection
    mid_year_patterns = [
        r'\bmid.?year\b', r'\bmidyear\b', r'\bmid.?year review\b', r'\bmidyear review\b',
        r'\bmid.?year report\b', r'\bmidyear report\b', r'\bmid.?year summary\b', r'\bmidyear summary\b',
        r'\bmid.?year stats\b', r'\bmidyear stats\b', r'\bmid.?year statistics\b', r'\bmidyear statistics\b',
        r'\bmid.?year numbers\b', r'\bmidyear numbers\b', r'\bmid.?year data\b', r'\bmidyear data\b',
        r'\bmid.?year recap\b', r'\bmidyear recap\b', r'\bmid.?year overview\b', r'\bmidyear overview\b',
        r'\bmid.?year dashboard\b', r'\bmidyear dashboard\b', r'\bmid.?year snapshot\b', r'\bmidyear snapshot\b',
        r'\bmid.?year full report\b', r'\bmidyear full report\b', r'\bmid.?year full review\b', r'\bmidyear full review\b',
        r'\bmid.?year full summary\b', r'\bmidyear full summary\b', r'\bmid.?year stat report\b', r'\bmidyear stat report\b',
        r'\bmid.?year stat summary\b', r'\bmidyear stat summary\b', r'\bmid.?year stat overview\b', r'\bmidyear stat overview\b',
        r'\bmid.?year stat recap\b', r'\bmidyear stat recap\b', r'\bmid.?year stats summary\b', r'\bmidyear stats summary\b',
        r'\bmid.?year stats overview\b', r'\bmidyear stats overview\b', r'\bmid.?year stats recap\b', r'\bmidyear stats recap\b'
    ]
    
    for pattern in mid_year_patterns:
        if re.search(pattern, q):
            # Extract year
            import re
            years = re.findall(r'\b(20\d{2})\b', question)
            year = int(years[0]) if years else datetime.now().year
            
            return "mid_year", None, year
    
    # Annual review detection (default)
    annual_patterns = [
        'review', 'annual review', 'anual review', 'report', 'summary', 'dashboard', 'snapshot', 'full report', 'overview', 'recap',
        'stats summary', 'stat summary', 'stat report', 'stat overview', 'stat recap',
        'year in review', 'yearly review', 'yearly report', 'year-end review', 'end of year report', 'end of year review',
        'give me a review', 'give me an annual review', 'can i get a review', 'can i get an annual review', 'show me a review', 'show me an annual review',
        'show me the annual report', 'show me the report', 'show me the summary', 'show me the dashboard', 'show me the stats summary',
        'generate a report', 'generate an annual report', 'generate a summary', 'generate an annual summary',
        'full stats', 'all stats', 'all statistics', 'all numbers', 'all data', 'all metrics',
        'recap of the year', 'recap for the year', 'recap', 'stat recap', 'stats recap',
        'big picture', 'big picture stats', 'big picture summary', 'big picture report',
        'comprehensive report', 'comprehensive review', 'comprehensive summary',
        'church report', 'church review', 'church summary',
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
        'give me an anual data', 'can i get an anual data', 'show me an anual data'
    ]
    
    for pattern in annual_patterns:
        if pattern in q:
            # Extract year
            import re
            years = re.findall(r'\b(20\d{2})\b', question)
            year = int(years[0]) if years else datetime.now().year
            
            return "annual", None, year
    
    return None, None, None

def is_review_intent(question: str) -> bool:
    """Check if the question is asking for a review (but not a comparison)"""
    # First check if this is a comparison request - if so, it's not a review intent
    is_comparison, _, _, _ = detect_comparison_request(question)
    if is_comparison:
        return False
    
    # Then check for review intent
    review_type, _, _ = detect_review_type(question)
    return review_type is not None

def generate_quarterly_report(campus: str, year: int, quarter: int) -> dict:
    """Generate a quarterly report for a specific quarter and year"""
    # Define quarter date ranges
    quarter_ranges = {
        1: (datetime(year, 1, 1), datetime(year, 3, 31)),
        2: (datetime(year, 4, 1), datetime(year, 6, 30)),
        3: (datetime(year, 7, 1), datetime(year, 9, 30)),
        4: (datetime(year, 10, 1), datetime(year, 12, 31))
    }
    
    start_date, end_date = quarter_ranges[quarter]
    
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
        campus_history = memory.get("session_stats", {}).get(campus, [])
        if not campus_history:
            campus_capitalized = campus.title()
            campus_history = memory.get("session_stats", {}).get(campus_capitalized, [])
            if campus_history:
                campus = campus_capitalized
        rows = campus_history
    
    # Filter rows by campus and date range
    filtered_rows = []
    campus_normalized = normalize_campus(campus)
    
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
                    continue
    
    # Calculate stats for the quarter
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
        if isinstance(entry, dict):
            def safe_int_stat(val):
                try:
                    if val is None or val == '':
                        return 0
                    return int(str(val).replace(',', '').strip())
                except Exception:
                    return 0
            attendance_val = safe_int_stat(entry.get('Total Attendance'))
            new_people_val = safe_int_stat(entry.get('New People'))
            new_christians_val = safe_int_stat(entry.get('New Christians'))
            youth_val = safe_int_stat(entry.get('Youth Attendance'))
            kids_val = safe_int_stat(entry.get('Kids Total'))
            connect_groups_val = safe_int_stat(entry.get('Connect Groups'))
            
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
    
    # Create results in the same format as annual report
    results = []
    stat_types = [
        ('attendance', 'Total Attendance', 'attendance'),
        ('new_people', 'New People', 'new_people'),
        ('new_christians', 'New Christians', 'new_christians'),
        ('youth', 'Youth Attendance', 'youth'),
        ('kids', 'Kids Total', 'kids'),
        ('connect_groups', 'Connect Groups', 'connect_groups'),
    ]
    
    for stat_type, stat_label, avg_key in stat_types:
        if stat_type == 'attendance':
            total = total_attendance
            avg = avg_attendance
        elif stat_type == 'new_people':
            total = total_new_people
            avg = avg_new_people
        elif stat_type == 'new_christians':
            total = total_new_christians
            avg = avg_new_christians
        elif stat_type == 'youth':
            total = total_youth
            avg = avg_youth
        elif stat_type == 'kids':
            total = total_kids
            avg = avg_kids
        elif stat_type == 'connect_groups':
            total = total_connect_groups
            avg = avg_connect_groups
        else:
            total = 0
            avg = 0
        
        results.append({
            "stat": stat_type,
            "label": stat_label,
            "year": year,
            "quarter": quarter,
            "campus": display_campus_name(campus),
            "total": total,
            "average": round(avg, 1),
            "count": entry_count
        })
    
    # Generate spoken summary
    quarter_names = {1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4"}
    spoken_summary = f"Here's your {quarter_names[quarter]} {year} report for {display_campus_name(campus)} campus."
    
    return {
        "report": results,
        "text": spoken_summary,
        "review_type": "quarterly",
        "quarter": quarter,
        "year": year
    }

def generate_mid_year_report(campus: str, year: int) -> dict:
    """Generate a mid-year report (January to June)"""
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 6, 30)
    
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
        campus_history = memory.get("session_stats", {}).get(campus, [])
        if not campus_history:
            campus_capitalized = campus.title()
            campus_history = memory.get("session_stats", {}).get(campus_capitalized, [])
            if campus_history:
                campus = campus_capitalized
        rows = campus_history
    
    # Filter rows by campus and date range
    filtered_rows = []
    campus_normalized = normalize_campus(campus)
    
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
                    continue
    
    # Calculate stats for the mid-year period
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
        if isinstance(entry, dict):
            def safe_int_stat(val):
                try:
                    if val is None or val == '':
                        return 0
                    return int(str(val).replace(',', '').strip())
                except Exception:
                    return 0
            attendance_val = safe_int_stat(entry.get('Total Attendance'))
            new_people_val = safe_int_stat(entry.get('New People'))
            new_christians_val = safe_int_stat(entry.get('New Christians'))
            youth_val = safe_int_stat(entry.get('Youth Attendance'))
            kids_val = safe_int_stat(entry.get('Kids Total'))
            connect_groups_val = safe_int_stat(entry.get('Connect Groups'))
            
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
    
    # Create results in the same format as annual report
    results = []
    stat_types = [
        ('attendance', 'Total Attendance', 'attendance'),
        ('new_people', 'New People', 'new_people'),
        ('new_christians', 'New Christians', 'new_christians'),
        ('youth', 'Youth Attendance', 'youth'),
        ('kids', 'Kids Total', 'kids'),
        ('connect_groups', 'Connect Groups', 'connect_groups'),
    ]
    
    for stat_type, stat_label, avg_key in stat_types:
        if stat_type == 'attendance':
            total = total_attendance
            avg = avg_attendance
        elif stat_type == 'new_people':
            total = total_new_people
            avg = avg_new_people
        elif stat_type == 'new_christians':
            total = total_new_christians
            avg = avg_new_christians
        elif stat_type == 'youth':
            total = total_youth
            avg = avg_youth
        elif stat_type == 'kids':
            total = total_kids
            avg = avg_kids
        elif stat_type == 'connect_groups':
            total = total_connect_groups
            avg = avg_connect_groups
        else:
            total = 0
            avg = 0
        
        results.append({
            "stat": stat_type,
            "label": stat_label,
            "year": year,
            "period": "mid_year",
            "campus": display_campus_name(campus),
            "total": total,
            "average": round(avg, 1),
            "count": entry_count
        })
    
    # Generate spoken summary
    spoken_summary = f"Here's your mid-year {year} report for {display_campus_name(campus)} campus."
    
    return {
        "report": results,
        "text": spoken_summary,
        "review_type": "mid_year",
        "year": year
    }

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
        year_stats = calculate_stats_for_year_range(rows, campus, year)
        for stat_type, stat_label, avg_key in stat_types:
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

def detect_specific_stat_in_comparison(question: str) -> Optional[str]:
    """Detect which specific stat is being compared in the question"""
    question_lower = question.lower()
    
    # Map of stat keywords to stat types
    stat_keywords = {
        'attendance': ['attendance', 'total attendance', 'total', 'people'],
        'new_people': ['new people', 'newpeople', 'np', 'new', 'visitors'],
        'new_christians': ['new christians', 'christians', 'souls', 'salvations', 'conversions'],
        'youth': ['youth', 'youth attendance', 'teens', 'teenagers'],
        'kids': ['kids', 'children', 'kids total', 'children total'],
        'connect_groups': ['connect groups', 'connectgroups', 'groups', 'small groups', 'cell groups'],
        'dream_team': ['volunteers', 'dream team', 'serving', 'team']
    }
    
    # Check for specific stat mentions
    for stat_type, keywords in stat_keywords.items():
        for keyword in keywords:
            if keyword in question_lower:
                logger.info(f"[COMPARE] Detected specific stat: {stat_type} (keyword: {keyword})")
                return stat_type
    
    # If no specific stat detected, return None (will show all stats)
    logger.info(f"[COMPARE] No specific stat detected, will show all stats")
    return None

def handle_period_comparison_request(question: str, campus: str, years: list, period_type: str, period_value: Optional[int] = None) -> dict:
    logger.info(f"[COMPARE] handle_period_comparison_request called with: question={question}, campus={campus}, years={years}, period_type={period_type}, period_value={period_value}")
    # period_type: 'mid_year' or 'quarterly'
    # period_value: quarter number if quarterly, None if mid_year
    
    # Detect which specific stat is being compared
    specific_stat = detect_specific_stat_in_comparison(question)
    logger.info(f"[COMPARE] Specific stat detected: {specific_stat}")
    
    try:
        reports = []
        for year in years:
            if period_type == 'mid_year':
                report = generate_mid_year_report(campus, year)
            elif period_type == 'quarterly' and period_value:
                report = generate_quarterly_report(campus, year, period_value)
            else:
                report = generate_full_stat_report(campus, [year])
            reports.append(report)
        
        logger.info(f"[COMPARE] Generated {len(reports)} reports")
        
        # Compose comparison summary
        if specific_stat:
            stat_labels = {
                'attendance': 'Attendance',
                'new_people': 'New People', 
                'new_christians': 'New Christians',
                'youth': 'Youth',
                'kids': 'Kids',
                'connect_groups': 'Connect Groups',
                'dream_team': 'Volunteers'
            }
            stat_name = stat_labels.get(specific_stat, specific_stat)
            summary = f"Comparison of {stat_name} for {years[0]} and {years[1]} at {display_campus_name(campus)} campus."
        else:
            summary = f"Comparison of {period_type.replace('_',' ')} "
            if period_type == 'quarterly' and period_value:
                summary += f"Q{period_value} "
            summary += f"for {years[0]} and {years[1]} at {display_campus_name(campus)} campus."

        # PATCH: Ensure both reports have all stat keys
        stat_keys = ['attendance', 'new_people', 'new_christians', 'youth', 'kids', 'connect_groups']
        stat_labels = {
            'attendance': 'Attendance',
            'new_people': 'New People',
            'new_christians': 'New Christians',
            'youth': 'Youth',
            'kids': 'Kids',
            'connect_groups': 'Connect Groups'
        }
        
        def fill_missing_stats(report, year):
            stats_dict = {stat['stat']: stat for stat in report.get('report', [])}
            filled = []
            
            # If specific stat requested, only include that stat
            if specific_stat:
                stat = stats_dict.get(specific_stat, {
                    'stat': specific_stat,
                    'label': stat_labels.get(specific_stat, specific_stat.title()),
                    'year': year,
                    'total': 0,
                    'average': 0,
                    'count': 0,
                    'campus': campus,
                    'quarter': period_value if period_type == 'quarterly' else None
                })
                filled.append(stat)
            else:
                # Include all stats
                for key in stat_keys:
                    stat = stats_dict.get(key, {
                        'stat': key,
                        'label': stat_labels[key],
                        'year': year,
                        'total': 0,
                        'average': 0,
                        'count': 0,
                        'campus': campus,
                        'quarter': period_value if period_type == 'quarterly' else None
                    })
                    filled.append(stat)
            return filled
        
        # Fill missing stats for both reports
        for i, year in enumerate(years):
            reports[i]['report'] = fill_missing_stats(reports[i], year)
        
        # Calculate percent changes
        percent_changes = {}
        if specific_stat:
            # Only calculate for the specific stat
            if len(reports[0]['report']) > 0 and len(reports[1]['report']) > 0:
                v1 = reports[0]['report'][0]['total']
                v2 = reports[1]['report'][0]['total']
                if v1 == 0 and v2 == 0:
                    pct = 0.0
                elif v1 == 0:
                    pct = 100.0
                else:
                    pct = ((v2 - v1) / abs(v1)) * 100.0
                percent_changes[specific_stat] = pct
        else:
            # Calculate for all stats
            for idx, key in enumerate(stat_keys):
                if idx < len(reports[0]['report']) and idx < len(reports[1]['report']):
                    v1 = reports[0]['report'][idx]['total']
                    v2 = reports[1]['report'][idx]['total']
                    if v1 == 0 and v2 == 0:
                        pct = 0.0
                    elif v1 == 0:
                        pct = 100.0
                    else:
                        pct = ((v2 - v1) / abs(v1)) * 100.0
                    percent_changes[key] = pct
        
        logger.info(f"[COMPARE] Calculated percent changes: {percent_changes}")
        
        # Compose and return the full comparison object
        result = {
            'comparison': True,
            'reports': reports,
            'percent_changes': percent_changes,
            'text': summary,
            'campus': campus,
            'insights': [summary],
            'years': years,
            'period_type': period_type,
            'period_value': period_value,
            'specific_stat': specific_stat
        }
        
        logger.info(f"[COMPARE] Returning comparison result with keys: {list(result.keys())}")
        logger.info(f"[COMPARE] Reports length: {len(result['reports'])}")
        logger.info(f"[COMPARE] Percent changes keys: {list(result['percent_changes'].keys())}")
        
        return result
        
    except Exception as e:
        logger.error(f"[COMPARE] Error in handle_period_comparison_request: {e}")
        # Return a fallback response
        return {
            'comparison': True,
            'reports': [],
            'percent_changes': {},
            'text': f"Error generating comparison for {campus} campus",
            'campus': campus,
            'insights': [f"Could not generate comparison: {str(e)}"],
            'years': years,
            'period_type': period_type,
            'period_value': period_value,
            'specific_stat': specific_stat
        }

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
        if isinstance(entry, dict):
            def safe_int_stat(val):
                try:
                    if val is None or val == '':
                        return 0
                    return int(str(val).replace(',', '').strip())
                except Exception:
                    return 0
            attendance_val = safe_int_stat(entry.get('Total Attendance'))
            new_people_val = safe_int_stat(entry.get('New People'))
            new_christians_val = safe_int_stat(entry.get('New Christians'))
            youth_val = safe_int_stat(entry.get('Youth Attendance'))
            kids_val = safe_int_stat(entry.get('Kids Total'))
            connect_groups_val = safe_int_stat(entry.get('Connect Groups'))
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
            # Helper for sorting rows by timestamp (available to both branches)
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
            filtered_rows = []
            for row in rows:
                row_campus = str(row.get('Campus', '')).strip().lower()
                if row_campus == campus_filter.lower():
                    total_attendance = row.get('Total Attendance', '')
                    if total_attendance and str(total_attendance).strip():
                        filtered_rows.append(row)
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

# Add a decorator to log endpoint and request data
from functools import wraps

def log_endpoint(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            data = request.get_json(silent=True)
        except Exception:
            data = None
        logger.info(f"[API LOG] Endpoint: {request.path} | Method: {request.method} | Data: {data}")
        return f(*args, **kwargs)
    return decorated_function

# Apply the decorator to all API endpoints
@app.route('/api/process_voice', methods=['POST'])
@log_endpoint
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
    import re
    
    # First, check if this looks like stat logging (contains numbers followed by stat types)
    stat_logging_patterns = [
        r'\d+\s+(?:people|attendance|total|had|got|there were)',
        r'\d+\s+(?:new(?:\s+people|visitors?|guests?)?|np)',
        r'\d+\s+(?:salvations|new\s+christians|decisions|baptisms?|nc)',
        r'\d+\s+(?:youth(?:\s+group|\s+ministry)?|teens?|yout)',
        r'\d+\s+(?:kids|children|kids\s+ministry|nursery)',
        r'\d+\s+(?:connect\s+groups?|small\s+groups?|connects?|life\s+groups?)',
        r'\$?\d+(?:,\d{3})*(?:\.\d{2})?\s+(?:tithe|offering|giving|in\s+tithe)',
        r'\d+\s+(?:volunteers?|team\s+members?|servers?)'
    ]
    
    # Check if text contains stat logging patterns
    contains_stat_logging = any(re.search(pattern, text_lower) for pattern in stat_logging_patterns)
    
    # If it contains stat logging patterns, it's NOT a query
    if contains_stat_logging:
        is_query = False
    else:
        # Only check for query patterns if it doesn't look like stat logging
        contains_year = bool(re.search(r'\b20\d{2}\b', text_lower))
        contains_quarter = any(q in text_lower for q in ['q1', 'q2', 'q3', 'q4', 'quarter 1', 'quarter 2', 'quarter 3', 'quarter 4', 'first quarter', 'second quarter', 'third quarter', 'fourth quarter'])
        
        # More specific query keywords that are less likely to appear in stat logging
        query_keywords = [
            'how many', 'what is', 'average', 'last week', 'this week', 'count', 'query', 'data', 'has had', 'had this year', 'had this month',
            'compare', 'comparison', 'vs', 'versus', 'between', 'year over year',
            'review', 'annual review', 'mid year review', 'mid-year review', 'report', 'summary', 'dashboard', 'snapshot', 'full report', 'overview', 'recap', 'stats summary', 'stat summary', 'stat report', 'stat overview', 'stat recap',
            'annual', 'mid year', 'mid-year', 'midyear'
        ]
        
        # Check for query patterns only if they're at the beginning or in question format
        is_query = (
            any(word in text_lower for word in query_keywords) or 
            contains_year or 
            contains_quarter or
            text_lower.startswith('what') or
            text_lower.startswith('how') or
            text_lower.startswith('show') or
            text_lower.startswith('give') or
            text_lower.startswith('can you') or
            text_lower.startswith('could you')
        )
    
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
        # Preserve comparison fields
        if "comparison" in query_response:
            response["comparison"] = query_response["comparison"]
        if "reports" in query_response:
            response["reports"] = query_response["reports"]
        if "percent_changes" in query_response:
            response["percent_changes"] = query_response["percent_changes"]
        if "years" in query_response:
            response["years"] = query_response["years"]
        if "period_type" in query_response:
            response["period_type"] = query_response["period_type"]
        if "period_value" in query_response:
            response["period_value"] = query_response["period_value"]
        
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
@log_endpoint
def query():
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

def detect_simple_stat_query(question: str) -> Optional[tuple]:
    """Detect if this is a simple stat query that should get a direct answer"""
    question_lower = question.lower()
    
    # Simple stat keywords
    stat_keywords = {
        'attendance': ['attendance', 'total attendance', 'total', 'people', 'how many people'],
        'new_people': ['new people', 'newpeople', 'np', 'new', 'visitors', 'how many new people'],
        'new_christians': ['new christians', 'christians', 'souls', 'salvations', 'conversions', 'how many new christians'],
        'youth': ['youth attendance', 'youth', 'teens', 'teenagers', 'how many youth'],
        'kids': ['kids total', 'kids', 'children', 'children total', 'how many kids'],
        'connect_groups': ['connect groups', 'connectgroups', 'groups', 'small groups', 'cell groups', 'how many connect groups']
    }
    
    # Flatten and sort keywords by length (longest first)
    keyword_to_stat = []
    for stat_type, keywords in stat_keywords.items():
        for keyword in keywords:
            keyword_to_stat.append((keyword, stat_type))
    keyword_to_stat.sort(key=lambda x: -len(x[0]))
    
    # Simple question patterns that indicate direct stat requests
    simple_patterns = [
        r'how many\s+\w+',
        r'what is the\s+\w+',
        r'what\'s the\s+\w+',
        r'give me the\s+\w+',
        r'tell me the\s+\w+',
        r'what was the\s+\w+',
        r'how much\s+\w+',
        r'total\s+\w+',
        r'average\s+\w+',
        r'what was the average\s+\w+',
        r'what is the average\s+\w+',
        r"what's the average\s+\w+"
    ]
    
    import re
    
    # Check for simple patterns first (including average patterns)
    for pattern in simple_patterns:
        if re.search(pattern, question_lower):
            # Find which stat they're asking about (longest keyword first)
            for keyword, stat_type in keyword_to_stat:
                if keyword in question_lower:
                    return (stat_type, keyword)
    
    # Check for direct stat keywords without complex analysis words
    analysis_words = ['trend', 'trends', 'pattern', 'growth', 'improve', 'attention', 'working', 'compare', 'vs', 'versus', 'against', 'difference', 'analysis', 'insight', 'why', 'how are we', 'what areas', 'review', 'report']
    
    has_analysis_words = any(word in question_lower for word in analysis_words)
    
    if not has_analysis_words:
        # Check for simple stat requests (longest keyword first)
        for keyword, stat_type in keyword_to_stat:
            if keyword in question_lower:
                return (stat_type, keyword)
    
    return None

def generate_simple_stat_answer(stat_type: str, analysis_data: dict, campus: str, date_range: str) -> str:
    """Generate a simple, direct answer for stat queries"""
    stat_labels = {
        'attendance': 'attendance',
        'new_people': 'new people', 
        'new_christians': 'new christians',
        'youth': 'youth',
        'kids': 'kids',
        'connect_groups': 'connect groups'
    }
    
    stat_label = stat_labels.get(stat_type, stat_type)
    
    # Check if this is a cross-campus response
    is_cross_campus = campus.lower() in ['futures church', 'all campuses', 'church-wide']
    
    # Get the total for the requested stat
    stat_totals = {
        'attendance': analysis_data.get('total_attendance', 0),
        'new_people': analysis_data.get('total_new_people', 0),
        'new_christians': analysis_data.get('total_new_christians', 0),
        'youth': analysis_data.get('total_youth', 0),
        'kids': analysis_data.get('total_kids', 0),
        'connect_groups': analysis_data.get('total_connect_groups', 0)
    }
    
    # Get averages for cross-campus queries
    stat_averages = {
        'attendance': analysis_data.get('averages', {}).get('attendance', 0),
        'new_people': analysis_data.get('averages', {}).get('new_people', 0),
        'new_christians': analysis_data.get('averages', {}).get('new_christians', 0),
        'youth': analysis_data.get('averages', {}).get('youth', 0),
        'kids': analysis_data.get('averages', {}).get('kids', 0),
        'connect_groups': analysis_data.get('averages', {}).get('connect_groups', 0)
    }
    
    total = stat_totals.get(stat_type, 0)
    average = stat_averages.get(stat_type, 0)
    
    # Clean up date range - remove "None" if it's empty
    clean_date_range = date_range if date_range and date_range != "None" else ""
    
    if is_cross_campus:
        return f"Futures Church had {total:,} total {stat_label} across all campuses with an average of {average:.1f} per week{clean_date_range}."
    else:
        return f"{campus} had {total:,} total {stat_label}{clean_date_range}."



def detect_cross_campus_review(question: str) -> Optional[tuple]:
    """Detect if this is a cross-campus review request"""
    question_lower = question.lower()
    
    # Cross-campus review indicators
    cross_campus_indicators = [
        'all campuses', 'all campus', 'every campus', 'across all', 'all sites', 'every site',
        'church wide', 'churchwide', 'whole church', 'entire church', 'all locations',
        'futures church', 'across futures', 'church total', 'total church'
    ]
    
    has_cross_campus = any(indicator in question_lower for indicator in cross_campus_indicators)
    
    if not has_cross_campus:
        return None
    
    # Check for review types (order matters: most specific first)
    review_indicators = [
        ('weekly', [
            'this week', 'this weekend', 'weekend', 'sunday', 'this sunday', 'weekly',
            'weekend review', 'sunday review', 'weekend report', 'sunday report'
        ]),
        ('mid_year', ['mid year', 'mid-year', 'midyear', 'mid year review', 'mid-year review']),
        ('quarterly', ['quarter', 'q1', 'q2', 'q3', 'q4', 'first quarter', 'second quarter', 'third quarter', 'fourth quarter']),
        ('monthly', ['this month', 'month', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']),
        ('annual', ['annual', 'year', 'yearly', 'this year', '2024', '2025'])
    ]
    
    for review_type, keywords in review_indicators:
        if any(keyword in question_lower for keyword in keywords):
            return (review_type, question_lower)
    
    # Default to weekly if 'review' or 'report' is present and no period is specified
    if 'review' in question_lower or 'report' in question_lower:
        return ('weekly', question_lower)
    
    # Otherwise, default to annual
    return ('annual', question_lower)

def generate_cross_campus_report(review_type: str, date_range: str) -> dict:
    """Generate a comprehensive cross-campus report with robust filtering and debug output."""
    # Get data from all campuses
    if sheet:
        try:
            rows = sheet.get_all_records()
        except Exception as e:
            logger.error(f"Failed to get stats from Google Sheets: {e}")
            rows = []
    else:
        rows = []

    # Always use the current system date/time
    now = datetime.now()
    if review_type == 'weekly':
        start_date = now - timedelta(days=7)
        end_date = now
        period_label = f"for the last 7 days ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})"
    elif review_type == 'monthly':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
        period_label = f"for {now.strftime('%B %Y')}"
    elif review_type == 'quarterly':
        quarter = (now.month - 1) // 3 + 1
        start_month = 3 * (quarter - 1) + 1
        start_date = now.replace(month=start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        if quarter == 4:
            end_date = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
        else:
            end_date = now.replace(month=start_month + 2, day=28, hour=23, minute=59, second=59, microsecond=999999)  # Approximate
        period_label = f"for Q{quarter} {now.year}"
    elif review_type == 'mid_year':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now.replace(month=6, day=30, hour=23, minute=59, second=59, microsecond=999999)
        period_label = f"for Jan-Jun {now.year}"
    else:  # annual
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
        period_label = f"for {now.year}"

    print(f"[CROSS-CAMPUS DEBUG] start_date={start_date}, end_date={end_date}, now={now}")

    # Filter rows by date range and valid stats/campus
    filtered_rows = []
    debug_included = 0
    debug_excluded = 0
    for row in rows:
        try:
            timestamp_str = row.get("Timestamp", "")
            # Parse timestamp robustly
            row_date = None
            if timestamp_str:
                try:
                    if "T" in timestamp_str:
                        row_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    else:
                        try:
                            row_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                        except Exception:
                            row_date = datetime.strptime(timestamp_str, "%Y-%m-%d")
                except Exception as e:
                    logger.warning(f"Could not parse timestamp for row: {e}")
            if not row_date or not (start_date <= row_date <= end_date):
                debug_excluded += 1
                continue
            campus = row.get("Campus", "").strip()
            if not campus:
                debug_excluded += 1
                continue
            # At least one stat must be > 0
            stat_fields = ["Total Attendance", "New People", "New Christians", "Youth Attendance", "Kids Total", "Connect Groups"]
            has_stat = False
            for field in stat_fields:
                val = row.get(field, "")
                try:
                    if val and int(str(val).replace(",", "").strip()) > 0:
                        has_stat = True
                        break
                except Exception:
                    continue
            if not has_stat:
                debug_excluded += 1
                continue
            filtered_rows.append(row)
            debug_included += 1
        except Exception as e:
            logger.warning(f"Error processing row: {e}")
            debug_excluded += 1
    print(f"[CROSS-CAMPUS DEBUG] Included {debug_included} rows, Excluded {debug_excluded} rows for period {period_label}")

    if not filtered_rows:
        return {
            "type": f"Cross-Campus {review_type.title()} Report",
            "campus": "Futures Church (All Campuses)",
            "date_range": period_label,
            "summary": f"No valid stats found for any campus {period_label}.",
            "stats": {},
            "entry_count": 0
        }

    # Aggregate stats (unchanged)
    total_attendance = 0
    total_new_people = 0
    total_new_christians = 0
    total_youth = 0
    total_kids = 0
    total_connect_groups = 0
    entry_count = 0
    attendance_values = []
    new_people_values = []
    new_christians_values = []
    youth_values = []
    kids_values = []
    connect_groups_values = []
    for entry in filtered_rows:
        def safe_int_stat(val):
            try:
                if val is None or val == '':
                    return 0
                return int(str(val).replace(',', '').strip())
            except Exception:
                return 0
        attendance_val = safe_int_stat(entry.get('Total Attendance'))
        new_people_val = safe_int_stat(entry.get('New People'))
        new_christians_val = safe_int_stat(entry.get('New Christians'))
        youth_val = safe_int_stat(entry.get('Youth Attendance'))
        kids_val = safe_int_stat(entry.get('Kids Total'))
        connect_groups_val = safe_int_stat(entry.get('Connect Groups'))
        if any([attendance_val, new_people_val, new_christians_val, youth_val, kids_val, connect_groups_val]):
            entry_count += 1
        total_attendance += attendance_val
        total_new_people += new_people_val
        total_new_christians += new_christians_val
        total_youth += youth_val
        total_kids += kids_val
        total_connect_groups += connect_groups_val
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
    avg_attendance = sum(attendance_values) / len(attendance_values) if attendance_values else 0
    avg_new_people = sum(new_people_values) / len(new_people_values) if new_people_values else 0
    avg_new_christians = sum(new_christians_values) / len(new_christians_values) if new_christians_values else 0
    avg_youth = sum(youth_values) / len(youth_values) if youth_values else 0
    avg_kids = sum(kids_values) / len(kids_values) if kids_values else 0
    avg_connect_groups = sum(connect_groups_values) / len(connect_groups_values) if connect_groups_values else 0
    report = {
        "type": f"Cross-Campus {review_type.title()} Report",
        "campus": "Futures Church (All Campuses)",
        "date_range": period_label,
        "summary": f"Futures Church {review_type} report across all campuses {period_label}",
        "stats": {
            "attendance": {
                "total": total_attendance,
                "average": round(avg_attendance, 1),
                "label": "Total Attendance"
            },
            "new_people": {
                "total": total_new_people,
                "average": round(avg_new_people, 1),
                "label": "New People"
            },
            "new_christians": {
                "total": total_new_christians,
                "average": round(avg_new_christians, 1),
                "label": "New Christians"
            },
            "youth": {
                "total": total_youth,
                "average": round(avg_youth, 1),
                "label": "Youth"
            },
            "kids": {
                "total": total_kids,
                "average": round(avg_kids, 1),
                "label": "Kids"
            },
            "connect_groups": {
                "total": total_connect_groups,
                "average": round(avg_connect_groups, 1),
                "label": "Connect Groups"
            }
        },
        "entry_count": entry_count
    }
    return report

# Add to the top of the file, after imports
WEEKEND_REVIEW_PHRASES = [
    'weekend review', 'weekend report', 'sunday review', 'sunday report',
    'how did the church go', 'how did futures church', 'how did the church do',
    'how did we go', 'church report', 'church review', 'futures church report',
    'futures church review', 'how did the church', 'how did futures', 'church summary',
    'church recap', 'church stats', 'futures church stats', 'futures church summary',
    'how did the church go this weekend', 'how did the church go this week',
    'how did futures church go', 'how did futures church go this weekend',
    'how did futures church go this week', 'how did the church go on sunday',
    'how did we go this weekend', 'how did we go this week', 'how did we go on sunday',
    'give me a weekend review', 'give me a church report', 'give me a church review',
    'give me a church summary', 'give me a church recap', 'give me a church stats',
    'give me a futures church report', 'give me a futures church review',
    'give me a futures church summary', 'give me a futures church recap',
    'give me a futures church stats', 'can i get a weekend review', 'can i get a church report',
    'can i get a church review', 'can i get a church summary', 'can i get a church recap',
    'can i get a church stats', 'can i get a futures church report', 'can i get a futures church review',
    'can i get a futures church summary', 'can i get a futures church recap',
    'can i get a futures church stats', 'church-wide report', 'church wide report',
    'church-wide review', 'church wide review', 'church-wide summary', 'church wide summary',
    'church-wide recap', 'church wide recap', 'church-wide stats', 'church wide stats',
]

# Patch the review detection logic in query_data_internal
# ... existing code ...
def query_data_internal(data: Dict[str, Any]) -> Dict[str, Any]:
    """Internal function to query data (same logic as /api/query endpoint)"""
    question = str(data.get("question", "")).strip()
    if not question:
        return {"error": "Missing question"}

    # Lowercase for matching
    question_lower = question.lower()
    # If any weekend review phrase is present, handle campus-specific or cross-campus weekend review
    if any(phrase in question_lower for phrase in WEEKEND_REVIEW_PHRASES):
        campus = detect_campus(question)
        if campus and campus != "all_campuses":
            # Generate campus-specific weekend review (last 7 days)
            start_date = datetime.now() - timedelta(days=7)
            end_date = datetime.now()
            # Get rows from Google Sheets or memory
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
                rows = campus_history
            # Filter rows for campus and date range
            campus_normalized = normalize_campus(campus)
            filtered_rows = []
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
                            continue
            # Calculate stats (reuse your existing logic)
            analysis_data = calculate_stats_for_year_range(filtered_rows, campus, start_date.year)
            summary = (
                f"{display_campus_name(campus)} Weekend Review\n"
                f"Total Attendance: {analysis_data.get('total_attendance', 0):,}\n"
                f"New People: {analysis_data.get('total_new_people', 0):,}\n"
                f"New Christians: {analysis_data.get('total_new_christians', 0):,}\n"
                f"Youth: {analysis_data.get('total_youth', 0):,}\n"
                f"Kids: {analysis_data.get('total_kids', 0):,}\n"
                f"Connect Groups: {analysis_data.get('total_connect_groups', 0):,}"
            )
            # Build report array for modal table
            report = [
                {"label": "Total Attendance", "total": analysis_data.get("total_attendance", 0), "average": analysis_data.get("averages", {}).get("attendance", 0), "count": analysis_data.get("total_entries", 0), "year": start_date.year},
                {"label": "New People", "total": analysis_data.get("total_new_people", 0), "average": analysis_data.get("averages", {}).get("new_people", 0), "count": analysis_data.get("total_entries", 0), "year": start_date.year},
                {"label": "New Christians", "total": analysis_data.get("total_new_christians", 0), "average": analysis_data.get("averages", {}).get("new_christians", 0), "count": analysis_data.get("total_entries", 0), "year": start_date.year},
                {"label": "Youth", "total": analysis_data.get("total_youth", 0), "average": analysis_data.get("averages", {}).get("youth", 0), "count": analysis_data.get("total_entries", 0), "year": start_date.year},
                {"label": "Kids", "total": analysis_data.get("total_kids", 0), "average": analysis_data.get("averages", {}).get("kids", 0), "count": analysis_data.get("total_entries", 0), "year": start_date.year},
                {"label": "Connect Groups", "total": analysis_data.get("total_connect_groups", 0), "average": analysis_data.get("averages", {}).get("connect_groups", 0), "count": analysis_data.get("total_entries", 0), "year": start_date.year},
            ]
            return {
                "question": question,
                "campus": display_campus_name(campus),
                "date_range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "summary": summary,
                "stats": analysis_data,
                "report": report,
                "text": summary,
                "popup": True
            }
        else:
            # No campus detected, do cross-campus as before
            report = generate_cross_campus_report('weekly', "")
            stats = report.get('stats', {})
            summary = (
                f"Futures Church Weekend Review\n"
                f"Total Attendance: {stats.get('attendance', {}).get('total', 0):,}\n"
                f"Average Attendance: {stats.get('attendance', {}).get('average', 0):,.1f}\n"
                f"New People: {stats.get('new_people', {}).get('total', 0):,}\n"
                f"New Christians: {stats.get('new_christians', {}).get('total', 0):,}\n"
                f"Youth: {stats.get('youth', {}).get('total', 0):,}\n"
                f"Kids: {stats.get('kids', {}).get('total', 0):,}\n"
                f"Connect Groups: {stats.get('connect_groups', {}).get('total', 0):,}"
            )
            return {
                "question": question,
                "campus": "Futures Church (All Campuses)",
                "date_range": report.get('date_range', ''),
                "summary": summary,
                "stats": stats,
                "report": report,  # Add report property for frontend popup detection
                "text": summary,
                "popup": True
            }
    # ... rest of the function unchanged ...

@app.route('/heartbeat')
def heartbeat():
    return render_template('heartbeat.html')

@app.route('/journey')
def journey():
    return render_template('journey.html')

if __name__ == '__main__':
    print("Starting app.py")
    print("App running on: http://localhost:5001")
    app.run(debug=False, port=5001)