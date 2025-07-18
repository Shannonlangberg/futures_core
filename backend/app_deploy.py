# === FULL FUNCTIONALITY RESTORED ===
# This file is now a copy of backend/app.py with all advanced features, endpoints, and logic.
# (If you want to keep deployment-specific tweaks, add them after this block.)

# --- BEGIN COPY ---

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

print("[DEBUG] Creating Flask app instance")
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
print("[DEBUG] Flask app instance created and CORS enabled")

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
        sheet = client.open(os.getenv("GOOGLE_SHEET_NAME", "Stats")).sheet1
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

# Utility functions
def safe_int(val: Any) -> int:
    """Safely convert a value to int, returning 0 on failure."""
    try:
        return int(str(val).replace(",", "").strip()) if str(val).strip() else 0
    except Exception:
        return 0

def get_row_timestamp(row: Any) -> datetime:
    """Extract and parse a timestamp from a row."""
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

def detect_campus(text: str) -> Optional[str]:
    """Detect campus from text"""
    text_lower = text.lower()
    campuses = {
        'futures church': 'Futures Church',
        'futures north': 'Futures North', 
        'futures south': 'Futures South',
        'futures east': 'Futures East',
        'futures west': 'Futures West'
    }
    for campus_key, campus_name in campuses.items():
        if campus_key in text_lower:
            return campus_name
    return None

def normalize_campus(name):
    """Normalize campus name"""
    if not name:
        return "Futures Church"
    return name.strip()

def display_campus_name(name):
    """Display campus name nicely"""
    if not name:
        return "Futures Church"
    return name.strip()

def generate_audio_with_elevenlabs(text: str, filename: Optional[str] = None) -> Optional[str]:
    """Generate audio with ElevenLabs"""
    if not elevenlabs_api_key:
        return None
    
    try:
        import requests
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
            if not filename:
                filename = f"response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            filepath = f"temp_audio/{filename}"
            os.makedirs("temp_audio", exist_ok=True)
            with open(filepath, "wb") as f:
                f.write(response.content)
            return filename
    except Exception as e:
        logger.error(f"ElevenLabs error: {e}")
    return None

def get_demo_data():
    """Get demo data when Google Sheets is not available"""
    return [
        {
            'Timestamp': '2024-01-07',
            'Campus': 'Futures Church',
            'Total Attendance': 125,
            'New People': 5,
            'New Christians': 2,
            'Youth': 18,
            'Kids': 12,
            'Connect Groups': 1
        },
        {
            'Timestamp': '2024-01-14', 
            'Campus': 'Futures Church',
            'Total Attendance': 132,
            'New People': 3,
            'New Christians': 1,
            'Youth': 20,
            'Kids': 15,
            'Connect Groups': 1
        },
        {
            'Timestamp': '2024-01-21',
            'Campus': 'Futures Church', 
            'Total Attendance': 128,
            'New People': 4,
            'New Christians': 2,
            'Youth': 19,
            'Kids': 13,
            'Connect Groups': 1
        }
    ]

