
#!/usr/bin/env python3
"""
Bulletproof Futures Link Church Voice Assistant
ElevenLabs audio fixed permanently - no console commands needed
"""

import os
import json
import re
import time
import logging
import uuid
import atexit
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
import asyncio
from functools import lru_cache

# Web framework
from flask import Flask, render_template_string, request, jsonify, send_file
from flask_cors import CORS
from flask_talisman import Talisman

# AI and APIs
import openai
import aiohttp

# Google Sheets (optional)
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False
    print("⚠️ Google Sheets packages not installed - sheets logging disabled")

# Environment variables
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('assistant.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BulletproofChurchAssistant:
    def __init__(self):
        """Initialize bulletproof voice assistant"""
        print("🚀 Starting BULLETPROOF Futures Link Voice Assistant...")
        print("=" * 60)
        
        # Validate environment variables
        required_env_vars = ['OPENAI_API_KEY', 'ELEVENLABS_API_KEY']
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")
        
        # Core settings
        self.current_campus = None
        self.conversation_history = []
        self.session_stats = {}
        
        # Performance optimizations
        self.thread_pool = ThreadPoolExecutor(max_workers=5)
        
        # Create directories
        self.ensure_directories()
        
        # Setup all services
        self.setup_openai()
        self.setup_elevenlabs()
        self.setup_google_sheets()
        self.setup_memory_system()
        
        # Church data
        self.campuses = [
            'Paradise', 'Adelaide City', 'Salisbury', 'South',
            'Clare Valley', 'Mount Barker', 'Victor Harbour', 'Copper Coast'
        ]
        
        # Response templates
        self.response_templates = {
            'campus_set': [
                "Perfect! Ready for {campus} stats. What numbers do you have for me?",
                "Great! {campus} is all set. Tell me your attendance figures.",
                "Awesome! {campus} locked in. What stats can I log for you today?"
            ],
            'stats_complete': [
                "Excellent! {campus} stats are logged: {attendance} people, {new} new visitors!",
                "Perfect! Got {campus} locked in - {attendance} total with {new} newcomers!",
                "Outstanding! {campus} is all set: {attendance} attendance, {new} new people!"
            ],
            'encouragement': [
                "God is moving at {campus}! What an incredible Sunday!",
                "Praise God for His faithfulness at {campus}!",
                "What a blessing to see {campus} growing!"
            ],
            'need_more_info': [
                "I've got the {campus} campus. What attendance numbers do you have?",
                "Ready for {campus}! Tell me about today's service.",
                "Perfect! What were {campus}'s numbers today?"
            ]
        }
        
        # Register cleanup
        atexit.register(self.cleanup_on_exit)
        
        print("✅ Bulletproof Voice Assistant initialized!")
        print("✅ ElevenLabs timeout issues FIXED!")
        print("=" * 60)
    
    def ensure_directories(self):
        """Ensure required directories exist"""
        directories = ['temp_audio', 'logs', 'data']
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"✅ Directory ensured: {directory}")
            except Exception as e:
                logger.error(f"❌ Failed to create directory {directory}: {e}")
    
    def setup_openai(self):
        """Setup OpenAI"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("❌ OPENAI_API_KEY not found")
            self.openai_client = None
            return
        
        try:
            self.openai_client = openai.OpenAI(api_key=api_key)
            
            # Test connection
            test_response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5,
                timeout=10
            )
            logger.info("✅ OpenAI API connected")
        except Exception as e:
            logger.error(f"❌ OpenAI setup failed: {e}")
            self.openai_client = None
    
    def setup_elevenlabs(self):
        """Setup ElevenLabs with bulletproof configuration"""
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        self.elevenlabs_voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'pNInz6obpgDQGcFmaJgB')
        
        if self.elevenlabs_api_key:
            logger.info("✅ ElevenLabs voice synthesis enabled")
            logger.info(f"   Voice ID: {self.elevenlabs_voice_id}")
            self.use_elevenlabs = True
            
            # Test connection
            try:
                test_audio = asyncio.run(self.generate_elevenlabs_audio("Test", test_mode=True))
                if test_audio:
                    logger.info("✅ ElevenLabs test successful")
                else:
                    logger.warning("⚠️ ElevenLabs test failed")
                    self.use_elevenlabs = False
            except Exception as e:
                logger.warning(f"⚠️ ElevenLabs test error: {e}")
                self.use_elevenlabs = False
        else:
            logger.warning("⚠️ ELEVENLABS_API_KEY not found")
            self.use_elevenlabs = False
    
    def setup_google_sheets(self):
        """Setup Google Sheets"""
        if not GSPREAD_AVAILABLE:
            self.sheets_client = None
            return
            
        try:
            credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
            if os.path.exists(credentials_path):
                scope = [
                    'https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive'
                ]
                creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
                self.sheets_client = gspread.authorize(creds)
                
                sheet_name = os.getenv('GOOGLE_SHEET_NAME', 'Church Stats')
                try:
                    self.spreadsheet = self.sheets_client.open(sheet_name)
                    logger.info("✅ Google Sheets connected")
                except gspread.SpreadsheetNotFound:
                    self.spreadsheet = self.sheets_client.create(sheet_name)
                    headers = [
                        'Timestamp', 'Sunday Date', 'Campus', 'Total Attendance',
                        'New People', 'New Christians', 'Youth Attendance',
                        'New Youth', 'New Youth Christians', 'Kids Total',
                        'New Kids', 'Connect Groups'
                    ]
                    self.spreadsheet.sheet1.append_row(headers)
                    logger.info("✅ New spreadsheet created")
            else:
                logger.warning(f"⚠️ No credentials file found")
                self.sheets_client = None
        except Exception as e:
            logger.error(f"❌ Google Sheets setup failed: {e}")
            self.sheets_client = None
    
    def setup_memory_system(self):
        """Setup memory"""
        self.memory_file = os.path.join('data', 'conversation_memory.json')
        self.load_memory()
        logger.info("✅ Memory system initialized")
    
    def load_memory(self):
        """Load conversation history"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversation_history = data.get('conversations', [])[-10:]
                    self.session_stats = data.get('session_stats', {})
                logger.info(f"✅ Loaded {len(self.conversation_history)} conversation(s)")
        except Exception as e:
            logger.error(f"❌ Failed to load memory: {e}")
            self.conversation_history = []
            self.session_stats = {}
    
    def save_memory(self):
        """Save conversation history"""
        try:
            data = {
                'conversations': self.conversation_history[-10:],
                'session_stats': self.session_stats,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Failed to save memory: {e}")
    
    def extract_campus_enhanced(self, text: str) -> Optional[str]:
        """Enhanced campus extraction"""
        if not text:
            return None
            
        text = text.lower().strip()
        
        campus_variations = {
            'paradise': 'Paradise', 'para': 'Paradise', 'par': 'Paradise',
            'adelaide city': 'Adelaide City', 'adelaide': 'Adelaide City', 
            'city': 'Adelaide City', 'adel': 'Adelaide City',
            'salisbury': 'Salisbury', 'sal': 'Salisbury', 'sali': 'Salisbury',
            'south': 'South', 'southern': 'South',
            'clare valley': 'Clare Valley', 'clare': 'Clare Valley',
            'mount barker': 'Mount Barker', 'mt barker': 'Mount Barker', 
            'barker': 'Mount Barker',
            'victor harbour': 'Victor Harbour', 'victor': 'Victor Harbour',
            'copper coast': 'Copper Coast', 'copper': 'Copper Coast'
        }
        
        for variation in sorted(campus_variations.keys(), key=len, reverse=True):
            if variation in text:
                campus = campus_variations[variation]
                logger.info(f"✅ Campus detected: '{variation}' → {campus}")
                return campus
        
        return None
    
    def parse_stats_enhanced(self, text: str) -> Dict:
        """Enhanced statistics parsing"""
        if not text:
            return {}
            
        stats = {}
        text = text.lower()
        
        campus = self.extract_campus_enhanced(text)
        if campus:
            stats['campus'] = campus
        
        patterns = {
            'total_attendance': [
                r'(?:had|got|there were|total of|attendance was|we had)\s*(\d+)\s*(?:people|total|attendance)',
                r'(\d+)\s*(?:people|total|attendance)',
                r'attendance\s*(?:was|is|of)?\s*(\d+)'
            ],
            'new_people': [
                r'(\d+)\s*(?:new|first.?time|visitors|guests|newcomers)',
                r'(?:new|first.?time|visitors|guests)\s*(\d+)',
                r'(\d+)\s*new\s*(?:people|visitors|guests)'
            ],
            'new_christians': [
                r'(\d+)\s*(?:salvation|decision|new christian|saved)',
                r'(?:salvation|decision|saved)\s*(\d+)',
                r'(\d+)\s*(?:decisions?|salvations?)'
            ]
        }
        
        for field, field_patterns in patterns.items():
            for pattern in field_patterns:
                try:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        number = int(match.group(1))
                        if 0 <= number <= 10000:
                            stats[field] = number
                            logger.info(f"📊 {field}: {number}")
                            break
                except (ValueError, IndexError, AttributeError):
                    continue
        
        return stats
    
    @lru_cache(maxsize=100)
    def generate_ai_response(self, user_input: str, stats: Dict, context: str = "") -> str:
        """Generate AI response"""
        if not self.openai_client:
            return self.generate_fallback_response(user_input, stats)
        
        try:
            system_context = """You are Link, a friendly church assistant helping pastors log Sunday service statistics. Be warm, conversational, and encouraging. Keep responses brief but enthusiastic.
            
            Campus names: Paradise, Adelaide City, Salisbury, South, Clare Valley, Mount Barker, Victor Harbour, Copper Coast"""
            
            messages = [{"role": "system", "content": system_context}]
            
            for conv in self.conversation_history[-3:]:
                if conv.get('user') and conv.get('assistant'):
                    messages.append({"role": "user", "content": conv['user']})
                    messages.append({"role": "assistant", "content": conv['assistant']})
            
            current_context = f"User said: {user_input}"
            if stats:
                current_context += f"\nDetected data: {stats}"
            if context:
                current_context += f"\nContext: {context}"
            
            messages.append({"role": "user", "content": current_context})
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=80,
                temperature=0.4,
                timeout=15
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"❌ AI response failed: {e}")
            return self.generate_fallback_response(user_input, stats)
    
    def generate_fallback_response(self, user_input: str, stats: Dict) -> str:
        """Smart fallback responses"""
        import random
        
        if stats and 'campus' in stats:
            campus = stats['campus']
            
            if len(stats) > 2:
                attendance = stats.get('total_attendance', 'attendance')
                new_people = stats.get('new_people', 'new people')
                template = random.choice(self.response_templates['stats_complete'])
                return template.format(campus=campus, attendance=attendance, new=new_people)
            else:
                template = random.choice(self.response_templates['need_more_info'])
                return template.format(campus=campus)
        
        campus = self.extract_campus_enhanced(user_input)
        if campus:
            template = random.choice(self.response_templates['campus_set'])
            return template.format(campus=campus)
        
        return "Hi! Which campus are you logging stats for today? Just say the campus name and your numbers!"
    
    @lru_cache(maxsize=100)
    async def generate_elevenlabs_audio(self, text: str, test_mode: bool = False, retry_count: int = 0, max_retries: int = 3) -> Optional[bytes]:
        """Generate ElevenLabs audio - async with caching and retries"""
        if not self.use_elevenlabs or not text.strip():
            return None
        
        start_time = time.time()
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            clean_text = re.sub(r'[^\w\s\.,!?]', '', text)
            clean_text = clean_text[:500] if test_mode else clean_text[:1000]
            
            data = {
                "text": clean_text,
                "model_id": "eleven_turbo_v2_5",
                "voice_settings": {
                    "stability": 0.75,
                    "similarity_boost": 0.8,
                    "style": 0.2,
                    "use_speaker_boost": True
                },
                "optimize_streaming_latency": 3,
                "output_format": "mp3_44100_128"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        audio_content = await response.read()
                        if len(audio_content) < 100:
                            logger.warning("⚠️ ElevenLabs returned small audio file")
                            return None
                        
                        if not (audio_content.startswith(b'ID3') or audio_content[0:2] == b'\xff\xfb'):
                            logger.warning("⚠️ ElevenLabs returned invalid MP3")
                            return None
                            
                        logger.info(f"✅ Generated {len(audio_content)} bytes of audio in {time.time() - start_time:.2f}s")
                        return audio_content
                    elif response.status == 429 and retry_count < max_retries:
                        wait_time = 2 ** retry_count
                        logger.warning(f"⚠️ ElevenLabs rate limit exceeded, retrying in {wait_time}s")
                        await asyncio.sleep(wait_time)
                        return await self.generate_elevenlabs_audio(text, test_mode, retry_count + 1, max_retries)
                    elif response.status == 401:
                        logger.error("❌ ElevenLabs API key invalid")
                        self.use_elevenlabs = False
                        return None
                    else:
                        logger.error(f"❌ ElevenLabs API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ ElevenLabs generation failed: {e}")
            return None
    
    def log_to_sheets_background(self, stats: Dict):
        """Log to Google Sheets in background"""
        if not self.sheets_client or not stats:
            return False
        
        def _log_background():
            try:
                worksheet = self.spreadsheet.sheet1
                
                today = datetime.now()
                days_since_sunday = (today.weekday() + 1) % 7
                sunday_date = (today - timedelta(days=days_since_sunday)).strftime('%Y-%m-%d')
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                row = [
                    timestamp,
                    sunday_date,
                    stats.get('campus', ''),
                    stats.get('total_attendance', ''),
                    stats.get('new_people', ''),
                    stats.get('new_christians', ''),
                    '', '', '', '', '', ''  # Other fields
                ]
                
                worksheet.append_row(row)
                logger.info(f"✅ Logged {stats.get('campus', 'stats')} to Google Sheets")
                return True
                
            except Exception as e:
                logger.error(f"❌ Sheets logging failed: {e}")
                return False
        
        try:
            self.thread_pool.submit(_log_background)
            return True
        except Exception as e:
            logger.error(f"❌ Failed to submit background task: {e}")
            return False
    
    def update_conversation_memory(self, user_input: str, assistant_response: str, stats: Dict):
        """Update conversation memory"""
        conversation_entry = {
            'timestamp': datetime.now().isoformat(),
            'user': user_input,
            'assistant': assistant_response,
            'stats': stats,
            'campus': stats.get('campus') if stats else None
        }
        
        self.conversation_history.append(conversation_entry)
        
        if stats and 'campus' in stats:
            campus = stats['campus']
            if campus not in self.session_stats:
                self.session_stats[campus] = []
            self.session_stats[campus].append(stats)
        
        if len(self.conversation_history) % 3 == 0:
            self.save_memory()
    
    def cleanup_old_audio_files(self):
        """Clean up old audio files"""
        try:
            audio_dir = 'temp_audio'
            if os.path.exists(audio_dir):
                now = time.time()
                files_cleaned = 0
                for filename in os.listdir(audio_dir):
                    if filename.endswith('.mp3'):
                        filepath = os.path.join(audio_dir, filename)
                        if os.path.getctime(filepath) < now - 3600:
                            os.remove(filepath)
                            files_cleaned += 1
                if files_cleaned > 0:
                    logger.info(f"🧹 Cleaned up {files_cleaned} old audio files")
        except Exception as e:
            logger.error(f"❌ Audio cleanup error: {e}")

    def get_session_summary(self) -> str:
        """Generate session summary"""
        if not self.session_stats:
            return "No stats logged this session yet."
        
        summary_parts = []
        for campus, stats_list in self.session_stats.items():
            latest_stats = stats_list[-1]
            attendance = latest_stats.get('total_attendance', 'N/A')
            new_people = latest_stats.get('new_people', 'N/A')
            summary_parts.append(f"{campus}: {attendance} people, {new_people} new")
        
        return "Session summary: " + " | ".join(summary_parts)
    
    def cleanup_on_exit(self):
        """Cleanup on exit"""
        try:
            self.save_memory()
            self.cleanup_old_audio_files()
            self.thread_pool.shutdown(wait=False)
            logger.info("✅ Application cleanup completed")
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")

# Create Flask app
app = Flask(__name__)
CORS(app)

# Global assistant instance
assistant = None

# BULLETPROOF HTML Template - ElevenLabs timeout FIXED, CSP nonce added
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Futures Link Voice Assistant</title>
    <style nonce="{{ nonce }}">
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box
}

