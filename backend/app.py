# app.py

print("[DEBUG] Starting import: Flask")
from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for, flash, session
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
    print("[DEBUG] Starting import: Flask-Login")
    from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
    print("[DEBUG] Imported Flask-Login")
except Exception as e:
    print(f"[ERROR] Failed to import Flask-Login: {e}")
    raise

try:
    print("[DEBUG] Starting import: werkzeug.security")
    from werkzeug.security import generate_password_hash, check_password_hash
    print("[DEBUG] Imported werkzeug.security")
except Exception as e:
    print(f"[ERROR] Failed to import werkzeug.security: {e}")
    raise

print("[DEBUG] Starting import: requests")
import requests
print("[DEBUG] Imported requests")

print("[DEBUG] Starting import: functools")
from functools import wraps
print("[DEBUG] Imported functools")

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
    # First try to load from environment variable (for Railway)
    credentials_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    if credentials_json:
        try:
            import json
            # Clean the JSON string - remove any extra whitespace or newlines
            credentials_json = credentials_json.strip()
            creds_dict = json.loads(credentials_json)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            sheet = client.open("Stats").sheet1
            logger.info("Google Sheets initialized successfully from environment variable")
            print("[DEBUG] Google Sheets initialized from environment variable")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in GOOGLE_SHEETS_CREDENTIALS: {e}")
            print(f"[ERROR] Invalid JSON in GOOGLE_SHEETS_CREDENTIALS: {e}")
            sheet = None
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets from environment variable: {e}")
            print(f"[ERROR] Failed to initialize Google Sheets from environment variable: {e}")
            sheet = None
    # Fallback to file (for local development)
    elif os.path.exists("credentials.json"):
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("Stats").sheet1
        logger.info("Google Sheets initialized successfully from file")
        print("[DEBUG] Google Sheets initialized from file")
    else:
        logger.warning("No Google Sheets credentials found - Google Sheets functionality disabled")
        print("[WARNING] No Google Sheets credentials found")
        sheet = None
except Exception as e:
    logger.error(f"Failed to initialize Google Sheets: {e}")
    print(f"[ERROR] Failed to initialize Google Sheets: {e}")
    sheet = None
print("[DEBUG] Finished Google Sheets client initialization")

