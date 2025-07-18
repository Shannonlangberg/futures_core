import os
import logging
import json
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from functools import wraps
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Enable CORS
CORS(app, origins=['*'])

# Initialize external services with graceful fallbacks
sheet = None
claude = None
elevenlabs_api_key = None
elevenlabs_voice_id = "21m00Tcm4TlvDq8ikWAM"

# Try to load Google Sheets
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    if os.path.exists("credentials.json"):
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        sheet_name = os.getenv("GOOGLE_SHEET_NAME", "Stats")
        sheet = client.open(sheet_name).sheet1
        logger.info(f"Google Sheets initialized successfully with sheet: {sheet_name}")
    else:
        logger.warning("credentials.json not found - using demo data")
except Exception as e:
    logger.warning(f"Google Sheets not available: {e}")

# Try to load Claude
try:
    import anthropic
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        claude = anthropic.Client(api_key=api_key)
        logger.info("Claude initialized successfully")
    else:
        logger.warning("ANTHROPIC_API_KEY not found")
except Exception as e:
    logger.warning(f"Claude not available: {e}")

# Try to load ElevenLabs
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

# Memory storage
conversation_memory_file = "data/conversation_memory.json"

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
    
    # Simple response for demo
    if 'attendance' in question:
        total = sum(safe_int(row.get('Total Attendance', 0)) for row in rows)
        return {
            'text': f"Total attendance for {campus} is {total:,} people.",
            'campus': campus,
            'status': 'success'
        }
    elif 'new people' in question or 'visitors' in question:
        total = sum(safe_int(row.get('New People', 0)) for row in rows)
        return {
            'text': f"Total new people for {campus} is {total:,}.",
            'campus': campus,
            'status': 'success'
        }
    elif 'new christians' in question:
        total = sum(safe_int(row.get('New Christians', 0)) for row in rows)
        return {
            'text': f"Total new Christians for {campus} is {total:,}.",
            'campus': campus,
            'status': 'success'
        }
    else:
        return {
            'text': f"I heard you ask about '{data.get('text', '')}' for {campus}. This is a demo response from the deployed app.",
            'campus': campus,
            'status': 'success'
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
    """Get stats from Google Sheets or demo data"""
    if sheet:
        try:
            rows = sheet.get_all_records()
            # Process real data
            total_attendance = sum(safe_int(row.get('Total Attendance', 0)) for row in rows)
            total_new_people = sum(safe_int(row.get('New People', 0)) for row in rows)
            total_new_christians = sum(safe_int(row.get('New Christians', 0)) for row in rows)
            total_youth = sum(safe_int(row.get('Youth', 0)) for row in rows)
            total_kids = sum(safe_int(row.get('Kids', 0)) for row in rows)
            total_connect_groups = sum(safe_int(row.get('Connect Groups', 0)) for row in rows)
            
            return jsonify({
                'attendance': {'total': total_attendance, 'average': total_attendance / max(len(rows), 1)},
                'new_people': {'total': total_new_people, 'average': total_new_people / max(len(rows), 1)},
                'new_christians': {'total': total_new_christians, 'average': total_new_christians / max(len(rows), 1)},
                'youth': {'total': total_youth, 'average': total_youth / max(len(rows), 1)},
                'kids': {'total': total_kids, 'average': total_kids / max(len(rows), 1)},
                'connect_groups': {'total': total_connect_groups, 'average': total_connect_groups / max(len(rows), 1)}
            })
        except Exception as e:
            logger.error(f"Error getting stats from sheet: {e}")
    
    # Return demo stats
    return jsonify({
        'attendance': {'total': 1250, 'average': 125.5},
        'new_people': {'total': 45, 'average': 4.5},
        'new_christians': {'total': 12, 'average': 1.2},
        'youth': {'total': 180, 'average': 18.0},
        'kids': {'total': 95, 'average': 9.5},
        'connect_groups': {'total': 8, 'average': 0.8}
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