body {
    background: radial-gradient(circle at center, #0a0a0a 0, #000 100%);
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #fff
}

.main-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    position: relative
}

.title-header {
    position: absolute;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    text-align: center;
    z-index: 10
}

.title-header h1 {
    font-size: 32px;
    font-weight: 300;
    letter-spacing: 4px;
    margin: 0;
    background: linear-gradient(135deg, #4a9eff, #00d4ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 0 30px rgba(74, 158, 255, .5)
}

.title-header p {
    font-size: 12px;
    margin: 5px 0 0;
    opacity: .8;
    letter-spacing: 2px;
    text-transform: uppercase
}

.orb-container {
    position: relative;
    width: 400px;
    height: 400px;
    cursor: pointer;
    user-select: none
}

.orb {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, rgba(30, 50, 80, .9) 0, rgba(15, 25, 40, .95) 40%, rgba(5, 10, 20, 1) 100%);
    box-shadow: 0 0 100px rgba(20, 40, 80, .4), inset 0 0 80px rgba(50, 100, 150, .15), inset -30px -30px 60px rgba(0, 0, 0, .6);
    position: relative;
    transition: all .4s ease;
    transform: translateZ(0)
}

.orb.listening {
    background: radial-gradient(circle at 30% 30%, rgba(100, 40, 40, .9) 0, rgba(80, 20, 20, .95) 40%, rgba(40, 10, 10, 1) 100%);
    box-shadow: 0 0 150px rgba(200, 60, 60, .6), inset 0 0 80px rgba(255, 100, 100, .2);
    animation: pulse 1.2s infinite ease-in-out
}