print("[DEBUG] Starting Claude setup")
# Claude setup
try:
    # Completely isolate the environment for Anthropic initialization
    import subprocess
    import tempfile
    import json
    import sys
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        # Create a temporary script to test Anthropic initialization
        test_script = '''
import os
import sys
try:
    from anthropic import Client
    api_key = sys.argv[1]
    client = Client(api_key=api_key)
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_script)
            temp_file = f.name
        
        try:
            # Run the test in a clean environment
            result = subprocess.run([sys.executable, temp_file, api_key], 
                                  capture_output=True, text=True, timeout=10)
            
            if "SUCCESS" in result.stdout:
                # If the test succeeds, initialize normally
                from anthropic import Client
                claude = Client(api_key=api_key)
                logger.info("Claude initialized successfully (isolated test)")
                print("[DEBUG] Claude initialized successfully (isolated test)")
            else:
                # If the test fails, try alternative initialization
                try:
                    from anthropic import Client
                    # Try with minimal configuration
                    claude = Client(api_key=api_key)
                    logger.info("Claude initialized successfully (fallback)")
                    print("[DEBUG] Claude initialized successfully (fallback)")
                except Exception as e:
                    logger.error(f"Failed to initialize Claude: {e}")
                    print(f"[ERROR] Failed to initialize Claude: {e}")
                    claude = None
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
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

def parse_any_date(date_str):
    """Parse date from various formats commonly found in Google Sheets"""
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%m/%d/%Y', '%-m/%-d/%Y'):
        try:
            return datetime.strptime(date_str, fmt)
        except Exception:
            continue
    raise ValueError(f"Unrecognized date format: {date_str}")

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
app.secret_key = os.environ.get('SECRET_KEY', 'futures-church-secret-key-2025')
# Get CORS origins from environment variable or use defaults
cors_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:3001,http://localhost:3002').split(',')
CORS(app, supports_credentials=True, origins=cors_origins, allow_headers=["Content-Type", "Authorization"])
print("[DEBUG] Flask app instance created and CORS enabled")

# Configure Flask-Login
print("[DEBUG] Starting Flask-Login setup")
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
print("[DEBUG] Flask-Login configured")

# User management functions
def load_users_database():
    """Load users from JSON file"""
    try:
        with open(os.path.join(os.path.dirname(__file__), 'users.json'), 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load users database: {e}")
        return {"users": {}, "roles": {}}

def save_users_database(data):
    """Save users to JSON file"""
    try:
        with open(os.path.join(os.path.dirname(__file__), 'users.json'), 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save users database: {e}")
        return False

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.username = user_data['username']
        self.email = user_data['email']
        self.full_name = user_data['full_name']
        self.role = user_data['role']
        self.campus = user_data['campus']
        self.active = user_data['active']
        self.password_hash = user_data['password_hash']
        
    def is_authenticated(self):
        return True
        
    def is_active(self):
        return self.active
        
    def is_anonymous(self):
        return False
        
    def get_id(self):
        return str(self.id)
        
    def check_password(self, password):
        """Check if the provided password is correct"""
        # Check if user has a password hash
        if hasattr(self, 'password_hash') and self.password_hash:
            # Use werkzeug's check_password_hash for secure comparison
            return check_password_hash(self.password_hash, password)
        else:
            # Fallback to simple comparison for backward compatibility
            return password == "futures2025"
        
    def has_permission(self, permission_type, campus=None):
        """Check if user has specific permission"""
        users_db = load_users_database()
        role_permissions = users_db.get('roles', {}).get(self.role, {}).get('permissions', {})
        
        if permission_type == 'log_stats':
            return role_permissions.get('log_stats') == 'all'
        elif permission_type == 'recall_stats':
            recall_perm = role_permissions.get('recall_stats')
            if recall_perm == 'all':
                return True
            elif recall_perm == 'assigned_campus':
                return campus is None or campus == self.campus or self.campus == 'all_campuses'
            elif recall_perm == 'none':
                return False
            else:
                return False
        elif permission_type == 'dashboard_access':
            dashboard_perm = role_permissions.get('dashboard_access')
            if dashboard_perm == 'all':
                return True
            elif dashboard_perm == 'assigned_campus':
                return campus is None or campus == self.campus or self.campus == 'all_campuses'
            elif dashboard_perm == 'none':
                return False
            else:
                return True  # Default to allow if not specified
        elif permission_type == 'query_access':
            query_perm = role_permissions.get('query_access')
            if query_perm == 'all':
                return True
            elif query_perm == 'assigned_campus':
                return campus is None or campus == self.campus or self.campus == 'all_campuses'
            elif query_perm == 'none':
                return False
            else:
                return True  # Default to allow if not specified
        elif permission_type == 'manage_users':
            return role_permissions.get('manage_users', False)
        elif permission_type == 'system_settings':
            return role_permissions.get('system_settings', False)
        elif permission_type == 'finance_access':
            return role_permissions.get('finance_access', False)
        elif permission_type == 'cross_location_comparison':
            return role_permissions.get('cross_location_comparison', False)
        
        return False
        
    def get_accessible_campuses(self):
        """Get list of campuses this user can access for data recall"""
        if self.has_permission('recall_stats'):
            if self.campus == 'all_campuses':
                return ['all_campuses', 'paradise', 'adelaide_city', 'salisbury', 'south', 'mount_barker']
            else:
                return [self.campus]
        return []

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    users_db = load_users_database()
    user_data = users_db.get('users', {}).get(user_id)
    if user_data:
        return User(user_data)
    return None

def authenticate_user(username, password):
    """Authenticate user and return User object if valid"""
    users_db = load_users_database()
    
    # Find user by username
    for user_id, user_data in users_db.get('users', {}).items():
        if user_data['username'] == username and user_data['active']:
            user = User(user_data)
            if user.check_password(password):
                # Update last login
                user_data['last_login'] = datetime.now().isoformat()
                save_users_database(users_db)
                return user
    return None

print("[DEBUG] User management functions and classes defined")

# Campus management functions
def load_campuses_database():
    """Load campuses from JSON file"""
    try:
        with open(os.path.join(os.path.dirname(__file__), 'campuses.json'), 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load campuses database: {e}")
        # Return basic fallback campuses
        return {
            "campuses": {
                "paradise": {"id": "paradise", "name": "Paradise Campus", "display_name": "Paradise", "active": True, "detection_patterns": ["paradise"]},
                "south": {"id": "south", "name": "South Campus", "display_name": "South", "active": True, "detection_patterns": ["south"]},
                "all_campuses": {"id": "all_campuses", "name": "All Campuses", "display_name": "All Campuses", "active": True, "special": True}
            },
            "metadata": {"version": "1.0"}
        }

def save_campuses_database(data):
    """Save campuses to JSON file"""
    try:
        # Update metadata
        data.setdefault('metadata', {})['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        active_count = sum(1 for campus in data.get('campuses', {}).values() if campus.get('active', False))
        data['metadata']['active_campuses'] = active_count
        data['metadata']['total_campuses'] = len(data.get('campuses', {}))
        
        with open(os.path.join(os.path.dirname(__file__), 'campuses.json'), 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save campuses database: {e}")
        return False

def get_active_campuses():
    """Get list of active campuses for dropdowns"""
    campuses_db = load_campuses_database()
    active_campuses = []
    
    for campus_id, campus_data in campuses_db.get('campuses', {}).items():
        if campus_data.get('active', False):
            active_campuses.append({
                'id': campus_id,
                'name': campus_data.get('display_name', campus_data.get('name', campus_id)),
                'full_name': campus_data.get('name', campus_id)
            })
    
    # Sort by name, but put "All Campuses" first if it exists
    active_campuses.sort(key=lambda x: (x['id'] != 'all_campuses', x['name']))
    return active_campuses

def get_campuses_for_user():
    """Get campuses accessible to current user based on their role"""
    try:
        if not hasattr(current_user, 'role'):
            return {'campuses': []}
            
        campuses_db = load_campuses_database()
        accessible_campuses = []
        
        # Finance team and admin roles can access all campuses
        if current_user.role in ['finance', 'admin', 'senior_leader']:
            for campus_id, campus_data in campuses_db.get('campuses', {}).items():
                if campus_data.get('active', False) and campus_id != 'all_campuses':
                    accessible_campuses.append({
                        'id': campus_id,
                        'name': campus_data.get('display_name', campus_data.get('name', campus_id)),
                        'full_name': campus_data.get('name', campus_id)
                    })
        elif current_user.role == 'campus_pastor':
            # Campus pastors only see their own campus
            user_campus = current_user.campus
            if user_campus in campuses_db.get('campuses', {}):
                campus_data = campuses_db['campuses'][user_campus]
                if campus_data.get('active', False):
                    accessible_campuses.append({
                        'id': user_campus,
                        'name': campus_data.get('display_name', campus_data.get('name', user_campus)),
                        'full_name': campus_data.get('name', user_campus)
                    })
        else:
            # Other roles get all campuses by default (except all_campuses)
            for campus_id, campus_data in campuses_db.get('campuses', {}).items():
                if campus_data.get('active', False) and campus_id != 'all_campuses':
                    accessible_campuses.append({
                        'id': campus_id,
                        'name': campus_data.get('display_name', campus_data.get('name', campus_id)),
                        'full_name': campus_data.get('name', campus_id)
                    })
        
        return {
            'campuses': sorted(accessible_campuses, key=lambda x: x['name'])
        }
    except Exception as e:
        logger.error(f"Error getting campuses for user: {e}")
        return {'campuses': []}

def get_campus_detection_patterns():
    """Get dynamic campus detection patterns from configuration with natural speech support"""
    campuses_db = load_campuses_database()
    patterns = {}
    
    for campus_id, campus_data in campuses_db.get('campuses', {}).items():
        if campus_data.get('active', False):
            detection_patterns = campus_data.get('detection_patterns', [campus_id])
            
            # Create flexible patterns that handle natural speech
            flexible_patterns = []
            for pattern in detection_patterns:
                # Add the base pattern
                flexible_patterns.append(rf'\b{re.escape(pattern)}\b')
                # Add common speech patterns
                flexible_patterns.append(rf'\bfor {re.escape(pattern)}\b')
                flexible_patterns.append(rf'\bat {re.escape(pattern)}\b')
                flexible_patterns.append(rf'\b{re.escape(pattern)} campus\b')
                flexible_patterns.append(rf'\bstats for {re.escape(pattern)}\b')
                flexible_patterns.append(rf'\blog stats for {re.escape(pattern)}\b')
                flexible_patterns.append(rf'\breporting for {re.escape(pattern)}\b')
            
            # Join patterns with OR regex
            pattern = '(?:' + '|'.join(flexible_patterns) + ')'
            patterns[campus_id] = pattern
    
    return patterns

print("[DEBUG] Campus management functions defined")

# Permission decorators
def require_permission(permission_type):
    """Decorator to check if user has specific permission"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.has_permission(permission_type):
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('serve_index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Administrator access required.', 'error')
            return redirect(url_for('serve_index'))
        return f(*args, **kwargs)
    return decorated_function

def can_recall_data(campus=None):
    """Check if current user can recall data for specified campus"""
    if not current_user.is_authenticated:
        return False
    return current_user.has_permission('recall_stats', campus)

def can_log_stats():
    """Check if current user can log stats"""
    if not current_user.is_authenticated:
        return False
    return current_user.has_permission('log_stats')

print("[DEBUG] Permission decorators defined")

# Enhanced regex patterns for parsing stats with better context awareness
patterns = {
    # Main attendance
    "total_attendance": r"(\d+)\s+(?:people|attendance|total|had|got|there were)",
    
    # New people breakdown
    "first_time_visitors": r"(\d+)\s+(?:first\s+time|first-time|first\s+timers?|new\s+people|newcomers?|ftv)",
    "visitors": r"(\d+)\s+(?:visitors?|guests?|passing\s+through|tourists?|visiting)",
            "information_gathered": r"(\d+)\s+(?:info\s+gathered|information\s+gathered|details\s+gathered|details\s+collected|contact\s+info|info|cards\s+back|contact\s+cards|response\s+cards|visitor\s+cards)",
    
    # Christian decisions breakdown  
    "first_time_christians": r"(\d+)\s+(?:first\s+time\s+(?:conversions?|decisions?|salvations?)|new\s+(?:conversions?|christians?)|(?:got\s+)?saved|baptisms?|ftc)",
    "rededications": r"(\d+)\s+(?:rededication|re-dedication|recommitment|re-commitment|renewed\s+(?:faith|commitment)|came\s+back)",
    
    # Youth breakdown
    "youth_attendance": r"(\d+)\s+(?:youth(?:\s+attendance|\s+group|\s+ministry)?|teens?|youth\s+people)",
    "youth_salvations": r"(\d+)\s+(?:youth\s+(?:salvations?|decisions?|saved)|teen\s+(?:salvations?|decisions?))",
    "youth_new_people": r"(\d+)\s+(?:youth\s+(?:new\s+people|visitors?|newcomers?)|teen\s+(?:new\s+people|visitors?))",
    
    # Kids breakdown
    "kids_attendance": r"(\d+)\s+(?:kids\s+attendance|children\s+attendance|kids\s+total)",
    "kids_leaders": r"(\d+)\s+(?:kids\s+leaders?|children\s+leaders?|kids\s+helpers?)",
    "new_kids": r"(\d+)\s+(?:new\s+kids|new\s+children|kids\s+visitors?)",
    "new_kids_salvations": r"(\d+)\s+(?:kids?\s+(?:salvations?|decisions?|saved)|children\s+(?:salvations?|decisions?))",
    
            # Ministry metrics
        "connect_groups": r"(\d+)\s+(?:connect\s+groups?|small\s+groups?|connects?|life\s+groups?|active\s+groups?)",
        "dream_team": r"(\d+)\s+(?:dream\s+team|dt|team\s+members?|serving\s+team)",
        
        # Special events
        "baptisms": r"(\d+)\s+(?:baptisms?|baptized|baptismal|water\s+baptism)",
        "child_dedications": r"(\d+)\s+(?:child\s+dedications?|baby\s+dedications?|dedications?|dedicated)",
        
        # Backward compatibility patterns
    "new_people": r"(\d+)\s+(?:new(?:\s+(?!time|people))|np)(?!\s+(?:visitors?|guests?))",
    "new_christians": r"(\d+)\s+(?:salvations?|decisions?|nc)(?!\s+(?:rededication|re-dedication))",
    "kids_total": r"(\d+)\s+(?:kids|children|kids\s+ministry|nursery)",
    "volunteers": r"(\d+)\s+(?:volunteers?|team\s+members?|servers?)"
}

# Campus detection patterns (loaded dynamically)
def get_campus_patterns():
    """Get campus patterns dynamically from configuration"""
    return get_campus_detection_patterns()

def detect_campus(text: str) -> Optional[str]:
    """Detect campus from text using dynamic patterns from configuration with fuzzy matching for voice recognition"""
    text_lower = text.lower()
    
    # Get dynamic campus patterns
    campus_patterns = get_campus_patterns()
    
    # Check each campus pattern with exact matching first
    for campus_id, pattern in campus_patterns.items():
        if re.search(pattern, text_lower, re.IGNORECASE):
            return campus_id
    
    # Enhanced fuzzy matching for voice recognition with common misspellings
    fuzzy_campus_patterns = {
        'south': [
            r'\bsouth\b', r'\bsowth\b', r'\bsow\b', r'\bsowf\b', r'\bsowth campus\b',
            r'\bsouth campus\b', r'\bsow campus\b', r'\bsowf campus\b'
        ],
        'salisbury': [
            r'\bsalisbury\b', r'\bsalsbury\b', r'\bsalsbery\b', r'\bsalisbery\b',
            r'\bsalisbury campus\b', r'\bsalsbury campus\b', r'\bsalsbery campus\b',
            r'\bsalisbery campus\b'
        ],
        'paradise': [
            r'\bparadise\b', r'\bparadice\b', r'\bparidise\b', r'\bparidice\b',
            r'\bparadise campus\b', r'\bparadice campus\b', r'\bparidise campus\b',
            r'\bparidice campus\b'
        ],
        'adelaide_city': [
            r'\badelaide\b', r'\badelaide city\b', r'\badelaide city campus\b',
            r'\badelaide campus\b', r'\badelaide city campus\b'
        ]
    }
    
    # Check fuzzy patterns for each campus
    for campus_id, patterns in fuzzy_campus_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.info(f"Fuzzy campus match: '{text}' -> {campus_id}")
                return campus_id
    
    # Check for partial matches (for voice recognition errors)
    partial_matches = {
        'south': ['sow', 'sowth', 'sowf', 'south'],
        'salisbury': ['sals', 'salis', 'salsbury', 'salisbury'],
        'paradise': ['parad', 'paradis', 'paradice'],
        'adelaide_city': ['adela', 'adelaide']
    }
    
    for campus_id, partials in partial_matches.items():
        for partial in partials:
            if partial in text_lower:
                logger.info(f"Partial campus match: '{text}' -> {campus_id}")
                return campus_id
    
    # If no specific campus is mentioned, default to all campuses for church-wide queries
    # Check if this looks like a church-wide stat query
    church_wide_indicators = [
        'how many', 'what is', "what's", 'give me', 'tell me', 'what was', 'how much',
        'total', 'average', 'church', 'this weekend', 'this week', 'this month', 'this year',
        'all campuses', 'church wide', 'across all', 'every campus', 'all locations'
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
                    row_date = parse_any_date(timestamp_str)
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
        return ["Thanks for inputting those stats!", "Keep up the great work!"]
    
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
    
    # Check if this contains actual numbers (indicating stat logging)
    text_lower = text.lower()
    contains_numbers = any(char.isdigit() for char in text)
    
    # Check for explicit query indicators
    is_query = any(word in text_lower for word in [
        'how many', 'what is', 'what was', 'what were', 'average', 'last week', 'this week', 'total', 'count', 'query', 'data', 'has had', 'had this year', 'had this month',
        'compare', 'comparison', 'vs', 'versus', 'between', 'year over year',
        'review', 'annual review', 'mid year review', 'mid-year review', 'report', 'summary', 'dashboard', 'snapshot', 'full report', 'overview', 'recap', 'stats summary', 'stat summary', 'stat report', 'stat overview', 'stat recap',
        'annual', 'mid year', 'mid-year', 'midyear'
    ]) or any(word in text_lower for word in ['q1', 'q2', 'q3', 'q4', 'quarter 1', 'quarter 2', 'quarter 3', 'quarter 4', 'first quarter', 'second quarter', 'third quarter', 'fourth quarter'])
    
    # Check if this is a request to log stats (no numbers yet)
    is_request = not contains_numbers and any(word in text_lower for word in ['log', 'record', 'enter', 'add', 'can i log', 'want to log', 'help me log', 'can we log'])
    
    # If it has numbers and is not explicitly a query, treat as stat logging
    is_stat_logging = contains_numbers and not is_query
    
    if is_query:
        prompt = f"""You are a helpful church AI assistant. A leader from the {campus} campus is asking for data:
"{text}"

{context}

Respond naturally as a helpful assistant. Tell them you'll look up that information for them right away! Be conversational and friendly. Keep it under 15 words. Examples:
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
    elif is_stat_logging:
        # For actual stat logging with numbers, give confirmation responses
        return ["Thanks for inputting those stats for " + campus + " campus!", "Great numbers this week!"]
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
                return ["Thanks for inputting those stats!", "Keep up the great work!"]
            
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        if is_request:
            return [f"Sure! I'd love to help input stats for {campus} campus. Just tell me the numbers!", "What were your attendance numbers today?"]
        else:
            return ["Thanks for inputting those stats!", "Keep up the great work!"]

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
            # Ensure temp_audio directory exists in backend folder
            temp_audio_dir = os.path.join(os.path.dirname(__file__), "temp_audio")
            os.makedirs(temp_audio_dir, exist_ok=True)
            
            if filename:
                # If filename provided, use it as-is
                audio_filename = filename  
                full_path = audio_filename
            else:
                # Generate filename and full path
                audio_filename = f"response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
                full_path = os.path.join(temp_audio_dir, audio_filename)
            
            with open(full_path, "wb") as f:
                f.write(response.content)
            logger.info(f"Generated audio file: {full_path}")
            
            # Return URL path for the audio file
            return f"/temp_audio/{audio_filename}"
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
    
    # Look for comparison keywords - more precise list
    comparison_keywords = [
        'compare', 'comparison', 'vs', 'versus', 'against', 'side by side', 'year over year',
        'between', 'difference', 'compared to', 'compared with', 'relative to',
        'q1 vs', 'q2 vs', 'q3 vs', 'q4 vs', 'quarter 1 vs', 'quarter 2 vs', 'quarter 3 vs', 'quarter 4 vs',
        'first quarter vs', 'second quarter vs', 'third quarter vs', 'fourth quarter vs',
        'mid-year vs', 'mid year vs', 'midyear vs', 'year to year',
        'growth', 'trend', 'improvement', 'decline', 'increase', 'decrease', 'change',
        'how are we doing', 'how did we do', 'performance', 'results'
    ]
    
    # Check for explicit comparison indicators
    explicit_comparison_indicators = [
        'compare', 'comparison', 'vs', 'versus', 'against', 'side by side', 'year over year',
        'between', 'difference', 'compared to', 'compared with', 'relative to',
        'year to year', 'growth', 'trend', 'improvement', 'decline', 'increase', 'decrease', 'change'
    ]
    
    # Check for specific comparison patterns
    has_explicit_comparison = any(indicator in question_lower for indicator in explicit_comparison_indicators)
    
    # Check for "this year" which should NOT be a comparison
    if 'this year' in question_lower or 'current year' in question_lower:
        return False, [], None, None
    
    # Check for "annual" or "yearly" only if they appear with comparison context
    annual_keywords = ['annual', 'yearly']
    has_annual_keyword = any(keyword in question_lower for keyword in annual_keywords)
    
    # Only treat as comparison if there's explicit comparison language OR annual/yearly with comparison context
    is_comparison = has_explicit_comparison or (has_annual_keyword and any(word in question_lower for word in ['compare', 'comparison', 'vs', 'versus', 'against', 'between', 'difference']))
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

    # Detect monthly comparison
    months = {
        'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
        'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7,
        'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'october': 10, 'oct': 10,
        'november': 11, 'nov': 11, 'december': 12, 'dec': 12
    }
    
    # Check for monthly comparison patterns like "march vs april" or "monthly comparison"
    monthly_indicators = ['monthly comparison', 'monthly vs', 'month vs', 'month comparison']
    has_monthly_indicator = any(indicator in question_lower for indicator in monthly_indicators)
    
    # Also check for month names in comparison
    mentioned_months = []
    for month_name, month_num in months.items():
        if month_name in question_lower:
            mentioned_months.append(month_num)
    
    if has_monthly_indicator or len(mentioned_months) >= 1:
        # If we found month names, use the first one; otherwise use current month
        month = mentioned_months[0] if mentioned_months else datetime.now().month
        
        years = re.findall(r'\b(20\d{2})\b', question)
        if len(years) >= 2:
            return True, [int(years[0]), int(years[1])], 'monthly', month
        elif len(years) == 1:
            y = int(years[0])
            return True, [y-1, y], 'monthly', month
        else:
            return True, [current_year-1, current_year], 'monthly', month

    # Default: annual comparison
    years = re.findall(r'\b(20\d{2})\b', question)
    if len(years) >= 2:
        return True, [int(year) for year in years], 'annual', None
    elif len(years) == 1:
        y = int(years[0])
        return True, [y-1, y], 'annual', None
    else:
        return True, [current_year-1, current_year], 'annual', None

def detect_cross_location_comparison(question: str) -> tuple:
    """Detect if this is a cross-location comparison request and extract campuses to compare"""
    question_lower = question.lower()
    
    logger.info(f"[CROSS_LOCATION_DEBUG] Processing question: '{question}'")
    
    # Check if user has permission for cross-location comparison
    if not current_user.is_authenticated or not current_user.has_permission('cross_location_comparison'):
        logger.info(f"[CROSS_LOCATION_DEBUG] User doesn't have cross_location_comparison permission")
        return False, [], None, None
    
    # Look for cross-location comparison keywords
    cross_location_keywords = [
        'compare', 'vs', 'versus', 'against', 'between', 'difference',
        'south vs', 'barker vs', 'paradise vs', 'adelaide vs', 'salisbury vs',
        'south compared to', 'barker compared to', 'paradise compared to', 'adelaide compared to', 'salisbury compared to',
        'how many', 'did south have', 'did barker have', 'did paradise have', 'did adelaide have', 'did salisbury have',
        'south and', 'barker and', 'paradise and', 'adelaide and', 'salisbury and'
    ]
    
    # Check for explicit cross-location comparison indicators
    has_cross_location_indicator = any(indicator in question_lower for indicator in cross_location_keywords)
    logger.info(f"[CROSS_LOCATION_DEBUG] Has cross-location indicator: {has_cross_location_indicator}")
    
    if not has_cross_location_indicator:
        logger.info(f"[CROSS_LOCATION_DEBUG] No cross-location indicator found")
        return False, [], None, None
    
    # Get all available campuses
    available_campuses = get_campuses_for_user()
    campus_names = [campus['id'] for campus in available_campuses.get('campuses', []) if campus['id'] != 'all_campuses']
    logger.info(f"[CROSS_LOCATION_DEBUG] Available campuses: {campus_names}")
    
    # Get campus detection patterns for better matching
    campus_patterns = get_campus_detection_patterns()
    
    # Detect mentioned campuses in the question
    mentioned_campuses = []
    for campus_id in campus_names:
        # Check if campus name appears in question
        if campus_id.lower() in question_lower:
            mentioned_campuses.append(campus_id)
            logger.info(f"[CROSS_LOCATION_DEBUG] Found campus '{campus_id}' directly in question")
        else:
            # Check campus detection patterns
            if campus_id in campus_patterns:
                pattern = campus_patterns[campus_id]
                if re.search(pattern, question_lower, re.IGNORECASE):
                    mentioned_campuses.append(campus_id)
                    logger.info(f"[CROSS_LOCATION_DEBUG] Found campus '{campus_id}' via pattern")
    
    # Also check for common campus name variations
    campus_variations = {
        'mount_barker': ['barker', 'mt barker', 'mount barker'],
        'south': ['south'],
        'paradise': ['paradise'],
        'adelaide_city': ['adelaide', 'city', 'cbd'],
        'salisbury': ['salisbury']
    }
    
    for campus_id, variations in campus_variations.items():
        if campus_id in campus_names:  # Only check if campus is available to user
            for variation in variations:
                if variation.lower() in question_lower and campus_id not in mentioned_campuses:
                    mentioned_campuses.append(campus_id)
                    logger.info(f"[CROSS_LOCATION_DEBUG] Found campus '{campus_id}' via variation '{variation}'")
                    break
    
    logger.info(f"[CROSS_LOCATION_DEBUG] Mentioned campuses: {mentioned_campuses}")
    
    # If no specific campuses mentioned, return False
    if len(mentioned_campuses) < 2:
        logger.info(f"[CROSS_LOCATION_DEBUG] Not enough campuses mentioned (found {len(mentioned_campuses)})")
        return False, [], None, None
    
    # Detect time period
    current_year = datetime.now().year
    years = re.findall(r'\b(20\d{2})\b', question)
    year = int(years[0]) if years else current_year
    
    # Detect specific stat being compared
    specific_stat = detect_specific_stat_in_comparison(question)
    
    logger.info(f"[CROSS_LOCATION] Detected cross-location comparison: campuses={mentioned_campuses}, year={year}, stat={specific_stat}")
    
    return True, mentioned_campuses, year, specific_stat

def handle_cross_location_comparison(question: str, campuses: list, year: int, specific_stat: str = None) -> dict:
    """Handle cross-location comparison requests between multiple campuses"""
    logger.info(f"[CROSS_LOCATION] handle_cross_location_comparison called with: question={question}, campuses={campuses}, year={year}, specific_stat={specific_stat}")
    
    try:
        # Get data for each campus
        campus_reports = []
        for campus in campuses:
            # Get data for the specific year
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
            
            # Filter rows for this campus and year
            filtered_rows = []
            for row in rows:
                try:
                    if isinstance(row, dict):
                        campus_field = row.get('Campus', '').lower()
                        if campus.lower() in campus_field:
                            timestamp_str = row.get("Timestamp", "")
                            if timestamp_str:
                                if "T" in timestamp_str:
                                    row_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                else:
                                    row_date = parse_any_date(timestamp_str)
                                if start_date <= row_date <= end_date:
                                    filtered_rows.append(row)
                except Exception as e:
                    logger.warning(f"Could not process row: {e}")
                    continue
            
            # Calculate stats for this campus
            if filtered_rows:
                analysis_data = calculate_stats_from_filtered_rows(filtered_rows)
                
                            # Create report for this campus
            campus_report = {
                "campus": display_campus_name(campus),
                "original_campus": campus,  # Keep the original campus name
                "year": year,
                "stats": analysis_data,
                "entry_count": len(filtered_rows)
            }
            campus_reports.append(campus_report)
        
        if not campus_reports:
            return {
                "error": "No data found for the specified campuses and year",
                "text": f"Sorry, I couldn't find data for {', '.join([display_campus_name(c) for c in campuses])} in {year}.",
                "popup": True
            }
        
        # Create comparison table
        comparison_data = []
        stat_mappings = [
            ("total_attendance", "Total Attendance"),
            ("total_first_time_visitors", "First Time Visitors"),
            ("total_new_people", "New People"),
            ("total_new_christians", "New Christians"),
            ("total_rededications", "Rededications"),
            ("total_youth_attendance", "Youth Attendance"),
            ("total_youth_salvations", "Youth Salvations"),
            ("total_youth_new_people", "Youth New People"),
            ("total_kids_attendance", "Kids Attendance"),
            ("total_kids_leaders", "Kids Leaders"),
            ("total_new_kids", "New Kids"),
            ("total_new_kids_salvations", "New Kids Salvations"),
            ("total_connect_groups", "Connect Groups"),
            ("total_dream_team", "Dream Team"),
            ("total_tithe", "Tithe"),
            ("total_baptisms", "Baptisms"),
            ("total_child_dedications", "Child Dedications"),
            ("total_information_gathered", "Information Gathered")
        ]
        
        # If specific stat requested, only include that stat
        if specific_stat:
            stat_mappings = [(f"total_{specific_stat}", specific_stat.replace('_', ' ').title())]
        
        for stat_key, stat_label in stat_mappings:
            row_data = {"stat": stat_label}
            for report in campus_reports:
                # Use the original campus name as the key, not the display name
                campus_name = report["campus"]
                stat_value = report["stats"].get(stat_key, 0)
                # Use the original campus name from the campuses list
                original_campus = next((c for c in campuses if display_campus_name(c) == campus_name), campus_name)
                row_data[original_campus] = stat_value
            comparison_data.append(row_data)
        
        # Create summary text
        campus_names = [display_campus_name(c) for c in campuses]
        if specific_stat:
            summary = f"Comparison of {specific_stat.replace('_', ' ').title()} between {', '.join(campus_names)} in {year}"
        else:
            summary = f"Comparison of all stats between {', '.join(campus_names)} in {year}"
        
        # Create spoken summary
        spoken_summary = f"Here's your comparison between {', '.join(campus_names)} for {year}."
        
        # Debug logging
        logger.info(f"[CROSS_LOCATION] Final response structure:")
        logger.info(f"[CROSS_LOCATION] - campuses: {campuses}")
        logger.info(f"[CROSS_LOCATION] - data rows: {len(comparison_data)}")
        logger.info(f"[CROSS_LOCATION] - first row keys: {list(comparison_data[0].keys()) if comparison_data else 'No data'}")
        logger.info(f"[CROSS_LOCATION] - sample data: {comparison_data[:2] if comparison_data else 'No data'}")
        
        return {
                            "question": question,
                            "comparison": True,
                            "cross_location": True,
                            "campuses": campuses,
                            "year": year,
                            "summary": summary,
                            "data": comparison_data,
                            "text": spoken_summary,
                            "popup": True
                        }
        
    except Exception as e:
        logger.error(f"[CROSS_LOCATION] Error in handle_cross_location_comparison: {e}")
        return {
            "error": "Failed to generate cross-location comparison",
            "text": "Sorry, I couldn't generate that cross-location comparison. Please try a different query.",
            "popup": True
        }

# Handler for mid-year and quarterly comparisons

def query_data_internal(data: Dict[str, Any]) -> Dict[str, Any]:
    """Internal function to query data - handles all types of stat queries with popup support"""
    question = str(data.get("question", "")).strip()
    if not question:
        return {"error": "Missing question"}

    # Extract campus from question using the same detection logic
    campus = detect_campus(question)
    question_lower = question.lower()
    
    # Smart campus defaulting based on user role when no campus is mentioned
    if not campus:
        if current_user.is_authenticated:
            if current_user.role == 'campus_pastor':
                # Campus pastors get their assigned campus by default
                campus = getattr(current_user, 'campus', 'main')
                logger.info(f"[QUERY] No campus mentioned - using campus pastor's campus: {campus}")
            elif current_user.role in ['senior_pastor', 'lead_pastor', 'admin']:
                # Senior leadership gets all campuses by default
                campus = 'all_campuses'
                logger.info(f"[QUERY] No campus mentioned - using all campuses for senior leadership")
            else:
                # Other roles default to main or all_campuses
                campus = 'all_campuses'
                logger.info(f"[QUERY] No campus mentioned - defaulting to all campuses")
        else:
            campus = 'all_campuses'
    else:
        logger.info(f"[QUERY] Campus detected from question: {campus}")
    
    logger.info(f"[QUERY] Processing question: '{question}' | Final Campus: {campus}")
    
    # 1. CROSS-LOCATION COMPARISON REQUESTS - CHECK FIRST
    is_cross_location, campuses, year, specific_stat = detect_cross_location_comparison(question)
    
    if is_cross_location:
        result = handle_cross_location_comparison(question, campuses, year, specific_stat)
        
        # Ensure the response has the correct format for the frontend
        if result.get('comparison'):
            # Add popup flag for comparison results
            result['popup'] = True
            return result
        else:
            logger.error(f"[QUERY] Cross-location comparison failed to return proper format")
            return {
                "error": "Failed to generate cross-location comparison",
                "text": "Sorry, I couldn't generate that cross-location comparison. Please try a different query.",
                "popup": True
            }

    # 2. COMPARISON REQUESTS (Year over year, quarterly, etc.)
    is_comparison, years, period_type, period_value = detect_comparison_request(question)
    if is_comparison:
        logger.info(f"[QUERY] Detected comparison: years={years}, period={period_type}, value={period_value}")
        campus = detect_campus(question) or campus or "main"
        
        # Add comprehensive logging
        logger.info(f"[QUERY] Processing comparison for campus: {campus}")
        logger.info(f"[QUERY] Question: '{question}'")
        
        result = handle_period_comparison_request(question, campus, years, period_type, period_value)
        
        # Ensure the response has the correct format for the frontend
        if result.get('comparison'):
            # Add popup flag for comparison results
            result['popup'] = True
            logger.info(f"[QUERY] Comparison result keys: {list(result.keys())}")
            return result
        else:
            logger.error(f"[QUERY] Comparison failed to return proper format")
            return {
                "error": "Failed to generate comparison",
                "text": "Sorry, I couldn't generate that comparison. Please try a different query.",
                "popup": True
            }

    # 2. REVIEW INTENTS (Annual, Quarterly, Mid-Year Reviews)
    if is_review_intent(question):
        logger.info(f"[QUERY] Detected review intent")
        campus = detect_campus(question) or campus or "main"
        import re
        years = re.findall(r'\b(20\d{2})\b', question)
        if len(years) == 0:
            years = [datetime.now().year]
        elif len(years) == 1:
            years = [int(y) for y in years]
        else:
            years = [int(y) for y in years]
        # Check if this is a cross-campus request
        if campus == "all_campuses" or any(indicator in question_lower for indicator in ['all campuses', 'futures church', 'church wide', 'across all']):  
            # Detect specific review type for cross-campus
            review_type, period_value, year = detect_review_type(question)
            year = years[0] if years else year  # Use detected year or default
            
            # Map review types to cross-campus report types
            if review_type == "quarterly":
                cross_campus_report = generate_cross_campus_report('quarterly', f"Q{period_value} {year}")
                spoken_summary = f"Here's your Q{period_value} {year} quarterly review for All Campuses."
            elif review_type == "monthly":
                month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                              'July', 'August', 'September', 'October', 'November', 'December']
                month_name = month_names[period_value]
                cross_campus_report = generate_cross_campus_report('monthly', f"{month_name} {year}")
                spoken_summary = f"Here's your {month_name} {year} monthly review for All Campuses."
            elif review_type == "mid_year":
                cross_campus_report = generate_cross_campus_report('mid_year', f"Jan-Jun {year}")
                spoken_summary = f"Here's your {year} mid-year review for All Campuses."
            else:
                # Default to annual
                cross_campus_report = generate_cross_campus_report('annual', "")
                spoken_summary = f"Here's your annual review for All Campuses campus in {year}."
            
            stats = cross_campus_report.get('stats', {})
            
            # Create report format for popup
            report_data = [
                {"label": "Total Attendance", "total": stats.get('attendance', {}).get('total', 0), "average": stats.get('attendance', {}).get('average', 0), "count": cross_campus_report.get('entry_count', 0), "year": year},
                {"label": "New People", "total": stats.get('new_people', {}).get('total', 0), "average": stats.get('new_people', {}).get('average', 0), "count": cross_campus_report.get('entry_count', 0), "year": year},
                {"label": "New Christians", "total": stats.get('new_christians', {}).get('total', 0), "average": stats.get('new_christians', {}).get('average', 0), "count": cross_campus_report.get('entry_count', 0), "year": year},
                {"label": "Youth Attendance", "total": stats.get('youth', {}).get('total', 0), "average": stats.get('youth', {}).get('average', 0), "count": cross_campus_report.get('entry_count', 0), "year": year},
                {"label": "Kids Total", "total": stats.get('kids', {}).get('total', 0), "average": stats.get('kids', {}).get('average', 0), "count": cross_campus_report.get('entry_count', 0), "year": year},
                {"label": "Connect Groups", "total": stats.get('connect_groups', {}).get('total', 0), "average": stats.get('connect_groups', {}).get('average', 0), "count": cross_campus_report.get('entry_count', 0), "year": year},
                {"label": "Volunteers", "total": 0, "average": 0, "count": 0, "year": year}  # Volunteers not tracked in cross-campus yet
            ]
            
            return {
                "report": report_data,
                "text": spoken_summary,
                "popup": True,
                "stats": stats,
                "campus": "All Campuses",
                "year": year
            }
        else:
            # Single campus review - detect specific review type
            review_type, period_value, year = detect_review_type(question)
            year = years[0] if years else year  # Use detected year or default
            
            if review_type == "quarterly":
                report = generate_quarterly_report(campus, year, period_value)
            elif review_type == "monthly":
                report = generate_monthly_report(campus, year, period_value)
            elif review_type == "mid_year":
                report = generate_mid_year_report(campus, year)
            else:
                # Default to annual review
                report = generate_full_stat_report(campus, [year])
            
            report["popup"] = True  # Enable popup for reviews
            return report

    # 2. WEEKEND REVIEWS
    if any(phrase in question_lower for phrase in WEEKEND_REVIEW_PHRASES):
        logger.info(f"[QUERY] Detected weekend review")
        
        # First check for pastor names (priority over campus detection)
        pastor_campus = detect_pastor_name(question)
        if pastor_campus:
            campus = pastor_campus
            logger.info(f"[QUERY] Pastor detected - using campus: {campus}")
        else:
            campus = detect_campus(question)
            logger.info(f"[QUERY] No pastor detected - using campus detection: {campus}")
        if campus and campus != "all_campuses":
            # Campus-specific weekend review
            start_date = datetime.now() - timedelta(days=7)
            end_date = datetime.now()
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
            
            logger.info(f"[WEEKEND_REVIEW] Found {len(rows)} total rows, {len(filtered_rows)} filtered rows for {campus} in last 7 days")
            analysis_data = calculate_stats_from_filtered_rows(filtered_rows)
            logger.info(f"[WEEKEND_REVIEW] Analysis data: {analysis_data}")
            
            # Check if we have any data
            has_data = (analysis_data.get('total_entries', 0) > 0 or 
                       any(analysis_data.get(key, 0) > 0 for key in ['total_attendance', 'total_new_people', 'total_new_christians', 'total_youth', 'total_kids', 'total_connect_groups']))
            
            if has_data:
                # Create detailed summary for display
                detailed_summary = (
                    f"{display_campus_name(campus)} Weekend Review\n"
                    f"Total Attendance: {analysis_data.get('total_attendance', 0):,}\n"
                    f"New People: {analysis_data.get('total_new_people', 0):,}\n"
                    f"New Christians: {analysis_data.get('total_new_christians', 0):,}\n"
                    f"Youth: {analysis_data.get('total_youth', 0):,}\n"
                    f"Kids: {analysis_data.get('total_kids', 0):,}\n"
                    f"Connect Groups: {analysis_data.get('total_connect_groups', 0):,}"
                )
                
                # Create spoken summary 
                spoken_summary = f"Here's your weekend review for {display_campus_name(campus)} campus."
            else:
                # No data found
                detailed_summary = (
                    f"{display_campus_name(campus)} Weekend Review\n"
                    f"No stats have been logged for {display_campus_name(campus)} campus in the last 7 days.\n"
                    f"This could mean:\n"
                    f"• Stats haven't been entered yet for this weekend\n"
                    f"• The campus name might not match our records\n"
                    f"• There was no service this weekend"
                )
                
                # Create spoken summary 
                spoken_summary = f"I couldn't find any weekend stats for {display_campus_name(campus)} campus in the last 7 days. You may need to enter the stats first or check if the campus name is correct."
            
            # Create comprehensive report with all available stats
            report = []
            stat_mappings = [
                ("total_attendance", "Total Attendance", "attendance"),
                ("total_first_time_visitors", "First Time Visitors", "first_time_visitors"),
                ("total_information_gathered", "Information Gathered", "information_gathered"),
                ("total_new_christians", "New Christians", "new_christians"),
                ("total_rededications", "Rededications", "rededications"),
                ("total_youth_attendance", "Youth Attendance", "youth_attendance"),
                ("total_youth_salvations", "Youth Salvations", "youth_salvations"),
                ("total_youth_new_people", "Youth New People", "youth_new_people"),
                ("total_kids_attendance", "Kids Attendance", "kids_attendance"),
                ("total_kids_leaders", "Kids Leaders", "kids_leaders"),
                ("total_new_kids", "New Kids", "new_kids"),
                ("total_new_kids_salvations", "New Kids Salvations", "new_kids_salvations"),
                ("total_connect_groups", "Connect Groups", "connect_groups"),
                ("total_dream_team", "Dream Team", "dream_team"),
                ("total_tithe", "Tithe", "tithe"),
                ("total_baptisms", "Baptisms", "baptisms"),
                ("total_child_dedications", "Child Dedications", "child_dedications"),
                ("total_new_people", "New People", "new_people"),  # Keep for backward compatibility
            ]
            
            for stat_key, label, avg_key in stat_mappings:
                total = analysis_data.get(stat_key, 0)
                average = analysis_data.get("averages", {}).get(avg_key, 0)
                count = analysis_data.get("total_entries", 0)
                
                # Only include stats that have data or are important to show
                if total > 0 or label in ["Total Attendance", "New Christians", "Youth Attendance", "Kids Attendance", "Connect Groups", "Dream Team"]:
                    report.append({
                        "label": label,
                        "total": total,
                        "average": average,
                        "count": count,
                        "year": start_date.year
                    })
            return {
                "question": question,
                "campus": display_campus_name(campus),
                "date_range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "summary": detailed_summary,
                "stats": analysis_data,
                "report": report,
                "text": spoken_summary,
                "popup": True
            }
        else:
            # Cross-campus weekend review
            logger.info(f"[WEEKEND_REVIEW] Processing cross-campus weekend review")
            report = generate_cross_campus_report('weekly', "")
            logger.info(f"[WEEKEND_REVIEW] Cross-campus report: {report}")
            stats = report.get('stats', {})
            
            # Create detailed summary for display
            detailed_summary = (
                f"Futures Church Weekend Review\n"
                f"Total Attendance: {stats.get('attendance', {}).get('total', 0):,}\n"
                f"Average Attendance: {stats.get('attendance', {}).get('average', 0):,.1f}\n"
                f"New People: {stats.get('new_people', {}).get('total', 0):,}\n"
                f"New Christians: {stats.get('new_christians', {}).get('total', 0):,}\n"
                f"Youth: {stats.get('youth', {}).get('total', 0):,}\n"
                f"Kids: {stats.get('kids', {}).get('total', 0):,}\n"
                f"Connect Groups: {stats.get('connect_groups', {}).get('total', 0):,}"
            )
            
            # Create spoken summary
            spoken_summary = f"Here's your weekend review for Futures Church across all campuses."
            return {
                "question": question,
                "campus": "Futures Church (All Campuses)",
                "date_range": report.get('date_range', ''),
                "summary": detailed_summary,
                "stats": stats,
                "report": report,
                "text": spoken_summary,
                "popup": True
            }

    # 3. CROSS-CAMPUS REVIEWS
    cross_campus_result = detect_cross_campus_review(question)
    if cross_campus_result:
        review_type, _ = cross_campus_result
        logger.info(f"[QUERY] Detected cross-campus review: {review_type}")
        report = generate_cross_campus_report(review_type, "")
        stats = report.get('stats', {})
        
        # Create comprehensive summary
        summary = f"Futures Church {review_type.title()} Report\n"
        summary += f"Total Attendance: {stats.get('attendance', {}).get('total', 0):,}\n"
        summary += f"Average Attendance: {stats.get('attendance', {}).get('average', 0):,.1f}\n"
        summary += f"New People: {stats.get('new_people', {}).get('total', 0):,}\n"
        summary += f"New Christians: {stats.get('new_christians', {}).get('total', 0):,}\n"
        summary += f"Youth: {stats.get('youth', {}).get('total', 0):,}\n"
        summary += f"Kids: {stats.get('kids', {}).get('total', 0):,}\n"
        summary += f"Connect Groups: {stats.get('connect_groups', {}).get('total', 0):,}"
        
        # Convert to report format for popup
        report_data = [
            {"label": "Total Attendance", "total": stats.get('attendance', {}).get('total', 0), "average": stats.get('attendance', {}).get('average', 0), "count": report.get('entry_count', 0), "year": datetime.now().year},
            {"label": "New People", "total": stats.get('new_people', {}).get('total', 0), "average": stats.get('new_people', {}).get('average', 0), "count": report.get('entry_count', 0), "year": datetime.now().year},
            {"label": "New Christians", "total": stats.get('new_christians', {}).get('total', 0), "average": stats.get('new_christians', {}).get('average', 0), "count": report.get('entry_count', 0), "year": datetime.now().year},
            {"label": "Youth", "total": stats.get('youth', {}).get('total', 0), "average": stats.get('youth', {}).get('average', 0), "count": report.get('entry_count', 0), "year": datetime.now().year},
            {"label": "Kids", "total": stats.get('kids', {}).get('total', 0), "average": stats.get('kids', {}).get('average', 0), "count": report.get('entry_count', 0), "year": datetime.now().year},
            {"label": "Connect Groups", "total": stats.get('connect_groups', {}).get('total', 0), "average": stats.get('connect_groups', {}).get('average', 0), "count": report.get('entry_count', 0), "year": datetime.now().year},
        ]
        
        return {
            "question": question,
            "campus": "Futures Church (All Campuses)",
            "date_range": report.get('date_range', ''),
            "summary": summary,
            "stats": stats,
            "report": report_data,
            "text": summary,
            "popup": True
        }

    # 5. SIMPLE STAT QUERIES (How many people, what was attendance, etc.)
    # First check for multiple stats (e.g., "np and nc")
    multiple_stats = detect_multiple_stats(question)
    simple_stat_result = detect_simple_stat_query(question)
    
    if multiple_stats:
        logger.info(f"[QUERY] Detected multiple stat query: {multiple_stats}")
        stat_types = multiple_stats
        keyword = "multiple stats"
    elif simple_stat_result:
        stat_type, keyword = simple_stat_result
        stat_types = [stat_type]  # Convert to list for consistency
        logger.info(f"[QUERY] Detected simple stat query: {stat_type} (keyword: {keyword})")
    else:
        stat_types = None
        keyword = None
    
    if stat_types:
        
        # Default campus if none detected
        if not campus or campus == "all_campuses":
            campus = "main"
        
        # Parse date range from question
        start_date, end_date, date_range_text = parse_date_range(question)
        
        # Get data
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
        
        # Handle cross-campus queries
        if campus == "all_campuses" or any(indicator in question_lower for indicator in ['all campuses', 'futures church', 'church wide', 'across all']):
            # Cross-campus simple stat query
            analysis_data = get_all_campuses_data(rows, start_date, end_date)
            campus_display = "Futures Church (All Campuses)"
            
            # Calculate cross-campus totals
            total_attendance = sum(safe_int(row.get('Total Attendance', 0)) for row in analysis_data)
            total_new_people = sum(safe_int(row.get('New People', 0)) for row in analysis_data)
            total_new_christians = sum(safe_int(row.get('New Christians', 0)) for row in analysis_data)
            total_youth = sum(safe_int(row.get('Youth Attendance', 0)) for row in analysis_data)
            total_kids = sum(safe_int(row.get('Kids Total', 0)) for row in analysis_data)
            total_connect_groups = sum(safe_int(row.get('Connect Groups', 0)) for row in analysis_data)
            
            # Calculate averages
            valid_entries = len([row for row in analysis_data if safe_int(row.get('Total Attendance', 0)) > 0])
            avg_attendance = total_attendance / valid_entries if valid_entries > 0 else 0
            avg_new_people = total_new_people / valid_entries if valid_entries > 0 else 0
            avg_new_christians = total_new_christians / valid_entries if valid_entries > 0 else 0
            avg_youth = total_youth / valid_entries if valid_entries > 0 else 0
            avg_kids = total_kids / valid_entries if valid_entries > 0 else 0
            avg_connect_groups = total_connect_groups / valid_entries if valid_entries > 0 else 0
            
            cross_campus_data = {
                'total_attendance': total_attendance,
                'total_new_people': total_new_people,
                'total_new_christians': total_new_christians,
                'total_youth': total_youth,
                'total_kids': total_kids,
                'total_connect_groups': total_connect_groups,
                'averages': {
                    'attendance': avg_attendance,
                    'new_people': avg_new_people,
                    'new_christians': avg_new_christians,
                    'youth': avg_youth,
                    'kids': avg_kids,
                    'connect_groups': avg_connect_groups
                }
            }
            
            answer = generate_simple_stat_answer(stat_types[0], cross_campus_data, campus_display, f" {date_range_text}")
            
            # Create targeted report data for popup - only show the requested stat(s)
            report_data = create_targeted_report_data(stat_types, cross_campus_data, start_date.year, valid_entries)
            
            return {
                "question": question,
                "campus": campus_display,
                "date_range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "answer": answer,
                "text": answer,
                "stats": cross_campus_data,
                "report": report_data,
                "popup": True
            }
        else:
            # Single campus simple stat query
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
            
            analysis_data = calculate_stats_for_year_range(filtered_rows, campus, start_date.year, end_date.year if end_date.year != start_date.year else None)
            answer = generate_simple_stat_answer(stat_types[0], analysis_data, display_campus_name(campus), f" {date_range_text}")
            
            # Create targeted report data for popup - only show the requested stat(s)
            report_data = create_targeted_report_data(stat_types, analysis_data, start_date.year, analysis_data.get("total_entries", 0))
            
            return {
                "question": question,
                "campus": display_campus_name(campus),
                "date_range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "answer": answer,
                "text": answer,
                "stats": analysis_data,
                "report": report_data,
                "popup": True
            }

    # 6. GENERAL/BIG PICTURE QUERIES
    general_patterns = [
        'summary', 'all numbers', 'big picture', 'overview', 'all stats', 'full stats',
        'church numbers', 'show me everything', 'what are our numbers', 'church stats'
    ]
    
    if any(pattern in question_lower for pattern in general_patterns):
        logger.info(f"[QUERY] Detected general/big picture query")
        
        # Default to current year if no specific period mentioned
        if not campus or campus == "all_campuses":
            campus = "main"
        
        start_date, end_date, date_range_text = parse_date_range(question)
        
        # Get data and calculate comprehensive stats
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
        
        # Filter by campus and date
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
                            row_date = parse_any_date(timestamp_str)
                        if start_date <= row_date <= end_date:
                            filtered_rows.append(row)
                    except Exception:
                        continue
        
        analysis_data = calculate_stats_for_year_range(filtered_rows, campus, start_date.year, end_date.year if end_date.year != start_date.year else None)
        
        # Create comprehensive summary
        campus_display = display_campus_name(campus)
        summary = f"{campus_display} Church Stats ({date_range_text})\n\n"
        summary += f"📊 Attendance: {analysis_data.get('total_attendance', 0):,} total (avg: {analysis_data.get('averages', {}).get('attendance', 0):.1f})\n"
        summary += f"👥 New People: {analysis_data.get('total_new_people', 0):,} total (avg: {analysis_data.get('averages', {}).get('new_people', 0):.1f})\n"
        summary += f"✝️ New Christians: {analysis_data.get('total_new_christians', 0):,} total (avg: {analysis_data.get('averages', {}).get('new_christians', 0):.1f})\n"
        summary += f"🎯 Youth: {analysis_data.get('total_youth', 0):,} total (avg: {analysis_data.get('averages', {}).get('youth', 0):.1f})\n"
        summary += f"👶 Kids: {analysis_data.get('total_kids', 0):,} total (avg: {analysis_data.get('averages', {}).get('kids', 0):.1f})\n"
        summary += f"🤝 Connect Groups: {analysis_data.get('total_connect_groups', 0):,} total (avg: {analysis_data.get('averages', {}).get('connect_groups', 0):.1f})"
        
        # Create report data for popup
        report_data = [
            {"label": "Total Attendance", "total": analysis_data.get("total_attendance", 0), "average": analysis_data.get("averages", {}).get("attendance", 0), "count": analysis_data.get("total_entries", 0), "year": start_date.year},
            {"label": "New People", "total": analysis_data.get("total_new_people", 0), "average": analysis_data.get("averages", {}).get("new_people", 0), "count": analysis_data.get("total_entries", 0), "year": start_date.year},
            {"label": "New Christians", "total": analysis_data.get("total_new_christians", 0), "average": analysis_data.get("averages", {}).get("new_christians", 0), "count": analysis_data.get("total_entries", 0), "year": start_date.year},
            {"label": "Youth", "total": analysis_data.get("total_youth", 0), "average": analysis_data.get("averages", {}).get("youth", 0), "count": analysis_data.get("total_entries", 0), "year": start_date.year},
            {"label": "Kids", "total": analysis_data.get("total_kids", 0), "average": analysis_data.get("averages", {}).get("kids", 0), "count": analysis_data.get("total_entries", 0), "year": start_date.year},
            {"label": "Connect Groups", "total": analysis_data.get("total_connect_groups", 0), "average": analysis_data.get("averages", {}).get("connect_groups", 0), "count": analysis_data.get("total_entries", 0), "year": start_date.year},
        ]
        
        return {
            "question": question,
            "campus": campus_display,
            "date_range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "answer": summary,
            "text": summary,
            "stats": analysis_data,
            "report": report_data,
            "popup": True
        }

    # 7. AI INSIGHTS for complex questions
    if any(word in question_lower for word in ['trend', 'trends', 'pattern', 'growth', 'improve', 'attention', 'working', 'analysis', 'insight', 'why', 'how are we', 'what areas']):
        logger.info(f"[QUERY] Detected AI insights query")
        
        if not campus or campus == "all_campuses":
            campus = "main"
        
        start_date, end_date, date_range_text = parse_date_range(question)
        
        # Get and filter data
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
                            row_date = parse_any_date(timestamp_str)
                        if start_date <= row_date <= end_date:
                            filtered_rows.append(row)
                    except Exception:
                        continue
        
        analysis_data = calculate_stats_for_year_range(filtered_rows, campus, start_date.year, end_date.year if end_date.year != start_date.year else None)
        ai_insights = generate_ai_insights(question, campus, analysis_data, filtered_rows)
        
        # Create report data for popup
        report_data = [
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
            "answer": ai_insights,
            "text": ai_insights,
            "insights": [ai_insights],
            "stats": analysis_data,
            "report": report_data,
            "popup": True
        }

    # 8. FALLBACK: Default response for unrecognized queries
    logger.info(f"[QUERY] No specific pattern matched, using fallback")
    return {
        "error": f"I'm not sure how to answer '{question}'. Try asking for specific stats like 'How many people attended this month?' or 'Show me the annual report for South campus'."
    }

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
    
    if any(word in question_lower for word in ['trend', 'trends', 'pattern', 'growth', 'improve', 'attention', 'working', 'analysis', 'insight', 'why', 'how are we', 'what areas']):
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
    
    # Monthly review detection
    monthly_patterns = [
        r'\bmonthly review\b', r'\bmonth review\b', r'\bmonthly report\b', r'\bmonth report\b',
        r'\bmonthly summary\b', r'\bmonth summary\b', r'\bmonthly stats\b', r'\bmonth stats\b',
        r'\bmonthly statistics\b', r'\bmonth statistics\b', r'\bmonthly numbers\b', r'\bmonth numbers\b',
        r'\bmonthly data\b', r'\bmonth data\b', r'\bmonthly recap\b', r'\bmonth recap\b',
        r'\bmonthly overview\b', r'\bmonth overview\b', r'\bmonthly dashboard\b', r'\bmonth dashboard\b',
        r'\bjanuary review\b', r'\bfebruary review\b', r'\bmarch review\b', r'\bapril review\b',
        r'\bmay review\b', r'\bjune review\b', r'\bjuly review\b', r'\baugust review\b',
        r'\bseptember review\b', r'\boctober review\b', r'\bnovember review\b', r'\bdecember review\b',
        r'\bjanuary report\b', r'\bfebruary report\b', r'\bmarch report\b', r'\bapril report\b',
        r'\bmay report\b', r'\bjune report\b', r'\bjuly report\b', r'\baugust report\b',
        r'\bseptember report\b', r'\boctober report\b', r'\bnovember report\b', r'\bdecember report\b'
    ]
    
    for pattern in monthly_patterns:
        if re.search(pattern, q):
            # Extract month number
            months = {
                'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
                'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7,
                'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'october': 10, 'oct': 10,
                'november': 11, 'nov': 11, 'december': 12, 'dec': 12
            }
            
            month = None
            for month_name, month_num in months.items():
                if month_name in q or month_name[:3] in q:
                    month = month_num
                    break
            
            # If no specific month found, default to current month
            if month is None:
                month = datetime.now().month
                
            # Extract year
            years = re.findall(r'\b(20\d{2})\b', question)
            year = int(years[0]) if years else datetime.now().year
            
            return "monthly", month, year

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
    """Check if the question is asking for a review (but not a comparison or weekend review)"""
    # First check if this is a comparison request - if so, it's not a review intent
    is_comparison, _, _, _ = detect_comparison_request(question)
    if is_comparison:
        return False
    
    # Check if this is a weekend review - if so, it's not a general review intent
    question_lower = question.lower()
    if any(phrase in question_lower for phrase in WEEKEND_REVIEW_PHRASES):
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

def generate_monthly_report(campus: str, year: int, month: int) -> dict:
    """Generate a monthly report for a specific month and year"""
    # Calculate month date range
    if month == 12:
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, 31)
    else:
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    
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
                    filtered_rows.append(row)
            else:
                filtered_rows.append(row)
    
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
    
    month_names = [
        '', 'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    for stat_type, stat_label, _ in stat_types:
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
            "month": month,
            "period": "monthly",
            "campus": display_campus_name(campus),
            "total": total,
            "average": round(avg, 1),
            "count": entry_count
        })
    
    # Generate spoken summary
    month_name = month_names[month]
    spoken_summary = f"Here's your {month_name} {year} monthly report for {display_campus_name(campus)} campus."
    
    return {
        "report": results,
        "text": spoken_summary,
        "review_type": "monthly",
        "month": month,
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
    # List of all stat types to include - comprehensive list
    stat_types = [
        ('attendance', 'Total Attendance', 'attendance'),
        ('first_time_visitors', 'First Time Visitors', 'first_time_visitors'),
        ('information_gathered', 'Information Gathered', 'information_gathered'),
        ('new_christians', 'New Christians', 'new_christians'),
        ('rededications', 'Rededications', 'rededications'),
        ('youth_attendance', 'Youth Attendance', 'youth_attendance'),
        ('youth_salvations', 'Youth Salvations', 'youth_salvations'),
        ('youth_new_people', 'Youth New People', 'youth_new_people'),
        ('kids_attendance', 'Kids Attendance', 'kids_attendance'),
        ('kids_leaders', 'Kids Leaders', 'kids_leaders'),
        ('new_kids', 'New Kids', 'new_kids'),
        ('new_kids_salvations', 'New Kids Salvations', 'new_kids_salvations'),
        ('connect_groups', 'Connect Groups', 'connect_groups'),
        ('dream_team', 'Dream Team', 'dream_team'),
        ('tithe', 'Tithe', 'tithe'),
        ('baptisms', 'Baptisms', 'baptisms'),
        ('child_dedications', 'Child Dedications', 'child_dedications'),
        ('new_people', 'New People', 'new_people'),  # Keep for backward compatibility
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
            # Get total and average from the calculated stats
            total = year_stats.get(f'total_{stat_type}', 0)
            avg = year_stats.get('averages', {}).get(stat_type, 0)
            count = year_stats.get('total_entries', 0)
            
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

def generate_targeted_comparison_report(campus: str, year: int, period_type: str, period_value: Optional[int], specific_stat: str) -> dict:
    """Generate a targeted report with only the specific stat for comparison"""
    # Generate the full report first
    if period_type == 'mid_year':
        full_report = generate_mid_year_report(campus, year)
    elif period_type == 'quarterly' and period_value:
        full_report = generate_quarterly_report(campus, year, period_value)
    elif period_type == 'monthly' and period_value:
        full_report = generate_monthly_report(campus, year, period_value)
    else:
        full_report = generate_full_stat_report(campus, [year])
    
    # Filter to only include the specific stat
    filtered_report = []
    for stat_entry in full_report.get('report', []):
        if stat_entry.get('stat') == specific_stat:
            filtered_report.append(stat_entry)
            break
    
    # Return the report with only the specific stat
    result = full_report.copy()
    result['report'] = filtered_report
    return result

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
            if specific_stat:
                # Generate targeted report with only the specific stat
                report = generate_targeted_comparison_report(campus, year, period_type, period_value, specific_stat)
            else:
                # Generate full report with all stats
                if period_type == 'mid_year':
                    report = generate_mid_year_report(campus, year)
                elif period_type == 'quarterly' and period_value:
                    report = generate_quarterly_report(campus, year, period_value)
                elif period_type == 'monthly' and period_value:
                    report = generate_monthly_report(campus, year, period_value)
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
        
        # Fill missing stats for both reports (only if not specific stat)
        if not specific_stat:
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

def calculate_stats_from_filtered_rows(filtered_rows: List[dict]) -> dict:
    """Calculate stats from already filtered rows without additional filtering"""
    # Initialize all stat totals
    stats = {
        'attendance': 0,
        'first_time_visitors': 0,
        'information_gathered': 0,
        'new_christians': 0,
        'rededications': 0,
        'youth_attendance': 0,
        'youth_salvations': 0,
        'youth_new_people': 0,
        'kids_attendance': 0,
        'kids_leaders': 0,
        'new_kids': 0,
        'new_kids_salvations': 0,
        'connect_groups': 0,
        'dream_team': 0,
        'tithe': 0,
        'baptisms': 0,
        'child_dedications': 0,
        'new_people': 0  # Keep for backward compatibility
    }
    
    # Track values for average calculation
    averages = {}
    entry_count = 0
    
    for entry in filtered_rows:
        if isinstance(entry, dict):
            def safe_int_stat(val):
                try:
                    if val is None or val == '':
                        return 0
                    return int(str(val).replace(',', '').strip())
                except Exception:
                    return 0
            
            # Extract all available stats with flexible field name matching
            def get_stat_value(field_names):
                """Get stat value from multiple possible field names"""
                for field_name in field_names:
                    value = entry.get(field_name)
                    if value is not None and value != '':
                        return safe_int_stat(value)
                return 0
            
            stat_values = {
                'attendance': get_stat_value(['Total Attendance']),
                'first_time_visitors': get_stat_value(['First Time Visitors']),
                'information_gathered': get_stat_value(['Information Gathered']),
                'new_christians': get_stat_value(['First Time Christians', 'New Christians']),
                'rededications': get_stat_value(['Rededications']),
                'youth_attendance': get_stat_value(['Youth Attendance']),
                'youth_salvations': get_stat_value(['Youth Salvations']),
                'youth_new_people': get_stat_value(['Youth New People']),
                'kids_attendance': get_stat_value(['Kids Attendance', 'Kids Total']),
                'kids_leaders': get_stat_value(['Kids Leaders']),
                'new_kids': get_stat_value(['New Kids']),
                'new_kids_salvations': get_stat_value(['New Kids Salvations']),
                'connect_groups': get_stat_value(['Connect Groups']),
                'dream_team': get_stat_value(['Dream Team']),
                'tithe': get_stat_value(['Tithe']),
                'baptisms': get_stat_value(['Baptisms']),
                'child_dedications': get_stat_value(['Child Dedications']),
                'new_people': get_stat_value(['New People'])  # Keep for backward compatibility
            }
            
            # Only count entries with at least one stat
            if any(stat_values.values()):
                entry_count += 1
            
            # Add to totals
            for stat_name, value in stat_values.items():
                stats[f'total_{stat_name}'] = stats.get(f'total_{stat_name}', 0) + value
                
                # Track for averages (only if > 0)
                if value > 0:
                    if stat_name not in averages:
                        averages[stat_name] = []
                    averages[stat_name].append(value)
    
    # Calculate averages
    avg_stats = {}
    for stat_name, values in averages.items():
        if values:
            avg_stats[stat_name] = round(sum(values) / len(values), 1)
        else:
            avg_stats[stat_name] = 0
    
    return {
        "total_entries": entry_count,
        **stats,
        "averages": avg_stats
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
    
    # Use the comprehensive calculate_stats_from_filtered_rows function
    stats = calculate_stats_from_filtered_rows(filtered_rows)
    stats["year"] = start_year
    return stats

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

def get_weekly_campus_comparison_data():
    """Get weekly comparison data across all campuses for senior leaders/admins (always last 7 days)"""
    try:
        if not sheet:
            return []
        
        # Get all records
        rows = sheet.get_all_records()
        if not rows:
            return []
        
        # Always use last 7 days for weekly comparison
        now = datetime.now()
        start_date = now - timedelta(days=7)
        end_date = now
        
        # Get active campuses (excluding 'all_campuses' special entry)
        campuses_db = load_campuses_database()
        active_campuses = []
        for campus_id, campus_info in campuses_db.get('campuses', {}).items():
            if campus_info.get('active', False) and not campus_info.get('special', False):
                active_campuses.append({
                    'id': campus_id,
                    'name': campus_info.get('display_name', campus_id),
                    'full_name': campus_info.get('name', campus_id)
                })
        
        comparison_data = []
        
        for campus_info in active_campuses:
            campus_id = campus_info['id']
            campus_name = campus_info['name']
            
            # Filter rows for this campus
            campus_normalized = normalize_campus(campus_id)
            campus_rows = []
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
                                campus_rows.append(row)
                        except Exception:
                            continue
            
            # Calculate campus stats
            total_attendance = 0
            total_new_people = 0
            total_new_christians = 0
            total_dream_team = 0
            entry_count = 0
            
            for row in campus_rows:
                total_attendance += safe_int(row.get('Total Attendance', 0))
                total_new_people += safe_int(row.get('New People', 0))
                total_new_christians += safe_int(row.get('New Christians', 0))
                total_dream_team += safe_int(row.get('Dream Team', 0))
                entry_count += 1
            
            # Calculate Dream Team percentage (dream team as % of attendance)
            dream_team_percentage = (total_dream_team / total_attendance * 100) if total_attendance > 0 else 0
            
            # Determine status based on performance
            status = determine_campus_status(total_attendance, total_new_people, total_new_christians, dream_team_percentage, entry_count)
            
            comparison_data.append({
                'campus': campus_name,
                'attendance': total_attendance,
                'new_people': total_new_people,
                'salvations': total_new_christians,
                'dream_team_percent': round(dream_team_percentage, 1),
                'status': status,
                'entries': entry_count
            })
        
        # Sort by attendance (highest first)
        comparison_data.sort(key=lambda x: x['attendance'], reverse=True)
        
        return comparison_data
        
    except Exception as e:
        logger.error(f"Campus comparison data error: {e}")
        return []

def determine_campus_status(attendance, new_people, salvations, dream_team_percent, entries):
    """Determine campus status based on performance metrics"""
    if entries == 0:
        return "No Data"
    
    # Calculate performance score (out of 100)
    score = 0
    
    # Attendance factor (30% of score)
    if attendance >= 400:
        score += 30
    elif attendance >= 200:
        score += 20
    elif attendance >= 100:
        score += 15
    else:
        score += 5
    
    # New People factor (25% of score)
    avg_new_people = new_people / entries if entries > 0 else 0
    if avg_new_people >= 8:
        score += 25
    elif avg_new_people >= 5:
        score += 20
    elif avg_new_people >= 2:
        score += 15
    else:
        score += 5
    
    # Salvations factor (25% of score)
    avg_salvations = salvations / entries if entries > 0 else 0
    if avg_salvations >= 3:
        score += 25
    elif avg_salvations >= 1:
        score += 20
    elif avg_salvations >= 0.5:
        score += 15
    else:
        score += 5
    
    # Dream Team factor (20% of score)
    if dream_team_percent >= 30:
        score += 20
    elif dream_team_percent >= 25:
        score += 15
    elif dream_team_percent >= 20:
        score += 10
    else:
        score += 5
    
    # Determine status based on total score
    if score >= 85:
        return "Excellent"
    elif score >= 65:
        return "Good"
    elif score >= 45:
        return "Fair"
    else:
        return "Needs Attention"

# Insights function removed - will be rebuilt from scratch

def calculate_date_range(date_filter, custom_start_date, custom_end_date, now):
    """Calculate start and end dates based on filter type"""
    try:
        if date_filter == 'last_7_days':
            start_date = now - timedelta(days=7)
            end_date = now
        elif date_filter == 'last_30_days':
            start_date = now - timedelta(days=30)
            end_date = now
        elif date_filter == 'last_90_days':
            start_date = now - timedelta(days=90)
            end_date = now
        elif date_filter == 'last_6_months':
            start_date = now - timedelta(days=180)  # Approximately 6 months
            end_date = now
        elif date_filter == 'last_12_months':
            start_date = now - timedelta(days=365)  # 12 months
            end_date = now
        elif date_filter == 'ytd':
            # Year to date
            start_date = datetime(now.year, 1, 1)
            end_date = now
        elif date_filter == 'last_year':
            # Previous full year
            start_date = datetime(now.year - 1, 1, 1)
            end_date = datetime(now.year - 1, 12, 31, 23, 59, 59)
        elif date_filter == 'custom' and custom_start_date and custom_end_date:
            # Custom date range
            start_date = datetime.strptime(custom_start_date, '%Y-%m-%d')
            end_date = datetime.strptime(custom_end_date, '%Y-%m-%d')
            # Set end date to end of day
            end_date = end_date.replace(hour=23, minute=59, second=59)
        else:
            # Default to last 30 days
            start_date = now - timedelta(days=30)
            end_date = now
        
        return start_date, end_date
    except Exception as e:
        logger.error(f"Date range calculation error: {e}")
        # Default fallback
        return now - timedelta(days=30), now

def get_dashboard_data(campus, date_filter='last_30_days', custom_start_date='', custom_end_date=''):
    """
    Get comprehensive dashboard data for a specific campus or all campuses with date filtering
    
    Enhanced Google Sheets Column Structure:
    A: Timestamp
    B: Date  
    C: Campus
    D: Total Attendance
    E: First Time Visitors
    F: Visitors  
    G: Information Gathered
    H: First Time Christians
    I: Rededications
    J: Youth Attendance
    K: Youth Salvations
    L: Youth New People
    M: Kids Attendance
    N: Kids Leaders
    O: New Kids
    P: New Kids Salvations
    Q: Connect Groups
    R: Dream Team
    S: Tithe
    T: Baptisms
    U: Child Dedications
    """
    try:
        if not sheet:
            return {"error": "Google Sheets not connected"}
        
        # Get all records
        rows = sheet.get_all_records()
        if not rows:
            return {"stats": {}, "recent_entries": [], "trends": {}}
        
        # Filter by campus if not all_campuses
        if campus != 'all_campuses':
            campus_normalized = normalize_campus(campus)
            filtered_rows = []
            for row in rows:
                row_campus = normalize_campus(row.get("Campus") or row.get("campus") or "")
                if row_campus == campus_normalized or campus_normalized in row_campus:
                    filtered_rows.append(row)
            rows = filtered_rows
        
        # Calculate date range based on filter type
        now = datetime.now()
        start_date, end_date = calculate_date_range(date_filter, custom_start_date, custom_end_date, now)
        
        period_stats = {
            # Main attendance
            'total_attendance': 0,
            
            # New people breakdown
            'first_time_visitors': 0,
            'visitors': 0,
            'information_gathered': 0,
            'new_people': 0,  # Calculated: first_time + visitors
            
            # Christian decisions breakdown
            'first_time_christians': 0,
            'rededications': 0,
            'new_christians': 0,  # Calculated: first_time + rededications
            
            # Youth breakdown
            'youth_attendance': 0,
            'youth_salvations': 0,
            'youth_new_people': 0,
            
            # Kids breakdown
            'kids_attendance': 0,
            'kids_leaders': 0,
            'new_kids': 0,
            'new_kids_salvations': 0,
            
            # Ministry metrics
            'connect_groups': 0,
            'dream_team': 0,
            
            # Financial data
            'tithe': 0,
            
            # Special events
            'baptisms': 0,
            'child_dedications': 0,
            
            # System tracking
            'entry_count': 0,
            
            # Backward compatibility
            'kids_total': 0,  # Will map to kids_attendance
            'volunteers': 0  # Will map to dream_team
        }
        
        recent_entries = []
        monthly_trends = {}
        
        for row in rows:
            timestamp_str = row.get("Timestamp", "")
            if timestamp_str:
                try:
                    # Parse timestamp
                    if "T" in timestamp_str:
                        row_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    else:
                        row_date = parse_any_date(timestamp_str)
                    
                    # Add to recent entries for display
                    if len(recent_entries) < 10:
                        recent_entries.append({
                            'date': row_date.strftime('%Y-%m-%d'),
                            'campus': row.get('Campus', 'Unknown'),
                            'attendance': safe_int(row.get('Total Attendance', 0)),
                            'new_people': safe_int(row.get('New People', 0)),
                            'new_christians': safe_int(row.get('New Christians', 0))
                        })
                    
                    # Calculate stats for the selected date range
                    if start_date <= row_date <= end_date:
                        # Main attendance
                        period_stats['total_attendance'] += safe_int(row.get('Total Attendance', 0))
                        
                        # New people breakdown
                        first_time = safe_int(row.get('First Time Visitors', 0))
                        visitors = safe_int(row.get('Visitors', 0))  
                        period_stats['first_time_visitors'] += first_time
                        period_stats['visitors'] += visitors
                        period_stats['information_gathered'] += safe_int(row.get('Information Gathered', 0))
                        
                        # Christian decisions breakdown
                        first_time_christians = safe_int(row.get('First Time Christians', 0))
                        rededications = safe_int(row.get('Rededications', 0))
                        period_stats['first_time_christians'] += first_time_christians
                        period_stats['rededications'] += rededications
                        
                        # Youth breakdown
                        period_stats['youth_attendance'] += safe_int(row.get('Youth Attendance', 0))
                        period_stats['youth_salvations'] += safe_int(row.get('Youth Salvations', 0))
                        period_stats['youth_new_people'] += safe_int(row.get('Youth New People', 0))
                        
                        # Kids breakdown
                        period_stats['kids_attendance'] += safe_int(row.get('Kids Attendance', 0))
                        period_stats['kids_leaders'] += safe_int(row.get('Kids Leaders', 0))
                        period_stats['new_kids'] += safe_int(row.get('New Kids', 0))
                        period_stats['new_kids_salvations'] += safe_int(row.get('New Kids Salvations', 0))
                        
                        # Ministry metrics
                        period_stats['connect_groups'] += safe_int(row.get('Connect Groups', 0))
                        period_stats['dream_team'] += safe_int(row.get('Dream Team', 0))
                        
                        # Financial data  
                        period_stats['tithe'] += safe_int(row.get('Tithe', 0))
                        
                        # Special events
                        period_stats['baptisms'] += safe_int(row.get('Baptisms', 0))
                        period_stats['child_dedications'] += safe_int(row.get('Child Dedications', 0))
                        
                        # Backward compatibility handling
                        legacy_new_people = safe_int(row.get('New People', 0))
                        legacy_new_christians = safe_int(row.get('New Christians', 0))
                        legacy_kids_total = safe_int(row.get('Kids Total', 0))
                        legacy_volunteers = safe_int(row.get('Volunteers', 0))
                        
                        # Use legacy data if new breakdown not available
                        if first_time == 0 and visitors == 0 and legacy_new_people > 0:
                            period_stats['first_time_visitors'] += legacy_new_people
                        if first_time_christians == 0 and rededications == 0 and legacy_new_christians > 0:
                            period_stats['first_time_christians'] += legacy_new_christians
                        if period_stats['kids_attendance'] == 0 and legacy_kids_total > 0:
                            period_stats['kids_attendance'] += legacy_kids_total
                        if period_stats['dream_team'] == 0 and legacy_volunteers > 0:
                            period_stats['dream_team'] += legacy_volunteers
                        
                        # Calculate totals
                        period_stats['new_people'] = period_stats['first_time_visitors'] + period_stats['visitors']
                        period_stats['new_christians'] = period_stats['first_time_christians'] + period_stats['rededications']
                        period_stats['kids_total'] = period_stats['kids_attendance']  # For compatibility
                        period_stats['volunteers'] = period_stats['dream_team']  # For compatibility
                        
                        period_stats['entry_count'] += 1
                    
                    # Monthly trends for charts
                    month_key = row_date.strftime('%Y-%m')
                    if month_key not in monthly_trends:
                        monthly_trends[month_key] = {
                            'attendance': 0, 'new_people': 0, 'new_christians': 0, 'entries': 0
                        }
                    monthly_trends[month_key]['attendance'] += safe_int(row.get('Total Attendance', 0))
                    monthly_trends[month_key]['new_people'] += safe_int(row.get('New People', 0))
                    monthly_trends[month_key]['new_christians'] += safe_int(row.get('New Christians', 0))
                    monthly_trends[month_key]['entries'] += 1
                    
                except Exception as e:
                    continue
        
        # Calculate averages for all metrics
        if period_stats['entry_count'] > 0:
            # Main metrics
            period_stats['avg_attendance'] = period_stats['total_attendance'] / period_stats['entry_count']
            
            # New people breakdown
            period_stats['avg_first_time_visitors'] = period_stats['first_time_visitors'] / period_stats['entry_count']
            period_stats['avg_visitors'] = period_stats['visitors'] / period_stats['entry_count']
            period_stats['avg_information_gathered'] = period_stats['information_gathered'] / period_stats['entry_count']
            period_stats['avg_new_people'] = period_stats['new_people'] / period_stats['entry_count']
            
            # Christian decisions breakdown
            period_stats['avg_first_time_christians'] = period_stats['first_time_christians'] / period_stats['entry_count']
            period_stats['avg_rededications'] = period_stats['rededications'] / period_stats['entry_count']
            period_stats['avg_new_christians'] = period_stats['new_christians'] / period_stats['entry_count']
            
            # Youth breakdown
            period_stats['avg_youth_attendance'] = period_stats['youth_attendance'] / period_stats['entry_count']
            period_stats['avg_youth_salvations'] = period_stats['youth_salvations'] / period_stats['entry_count']
            period_stats['avg_youth_new_people'] = period_stats['youth_new_people'] / period_stats['entry_count']
            
            # Kids breakdown
            period_stats['avg_kids_attendance'] = period_stats['kids_attendance'] / period_stats['entry_count']
            period_stats['avg_kids_leaders'] = period_stats['kids_leaders'] / period_stats['entry_count']
            period_stats['avg_new_kids'] = period_stats['new_kids'] / period_stats['entry_count']
            period_stats['avg_new_kids_salvations'] = period_stats['new_kids_salvations'] / period_stats['entry_count']
            
            # Ministry metrics
            period_stats['avg_connect_groups'] = period_stats['connect_groups'] / period_stats['entry_count']
            period_stats['avg_dream_team'] = period_stats['dream_team'] / period_stats['entry_count']
            
            # Financial data
            period_stats['avg_tithe'] = period_stats['tithe'] / period_stats['entry_count']
            
            # Special events
            period_stats['avg_baptisms'] = period_stats['baptisms'] / period_stats['entry_count']
            period_stats['avg_child_dedications'] = period_stats['child_dedications'] / period_stats['entry_count']
            
            # Backward compatibility
            period_stats['avg_kids_total'] = period_stats['kids_total'] / period_stats['entry_count']
            period_stats['avg_volunteers'] = period_stats['volunteers'] / period_stats['entry_count']
        else:
            # Zero out all averages if no entries
            period_stats['avg_attendance'] = 0
            period_stats['avg_first_time_visitors'] = 0
            period_stats['avg_visitors'] = 0
            period_stats['avg_information_gathered'] = 0
            period_stats['avg_new_people'] = 0
            period_stats['avg_first_time_christians'] = 0
            period_stats['avg_rededications'] = 0
            period_stats['avg_new_christians'] = 0
            period_stats['avg_youth_attendance'] = 0
            period_stats['avg_youth_salvations'] = 0
            period_stats['avg_youth_new_people'] = 0
            period_stats['avg_kids_attendance'] = 0
            period_stats['avg_kids_leaders'] = 0
            period_stats['avg_new_kids'] = 0
            period_stats['avg_new_kids_salvations'] = 0
            period_stats['avg_connect_groups'] = 0
            period_stats['avg_dream_team'] = 0
            period_stats['avg_tithe'] = 0
            period_stats['avg_baptisms'] = 0
            period_stats['avg_child_dedications'] = 0
            period_stats['avg_kids_total'] = 0
            period_stats['avg_volunteers'] = 0
        
        # Sort trends by month (show more months for longer date ranges)
        trend_months = min(12, max(6, int((end_date - start_date).days / 30)))  # Adaptive trend period
        sorted_trends = dict(sorted(monthly_trends.items())[-trend_months:])
        
        # Prepare dashboard data for insights generation
        dashboard_data_for_insights = {
            'stats': period_stats,
            'trends': sorted_trends,
            'campus': campus
        }
        
        return {
            'stats': period_stats,
            'recent_entries': recent_entries[:10],
            'trends': sorted_trends,
            'campus': campus,
            'date_range': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d'),
                'filter_type': date_filter
            }
        }
        
    except Exception as e:
        logger.error(f"Dashboard data error: {e}")
        return {"error": str(e)}

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and authentication handler"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return jsonify({"error": "Please enter both username and password."}), 400
        
        user = authenticate_user(username, password)
        if user:
            login_user(user, remember=True)
            return jsonify({"success": True, "redirect": "/dashboard"})
        else:
            return jsonify({"error": "Invalid username or password."}), 401
    
    # GET request - serve login page
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout and redirect to login page"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

def get_dashboard_data(campus, date_filter='last_7_days', custom_start_date='', custom_end_date=''):
    """Get dashboard data with date filtering"""
    try:
        # Get data from Google Sheets
        rows = []
        if sheet:
            try:
                rows = sheet.get_all_records()
            except Exception as e:
                logger.error(f"Failed to get stats from Google Sheets: {e}")
                rows = []
        
        if not rows:
            # Fallback to conversation memory
            memory = load_conversation_memory()
            campus_history = memory.get("session_stats", {}).get(campus, [])
            rows = campus_history
        
        # Calculate date range based on filter
        end_date = datetime.now()
        if date_filter == 'last_7_days':
            start_date = end_date - timedelta(days=7)
        elif date_filter == 'last_30_days':
            start_date = end_date - timedelta(days=30)
        elif date_filter == 'last_90_days':
            start_date = end_date - timedelta(days=90)
        elif date_filter == 'this_year':
            start_date = datetime(end_date.year, 1, 1)
        elif custom_start_date and custom_end_date:
            start_date = datetime.strptime(custom_start_date, '%Y-%m-%d')
            end_date = datetime.strptime(custom_end_date, '%Y-%m-%d')
        else:
            start_date = end_date - timedelta(days=30)  # Default to 30 days
        
        # Filter rows by campus and date range
        filtered_rows = []
        campus_normalized = normalize_campus(campus) if campus != 'all_campuses' else None
        
        for row in rows:
            try:
                # Check campus filter
                if campus_normalized:
                    row_campus = normalize_campus(row.get("Campus") or row.get("campus") or "")
                    if row_campus != campus_normalized and campus_normalized not in row_campus:
                        continue
                
                # Check date filter
                timestamp_str = row.get("Timestamp", "")
                if timestamp_str:
                    if "T" in timestamp_str:
                        row_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    else:
                        row_date = parse_any_date(timestamp_str)
                    if start_date <= row_date <= end_date:
                        filtered_rows.append(row)
                else:
                    filtered_rows.append(row)  # Include rows without timestamps
            except Exception as e:
                logger.warning(f"Error processing row: {e}")
                continue
        
        # Calculate stats using correct Google Sheets headers
        total_attendance = sum(safe_int(row.get('Total Attendance', 0)) for row in filtered_rows)
        
        # New People = First Time Visitors + Visitors
        total_new_people = sum(
            safe_int(row.get('First Time Visitors', 0)) + safe_int(row.get('Visitors', 0)) 
            for row in filtered_rows
        )
        
        # New Christians = First Time Christians + Rededications
        total_new_christians = sum(
            safe_int(row.get('First Time Christians', 0)) + safe_int(row.get('Rededications', 0))
            for row in filtered_rows
        )
        
        total_youth = sum(safe_int(row.get('Youth Attendance', 0)) for row in filtered_rows)
        total_kids = sum(safe_int(row.get('Kids Attendance', 0)) for row in filtered_rows)
        total_connect_groups = sum(safe_int(row.get('Connect Groups', 0)) for row in filtered_rows)
        total_dream_team = sum(safe_int(row.get('Dream Team', 0)) for row in filtered_rows)
        total_tithe = sum(safe_int(row.get('Tithe', 0)) for row in filtered_rows)
        
        # Calculate averages
        valid_entries = len([row for row in filtered_rows if safe_int(row.get('Total Attendance', 0)) > 0])
        avg_attendance = total_attendance / valid_entries if valid_entries > 0 else 0
        avg_new_people = total_new_people / valid_entries if valid_entries > 0 else 0
        avg_new_christians = total_new_christians / valid_entries if valid_entries > 0 else 0
        avg_youth = total_youth / valid_entries if valid_entries > 0 else 0
        avg_kids = total_kids / valid_entries if valid_entries > 0 else 0
        avg_connect_groups = total_connect_groups / valid_entries if valid_entries > 0 else 0
        avg_dream_team = total_dream_team / valid_entries if valid_entries > 0 else 0
        
        # Prepare chart data (last 10 entries for trends)
        chart_rows = sorted(filtered_rows, key=lambda x: x.get('Timestamp', ''))[-10:]
        attendance_labels = []
        attendance_values = []
        
        for row in chart_rows:
            try:
                timestamp_str = row.get("Timestamp", "")
                if timestamp_str:
                    if "T" in timestamp_str:
                        date_obj = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    else:
                        date_obj = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    attendance_labels.append(date_obj.strftime('%m/%d'))
                else:
                    attendance_labels.append('Unknown')
                attendance_values.append(safe_int(row.get('Total Attendance', 0)))
            except Exception:
                continue
        
        # Calculate detailed breakdown stats for modals using correct headers
        total_first_time_visitors = sum(safe_int(row.get('First Time Visitors', 0)) for row in filtered_rows)
        total_visitors = sum(safe_int(row.get('Visitors', 0)) for row in filtered_rows)
        total_first_time_christians = sum(safe_int(row.get('First Time Christians', 0)) for row in filtered_rows)
        total_rededications = sum(safe_int(row.get('Rededications', 0)) for row in filtered_rows)
        total_youth_attendance = sum(safe_int(row.get('Youth Attendance', 0)) for row in filtered_rows)
        total_youth_salvations = sum(safe_int(row.get('Youth Salvations', 0)) for row in filtered_rows)
        total_youth_new_people = sum(safe_int(row.get('Youth New People', 0)) for row in filtered_rows)
        total_kids_attendance = sum(safe_int(row.get('Kids Attendance', 0)) for row in filtered_rows)
        total_kids_leaders = sum(safe_int(row.get('Kids Leaders', 0)) for row in filtered_rows)
        total_new_kids = sum(safe_int(row.get('New Kids', 0)) for row in filtered_rows)
        total_new_kids_salvations = sum(safe_int(row.get('New Kids Salvations', 0)) for row in filtered_rows)

        return {
            'stats': {
                'total_attendance': total_attendance,
                'total_new_people': total_new_people,
                'total_new_christians': total_new_christians,
                'total_youth': total_youth,
                'total_kids': total_kids,
                'total_connect_groups': total_connect_groups,
                'total_dream_team': total_dream_team,
                'total_tithe': total_tithe,
                'avg_attendance': avg_attendance,
                'avg_new_people': avg_new_people,
                'avg_new_christians': avg_new_christians,
                'avg_youth': avg_youth,
                'avg_kids': avg_kids,
                'avg_connect_groups': avg_connect_groups,
                'avg_dream_team': avg_dream_team,
                # Breakdown stats for modals
                'first_time_visitors': total_first_time_visitors,
                'visitors': total_visitors,
                'first_time_christians': total_first_time_christians,
                'rededications': total_rededications,
                'youth_attendance': total_youth_attendance,
                'youth_salvations': total_youth_salvations,
                'youth_new_people': total_youth_new_people,
                'kids_attendance': total_kids_attendance,
                'kids_leaders': total_kids_leaders,
                'new_kids': total_new_kids,
                'new_kids_salvations': total_new_kids_salvations
            },
            'chart_data': {
                'attendance_labels': attendance_labels,
                'attendance_values': attendance_values
            },
            'date_range': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        }
    
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return {
            'error': f'Error loading dashboard data: {str(e)}',
            'stats': {},
            'chart_data': {'attendance_labels': [], 'attendance_values': []}
        }

def get_campus_comparison_data(campus_filter=None):
    """Get comparison data across campuses for leadership insights"""
    try:
        if not sheet:
            return []
        
        # sheet is already a worksheet object, not a spreadsheet
        data = sheet.get_all_records()
        
        if not data:
            return []
        
        # Get data for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # If campus_filter is provided, only analyze that campus
        if campus_filter:
            campuses = [campus_filter.lower()]
        else:
            campuses = ['paradise', 'south', 'adelaide_city', 'salisbury', 'clare_valley', 
                       'mount_barker', 'victor_harbour', 'copper_coast']
        
        campus_stats = []
        
        for campus in campuses:
            # Filter data for this campus and date range
            campus_data = []
            for row in data:
                try:
                    date_str = row.get('Date', '')
                    if not date_str:
                        continue
                    
                    # Try multiple date formats
                    row_date = None
                    date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']
                    
                    for date_format in date_formats:
                        try:
                            row_date = datetime.strptime(date_str, date_format)
                            break
                        except ValueError:
                            continue
                    
                    if row_date and start_date <= row_date <= end_date and row.get('Campus', '').lower() == campus.lower():
                        campus_data.append(row)
                except (ValueError, TypeError):
                    continue
            
            if campus_data:
                # Calculate basic stats for this campus using correct headers
                total_attendance = sum(safe_int(row.get('Total Attendance', 0)) for row in campus_data)
                
                # New People = First Time Visitors + Visitors  
                total_new_people = sum(
                    safe_int(row.get('First Time Visitors', 0)) + safe_int(row.get('Visitors', 0))
                    for row in campus_data
                )
                
                # New Christians = First Time Christians + Rededications
                total_new_christians = sum(
                    safe_int(row.get('First Time Christians', 0)) + safe_int(row.get('Rededications', 0))
                    for row in campus_data
                )
                
                total_youth = sum(safe_int(row.get('Youth Attendance', 0)) for row in campus_data)
                total_kids = sum(safe_int(row.get('Kids Attendance', 0)) for row in campus_data)
                
                avg_attendance = total_attendance / len(campus_data) if campus_data else 0
                avg_new_people = total_new_people / len(campus_data) if campus_data else 0
                avg_new_christians = total_new_christians / len(campus_data) if campus_data else 0
                
                # Calculate growth rates compared to previous period
                prev_start = start_date - timedelta(days=30)
                prev_data = []
                for row in data:
                    try:
                        date_str = row.get('Date', '')
                        if not date_str:
                            continue
                        
                        # Try multiple date formats
                        row_date = None
                        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']
                        
                        for date_format in date_formats:
                            try:
                                row_date = datetime.strptime(date_str, date_format)
                                break
                            except ValueError:
                                continue
                        
                        if row_date and prev_start <= row_date < start_date and row.get('Campus', '').lower() == campus.lower():
                            prev_data.append(row)
                    except (ValueError, TypeError):
                        continue
                
                # Calculate growth percentages
                attendance_growth = 0
                new_people_growth = 0
                new_christians_growth = 0
                
                if prev_data:
                    prev_avg_attendance = sum(safe_int(row.get('Total Attendance', 0)) for row in prev_data) / len(prev_data)
                    
                    # Calculate previous period averages with correct headers
                    prev_total_new_people = sum(
                        safe_int(row.get('First Time Visitors', 0)) + safe_int(row.get('Visitors', 0))
                        for row in prev_data
                    )
                    prev_avg_new_people = prev_total_new_people / len(prev_data)
                    
                    prev_total_new_christians = sum(
                        safe_int(row.get('First Time Christians', 0)) + safe_int(row.get('Rededications', 0))
                        for row in prev_data
                    )
                    prev_avg_new_christians = prev_total_new_christians / len(prev_data)
                    
                    if prev_avg_attendance > 0:
                        attendance_growth = ((avg_attendance - prev_avg_attendance) / prev_avg_attendance) * 100
                    
                    if prev_avg_new_people > 0:
                        new_people_growth = ((avg_new_people - prev_avg_new_people) / prev_avg_new_people) * 100
                    
                    if prev_avg_new_christians > 0:
                        new_christians_growth = ((avg_new_christians - prev_avg_new_christians) / prev_avg_new_christians) * 100
                
                campus_stats.append({
                    'campus': campus,
                    'display_name': campus.replace('_', ' ').title(),
                    'attendance': round(avg_attendance, 1),
                    'new_people': round(avg_new_people, 1),
                    'new_christians': round(avg_new_christians, 1),
                    'youth': round(total_youth / len(campus_data), 1) if campus_data else 0,
                    'kids': round(total_kids / len(campus_data), 1) if campus_data else 0,
                    'attendance_growth': round(attendance_growth, 1),
                    'new_people_growth': round(new_people_growth, 1),
                    'new_christians_growth': round(new_christians_growth, 1),
                    'total_records': len(campus_data),
                    'conversion_rate': round((avg_new_christians / max(avg_new_people, 1)) * 100, 1)
                })
        
        return sorted(campus_stats, key=lambda x: x['attendance'], reverse=True)
        
    except Exception as e:
        logger.error(f"Campus comparison data error: {e}")
        return []

def generate_campus_insights(campus_data, campus_filter=None):
    """Generate AI-powered insights from campus data"""
    try:
        if not campus_data:
            return ["No campus data available for insights generation."]
        
        insights = []
        
        # If this is campus-specific data (single campus)
        if campus_filter and len(campus_data) == 1:
            campus = campus_data[0]
            
            # Campus-specific insights
            insights.append(f"📊 {campus['display_name']} current performance: {campus['attendance']} average attendance, {campus['new_people']} new people per week")
            
            # Growth insights
            if campus['attendance_growth'] > 10:
                insights.append(f"🚀 Excellent growth! Your attendance is up {campus['attendance_growth']}% from last month")
            elif campus['attendance_growth'] > 0:
                insights.append(f"📈 Positive growth: {campus['attendance_growth']}% attendance increase from last month")
            elif campus['attendance_growth'] < -10:
                insights.append(f"⚠️ Attendance declined {abs(campus['attendance_growth'])}% - consider community outreach initiatives")
            else:
                insights.append(f"📊 Attendance stable with {campus['attendance_growth']}% change from last month")
            
            # Conversion insights
            if campus['conversion_rate'] > 25:
                insights.append(f"🎯 Outstanding conversion rate! {campus['conversion_rate']}% of new people are becoming Christians")
            elif campus['conversion_rate'] > 15:
                insights.append(f"✅ Good conversion rate: {campus['conversion_rate']}% of new people becoming Christians")
            else:
                insights.append(f"💡 Focus opportunity: {campus['conversion_rate']}% conversion rate - consider follow-up strategies")
            
            # Youth and kids
            if campus['youth'] > 25:
                insights.append(f"👥 Strong youth program with {campus['youth']} average attendance")
            elif campus['youth'] > 0:
                insights.append(f"👥 Youth engagement: {campus['youth']} average - room for growth")
            
            if campus['kids'] > 20:
                insights.append(f"👶 Thriving kids ministry with {campus['kids']} average attendance")
            elif campus['kids'] > 0:
                insights.append(f"👶 Kids ministry: {campus['kids']} average - potential for expansion")
            
            # Encouragement
            insights.append(f"💪 Keep up the great work! {campus['display_name']} is making a real impact in the community")
            
        else:
            # Multi-campus insights (for senior leadership/admin)
            
            # Top performing campus
            if campus_data:
                top_campus = campus_data[0]
                insights.append(f"🏆 {top_campus['display_name']} leads in attendance with {top_campus['attendance']} average weekly attendance")
            
            # Growth analysis
            growth_leaders = [campus for campus in campus_data if campus['attendance_growth'] > 10]
            if growth_leaders:
                campus_names = [campus['display_name'] for campus in growth_leaders[:3]]
                insights.append(f"📈 Strong growth at {', '.join(campus_names)} - attendance up 10%+ from last month")
            
            declining_campuses = [campus for campus in campus_data if campus['attendance_growth'] < -10]
            if declining_campuses:
                campus_names = [campus['display_name'] for campus in declining_campuses[:2]]
                insights.append(f"⚠️ {', '.join(campus_names)} showing declining attendance - may need attention")
            
            # New people conversion insights
            high_conversion = [campus for campus in campus_data if campus['conversion_rate'] > 20]
            if high_conversion:
                campus_names = [campus['display_name'] for campus in high_conversion[:2]]
                insights.append(f"🎯 Excellent conversion rates at {', '.join(campus_names)} - over 20% of new people becoming Christians")
            
            # Youth and kids analysis
            youth_leaders = sorted([campus for campus in campus_data if campus['youth'] > 0], key=lambda x: x['youth'], reverse=True)[:2]
            if youth_leaders:
                campus_names = [f"{campus['display_name']} ({campus['youth']})" for campus in youth_leaders]
                insights.append(f"👥 Youth engagement leaders: {', '.join(campus_names)}")
            
            # Overall network performance
            total_attendance = sum(campus['attendance'] * campus['total_records'] for campus in campus_data)
            total_records = sum(campus['total_records'] for campus in campus_data)
            network_avg = total_attendance / max(total_records, 1)
            
            total_new_people = sum(campus['new_people'] * campus['total_records'] for campus in campus_data)
            total_new_christians = sum(campus['new_christians'] * campus['total_records'] for campus in campus_data)
            network_conversion = (total_new_christians / max(total_new_people, 1)) * 100
            
            insights.append(f"🌟 Network average: {network_avg:.1f} attendance, {network_conversion:.1f}% conversion rate across all campuses")
            
            # Opportunities
            underperforming = [campus for campus in campus_data if campus['attendance'] < network_avg * 0.7]
            if underperforming:
                campus_names = [campus['display_name'] for campus in underperforming[:2]]
                insights.append(f"💡 Growth opportunities at {', '.join(campus_names)} - below network average")
        
        return insights[:6]  # Limit to 6 insights
        
    except Exception as e:
        logger.error(f"Insights generation error: {e}")
        return ["Unable to generate insights at this time. Please try again later."]

def get_weekly_campus_comparison_data():
    """Get campus comparison data for the current week"""
    try:
        # Get data from Google Sheets
        rows = []
        if sheet:
            try:
                rows = sheet.get_all_records()
            except Exception as e:
                logger.error(f"Failed to get stats from Google Sheets: {e}")
                rows = []
        
        if not rows:
            return []
        
        # Get current week's data (last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Group by campus
        campus_data = {}
        for row in rows:
            try:
                # Check if row is within current week
                timestamp_str = row.get("Timestamp", "")
                if timestamp_str:
                    if "T" in timestamp_str:
                        row_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    else:
                        row_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    
                    if start_date <= row_date <= end_date:
                        campus = row.get("Campus", "").lower()
                        if campus not in campus_data:
                            campus_data[campus] = {
                                'campus': campus,
                                'attendance': 0,
                                'new_people': 0,
                                'new_christians': 0
                            }
                        
                        campus_data[campus]['attendance'] += safe_int(row.get('Total Attendance', 0))
                        campus_data[campus]['new_people'] += safe_int(row.get('New People', 0))
                        campus_data[campus]['new_christians'] += safe_int(row.get('New Christians', 0))
            except Exception:
                continue
        
        # Convert to list and sort by attendance
        comparison_list = list(campus_data.values())
        comparison_list.sort(key=lambda x: x['attendance'], reverse=True)
        
        return comparison_list
    
    except Exception as e:
        logger.error(f"Error getting campus comparison data: {e}")
        return []

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard with analytics and statistics"""
    try:
        # Check if user has dashboard access
        if not current_user.has_permission('dashboard_access'):
            flash('Access denied. Dashboard access not available for your role.', 'error')
            return redirect(url_for('serve_index'))
        
        # Finance users should be redirected to their finance dashboard
        if current_user.role == 'finance':
            return redirect(url_for('finance_dashboard'))
        
        # Get dashboard data
        campus = request.args.get('campus', 'all_campuses')
        date_filter = request.args.get('date_filter', 'last_7_days')
        
        # For campus pastors, restrict to their assigned campus
        if current_user.role == 'campus_pastor' and campus != current_user.campus:
            campus = current_user.campus
        
        dashboard_data = get_dashboard_data(campus, date_filter)
        
        # Ensure we have all detailed breakdown stats
        if 'stats' not in dashboard_data:
            dashboard_data['stats'] = {}
        
        # Add missing breakdown stats if not present
        breakdown_stats = [
            'first_time_visitors', 'visitors', 'first_time_christians', 'rededications',
            'youth_attendance', 'youth_new_people', 'youth_salvations',
            'kids_attendance', 'new_kids', 'kids_leaders', 'new_kids_salvations'
        ]
        
        for stat in breakdown_stats:
            if stat not in dashboard_data['stats']:
                dashboard_data['stats'][stat] = 0
        
        return render_template('dashboard.html', 
                             dashboard_data=dashboard_data,
                             current_user=current_user)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        flash('Dashboard temporarily unavailable', 'error')
        return redirect(url_for('serve_index'))

@app.route('/finance')
@login_required
def finance_dashboard():
    """Finance team tithe logging interface"""
    try:
        # Only users with finance access can access this
        if not current_user.has_permission('finance_access'):
            flash('Access denied. Finance access required.', 'error')
            return redirect(url_for('serve_index'))
        
        # Get all campuses for the finance team
        campuses_data = get_campuses_for_user()
        campuses = campuses_data.get('campuses', [])
        
        # Get selected date (default to today)
        selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Get existing tithe data for the selected date if any
        existing_data = get_existing_tithe_data(selected_date)
        
        return render_template('finance.html', 
                             campuses=campuses,
                             selected_date=selected_date,
                             existing_data=existing_data,
                             user=current_user)
                             
    except Exception as e:
        logger.error(f"Error in finance dashboard: {str(e)}")
        flash('An error occurred while loading the finance dashboard.', 'error')
        return redirect(url_for('login'))

def get_existing_tithe_data(selected_date):
    """Get existing tithe data for the selected date"""
    try:
        if not sheet:
            return {}
        
        # Get all rows from the sheet
        rows = sheet.get_all_records()
        existing_data = {}
        
        # Parse the selected date
        target_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        
        for row in rows:
            date_str = row.get("Date", "")
            if date_str:
                try:
                    # Parse the date from the row
                    if "T" in date_str:
                        row_date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
                    else:
                        row_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    
                    # If dates match, collect tithe data
                    if row_date == target_date:
                        campus = row.get('Campus', '')
                        tithe_amount = row.get('Tithe', 0)
                        if campus and tithe_amount:
                            existing_data[campus.lower()] = {
                                'amount': safe_int(tithe_amount),
                                'row_index': rows.index(row) + 2  # +2 because sheets are 1-indexed and have header
                            }
                except Exception as e:
                    logger.warning(f"Error parsing date {date_str}: {e}")
                    continue
        
        return existing_data
        
    except Exception as e:
        logger.error(f"Error getting existing tithe data: {str(e)}")
        return {}

@app.route('/finance/submit', methods=['POST'])
@login_required
def submit_tithe_data():
    """Submit tithe data for multiple campuses"""
    try:
        # Only users with finance access can access this
        if not current_user.has_permission('finance_access'):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        selected_date = data.get('date')
        tithe_data = data.get('tithe_data', {})
        
        if not selected_date or not tithe_data:
            return jsonify({'error': 'Missing date or tithe data'}), 400
        
        results = []
        
        # Process each campus's tithe data
        for campus_id, amount in tithe_data.items():
            if amount and float(amount) > 0:
                result = update_tithe_for_campus(campus_id, selected_date, float(amount))
                results.append({
                    'campus': campus_id,
                    'amount': amount,
                    'success': result['success'],
                    'message': result['message']
                })
        
        return jsonify({
            'success': True,
            'message': f'Tithe data submitted for {len(results)} campuses',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error submitting tithe data: {str(e)}")
        return jsonify({'error': str(e)}), 500

def update_tithe_for_campus(campus_id, date_str, tithe_amount):
    """Update or add tithe data for a specific campus and date"""
    try:
        if not sheet:
            return {'success': False, 'message': 'Sheet not available'}
        
        # Get all rows
        rows = sheet.get_all_records()
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Look for existing row for this campus and date
        existing_row_index = None
        for i, row in enumerate(rows):
            date_str_row = row.get("Date", "")
            if date_str_row:
                try:
                    if "T" in date_str_row:
                        row_date = datetime.fromisoformat(date_str_row.replace('Z', '+00:00')).date()
                    else:
                        row_date = datetime.strptime(date_str_row, "%Y-%m-%d").date()
                    
                    if row_date == target_date and row.get('Campus', '').lower() == campus_id.lower():
                        existing_row_index = i + 2  # +2 for 1-indexed and header
                        break
                except:
                    continue
        
        if existing_row_index:
            # Update existing row - just update the Tithe column (Column S)
            sheet.update(f'S{existing_row_index}', [[tithe_amount]])
            logger.info(f"Updated tithe for {campus_id} on {date_str}: ${tithe_amount}")
            return {'success': True, 'message': f'Updated existing entry for {campus_id}'}
        else:
            # Create new row with minimal data - just campus, date, and tithe
            new_row = [
                datetime.now().isoformat(),  # Timestamp (A)
                date_str,                    # Date (B)
                campus_id.replace('_', ' ').title(),  # Campus (C)
                '',  # D: Total Attendance
                '',  # E: First Time Visitors
                '',  # F: Visitors
                '',  # G: Information Gathered
                '',  # H: First Time Christians
                '',  # I: Rededications
                '',  # J: Youth Attendance
                '',  # K: Youth Salvations
                '',  # L: Youth New People
                '',  # M: Kids Attendance
                '',  # N: Kids Leaders
                '',  # O: New Kids
                '',  # P: New Kids Salvations
                '',  # Q: Connect Groups
                '',  # R: Dream Team
                tithe_amount,  # S: Tithe
                '',  # T: Baptisms
                ''   # U: Child Dedications
            ]
            
            sheet.append_row(new_row)
            logger.info(f"Created new tithe entry for {campus_id} on {date_str}: ${tithe_amount}")
            return {'success': True, 'message': f'Created new entry for {campus_id}'}
            
    except Exception as e:
        logger.error(f"Error updating tithe for {campus_id}: {str(e)}")
        return {'success': False, 'message': str(e)}

# User Management Routes
@app.route('/users')
@admin_required
def user_list():
    """List all users - admin only"""
    users_db = load_users_database()
    users = users_db.get('users', {})
    roles = users_db.get('roles', {})
    
    # Convert to list for template
    user_list = []
    for user_id, user_data in users.items():
        user_data['id'] = user_id
        user_data['role_name'] = roles.get(user_data['role'], {}).get('name', user_data['role'])
        user_list.append(user_data)
    
    return render_template('users.html', users=user_list, roles=roles)

@app.route('/users/create', methods=['GET', 'POST'])
@admin_required
def user_create():
    """Create new user - admin only"""
    users_db = load_users_database()
    roles = users_db.get('roles', {})
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        role = request.form.get('role', '').strip()
        campus = request.form.get('campus', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validation
        if not username or not full_name or not email or not role or not password:
            flash('All fields are required.', 'error')
            return render_template('user_form.html', roles=roles, action='Create', user=None)
        
        # Check if username already exists
        if username in users_db.get('users', {}):
            flash('Username already exists.', 'error')
            return render_template('user_form.html', roles=roles, action='Create', user=None)
        
        # Create user
        user_id = username.lower().replace(' ', '_')
        new_user = {
            'id': user_id,
            'username': username,
            'password_hash': 'placeholder',  # We'll use simple password for now
            'email': email,
            'full_name': full_name,
            'role': role,
            'campus': campus,
            'active': True,
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'last_login': None
        }
        
        # Add to database
        users_db.setdefault('users', {})[user_id] = new_user
        
        if save_users_database(users_db):
            flash(f'User {full_name} created successfully!', 'success')
            return redirect(url_for('user_list'))
        else:
            flash('Failed to save user. Please try again.', 'error')
    
    return render_template('user_form.html', roles=roles, action='Create', user=None)

@app.route('/users/<user_id>/edit', methods=['GET', 'POST'])
@admin_required
def user_edit(user_id):
    """Edit existing user - admin only"""
    users_db = load_users_database()
    roles = users_db.get('roles', {})
    user = users_db.get('users', {}).get(user_id)
    
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('user_list'))
    
    if request.method == 'POST':
        # Get form data
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        role = request.form.get('role', '').strip()
        campus = request.form.get('campus', '').strip()
        active = request.form.get('active') == 'on'
        password = request.form.get('password', '').strip()
        
        # Validation
        if not full_name or not email or not role:
            flash('Name, email, and role are required.', 'error')
            return render_template('user_form.html', roles=roles, action='Edit', user=user)
        
        # Update user
        user['full_name'] = full_name
        user['email'] = email
        user['role'] = role
        user['campus'] = campus
        user['active'] = active
        
        # Update password if provided
        if password:
            user['password_hash'] = 'placeholder'  # We'll use simple password for now
        
        if save_users_database(users_db):
            flash(f'User {full_name} updated successfully!', 'success')
            return redirect(url_for('user_list'))
        else:
            flash('Failed to update user. Please try again.', 'error')
    
    return render_template('user_form.html', roles=roles, action='Edit', user=user)

@app.route('/campuses/<campus_id>/delete', methods=['POST'])
@admin_required
def campus_delete(campus_id):
    """Delete campus - admin only"""
    campuses_db = load_campuses_database()
    campus = campuses_db.get('campuses', {}).get(campus_id)
    
    if not campus:
        flash('Campus not found.', 'error')
        return redirect(url_for('campus_list'))
    
    # Prevent deleting special campuses
    if campus.get('special'):
        flash('Cannot delete special campus configurations.', 'error')
        return redirect(url_for('campus_list'))
    
    # Delete campus
    del campuses_db['campuses'][campus_id]
    
    if save_campuses_database(campuses_db):
        flash(f'Campus {campus["name"]} deleted successfully!', 'success')
    else:
        flash('Failed to delete campus. Please try again.', 'error')
    
    return redirect(url_for('campus_list'))

@app.route('/')
def serve_index():
    """Main application page - serve the React app"""
    try:
        if not app.static_folder:
            return jsonify({"error": "Static folder not configured"}), 500
        
        # Check if index.html exists
        index_path = os.path.join(app.static_folder, 'index.html')
        if not os.path.exists(index_path):
            return jsonify({
                "error": "React app not built",
                "static_folder": app.static_folder,
                "files": os.listdir(app.static_folder) if os.path.exists(app.static_folder) else []
            }), 404
        
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        return jsonify({"error": f"Error serving index: {str(e)}"}), 500

@app.route('/<path:filename>')
def serve_static(filename):
    if app.static_folder:
        return send_from_directory(app.static_folder, filename)
    return jsonify({"error": "Static folder not configured"}), 404

@app.route('/<path:path>')
def catch_all(path):
    """Catch-all route for React Router - serve index.html for all non-API routes"""
    if path.startswith('api/'):
        return jsonify({"error": "API endpoint not found"}), 404
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/temp_audio/<path:filename>')
def serve_audio(filename):
    """Serve generated audio files"""
    # Use absolute path to temp_audio directory in backend folder
    temp_audio_dir = os.path.join(os.path.dirname(__file__), "temp_audio")
    return send_from_directory(temp_audio_dir, filename)

@app.route('/query')
@login_required
def serve_query():
    """Query page with voice interface"""
    try:
        # Check if user has query access
        if not current_user.has_permission('query_access'):
            flash('Access denied. Query access not available for your role.', 'error')
            return redirect(url_for('serve_index'))
        
        return render_template('query.html')
    except Exception as e:
        logger.error(f"Query page error: {e}")
        flash('Query page temporarily unavailable', 'error')
        return redirect(url_for('serve_index'))

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "ok",
        "sheets_connected": sheet is not None,
        "claude_connected": claude is not None,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.route('/health')
def simple_health():
    """Simple health check that doesn't require authentication"""
    return jsonify({
        "status": "ok",
        "message": "Church Voice Assistant is running",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.route('/debug/static')
def debug_static():
    """Debug route to check static folder contents"""
    try:
        if not app.static_folder:
            return jsonify({"error": "Static folder not configured"}), 500
        
        if not os.path.exists(app.static_folder):
            return jsonify({"error": "Static folder does not exist"}), 500
        
        files = os.listdir(app.static_folder)
        return jsonify({
            "static_folder": app.static_folder,
            "files": files,
            "index_exists": os.path.exists(os.path.join(app.static_folder, 'index.html'))
        })
    except Exception as e:
        return jsonify({"error": f"Debug error: {str(e)}"}), 500

@app.route('/api/session')
def session_info():
    if current_user.is_authenticated:
        return jsonify({
            "authenticated": True,
            "user": current_user.username,
            "role": current_user.role,
            "campus": current_user.campus,
            "full_name": current_user.full_name,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    else:
        return jsonify({
            "authenticated": False,
            "user": None,
            "role": None,
            "campus": None,
            "full_name": None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

@app.route('/api/stats')
@login_required
def get_stats():
    # Check if user has recall permissions
    if not current_user.has_permission('recall_stats'):
        return jsonify({"error": "You do not have permission to recall statistics data"}), 403
    
    if not sheet:
        return jsonify({"error": "Google Sheets not connected"}), 500
    try:
        campus_filter = request.args.get('campus', '').strip()
        
        # For campus pastors, restrict to their campus only
        if current_user.role == 'campus_pastor':
            if campus_filter and campus_filter != current_user.campus:
                return jsonify({
                    "error": f"You can only access data for {safe_campus_name(current_user.campus)[1]} campus"
                }), 403
            # Force campus filter to user's campus
            campus_filter = current_user.campus
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
@login_required
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
        # Smart campus defaulting based on user role when no campus is mentioned
        if current_user.is_authenticated:
            if current_user.role == 'campus_pastor':
                # Campus pastors get their assigned campus by default
                campus = getattr(current_user, 'campus', None)
                if campus:
                    logger.info(f"No campus mentioned - using campus pastor's campus: {campus}")
                else:
                    campus = None  # No assigned campus - will prompt user
            elif current_user.role in ['senior_pastor', 'lead_pastor', 'admin']:
                # Senior leadership gets all campuses by default for queries
                # For stat logging, they'll still need to specify
                campus = None  # Will be handled differently for queries vs logging
                logger.info(f"No campus mentioned - senior leadership (will default to all_campuses for queries)")
            else:
                campus = None  # No campus detected - will prompt user
        else:
            campus = None  # No campus detected - will prompt user
    
    logger.info(f"Final campus: {campus}")
    
    # Enhanced query detection with better natural language understanding
    import re
    text_lower = text.lower()
    
    # Query intent patterns (questions, requests for information)
    query_patterns = [
        r'\b(?:what|how|when|where|why|which|who)\b',
        r'\b(?:tell me|show me|give me|can you|could you|would you)\b',
        r'\b(?:what is|what was|what are|what were)\b',
        r'\b(?:how many|how much|how often|how long)\b',
        r'\b(?:average|total|sum|count|number)\b',
        r'\b(?:compare|comparison|versus|vs)\b',
        r'\b(?:trend|trends|pattern|growth|change)\b',
        r'\b(?:report|summary|overview|recap|review)\b',
        r'\b(?:this week|this month|this year|last week|last month|last year)\b',
        r'\b(?:quarterly|monthly|annual|yearly)\b',
        r'\b(?:best|worst|highest|lowest|top|bottom)\b',
        r'\b(?:percentage|percent|%)\b',
        r'\b(?:increase|decrease|up|down|better|worse)\b'
    ]
    
    # Stat logging patterns (specific numbers being reported)
    stat_patterns = [
        r'\d+\s+(?:people|attendance|total|had|got|there were)',
        r'\d+\s+(?:first\s+time|first-time|first\s+timers?|new\s+people|newcomers?)',
        r'\d+\s+(?:visitors?|guests?)',
        r'\d+\s+(?:info\s+gathered|information\s+gathered|details\s+gathered|cards\s+back|contact\s+cards)',
        r'\d+\s+(?:salvations?|decisions?|got\s+saved|conversions?)',
        r'\d+\s+(?:rededication|re-dedication)',
        r'\d+\s+(?:youth|teens?)',
        r'\d+\s+(?:kids|children)',
        r'\d+\s+(?:connect\s+groups?|small\s+groups?|groups?)',
        r'\d+\s+(?:dream\s+team|volunteers?|team\s+members?)',
        r'\d+\s+(?:baptisms?|baptized|baptismal)',
        r'\d+\s+(?:child\s+dedications?|baby\s+dedications?|dedications?)'
    ]
    
    is_stat_logging = any(re.search(pattern, text.lower()) for pattern in stat_patterns)
        
    # Load conversation memory
    memory = load_conversation_memory()
    
    # Check if this is a query request vs stat logging
    text_lower = text.lower()
    import re
    
    # FIRST: Check for clear query patterns (these take priority)
    query_keywords = [
        'how many', 'what is', 'what was', "what's", 'tell me', 'give me', 'show me',
        'average', 'last week', 'this week', 'last month', 'this month', 'count', 'query', 'data', 
        'has had', 'had this year', 'had this month', 'had last', 'compare', 'comparison', 
        'vs', 'versus', 'between', 'year over year', 'review', 'annual review', 
        'mid year review', 'mid-year review', 'midyear'
    ]
    
    contains_year = bool(re.search(r'\b20\d{2}\b', text_lower))
    contains_quarter = any(q in text_lower for q in ['q1', 'q2', 'q3', 'q4', 'quarter 1', 'quarter 2', 'quarter 3', 'quarter 4', 'first quarter', 'second quarter', 'third quarter', 'fourth quarter'])
    
    # Enhanced query detection with better natural language understanding
    is_query = False
    
    # Check for query patterns with improved detection
    query_indicators = [
        # Question words
        any(word in text_lower for word in ['what', 'how', 'when', 'where', 'why', 'which', 'who']),
        # Request words
        any(phrase in text_lower for phrase in ['tell me', 'show me', 'give me', 'can you', 'could you', 'would you']),
        # Information seeking
        any(phrase in text_lower for phrase in ['what is', 'what was', 'what are', 'what were', 'how many', 'how much']),
        # Analysis words
        any(word in text_lower for word in ['average', 'total', 'sum', 'count', 'number', 'compare', 'comparison']),
        # Time references
        any(phrase in text_lower for phrase in ['this week', 'this month', 'this year', 'last week', 'last month', 'last year']),
        # Report words
        any(word in text_lower for word in ['report', 'summary', 'overview', 'recap', 'review', 'trend', 'trends']),
        # Year/quarter references
        contains_year or contains_quarter,
        # Starts with question words
        text_lower.startswith(('what', 'how', 'show', 'give', 'tell', 'can you', 'could you'))
    ]
    
    is_query = any(query_indicators)
    
    # Validate campus exists if provided (AFTER query detection)
    if campus and campus.lower() != 'all_campuses':  # Skip validation for all_campuses
        try:
            campuses_data = get_campuses_for_user()
            valid_campus_ids = [c['id'] for c in campuses_data.get('campuses', [])]
            
            if campus.lower() not in [c_id.lower() for c_id in valid_campus_ids]:
                return jsonify({
                    'error': f'Invalid campus: {campus}. Please select a valid campus.',
                    'text': f'Invalid campus selected. Please choose from the available campuses.',
                    'requires_campus_selection': True
                }), 400
                
        except Exception as e:
            logger.warning(f"Could not validate campus access: {str(e)}")
            # Continue processing if campus validation fails (for backward compatibility)

    # Load conversation memory
    memory = load_conversation_memory()
    
    # Check if this is a query request vs stat logging
    text_lower = text.lower()
    import re
    
    # FIRST: Check for clear query patterns (these take priority)
    query_keywords = [
        'how many', 'what is', 'what was', "what's", 'tell me', 'give me', 'show me',
        'average', 'last week', 'this week', 'last month', 'this month', 'count', 'query', 'data', 
        'has had', 'had this year', 'had this month', 'had last', 'compare', 'comparison', 
        'vs', 'versus', 'between', 'year over year', 'review', 'annual review', 
        'mid year review', 'mid-year review', 'midyear'
    ]
    
    contains_year = bool(re.search(r'\b20\d{2}\b', text_lower))
    contains_quarter = any(q in text_lower for q in ['q1', 'q2', 'q3', 'q4', 'quarter 1', 'quarter 2', 'quarter 3', 'quarter 4', 'first quarter', 'second quarter', 'third quarter', 'fourth quarter'])
    
    # Enhanced query detection with better natural language understanding
    is_query = False
    
    # Check for query patterns with improved detection
    query_indicators = [
        # Question words
        any(word in text_lower for word in ['what', 'how', 'when', 'where', 'why', 'which', 'who']),
        # Request words
        any(phrase in text_lower for phrase in ['tell me', 'show me', 'give me', 'can you', 'could you', 'would you']),
        # Information seeking
        any(phrase in text_lower for phrase in ['what is', 'what was', 'what are', 'what were', 'how many', 'how much']),
        # Analysis words
        any(word in text_lower for word in ['average', 'total', 'sum', 'count', 'number', 'compare', 'comparison']),
        # Time references
        any(phrase in text_lower for phrase in ['this week', 'this month', 'this year', 'last week', 'last month', 'last year']),
        # Report words
        any(word in text_lower for word in ['report', 'summary', 'overview', 'recap', 'review', 'trend', 'trends']),
        # Year/quarter references
        contains_year or contains_quarter,
        # Starts with question words
        text_lower.startswith(('what', 'how', 'show', 'give', 'tell', 'can you', 'could you'))
    ]
    
    is_query = any(query_indicators)
    
    # If it's not clearly a query, check for stat logging patterns
    if not is_query:
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
        
        # Only treat as stat logging if it contains actual numbers and no query keywords
        contains_stat_logging = any(re.search(pattern, text_lower) for pattern in stat_logging_patterns)
        
        # Final check: if it has stat logging patterns but also query words, it's a query
        if contains_stat_logging and any(word in text_lower for word in query_keywords):
            is_query = True
    
    # Handle case where no campus is detected
    if campus is None or campus == "None" or campus == "null":
        # For queries, apply smart defaulting based on user role
        if is_query and current_user.is_authenticated:
            if current_user.role in ['senior_pastor', 'lead_pastor', 'admin']:
                campus = 'all_campuses'
                logger.info(f"Query with no campus - defaulting to all_campuses for senior leadership")
            elif current_user.role == 'campus_pastor':
                campus = getattr(current_user, 'campus', 'all_campuses')
                logger.info(f"Query with no campus - using campus pastor's assigned campus: {campus}")
        else:
            campus = 'all_campuses'  # Default for other roles
            logger.info(f"Query with no campus - defaulting to all_campuses for other roles")
    
    # For stat logging, require campus selection
            return jsonify({
                "text": "I'd be happy to help you input stats! Which campus would you like to input stats for? You can say something like 'Salisbury campus', 'South campus', or just 'Salisbury' or 'South'.",
                "campus": None,
                "stats": {},
                "missing_stats": [],
                "suggestions": ["Try saying: 'Salisbury campus', 'South campus', 'Paradise campus', 'Adelaide City campus'"],
                "insights": ["Please select a campus first"]
            })
    
    # Check permissions based on operation type
    if is_query:
        # Check if user has recall permissions
        if not current_user.has_permission('recall_stats'):
            error_text = "I'm sorry, you don't have permission to query statistics data. You can only log new statistics."
            
            # Generate audio with ElevenLabs if available
            audio_url = None
            if elevenlabs_api_key:
                audio_url = generate_audio_with_elevenlabs(error_text)
            
            return jsonify({
                "error": "You do not have permission to query statistics data",
                "text": error_text,
                "campus": campus,
                "stats": {},
                "missing_stats": [],
                "suggestions": [],
                "insights": ["Permission denied for data queries"],
                "audio_url": audio_url
            }), 403
            
        # For campus pastors, validate they can only access their campus data
        if current_user.role == 'campus_pastor':
            detected_campus = detect_campus(text)
            if detected_campus and detected_campus != 'all_campuses':
                if not current_user.has_permission('recall_stats', detected_campus):
                    error_text = f"I'm sorry, you can only access data for {safe_campus_name(current_user.campus)[1]} campus."
                    
                    # Generate audio with ElevenLabs if available
                    audio_url = None
                    if elevenlabs_api_key:
                        audio_url = generate_audio_with_elevenlabs(error_text)
                    
                    return jsonify({
                        "error": f"You can only access data for {safe_campus_name(current_user.campus)[1]} campus",
                        "text": error_text,
                        "campus": campus,
                        "stats": {},
                        "missing_stats": [],
                        "suggestions": [],
                        "insights": ["Access restricted to your campus only"],
                        "audio_url": audio_url
                    }), 403
            elif detected_campus == 'all_campuses' or not detected_campus:
                # Modify query to restrict to user's campus
                text = text + f" for {safe_campus_name(current_user.campus)[1]}"
                
        # Call the query endpoint internally
        query_data = {"question": text}
    else:
        # Check if user has log permissions for stat logging
        if not current_user.has_permission('log_stats'):
            error_text = "I'm sorry, you don't have permission to log statistics data."
            
            # Generate audio with ElevenLabs if available
            audio_url = None
            if elevenlabs_api_key:
                audio_url = generate_audio_with_elevenlabs(error_text)
            
            return jsonify({
                "error": "You do not have permission to log statistics",
                "text": error_text,
                "campus": campus,
                "stats": {},
                "missing_stats": [],
                "suggestions": [],
                "insights": ["Permission denied for data logging"],
                "audio_url": audio_url
            }), 403

    # Process based on operation type
    if is_query:
        # Call the query endpoint internally
        query_data = {"question": text}
        query_response = query_data_internal(query_data)
        if not query_response:
            return jsonify({"error": "No response from query_data_internal"}), 500
        # Format response for frontend
        if query_response and "error" in query_response:
            response_text = query_response["error"]
        else:
            # Use the actual report text if available, otherwise fallback
            response_text = query_response.get("text", query_response.get("answer", "I couldn't find that information."))
        
        # Generate audio with ElevenLabs if available
        audio_url = None
        if elevenlabs_api_key:
            audio_url = generate_audio_with_elevenlabs(response_text)
        
        # Format response for frontend - preserve all query fields and force popup
        response = {
            "text": response_text,
            "campus": display_campus_name(campus),
            "stats": {},
            "missing_stats": [],
            "suggestions": [],
            "insights": [response_text],
            "audio_url": audio_url,
            "popup": True  # Force popup for all queries
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
        if "cross_location" in query_response:
            response["cross_location"] = query_response["cross_location"]
        if "campuses" in query_response:
            response["campuses"] = query_response["campuses"]
        if "data" in query_response:
            response["data"] = query_response["data"]
        if "year" in query_response:
            response["year"] = query_response["year"]
        if "summary" in query_response:
            response["summary"] = query_response["summary"]
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
            
            # Calculate Sunday date (the Sunday that just passed)
            today = datetime.now()
            days_since_sunday = (today.weekday() + 1) % 7
            sunday_date = (today - timedelta(days=days_since_sunday)).strftime('%Y-%m-%d')
            
            date = sunday_date
            
            # Create row in exact column order matching full structure:
            # A=Timestamp, B=Date, C=Campus, D=Total Attendance, E=First Time Visitors, F=Visitors, G=Information Gathered,
            # H=First Time Christians, I=Rededications, J=Youth Attendance, K=Youth Salvations, L=Youth New People,
            # M=Kids Attendance, N=Kids Leaders, O=New Kids, P=New Kids Salvations, Q=Connect Groups, R=Dream Team, S=Tithe, T=Baptisms, U=Child Dedications
            row = [
                timestamp,  # A - Timestamp
                date,  # B - Date (Sunday date)
                result.get("Campus", display_campus_name(campus)),  # C - Campus
                result.get("Total Attendance", ""),  # D - Total Attendance
                result.get("First Time Visitors", ""),  # E - First Time Visitors
                result.get("Visitors", ""),  # F - Visitors
                result.get("Information Gathered", ""),  # G - Information Gathered
                result.get("First Time Christians", ""),  # H - First Time Christians
                result.get("Rededications", ""),  # I - Rededications
                result.get("Youth Attendance", ""),  # J - Youth Attendance
                result.get("Youth Salvations", ""),  # K - Youth Salvations
                result.get("Youth New People", ""),  # L - Youth New People
                result.get("Kids Attendance", ""),  # M - Kids Attendance
                result.get("Kids Leaders", ""),  # N - Kids Leaders
                result.get("New Kids", ""),  # O - New Kids
                result.get("New Kids Salvations", ""),  # P - New Kids Salvations
                result.get("Connect Groups", ""),  # Q - Connect Groups
                result.get("Dream Team", ""),  # R - Dream Team
                result.get("Tithe", ""),  # S - Tithe
                result.get("Baptisms", ""),  # T - Baptisms
                result.get("Child Dedications", "")  # U - Child Dedications
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
    response_text = insights[0] if insights else "Thanks for inputting those stats!"
    
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
@login_required
def get_campuses():
    """Get list of active campuses for dropdowns based on user permissions"""
    active_campuses = get_active_campuses()
    
    # Filter campuses based on user role and permissions
    if current_user.role == 'admin' or current_user.role == 'senior_leader':
        # Admin and senior leaders see all campuses
        filtered_campuses = active_campuses
        default_campus = "all_campuses"
    elif current_user.role == 'campus_pastor':
        # Campus pastors only see their assigned campus
        filtered_campuses = [c for c in active_campuses if c['id'] == current_user.campus]
        default_campus = current_user.campus
    elif current_user.role == 'finance':
        # Finance users see all campuses (for logging purposes)
        filtered_campuses = active_campuses
        default_campus = "all_campuses"
    elif current_user.role == 'pastor':
        # Pastors see all campuses (for logging purposes)
        filtered_campuses = active_campuses
        default_campus = "all_campuses"
    else:
        # Default to all campuses for unknown roles
        filtered_campuses = active_campuses
        default_campus = "all_campuses"
    
    return jsonify({
        "campuses": [{'id': c['id'], 'name': c['name']} for c in filtered_campuses],
        "default": default_campus
    })

@app.route('/api/campuses/create', methods=['POST'])
@admin_required
def create_campus_api():
    """Create a new campus via API"""
    if not request.is_json:
        return jsonify({"error": "Expected JSON request"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing or invalid JSON body"}), 400
    
    # Extract campus data
    campus_name = data.get('name', '').strip()
    campus_address = data.get('address', '').strip()
    campus_pastor = data.get('pastor', '').strip()
    campus_status = data.get('status', 'active')
    
    if not campus_name:
        return jsonify({"error": "Campus name is required"}), 400
    
    # Load existing campuses
    campuses_db = load_campuses_database()
    
    # Generate campus ID from name
    campus_id = campus_name.lower().replace(' ', '_').replace('-', '_')
    
    # Check if campus already exists
    if campus_id in campuses_db.get('campuses', {}):
        return jsonify({"error": "Campus already exists"}), 400
    
    # Create new campus
    new_campus = {
        "id": campus_id,
        "name": campus_name,
        "display_name": campus_name,
        "slug": campus_id,
        "active": campus_status == 'active',
        "address": campus_address,
        "pastor": campus_pastor,
        "detection_patterns": [campus_name.lower()],
        "created_date": datetime.now().strftime('%Y-%m-%d'),
        "notes": None
    }
    
    # Add to database
    campuses_db['campuses'][campus_id] = new_campus
    
    # Save database
    if save_campuses_database(campuses_db):
        return jsonify({
            "success": True,
            "message": "Campus created successfully",
            "campus": new_campus
        })
    else:
        return jsonify({"error": "Failed to save campus"}), 500

@app.route('/api/campuses/<campus_id>/edit', methods=['POST'])
@admin_required
def edit_campus_api(campus_id):
    """Edit an existing campus via API"""
    if not request.is_json:
        return jsonify({"error": "Expected JSON request"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing or invalid JSON body"}), 400
    
    # Load existing campuses
    campuses_db = load_campuses_database()
    
    # Check if campus exists
    if campus_id not in campuses_db.get('campuses', {}):
        return jsonify({"error": "Campus not found"}), 404
    
    # Update campus data
    campus = campuses_db['campuses'][campus_id]
    
    if 'name' in data:
        campus['name'] = data['name'].strip()
        campus['display_name'] = data['name'].strip()
    
    if 'address' in data:
        campus['address'] = data['address'].strip()
    
    if 'pastor' in data:
        campus['pastor'] = data['pastor'].strip()
    
    if 'status' in data:
        campus['active'] = data['status'] == 'active'
    
    # Save database
    if save_campuses_database(campuses_db):
        return jsonify({
            "success": True,
            "message": "Campus updated successfully",
            "campus": campus
        })
    else:
        return jsonify({"error": "Failed to save campus"}), 500

@app.route('/api/campuses/<campus_id>/delete', methods=['POST'])
@admin_required
def delete_campus_api(campus_id):
    """Delete a campus via API"""
    # Load existing campuses
    campuses_db = load_campuses_database()
    
    # Check if campus exists
    if campus_id not in campuses_db.get('campuses', {}):
        return jsonify({"error": "Campus not found"}), 404
    
    # Check if it's a special campus that shouldn't be deleted
    if campus_id == 'all_campuses':
        return jsonify({"error": "Cannot delete special campus 'all_campuses'"}), 400
    
    # Remove campus
    del campuses_db['campuses'][campus_id]
    
    # Save database
    if save_campuses_database(campuses_db):
        return jsonify({
            "success": True,
            "message": "Campus deleted successfully"
        })
    else:
        return jsonify({"error": "Failed to save campus"}), 500

@app.route('/api/query', methods=['POST'])
@log_endpoint
@login_required
def query():
    """Query historical data and answer questions about stats"""
    if not request.is_json:
        return jsonify({"error": "Expected JSON request"}), 400

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Missing or invalid JSON body"}), 400

    # Check if user has recall permissions
    if not current_user.has_permission('recall_stats'):
        return jsonify({"error": "You do not have permission to recall statistics data"}), 403

    # For campus pastors, validate they can only access their campus data
    if current_user.role == 'campus_pastor':
        # Extract campus from query if possible
        question = data.get('question', '').lower()
        detected_campus = detect_campus(question)
        
        # If a specific campus is detected, check if user can access it
        if detected_campus and detected_campus != 'all_campuses':
            if not current_user.has_permission('recall_stats', detected_campus):
                return jsonify({
                    "error": f"You can only access data for {safe_campus_name(current_user.campus)[1]} campus"
                }), 403
        # If query is for all campuses, restrict to user's campus
        elif detected_campus == 'all_campuses' or not detected_campus:
            data['question'] = data.get('question', '') + f" for {safe_campus_name(current_user.campus)[1]}"

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

@app.route('/api/test_voice', methods=['POST'])
def test_voice_processing():
    """Test endpoint for voice processing"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    text = data.get('text', '')
    campus = data.get('campus', '')
    
    # Test campus detection
    detected_campus = detect_campus(text)
    
    # Test query detection
    text_lower = text.lower()
    query_keywords = [
        'how many', 'what is', 'what was', "what's", 'tell me', 'give me', 'show me',
        'average', 'last week', 'this week', 'last month', 'this month', 'count', 'query', 'data'
    ]
    is_query = any(word in text_lower for word in query_keywords)
    
    return jsonify({
        "text": text,
        "provided_campus": campus,
        "detected_campus": detected_campus,
        "is_query": is_query,
        "message": "Voice processing test completed"
    })

# Update greeting_audio endpoint to use the correct filename
@app.route('/api/greeting_audio')
def greeting_audio():
    """Generate and serve the greeting audio using ElevenLabs, cache for reuse."""
    logger.info("Greeting audio endpoint called")
    greeting_text = "Connected to Futures Link, how can I help you today?"
    
    # Use absolute path for temp_audio directory
    temp_audio_dir = os.path.join(os.path.dirname(__file__), "temp_audio")
    audio_filename = os.path.join(temp_audio_dir, "greeting_elevenlabs.mp3")
    
    try:
        if not os.path.exists(audio_filename):
            logger.info("Greeting audio file does not exist, generating with ElevenLabs...")
            os.makedirs(temp_audio_dir, exist_ok=True)
            audio_url = generate_audio_with_elevenlabs(greeting_text, filename=audio_filename)
            if not audio_url or not os.path.exists(audio_filename):
                logger.error("Failed to generate greeting audio file with ElevenLabs.")
                return jsonify({"error": "Failed to generate greeting audio file."}), 500
            logger.info(f"Greeting audio file generated: {audio_filename}")
        else:
            logger.info(f"Greeting audio file already exists: {audio_filename}")
        logger.info(f"Serving greeting audio file: {audio_filename}")
        return send_from_directory(temp_audio_dir, 'greeting_elevenlabs.mp3')
    except Exception as e:
        logger.error(f"Error in greeting_audio route: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/quick_input', methods=['POST'])
@login_required
def quick_input():
    """Handle quick input form submissions"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        campus = data.get('campus', '').strip()
        date_str = data.get('date', '').strip()
        stats = data.get('stats', {})
        
        if not campus:
            return jsonify({"error": "Campus is required"}), 400
        
        if not date_str:
            return jsonify({"error": "Date is required"}), 400
        
        # Check if user has permission to log stats
        if not current_user.has_permission('log_stats'):
            return jsonify({"error": "You don't have permission to log stats"}), 403
        
        # Convert stats to the format expected by the existing system
        stat_text_parts = []
        for stat_name, value in stats.items():
            if value and value.strip():
                # Convert stat names to match the expected format
                stat_mapping = {
                    'Sunday Total': 'total_attendance',
                    'New People': 'new_people', 
                    'Salvations': 'new_christians',
                    'Kids Total': 'kids_total',
                    'New Kids': 'kids_new_people',
                    'Kids Salvations': 'kids_salvations',
                    'Youth Total': 'youth_attendance',
                    'Youth NP': 'youth_new_people',
                    'Youth Salvations': 'youth_salvations',
                    'Connect Groups': 'connect_groups',
                    'Baptisms': 'baptisms'
                }
                
                mapped_stat = stat_mapping.get(stat_name, stat_name.lower().replace(' ', '_'))
                stat_text_parts.append(f"{value} {mapped_stat}")
        
        if not stat_text_parts:
            return jsonify({"error": "No stats provided"}), 400
        
        # Create the text input that the existing system can process
        stat_text = f"{', '.join(stat_text_parts)} for {campus} campus on {date_str}"
        
        # Process the stats using the existing voice processing logic
        result = extract_stats_with_context(stat_text, campus)
        
        if not result:
            return jsonify({"error": "Failed to process stats"}), 500
        
        # Save to Google Sheets using existing logic
        try:
            # Get the Google Sheets worksheet
            worksheet = gc.open_by_key(google_sheets_id).worksheet('Church_Stats')
            
            # Prepare the row data
            row_data = {
                'Campus': campus,
                'Date': date_str,
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Raw_Text': stat_text,
                'User': current_user.username
            }
            
            # Add the extracted stats
            for key, value in result.items():
                if value and value != 0:
                    row_data[key] = value
            
            # Convert to list format for Google Sheets
            headers = worksheet.row_values(1)
            row_values = []
            for header in headers:
                row_values.append(row_data.get(header, ''))
            
            # Append the row
            worksheet.append_row(row_values)
            
            # Generate response text
            total_stats = len([v for v in result.values() if v and v != 0])
            response_text = f"Successfully input {total_stats} stats for {campus} campus on {date_str}!"
            
            return jsonify({
                "success": True,
                "text": response_text,
                "stats": result,
                "campus": campus,
                "date": date_str
            })
            
        except Exception as e:
            logger.error(f"Failed to save to Google Sheets: {e}")
            return jsonify({"error": "Failed to save to database"}), 500
            
    except Exception as e:
        logger.error(f"Quick input error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/generate_audio', methods=['POST'])
@login_required
def generate_audio():
    """Generate audio using ElevenLabs for any text"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Create temp_audio directory if it doesn't exist
        temp_audio_dir = os.path.join(os.path.dirname(__file__), "temp_audio")
        if not os.path.exists(temp_audio_dir):
            os.makedirs(temp_audio_dir)
        
        # Generate unique filename based on text hash
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        audio_filename = os.path.join(temp_audio_dir, f"query_{text_hash}.mp3")
        
        # Check if audio file already exists
        if os.path.exists(audio_filename):
            return jsonify({
                "audio_url": f"/temp_audio/query_{text_hash}.mp3"
            })
        
        # Generate new audio
        audio_url = generate_audio_with_elevenlabs(text, filename=audio_filename)
        
        if audio_url:
            return jsonify({
                "audio_url": f"/temp_audio/query_{text_hash}.mp3"
            })
        else:
            return jsonify({"error": "Failed to generate audio"}), 500
            
    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        return jsonify({"error": "Failed to generate audio"}), 500

# Update demo_status to use the correct filename for greeting audio
# Insights API endpoint removed - will be rebuilt from scratch

@app.route('/api/sheets/headers')
@login_required
def get_sheets_headers():
    """Debug endpoint to check Google Sheets headers"""
    try:
        if not sheet:
            return jsonify({'error': 'Google Sheets not available'}), 500
        
        # Get first row to see headers
        data = sheet.get_all_records()
        if data and len(data) > 0:
            first_row = data[0]
            headers = list(first_row.keys())
            
            # Sample first few rows for debugging
            sample_data = data[:3] if len(data) >= 3 else data
            
            return jsonify({
                'available_headers': headers,
                'expected_headers': [
                    'Timestamp', 'Date', 'Campus', 'Total Attendance', 'First Time Visitors', 
                    'Visitors', 'Information Gathered', 'First Time Christians', 'Rededications',
                    'Youth Attendance', 'Youth Salvations', 'Youth New People', 'Kids Attendance',
                    'Kids Leaders', 'New Kids', 'New Kids Salvations', 'Connect Groups', 
                    'Dream Team', 'Tithe', 'Baptisms', 'Child Dedications'
                ],
                'sample_data': sample_data,
                'total_rows': len(data)
            })
        else:
            return jsonify({'error': 'No data found in sheets', 'available_headers': []})
            
    except Exception as e:
        logger.error(f"Error getting sheets headers: {e}")
        return jsonify({'error': f'Failed to get headers: {str(e)}'}), 500

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
        
        # Use absolute path for temp_audio directory
        temp_audio_dir = os.path.join(os.path.dirname(__file__), "temp_audio")
        audio_filename = os.path.join(temp_audio_dir, "greeting_elevenlabs.mp3")
        
        if not os.path.exists(audio_filename):
            if elevenlabs_api_key:
                os.makedirs(temp_audio_dir, exist_ok=True)
                audio_url = generate_audio_with_elevenlabs(greeting_text, filename=audio_filename)
                status["greeting_audio"] = "generated" if audio_url else "failed"
            else:
                status["greeting_audio"] = "no_elevenlabs_key"
        else:
            status["greeting_audio"] = "cached"
    except Exception as e:
        status["greeting_audio"] = f"error: {str(e)}"
    return jsonify(status)

@app.route('/api/dashboard/data')
@login_required
def get_dashboard_api_data():
    """API endpoint for dashboard data"""
    try:
        campus = request.args.get('campus', 'all_campuses')
        date_filter = request.args.get('date_filter', 'last_7_days')
        custom_start_date = request.args.get('custom_start_date', '')
        custom_end_date = request.args.get('custom_end_date', '')
        
        # Get dashboard data using existing function with custom date support
        dashboard_data = get_dashboard_data(campus, date_filter, custom_start_date, custom_end_date)
        
        # Return JSON response
        return jsonify(dashboard_data)
    except Exception as e:
        logger.error(f"Dashboard API error: {e}")
        return jsonify({"error": "Failed to load dashboard data"}), 500

@app.route('/api/users')
@admin_required
def get_users_api():
    """API endpoint for getting all users"""
    try:
        users_data = load_users_database()
        # Convert dictionary to list for frontend compatibility
        users_list = []
        for user_id, user_data in users_data.get('users', {}).items():
            user_data['id'] = user_id  # Ensure ID is included
            users_list.append(user_data)
        return jsonify({"users": users_list})
    except Exception as e:
        logger.error(f"Users API error: {e}")
        return jsonify({"error": "Failed to load users"}), 500

@app.route('/api/users/create', methods=['POST'])
@admin_required
def create_user_api():
    """API endpoint for creating a new user"""
    try:
        data = request.get_json()
        users_data = load_users_database()
        
        # Generate new user ID
        new_id = str(len(users_data.get('users', {})) + 1)
        
        # Create new user
        new_user = {
            'id': new_id,
            'username': data.get('username'),
            'email': data.get('email', f"{data.get('username')}@futures.church"),
            'full_name': data.get('full_name', data.get('username')),
            'password_hash': generate_password_hash(data.get('password')),
            'role': data.get('role', 'campus_pastor'),
            'campus': data.get('campus', 'all_campuses'),
            'active': True,
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'last_login': None
        }
        
        users_data['users'][new_id] = new_user
        save_users_database(users_data)
        
        return jsonify({"success": True, "message": "User created successfully"})
    except Exception as e:
        logger.error(f"Create user API error: {e}")
        return jsonify({"error": "Failed to create user"}), 500

@app.route('/api/users/<user_id>/edit', methods=['POST'])
@admin_required
def edit_user_api(user_id):
    """API endpoint for editing a user"""
    try:
        data = request.get_json()
        users_data = load_users_database()
        
        # Find user by ID
        user = users_data.get('users', {}).get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Update user data
        user['username'] = data.get('username', user['username'])
        if data.get('password'):
            user['password_hash'] = generate_password_hash(data['password'])
        user['role'] = data.get('role', user['role'])
        user['campus'] = data.get('campus', user.get('campus', 'all_campuses'))
        user['full_name'] = data.get('full_name', user.get('full_name', user['username']))
        user['email'] = data.get('email', user.get('email', f"{user['username']}@futures.church"))
        
        save_users_database(users_data)
        
        return jsonify({"success": True, "message": "User updated successfully"})
    except Exception as e:
        logger.error(f"Edit user API error: {e}")
        return jsonify({"error": "Failed to update user"}), 500

@app.route('/api/users/<user_id>/delete', methods=['POST'])
@admin_required
def delete_user_api(user_id):
    """API endpoint for deleting a user"""
    try:
        users_data = load_users_database()
        
        # Check if user exists
        if user_id not in users_data.get('users', {}):
            return jsonify({"error": "User not found"}), 404
        
        # Remove user
        del users_data['users'][user_id]
        save_users_database(users_data)
        
        return jsonify({"success": True, "message": "User deleted successfully"})
    except Exception as e:
        logger.error(f"Delete user API error: {e}")
        return jsonify({"error": "Failed to delete user"}), 500

def normalize_campus(name):
    return str(name).strip().lower().replace("_", " ")

# Add this helper near the top of the file (after imports)
def display_campus_name(name):
    return str(name).replace('_', ' ').title()

def safe_campus_name(campus_attr) -> tuple:
    """Safely get campus name and display name from user campus attribute"""
    if campus_attr is None:
        return 'main', 'Main Campus'
    elif isinstance(campus_attr, str):
        return campus_attr, campus_attr.replace('_', ' ').title()
    elif isinstance(campus_attr, dict):
        # If it's a dict, try to get a name field
        campus_name = campus_attr.get('name', campus_attr.get('id', 'main'))
        if isinstance(campus_name, str):
            return campus_name, campus_name.replace('_', ' ').title()
    
    # Fallback
    return 'main', 'Main Campus'

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

def detect_multiple_stats(question: str) -> list:
    """Detect multiple stat requests like 'np and nc' or 'new people and new christians'"""
    question_lower = question.lower()
    
    stat_keywords = {
        'attendance': ['attendance', 'people attended', 'how many people', 'total attendance', 'people came', 'came to church'],
        'new_people': ['new people', 'new visitors', 'visitors', 'first time', 'np', 'new guests'],
        'new_christians': ['new christians', 'salvations', 'souls', 'decisions', 'gave their lives', 'nc', 'new believers'],
        'youth': ['youth', 'teens', 'teenagers', 'young people', 'youth ministry', 'youth group'],
        'kids': ['kids', 'children', 'little ones', 'nursery', 'kids ministry'],
        'connect_groups': ['connect groups', 'connectgroups', 'groups', 'small groups', 'cell groups', 'how many connect groups']
    }
    
    detected_stats = []
    
    # Check for each stat type in the question
    for stat_type, keywords in stat_keywords.items():
        for keyword in keywords:
            if keyword in question_lower:
                if stat_type not in detected_stats:
                    detected_stats.append(stat_type)
                break
    
    # Special handling for common abbreviations combinations
    if 'np and nc' in question_lower or 'new people and new christians' in question_lower:
        detected_stats = ['new_people', 'new_christians']
    elif 'youth and kids' in question_lower:
        detected_stats = ['youth', 'kids']
    elif 'attendance and new people' in question_lower:
        detected_stats = ['attendance', 'new_people']
    
    return detected_stats

def create_targeted_report_data(stat_types, analysis_data: dict, year: int, count: int) -> list:
    """Create report data showing only the requested stat(s) instead of all stats"""
    # Handle single stat type or list of stat types
    if isinstance(stat_types, str):
        stat_types = [stat_types]
    
    stat_mapping = {
        'attendance': {
            'label': 'Total Attendance',
            'total': analysis_data.get('total_attendance', 0),
            'average': analysis_data.get('averages', {}).get('attendance', 0)
        },
        'new_people': {
            'label': 'New People',
            'total': analysis_data.get('total_new_people', 0),
            'average': analysis_data.get('averages', {}).get('new_people', 0)
        },
        'new_christians': {
            'label': 'New Christians',
            'total': analysis_data.get('total_new_christians', 0),
            'average': analysis_data.get('averages', {}).get('new_christians', 0)
        },
        'youth': {
            'label': 'Youth',
            'total': analysis_data.get('total_youth', 0),
            'average': analysis_data.get('averages', {}).get('youth', 0)
        },
        'kids': {
            'label': 'Kids',
            'total': analysis_data.get('total_kids', 0),
            'average': analysis_data.get('averages', {}).get('kids', 0)
        },
        'connect_groups': {
            'label': 'Connect Groups',
            'total': analysis_data.get('total_connect_groups', 0),
            'average': analysis_data.get('averages', {}).get('connect_groups', 0)
        }
    }
    
    # Build report data for the requested stats
    report_data = []
    valid_stats_found = False
    
    for stat_type in stat_types:
        if stat_type in stat_mapping:
            valid_stats_found = True
            stat_info = stat_mapping[stat_type]
            report_data.append({
                "label": stat_info['label'],
                "total": stat_info['total'],
                "average": stat_info['average'],
                "count": count,
                "year": year
            })
    
    # If no valid stats found, fallback to all stats
    if not valid_stats_found:
        return [
            {"label": "Total Attendance", "total": analysis_data.get("total_attendance", 0), "average": analysis_data.get("averages", {}).get("attendance", 0), "count": count, "year": year},
            {"label": "New People", "total": analysis_data.get("total_new_people", 0), "average": analysis_data.get("averages", {}).get("new_people", 0), "count": count, "year": year},
            {"label": "New Christians", "total": analysis_data.get("total_new_christians", 0), "average": analysis_data.get("averages", {}).get("new_christians", 0), "count": count, "year": year},
            {"label": "Youth", "total": analysis_data.get("total_youth", 0), "average": analysis_data.get("averages", {}).get("youth", 0), "count": count, "year": year},
            {"label": "Kids", "total": analysis_data.get("total_kids", 0), "average": analysis_data.get("averages", {}).get("kids", 0), "count": count, "year": year},
            {"label": "Connect Groups", "total": analysis_data.get("total_connect_groups", 0), "average": analysis_data.get("averages", {}).get("connect_groups", 0), "count": count, "year": year},
        ]
    
    return report_data

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
    
    # Clean up date range - remove generic or empty date ranges
    generic_ranges = ["None", "recent data", " recent data", "recent", " recent"]
    clean_date_range = ""
    if date_range and date_range.strip() not in generic_ranges:
        clean_date_range = f" {date_range.strip()}" if not date_range.strip().startswith(" ") else date_range
    
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

    # Set up date ranges based on review type and date_range parameter
    now = datetime.now()
    
    if review_type == 'weekly':
        start_date = now - timedelta(days=7)
        end_date = now
        period_label = f"for the last 7 days ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})"
    elif review_type == 'monthly':
        # Parse month and year from date_range (e.g., "January 2024")
        if date_range and ' ' in date_range:
            try:
                month_name, year_str = date_range.split(' ')
                month_num = {
                    'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                    'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
                }[month_name]
                year = int(year_str)
                start_date = datetime(year, month_num, 1)
                if month_num == 12:
                    end_date = datetime(year, month_num, 31)
                else:
                    end_date = datetime(year, month_num + 1, 1) - timedelta(days=1)
                period_label = f"for {month_name} {year}"
            except (ValueError, KeyError):
                # Fallback to current month
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = now
                period_label = f"for {now.strftime('%B %Y')}"
        else:
            # Default to current month
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
            period_label = f"for {now.strftime('%B %Y')}"
    elif review_type == 'quarterly':
        # Parse quarter and year from date_range (e.g., "Q1 2024")
        if date_range and ' ' in date_range:
            try:
                quarter_str, year_str = date_range.split(' ')
                quarter = int(quarter_str[1])  # Extract number from "Q1", "Q2", etc.
                year = int(year_str)
                start_month = 3 * (quarter - 1) + 1
                start_date = datetime(year, start_month, 1)
                if quarter == 4:
                    end_date = datetime(year, 12, 31)
                else:
                    end_date = datetime(year, start_month + 2, 28)  # Approximate end of quarter
                    if start_month + 2 <= 12:
                        end_date = datetime(year, start_month + 3, 1) - timedelta(days=1)
                period_label = f"for Q{quarter} {year}"
            except (ValueError, IndexError):
                # Fallback to current quarter
                quarter = (now.month - 1) // 3 + 1
                start_month = 3 * (quarter - 1) + 1
                start_date = now.replace(month=start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
                if quarter == 4:
                    end_date = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
                else:
                    end_date = now.replace(month=start_month + 2, day=28, hour=23, minute=59, second=59, microsecond=999999)
                period_label = f"for Q{quarter} {now.year}"
        else:
            # Default to current quarter
            quarter = (now.month - 1) // 3 + 1
            start_month = 3 * (quarter - 1) + 1
            start_date = now.replace(month=start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
            if quarter == 4:
                end_date = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
            else:
                end_date = now.replace(month=start_month + 2, day=28, hour=23, minute=59, second=59, microsecond=999999)
            period_label = f"for Q{quarter} {now.year}"
    elif review_type == 'mid_year':
        # Parse year from date_range (e.g., "Jan-Jun 2024")
        if date_range and ' ' in date_range:
            try:
                _, year_str = date_range.split(' ')
                year = int(year_str)
                start_date = datetime(year, 1, 1)
                end_date = datetime(year, 6, 30)
                period_label = f"for Jan-Jun {year}"
            except ValueError:
                # Fallback to current year
                start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(month=6, day=30, hour=23, minute=59, second=59, microsecond=999999)
                period_label = f"for Jan-Jun {now.year}"
        else:
            # Default to current year
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(month=6, day=30, hour=23, minute=59, second=59, microsecond=999999)
            period_label = f"for Jan-Jun {now.year}"
    else:  # annual
        # Use current year by default
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
            stat_fields = ["Total Attendance", "New People", "New Christians", "First Time Christians", "Youth Attendance", "Kids Total", "Kids Attendance", "Connect Groups", "Tithe"]
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
    
    # DEBUG: Show what data was actually found
    if filtered_rows:
        print(f"[CROSS-CAMPUS DEBUG] Found data from these rows:")
        for i, row in enumerate(filtered_rows[:5]):  # Show first 5 rows
            campus = row.get("Campus", "Unknown")
            timestamp = row.get("Timestamp", "Unknown")
            attendance = row.get("Total Attendance", 0)
            new_people = row.get("New People", 0)
            new_christians = row.get("New Christians", 0)
            youth = row.get("Youth Attendance", 0)
            kids = row.get("Kids Total", 0)
            connect_groups = row.get("Connect Groups", 0)
            print(f"  {i+1}. {campus} ({timestamp}): Att={attendance}, NP={new_people}, NC={new_christians}, Youth={youth}, Kids={kids}, CG={connect_groups}")

    if not filtered_rows:
        return {
            "type": f"Cross-Campus {review_type.title()} Report",
            "campus": "Futures Church (All Campuses)",
            "date_range": period_label,
            "summary": f"No valid stats found for any campus {period_label}.",
            "stats": {},
            "entry_count": 0
        }

    # Use comprehensive stats calculation
    analysis_data = calculate_stats_from_filtered_rows(filtered_rows)
    # Create comprehensive stats structure
    comprehensive_stats = {}
    stat_mappings = [
        ("total_attendance", "attendance", "Total Attendance"),
        ("total_first_time_visitors", "first_time_visitors", "First Time Visitors"),
        ("total_information_gathered", "information_gathered", "Information Gathered"),
        ("total_new_christians", "new_christians", "New Christians"),
        ("total_rededications", "rededications", "Rededications"),
        ("total_youth_attendance", "youth_attendance", "Youth Attendance"),
        ("total_youth_salvations", "youth_salvations", "Youth Salvations"),
        ("total_youth_new_people", "youth_new_people", "Youth New People"),
        ("total_kids_attendance", "kids_attendance", "Kids Attendance"),
        ("total_kids_leaders", "kids_leaders", "Kids Leaders"),
        ("total_new_kids", "new_kids", "New Kids"),
        ("total_new_kids_salvations", "new_kids_salvations", "New Kids Salvations"),
        ("total_connect_groups", "connect_groups", "Connect Groups"),
        ("total_dream_team", "dream_team", "Dream Team"),
        ("total_tithe", "tithe", "Tithe"),
        ("total_baptisms", "baptisms", "Baptisms"),
        ("total_child_dedications", "child_dedications", "Child Dedications"),
        ("total_new_people", "new_people", "New People"),  # Keep for backward compatibility
    ]
    
    for stat_key, avg_key, label in stat_mappings:
        total = analysis_data.get(stat_key, 0)
        average = analysis_data.get("averages", {}).get(avg_key, 0)
        
        # Include all stats that have data or are important to show (including tithe)
        if total > 0 or label in ["Total Attendance", "First Time Visitors", "New People", "New Christians", "Rededications", "Youth Attendance", "Youth Salvations", "Youth New People", "Kids Attendance", "Kids Leaders", "New Kids", "New Kids Salvations", "Connect Groups", "Dream Team", "Tithe", "Baptisms", "Child Dedications", "Information Gathered"]:
            comprehensive_stats[avg_key] = {
                "total": total,
                "average": round(average, 1),
                "label": label
            }
    
    report = {
        "type": f"Cross-Campus {review_type.title()} Report",
        "campus": "Futures Church (All Campuses)",
        "date_range": period_label,
        "summary": f"Futures Church {review_type} report across all campuses {period_label}",
        "stats": comprehensive_stats,
        "entry_count": analysis_data.get("total_entries", 0)
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

# Pastor to review type mapping
PASTOR_MAPPING = {
    # Senior/Lead Pastors - get comprehensive all-campus reviews
    'ps ashley': 'all_campuses',
    'pastor ashley': 'all_campuses',
    'ashley': 'all_campuses',
    
    'ps josh': 'all_campuses',  # Lead Pastor - gets all campus data
    'pastor josh': 'all_campuses',
    'josh': 'all_campuses',
    
    'ps peter': 'paradise',
    'pastor peter': 'paradise',
    'peter': 'paradise',
    
    'ps david': 'adelaide_city',
    'pastor david': 'adelaide_city',
    'david': 'adelaide_city',
    
    'ps sarah': 'salisbury',
    'pastor sarah': 'salisbury',
    'sarah': 'salisbury',
    
    'ps mark': 'mount_barker',
    'pastor mark': 'mount_barker',
    'mark': 'mount_barker',
}

def detect_pastor_name(question: str) -> Optional[str]:
    """Detect pastor names in the question and return the campus they map to"""
    question_lower = question.lower()
    
    # Check for pastor names
    for pastor_name, campus in PASTOR_MAPPING.items():
        if pastor_name in question_lower:
            logger.info(f"[PASTOR_DETECTION] Found pastor '{pastor_name}' -> maps to '{campus}'")
            return campus
    
    return None

# Patch the review detection logic in query_data_internal
# ... existing code ...

@app.route('/heartbeat')
def heartbeat():
    return render_template('heartbeat.html')

@app.route('/journey')
def journey():
    return render_template('journey.html')

if __name__ == '__main__':
    print("Starting app.py")
    print("App running on: http://localhost:5002")
    app.run(debug=False, port=5002)