def query_data_internal(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process voice queries with demo or real data"""
    question = data.get('text', '').lower()
    campus = data.get('campus', 'Futures Church')
    
    # Get data (demo or real)
    if sheet:
        try:
            rows = sheet.get_all_records()
        except Exception as e:
            logger.error(f"Error getting sheet data: {e}")
            rows = get_demo_data()
    else:
        rows = get_demo_data()
    
    # Filter by campus
    campus_rows = [row for row in rows if normalize_campus(row.get('Campus', '')) == normalize_campus(campus)]
    
    # Process the filtered data to get totals and averages
    total_attendance = sum(safe_int(row.get('Total Attendance', 0)) for row in campus_rows)
    total_new_people = sum(safe_int(row.get('New People', 0)) for row in campus_rows)
    total_new_christians = sum(safe_int(row.get('New Christians', 0)) for row in campus_rows)
    total_youth = sum(safe_int(row.get('Youth', 0)) for row in campus_rows)
    total_kids = sum(safe_int(row.get('Kids', 0)) for row in campus_rows)
    total_connect_groups = sum(safe_int(row.get('Connect Groups', 0)) for row in campus_rows)
    
    num_entries = len(campus_rows) if campus_rows else 1
    avg_attendance = total_attendance / num_entries
    avg_new_people = total_new_people / num_entries
    avg_new_christians = total_new_christians / num_entries
    avg_youth = total_youth / num_entries
    avg_kids = total_kids / num_entries
    avg_connect_groups = total_connect_groups / num_entries
    
    # Generate AI insights if Claude is available
    insights = ""
    if claude:
        try:
            data_summary = f"""
Here's what I found for {campus} campus:

Their numbers:
- {total_attendance:,} total attendance
- {total_new_people:,} new people
- {total_new_christians:,} new christians
- {total_youth:,} youth
- {total_kids:,} kids
- {total_connect_groups:,} connect groups

Weekly averages:
- {avg_attendance:.1f} people per week
- {avg_new_people:.1f} new people per week
- {avg_new_christians:.1f} new christians per week
- {avg_youth:.1f} youth per week
- {avg_kids:.1f} kids per week
- {avg_connect_groups:.1f} connect groups per week
"""
            
            # Create intelligent prompt based on question type
            if any(word in question for word in ['trend', 'trends', 'pattern', 'growth', 'improve', 'attention', 'working']):
                prompt = f"You are a church analytics expert. Based on this data: {data_summary}\n\nQuestion: {data.get('text', '')}\n\nProvide 2-3 specific insights about trends, patterns, or areas for improvement. Be encouraging and actionable."
            elif any(word in question for word in ['compare', 'comparison', 'versus', 'vs', 'difference']):
                prompt = f"You are a church analytics expert. Based on this data: {data_summary}\n\nQuestion: {data.get('text', '')}\n\nProvide 2-3 specific insights about comparisons or differences. Be encouraging and actionable."
            else:
                prompt = f"You are a church analytics expert. Based on this data: {data_summary}\n\nQuestion: {data.get('text', '')}\n\nProvide 2-3 specific insights about the data. Be encouraging and actionable."
            
            response = claude.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            insights = response.content[0].text
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            insights = "I'd be happy to analyze your data, but I need to connect to my AI assistant first."
    
    # Simple response for demo
    if 'attendance' in question:
        response_text = f"Total attendance for {campus} is {total_attendance:,} people."
        if insights:
            response_text += f"\n\nAI Insights:\n{insights}"
        return {
            'text': response_text,
            'campus': campus,
            'status': 'success',
            'insights': insights
        }
    elif 'new people' in question or 'visitors' in question:
        response_text = f"Total new people for {campus} is {total_new_people:,}."
        if insights:
            response_text += f"\n\nAI Insights:\n{insights}"
        return {
            'text': response_text,
            'campus': campus,
            'status': 'success',
            'insights': insights
        }
    elif 'new christians' in question:
        response_text = f"Total new Christians for {campus} is {total_new_christians:,}."
        if insights:
            response_text += f"\n\nAI Insights:\n{insights}"
        return {
            'text': response_text,
            'campus': campus,
            'status': 'success',
            'insights': insights
        }
    else:
        response_text = f"I heard you ask about '{data.get('text', '')}' for {campus}. Here's what I found:\n\nTotal Attendance: {total_attendance:,}\nNew People: {total_new_people:,}\nNew Christians: {total_new_christians:,}\nYouth: {total_youth:,}\nKids: {total_kids:,}\nConnect Groups: {total_connect_groups:,}"
        if insights:
            response_text += f"\n\nAI Insights:\n{insights}"
        return {
            'text': response_text,
            'campus': campus,
            'status': 'success',
            'insights': insights
        }

# Security middleware
@app.before_request
def log_request():
    logger.info(f"{request.method} {request.path} from {request.remote_addr}")

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# Main routes
@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return app.send_static_file(filename)

@app.route('/temp_audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory('temp_audio', filename)

@app.route('/query')
def serve_query():
    return render_template('index.html')

@app.route('/heartbeat')
def heartbeat():
    return render_template('heartbeat.html')

@app.route('/journey')
def journey():
    return render_template('journey.html')

# API endpoints
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'services': {
            'google_sheets': sheet is not None,
            'claude': claude is not None,
            'elevenlabs': elevenlabs_api_key is not None
        }
    })

@app.route('/api/session')
def session_info():
    return jsonify({
        'status': 'connected',
        'timestamp': datetime.now().isoformat(),
        'message': 'Church Voice Assistant API is running',
        'services': {
            'google_sheets': sheet is not None,
            'claude': claude is not None,
            'elevenlabs': elevenlabs_api_key is not None
        }
    })

@app.route('/api/stats')
def get_stats():
    """Get stats from Google Sheets or demo data, filtered by campus"""
    campus = request.args.get('campus', 'Futures Church')
    
    if sheet:
        try:
            rows = sheet.get_all_records()
            # Filter by campus
            campus_rows = [row for row in rows if normalize_campus(row.get('Campus', '')) == normalize_campus(campus)]
            
            if not campus_rows:
                # If no data for this campus, return zeros
                return jsonify({
                    'attendance': {'total': 0, 'average': 0},
                    'new_people': {'total': 0, 'average': 0},
                    'new_christians': {'total': 0, 'average': 0},
                    'youth': {'total': 0, 'average': 0},
                    'kids': {'total': 0, 'average': 0},
                    'connect_groups': {'total': 0, 'average': 0}
                })
            
            # Process filtered data
            total_attendance = sum(safe_int(row.get('Total Attendance', 0)) for row in campus_rows)
            total_new_people = sum(safe_int(row.get('New People', 0)) for row in campus_rows)
            total_new_christians = sum(safe_int(row.get('New Christians', 0)) for row in campus_rows)
            total_youth = sum(safe_int(row.get('Youth', 0)) for row in campus_rows)
            total_kids = sum(safe_int(row.get('Kids', 0)) for row in campus_rows)
            total_connect_groups = sum(safe_int(row.get('Connect Groups', 0)) for row in campus_rows)
            
            num_entries = len(campus_rows)
            return jsonify({
                'attendance': {'total': total_attendance, 'average': total_attendance / max(num_entries, 1)},
                'new_people': {'total': total_new_people, 'average': total_new_people / max(num_entries, 1)},
                'new_christians': {'total': total_new_christians, 'average': total_new_christians / max(num_entries, 1)},
                'youth': {'total': total_youth, 'average': total_youth / max(num_entries, 1)},
                'kids': {'total': total_kids, 'average': total_kids / max(num_entries, 1)},
                'connect_groups': {'total': total_connect_groups, 'average': total_connect_groups / max(num_entries, 1)}
            })
        except Exception as e:
            logger.error(f"Error getting stats from sheet: {e}")
    
    # Return demo stats (filtered by campus for demo)
    demo_data = get_demo_data()
    campus_demo_data = [row for row in demo_data if normalize_campus(row.get('Campus', '')) == normalize_campus(campus)]
    
    if campus_demo_data:
        total_attendance = sum(safe_int(row.get('Total Attendance', 0)) for row in campus_demo_data)
        total_new_people = sum(safe_int(row.get('New People', 0)) for row in campus_demo_data)
        total_new_christians = sum(safe_int(row.get('New Christians', 0)) for row in campus_demo_data)
        total_youth = sum(safe_int(row.get('Youth', 0)) for row in campus_demo_data)
        total_kids = sum(safe_int(row.get('Kids', 0)) for row in campus_demo_data)
        total_connect_groups = sum(safe_int(row.get('Connect Groups', 0)) for row in campus_demo_data)
        
        num_entries = len(campus_demo_data)
        return jsonify({
            'attendance': {'total': total_attendance, 'average': total_attendance / max(num_entries, 1)},
            'new_people': {'total': total_new_people, 'average': total_new_people / max(num_entries, 1)},
            'new_christians': {'total': total_new_christians, 'average': total_new_christians / max(num_entries, 1)},
            'youth': {'total': total_youth, 'average': total_youth / max(num_entries, 1)},
            'kids': {'total': total_kids, 'average': total_kids / max(num_entries, 1)},
            'connect_groups': {'total': total_connect_groups, 'average': total_connect_groups / max(num_entries, 1)}
        })
    else:
        # Return zeros if no data for this campus
        return jsonify({
            'attendance': {'total': 0, 'average': 0},
            'new_people': {'total': 0, 'average': 0},
            'new_christians': {'total': 0, 'average': 0},
            'youth': {'total': 0, 'average': 0},
            'kids': {'total': 0, 'average': 0},
            'connect_groups': {'total': 0, 'average': 0}
        })

@app.route('/api/process_voice', methods=['POST'])
def process_voice():
    """Process voice input with full functionality"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        campus = data.get('campus', 'Futures Church')
        
        # Process the query
        result = query_data_internal({
            'text': text,
            'campus': campus
        })
        
        # Generate audio if ElevenLabs is available
        audio_url = None
        if elevenlabs_api_key and result.get('text'):
            audio_filename = generate_audio_with_elevenlabs(result['text'])
            if audio_filename:
                audio_url = f"/temp_audio/{audio_filename}"
        
        result['audio_url'] = audio_url
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing voice: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/query', methods=['POST'])
def query():
    """Process text queries"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        campus = data.get('campus', 'Futures Church')
        
        # Process the query
        result = query_data_internal({
            'text': text,
            'campus': campus
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/campuses')
def get_campuses():
    return jsonify([
        'Futures Church',
        'Futures North',
        'Futures South',
        'Futures East',
        'Futures West'
    ])

@app.route('/api/memory/<campus>')
def get_campus_memory(campus):
    memory = load_conversation_memory()
    campus_memory = memory.get(campus, {})
    return jsonify({
        'campus': campus,
        'memory': campus_memory
    })

@app.route('/api/greeting_audio')
def greeting_audio():
    """Generate greeting audio"""
    if elevenlabs_api_key:
        greeting_text = "Hello! I'm your Church Voice Assistant. How can I help you today?"
        audio_filename = generate_audio_with_elevenlabs(greeting_text, "greeting_elevenlabs.mp3")
        if audio_filename:
            return jsonify({'audio_url': f"/temp_audio/{audio_filename}"})
    
    return jsonify({'message': 'Greeting audio not available'})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False) 