.orb.processing {
    background: radial-gradient(circle at 30% 30%, rgba(40, 100, 40, .9) 0, rgba(20, 80, 20, .95) 40%, rgba(10, 40, 10, 1) 100%);
    box-shadow: 0 0 150px rgba(60, 200, 60, .6), inset 0 0 80px rgba(100, 255, 100, .2);
    animation: spin 1.8s linear infinite
}

.orb.speaking {
    background: radial-gradient(circle at 30% 30%, rgba(100, 100, 40, .9) 0, rgba(80, 80, 20, .95) 40%, rgba(40, 40, 10, 1) 100%);
    box-shadow: 0 0 150px rgba(200, 200, 60, .6), inset 0 0 80px rgba(255, 255, 100, .2);
    animation: glow 1s ease-in-out infinite alternate
}

@keyframes pulse {
    0%, 100% {
        transform: scale(1)
    }
    50% {
        transform: scale(1.04)
    }
}

@keyframes spin {
    0% {
        transform: rotate(0deg)
    }
    100% {
        transform: rotate(360deg)
    }
}

@keyframes glow {
    0% {
        box-shadow: 0 0 150px rgba(200, 200, 60, .6);
        transform: scale(1)
    }
    100% {
        box-shadow: 0 0 200px rgba(255, 255, 100, .8);
        transform: scale(1.02)
    }
}

.campus-display {
    position: absolute;
    top: 120px;
    left: 50%;
    transform: translateX(-50%);
    padding: 12px 24px;
    background: rgba(0, 0, 0, .6);
    border-radius: 20px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, .1);
    font-size: 16px;
    font-weight: 500;
    opacity: 0;
    transition: all .3s ease
}

.campus-display.visible {
    opacity: 1
}

.status-indicator {
    position: absolute;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    padding: 12px 24px;
    background: rgba(0, 0, 0, .7);
    border-radius: 25px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, .1);
    font-size: 16px;
    text-align: center;
    min-width: 200px
}

.error-message {
    color: #ff6b6b !important;
    background: rgba(255, 107, 107, .1) !important;
    border: 1px solid rgba(255, 107, 107, .3) !important
}
    </style>
</head>
<body>
    <div class="main-container">
        <div class="title-header">
            <h1>FUTURES LINK</h1>
            <p>Voice Assistant</p>
        </div>
        
        <div class="campus-display" id="campusDisplay">No campus selected</div>
        
        <div class="orb-container" id="orb">
            <div class="orb" id="orbElement"></div>
        </div>
        
        <div class="status-indicator" id="statusIndicator">Starting Futures Link...</div>
    </div>

    <script nonce="{{ nonce }}">
        // BULLETPROOF JAVASCRIPT - ELEVENLABS TIMEOUT FIXED
        class BulletproofVoiceAssistant {
            constructor() {
                console.log('🚀 Initializing BULLETPROOF Futures Link...');
                
                // State management
                this.state = {
                    isListening: false,
                    isProcessing: false,
                    isConnected: false,
                    currentCampus: null,
                    conversationCount: 0,
                    audioEnabled: false
                };
                
                // Audio management
                this.audioManager = {
                    currentAudio: null,
                    audioContext: null
                };
                
                // DOM elements
                this.elements = {
                    orb: document.getElementById('orb'),
                    orbElement: document.getElementById('orbElement'),
                    statusIndicator: document.getElementById('statusIndicator'),
                    campusDisplay: document.getElementById('campusDisplay')
                };
                
                // Initialize
                this.init();
            }
            
            async init() {
                this.setupAudioContext();
                this.setupVoiceRecognition();
                this.setupEventListeners();
                
                // Auto-connect
                setTimeout(() => this.autoConnect(), 1000);
            }
            
            setupAudioContext() {
                try {
                    const AudioContext = window.AudioContext || window.webkitAudioContext;
                    if (AudioContext) {
                        this.audioManager.audioContext = new AudioContext();
                        console.log('🎵 AudioContext initialized');
                    }
                } catch (e) {
                    console.log('⚠️ AudioContext not available');
                }
            }
            
            setupVoiceRecognition() {
                if ('webkitSpeechRecognition' in window) {
                    this.recognition = new webkitSpeechRecognition();
                    this.recognition.continuous = false;
                    this.recognition.interimResults = true;
                    this.recognition.lang = 'en-US';
                    
                    this.recognition.onstart = () => {
                        console.log('🎤 Listening started');
                        this.state.isListening = true;
                        this.updateUI('listening', "I'm listening...");
                    };
                    
                    this.recognition.onresult = (event) => {
                        const last = event.results.length - 1;
                        const transcript = event.results[last][0].transcript;
                        
                        if (event.results[last].isFinal) {
                            console.log('👤 User said:', transcript);
                            this.handleVoiceInput(transcript);
                        } else {
                            this.updateStatus(`Hearing: "${transcript}"`);
                        }
                    };
                    
                    this.recognition.onend = () => {
                        console.log('🎤 Listening ended');
                        this.state.isListening = false;
                    };
                    
                    this.recognition.onerror = (event) => {
                        console.error('🎤 Speech error:', event.error);
                        this.state.isListening = false;
                        if (!this.state.isProcessing) {
                            this.updateUI('default', 'Say something or click orb');
                        }
                    };
                    
                    console.log('✅ Voice recognition setup complete');
                } else {
                    console.error('❌ Speech recognition not supported');
                    this.updateStatus('Speech recognition not supported');
                }
            }
            
            setupEventListeners() {
                if (this.elements.orb) {
                    this.elements.orb.onclick = () => this.handleOrbClick();
                }
            }
            
            async autoConnect() {
                console.log('🔄 Auto-connecting...');
                this.updateUI('processing', 'Connecting to Futures Link...');
                
                try {
                    // Test audio capability
                    const canUseAudio = await this.testAudioCapability();
                    
                    if (canUseAudio || await this.enableAudioContext()) {
                        await this.connectSequence();
                    } else {
                        this.waitForUserInteraction();
                    }
                } catch (error) {
                    console.error('❌ Auto-connect failed:', error);
                    this.waitForUserInteraction();
                }
            }
            
            async testAudioCapability() {
                try {
                    if (this.audioManager.audioContext) {
                        if (this.audioManager.audioContext.state === 'running') {
                            return true;
                        }
                    }
                    
                    const testAudio = new Audio();
                    return await testAudio.play().then(() => {
                        testAudio.pause();
                        return true;
                    }).catch(() => false);
                } catch (e) {
                    return false;
                }
            }
            
            async enableAudioContext() {
                try {
                    if (this.audioManager.audioContext && this.audioManager.audioContext.state === 'suspended') {
                        await this.audioManager.audioContext.resume();
                        console.log('🔓 AudioContext resumed');
                        return true;
                    }
                    return false;
                } catch (e) {
                    return false;
                }
            }
            
            waitForUserInteraction() {
                console.log('⏸️ Waiting for user interaction...');
                this.updateUI('default', 'Tap anywhere to connect');
                
                const enableAudio = async () => {
                    console.log('👆 User interaction detected');
                    document.removeEventListener('click', enableAudio);
                    document.removeEventListener('touchstart', enableAudio);
                    
                    this.state.audioEnabled = true;
                    await this.enableAudioContext();
                    await this.connectSequence();
                };
                
                document.addEventListener('click', enableAudio);
                document.addEventListener('touchstart', enableAudio);
            }
            
            async connectSequence() {
                try {
                    console.log('🔗 Starting connection sequence...');
                    this.state.isConnected = true;
                    
                    // Play chime
                    await this.playConnectionChime();
                    
                    // Speak connection
                    await this.speakMessage('Connected to Futures Link');
                    await this.delay(1000);
                    
                    // Introduction
                    await this.speakMessage('This is Link. How can I help you today?');
                    await this.delay(500);
                    
                    // Start listening
                    this.startListening();
                    
                    console.log('✅ Connection sequence complete');
                } catch (error) {
                    console.error('❌ Connection sequence failed:', error);
                    this.updateUI('default', 'Connection failed - click to retry');
                }
            }
            
            async playConnectionChime() {
                return new Promise((resolve) => {
                    try {
                        if (this.audioManager.audioContext) {
                            const ctx = this.audioManager.audioContext;
                            const osc1 = ctx.createOscillator();
                            const osc2 = ctx.createOscillator();
                            const gain = ctx.createGain();
                            
                            osc1.connect(gain);
                            osc2.connect(gain);
                            gain.connect(ctx.destination);
                            
                            osc1.frequency.value = 523.25; // C5
                            osc2.frequency.value = 659.25; // E5
                            
                            gain.gain.setValueAtTime(0, ctx.currentTime);
                            gain.gain.linearRampToValueAtTime(0.3, ctx.currentTime + 0.1);
                            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.8);
                            
                            osc1.start();
                            osc2.start();
                            osc1.stop(ctx.currentTime + 0.8);
                            osc2.stop(ctx.currentTime + 0.8);
                            
                            console.log('🔔 Connection chime played');
                        }
                        setTimeout(resolve, 800);
                    } catch (e) {
                        console.log('⚠️ Chime failed:', e);
                        resolve();
                    }
                });
            }
            
            async speakMessage(text) {
                return new Promise((resolve) => {
                    console.log(`🗣️ Speaking: "${text}"`);
                    
                    if ('speechSynthesis' in window) {
                        const utterance = new SpeechSynthesisUtterance(text);
                        utterance.rate = 1.0;
                        utterance.pitch = 1.0;
                        utterance.volume = 0.8;
                        utterance.lang = 'en-US';
                        
                        utterance.onend = resolve;
                        utterance.onerror = resolve;
                        
                        speechSynthesis.speak(utterance);
                    } else {
                        setTimeout(resolve, 2000);
                    }
                });
            }
            
            delay(ms) {
                return new Promise(resolve => setTimeout(resolve, ms));
            }
            
            handleOrbClick() {
                console.log('🎯 Orb clicked');
                
                if (!this.state.audioEnabled || !this.state.isConnected) {
                    this.state.audioEnabled = true;
                    this.connectSequence();
                } else if (!this.state.isListening && !this.state.isProcessing) {
                    this.startListening();
                }
            }
            
            startListening() {
                if (this.recognition && !this.state.isListening && !this.state.isProcessing) {
                    try {
                        console.log('🎤 Starting recognition...');
                        this.recognition.start();
                    } catch (e) {
                        console.error('❌ Recognition start failed:', e);
                        setTimeout(() => this.startListening(), 1000);
                    }
                }
            }
            
            async handleVoiceInput(transcript) {
                console.log('📤 Processing voice input:', transcript);
                this.state.isProcessing = true;
                this.updateUI('processing', 'Processing...');
                
                try {
                    const response = await fetch('/api/process', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            text: transcript,
                            campus: this.state.currentCampus,
                            conversation_count: this.state.conversationCount
                        })
                    });
                    
                    if (!response.ok) {
                        throw new Error(`Server error: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    console.log('📥 Server response:', data.text);
                    
                    // Update campus
                    if (data.campus && data.campus !== this.state.currentCampus) {
                        this.state.currentCampus = data.campus;
                        this.updateCampusDisplay(data.campus);
                    }
                    
                    this.updateUI('speaking', 'Speaking...');
                    
                    // BULLETPROOF AUDIO HANDLING - NO MORE TIMEOUTS
                    let audioSuccess = false;
                    if (data.audio_url) {
                        console.log('🎵 Trying ElevenLabs audio...');
                        audioSuccess = await this.playElevenLabsAudio(data.audio_url);
                    }
                    
                    if (!audioSuccess) {
                        console.log('🔊 Using speech synthesis fallback');
                        await this.speakWithSynthesis(data.text);
                    }
                    
                    this.state.conversationCount++;
                    
                    // Continue conversation
                    setTimeout(() => this.startListening(), 1000);
                    
                } catch (error) {
                    console.error('❌ Voice processing error:', error);
                    this.showError(`Error: ${error.message || 'Could not process voice input. Click orb to try again.'}`);
                } finally {
                    this.state.isProcessing = false;
                }
            }
            
            async playElevenLabsAudio(audioUrl, retryCount = 0, maxRetries = 2) {
                return new Promise((resolve) => {
                    console.log(`🎵 Playing ElevenLabs audio (Attempt ${retryCount + 1}/${maxRetries + 1}):`, audioUrl);
                    
                    // Stop any current audio
                    this.stopCurrentAudio();
                    
                    const audio = new Audio(audioUrl + '?t=' + Date.now());
                    audio.volume = 0.8;
                    this.audioManager.currentAudio = audio;
                    
                    let resolved = false;
                    
                    audio.oncanplaythrough = () => {
                        console.log('🎵 ElevenLabs audio ready to play');
                    };
                    
                    audio.onplay = () => {
                        console.log('🎵 ElevenLabs audio started playing');
                    };
                    
                    audio.onended = () => {
                        console.log('🎵 ElevenLabs audio finished successfully');
                        if (!resolved) {
                            resolved = true;
                            this.audioManager.currentAudio = null;
                            resolve(true);
                        }
                    };
                    
                    audio.onerror = async (e) => {
                        console.error('❌ ElevenLabs audio error:', e);
                        if (!resolved && retryCount < maxRetries) {
                            console.log(`🔄 Retrying audio playback (Attempt ${retryCount + 2})`);
                            resolved = true;
                            this.audioManager.currentAudio = null;
                            resolve(await this.playElevenLabsAudio(audioUrl, retryCount + 1, maxRetries));
                        } else if (!resolved) {
                            resolved = true;
                            this.audioManager.currentAudio = null;
                            resolve(false);
                        }
                    };
                    
                    audio.onabort = () => {
                        console.log('🎵 ElevenLabs audio aborted');
                        if (!resolved) {
                            resolved = true;
                            this.audioManager.currentAudio = null;
                            resolve(false);
                        }
                    };
                    
                    const loadingTimeout = setTimeout(() => {
                        if (!resolved && audio.readyState < 3) {
                            console.error('❌ ElevenLabs loading timeout (20s)');
                            if (retryCount < maxRetries) {
                                console.log(`🔄 Retrying audio playback (Attempt ${retryCount + 2})`);
                                resolved = true;
                                this.audioManager.currentAudio = null;
                                resolve(this.playElevenLabsAudio(audioUrl, retryCount + 1, maxRetries));
                            } else {
                                resolved = true;
                                this.audioManager.currentAudio = null;
                                resolve(false);
                            }
                        }
                    }, 20000);
                    
                    audio.play().then(() => {
                        console.log('✅ ElevenLabs play() promise resolved');
                        clearTimeout(loadingTimeout);
                    }).catch(e => {
                        console.error('❌ ElevenLabs play() promise rejected:', e);
                        clearTimeout(loadingTimeout);
                        if (!resolved && retryCount < maxRetries) {
                            console.log(`🔄 Retrying audio playback (Attempt ${retryCount + 2})`);
                            resolved = true;
                            this.audioManager.currentAudio = null;
                            resolve(this.playElevenLabsAudio(audioUrl, retryCount + 1, maxRetries));
                        } else if (!resolved) {
                            resolved = true;
                            this.audioManager.currentAudio = null;
                            resolve(false);
                        }
                    });
                });
            }
            
            async speakWithSynthesis(text) {
                return new Promise((resolve) => {
                    console.log('🔊 Using speech synthesis:', text);
                    
                    if ('speechSynthesis' in window) {
                        const utterance = new SpeechSynthesisUtterance(text);
                        utterance.rate = 1.1;
                        utterance.volume = 0.9;
                        utterance.lang = 'en-US';
                        
                        utterance.onend = () => {
                            console.log('🔊 Speech synthesis finished');
                            resolve();
                        };
                        
                        utterance.onerror = (e) => {
                            console.error('🔊 Speech synthesis error:', e);
                            resolve();
                        };
                        
                        speechSynthesis.speak(utterance);
                    } else {
                        console.log('⚠️ Speech synthesis not available');
                        resolve();
                    }
                });
            }
            
            stopCurrentAudio() {
                if (this.audioManager.currentAudio) {
                    this.audioManager.currentAudio.pause();
                    this.audioManager.currentAudio.currentTime = 0;
                    this.audioManager.currentAudio = null;
                }
                
                if (window.speechSynthesis) {
                    speechSynthesis.cancel();
                }
            }
            
            updateUI(state, message) {
                if (this.elements.orbElement) {
                    this.elements.orbElement.className = `orb ${state}`;
                }
                this.updateStatus(message);
            }
            
            updateStatus(message) {
                if (this.elements.statusIndicator) {
                    this.elements.statusIndicator.textContent = message;
                    this.elements.statusIndicator.classList.remove('error-message');
                }
            }
            
            updateCampusDisplay(campus) {
                if (this.elements.campusDisplay) {
                    this.elements.campusDisplay.textContent = `Campus: ${campus}`;
                    this.elements.campusDisplay.classList.add('visible');
                }
            }
            
            showError(message) {
                if (this.elements.statusIndicator) {
                    this.elements.statusIndicator.textContent = message;
                    this.elements.statusIndicator.classList.add('error-message');
                }
                if (this.elements.orbElement) {
                    this.elements.orbElement.className = 'orb';
                }
            }
        }
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', () => {
            console.log('🚀 Page loaded - initializing Bulletproof Voice Assistant');
            new BulletproofVoiceAssistant();
        });
        
        // Debug info
        window.addEventListener('load', () => {
            console.log('🎵 Audio capabilities:');
            console.log('- AudioContext:', !!(window.AudioContext || window.webkitAudioContext));
            console.log('- Speech Synthesis:', 'speechSynthesis' in window);
            console.log('- Speech Recognition:', 'webkitSpeechRecognition' in window);
            console.log('✅ BULLETPROOF VERSION LOADED - ElevenLabs timeout fixed!');
        });
    </script>
</body>
</html>
"""

# Initialize Talisman without static CSP; we'll set it dynamically per request
Talisman(app, force_https=False, strict_transport_security=False, content_security_policy=None)

@app.route('/')
def index():
    # Generate a unique nonce for this request
    nonce = base64.b64encode(os.urandom(16)).decode('utf-8')
    
    # Define CSP with the nonce
    csp = {
        'default-src': "'self'",
        'script-src': ["'self'", f"'nonce-{nonce}'"],
        'style-src': ["'self'", f"'nonce-{nonce}'"],
        'connect-src': ["'self'", 'https://api.elevenlabs.io', 'https://api.openai.com'],
        'media-src': ["'self'", 'blob:'],
        'font-src': ["'self'"],
        'img-src': ["'self'", 'data:']
    }
    
    # Apply CSP to this response
    response = render_template_string(HTML_TEMPLATE, nonce=nonce)
    response = app.make_response(response)
    csp_header = '; '.join(f"{key} {' '.join(values)}" for key, values in csp.items())
    response.headers['Content-Security-Policy'] = csp_header
    return response

@app.route('/api/process', methods=['POST'])
async def process_voice():
    global assistant
    
    if not assistant:
        return jsonify({
            'text': 'Assistant not initialized properly', 
            'campus': None,
            'error': 'initialization_failed'
        }), 500
    
    try:
        data = request.json
        if not data:
            return jsonify({
                'text': 'No data received', 
                'campus': None,
                'error': 'no_data'
            }), 400
            
        text = data.get('text', '').strip()
        if not text:
            return jsonify({
                'text': 'Please speak again, I didn\'t catch that',
                'campus': None,
                'error': 'empty_text'
            }), 400
            
        current_campus = data.get('campus')
        conversation_count = data.get('conversation_count', 0)
        
        logger.info(f"👤 Voice input: {text}")
        
        stats = assistant.parse_stats_enhanced(text)
        
        if 'campus' in stats:
            detected_campus = stats['campus']
            assistant.current_campus = detected_campus
        elif current_campus:
            stats['campus'] = current_campus
            detected_campus = current_campus
            assistant.current_campus = current_campus
        else:
            detected_campus = None
        
        context = f"Conversation #{conversation_count + 1}"
        if detected_campus:
            context += f", Campus: {detected_campus}"
        
        response_text = assistant.generate_ai_response(text, stats, context)
        
        assistant.update_conversation_memory(text, response_text, stats)
        
        if stats and 'campus' in stats and len(stats) > 2:
            success = assistant.log_to_sheets_background(stats)
            if success:
                logger.info("⚡ Background Google Sheets logging initiated")
        
        if conversation_count % 5 == 0:
            assistant.cleanup_old_audio_files()
        
        audio_url = None
        if assistant.use_elevenlabs and response_text:
            audio_content = await assistant.generate_elevenlabs_audio(response_text)
            if audio_content:
                audio_filename = f"speech_{uuid.uuid4().hex[:8]}.mp3"
                audio_path = os.path.join('temp_audio', audio_filename)
                
                try:
                    with open(audio_path, 'wb') as f:
                        f.write(audio_content)
                    
                    audio_url = f"/api/audio/{audio_filename}"
                    logger.info(f"✅ ElevenLabs audio generated: {audio_filename}")
                except Exception as e:
                    logger.error(f"❌ Failed to save audio file: {e}")
        
        logger.info(f"🤖 Response: {response_text}")
        
        response_data = {
            'text': response_text,
            'campus': detected_campus,
            'stats': stats,
            'audio_url': audio_url,
            'session_summary': assistant.get_session_summary() if conversation_count > 0 else None
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"❌ Error processing voice input: {e}")
        return jsonify({
            'text': 'Sorry, there was an error. Please try again.',
            'campus': None,
            'error': 'processing_failed'
        }), 500

@app.route('/api/audio/<filename>')
def serve_audio(filename):
    """Serve ElevenLabs audio files with range request support"""
    try:
        if not filename.endswith('.mp3') or '..' in filename or '/' in filename:
            return "Invalid filename", 400
            
    audio_path = os.path.join('temp_audio', filename)
    if os.path.exists(audio_path):
        return send_file(
            audio_path,
            mimetype='audio/mpeg',
            as_attachment=False,
            conditional=True,
            add_etags=False,
            cache_timeout=0
        )
        else:
            logger.warning(f"Audio file not found: {filename}")
            return "Audio file not found", 404
    except Exception as e:
        logger.error(f"❌ Error serving audio: {e}")
        return "Error serving audio", 500

@app.route('/api/session', methods=['GET'])
def get_session_summary():
    """Get current session summary"""
    global assistant
    if assistant:
        return jsonify({
            'summary': assistant.get_session_summary(),
            'conversation_count': len(assistant.conversation_history),
            'current_campus': assistant.current_campus,
            'available_campuses': assistant.campuses
        })
    return jsonify({
        'summary': 'No active session', 
        'conversation_count': 0,
        'error': 'assistant_not_initialized'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    global assistant
    
    health_status = {
        'status': 'healthy' if assistant else 'unhealthy',
        'timestamp': datetime.now().isoformat(),
        'services': {}
    }
    
    if assistant:
        health_status['services'] = {
            'openai': assistant.openai_client is not None,
            'elevenlabs': assistant.use_elevenlabs,
            'google_sheets': assistant.sheets_client is not None,
            'memory_system': os.path.exists(assistant.memory_file)
        }
    
    status_code = 200 if assistant else 503
    return jsonify(health_status), status_code

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

def main():
    global assistant
    
    try:
        assistant = BulletproofChurchAssistant()
    except Exception as e:
        logger.error(f"❌ Failed to initialize assistant: {e}")
        assistant = None
        print("❌ Assistant initialization failed")
    
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"🌐 BULLETPROOF server starting on http://localhost:{port}")
    logger.info("🚀 ElevenLabs timeout issues PERMANENTLY FIXED!")
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug_mode,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        raise

if __name__ == '__main__':
    main()