# Add this to the very top of your app.py file, before any other imports

import os
from pathlib import Path

# Method 1: Try to load from .env file using python-dotenv
try:
    from dotenv import load_dotenv
    # Load .env file from current directory or parent directories
    env_path = Path('.') / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded .env file from: {env_path.absolute()}")
    else:
        # Try parent directory
        parent_env = Path('..') / '.env'
        if parent_env.exists():
            load_dotenv(parent_env)
            print(f"✅ Loaded .env file from: {parent_env.absolute()}")
        else:
            print("⚠️ No .env file found, using system environment variables")
    DOTENV_AVAILABLE = True
except ImportError:
    print("⚠️ python-dotenv not installed. Install with: pip install python-dotenv")
    DOTENV_AVAILABLE = False

# Method 2: Manual .env loading (fallback)
def load_env_manual():
    """Manually load .env file if dotenv is not available"""
    env_files = ['.env', '../.env', '../../.env']
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"📁 Loading environment variables from: {os.path.abspath(env_file)}")
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        os.environ[key] = value
                        print(f"✅ Set {key}")
            return True
    return False

# If dotenv is not available, try manual loading
if not DOTENV_AVAILABLE:
    if load_env_manual():
        print("✅ Environment variables loaded manually")
    else:
        print("❌ No .env file found in current or parent directories")

# Method 3: Print current environment for debugging
print("\n🔍 ENVIRONMENT VARIABLE DEBUG:")
print(f"Current working directory: {os.getcwd()}")
print(f"ANTHROPIC_API_KEY present: {'Yes' if os.getenv('ANTHROPIC_API_KEY') else 'No'}")
print(f"ELEVENLABS_API_KEY present: {'Yes' if os.getenv('ELEVENLABS_API_KEY') else 'No'}")
print(f"GOOGLE_CREDENTIALS_PATH: {os.getenv('GOOGLE_CREDENTIALS_PATH', 'Not set')}")

# Method 4: Try different environment variable names (common variations)
def get_api_key(primary_name, alternatives=None):
    """Try multiple environment variable names"""
    if alternatives is None:
        alternatives = []
    
    # Try primary name first
    value = os.getenv(primary_name)
    if value:
        return value
    
    # Try alternatives
    for alt_name in alternatives:
        value = os.getenv(alt_name)
        if value:
            print(f"✅ Found {primary_name} using alternative name: {alt_name}")
            return value
    
    return None

# Try common API key variations
ANTHROPIC_KEY = get_api_key('ANTHROPIC_API_KEY', ['CLAUDE_API_KEY', 'ANTHROPIC_KEY', 'CLAUDE_KEY'])
ELEVENLABS_KEY = get_api_key('ELEVENLABS_API_KEY', ['ELEVENLABS_KEY', 'ELEVEN_LABS_KEY', 'EL_API_KEY'])

if ANTHROPIC_KEY:
    os.environ['ANTHROPIC_API_KEY'] = ANTHROPIC_KEY
    print("✅ Anthropic API key found and set")

if ELEVENLABS_KEY:
    os.environ['ELEVENLABS_API_KEY'] = ELEVENLABS_KEY
    print("✅ ElevenLabs API key found and set")

print("=" * 60)

from flask import Flask, request, jsonify, send_from_directory, render_template, send_file
from flask_cors import CORS
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import logging
import random
import time
import re
import base64
import uuid
import atexit
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor

# Import handling with fallbacks
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False
    print("⚠️ Google Sheets support not available - install gspread and google-auth")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠️ Anthropic Claude support not available - install anthropic")

try:
    from elevenlabs import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    print("⚠️ ElevenLabs support not available - install elevenlabs")

import json

app = Flask(__name__)
CORS(app)

# ADD THESE IMPORTS AT THE TOP (after your existing imports)
import pygame
import threading
import sys

# ADD THIS AFTER YOUR EXISTING IMPORTS
# Initialize pygame mixer for audio playback
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    PYGAME_AVAILABLE = True
    print("✅ Audio playback system initialized")
except Exception as e:
    PYGAME_AVAILABLE = False
    print(f"⚠️ Audio playback not available: {e}")

# ADD THESE FUNCTIONS ANYWHERE IN YOUR FILE (before the main() function)
def play_startup_chime():
    """Play startup chime with fallback options"""
    if not PYGAME_AVAILABLE:
        print("🔊 Audio playback not available - using system sounds")
        play_system_chime()
        return
    
    def play_audio_thread():
        try:
            # Try to play the generated startup audio first
            startup_files = [
                'temp_audio/startup_message.mp3',
                'temp_audio/startup_chime.mp3',
                'static/startup.mp3',
                'startup.mp3'
            ]
            
            audio_played = False
            for audio_file in startup_files:
                if os.path.exists(audio_file):
                    try:
                        print(f"🎵 Playing startup chime: {audio_file}")
                        pygame.mixer.music.load(audio_file)
                        pygame.mixer.music.play()
                        
                        # Wait for audio to finish
                        while pygame.mixer.music.get_busy():
                            time.sleep(0.1)
                        
                        audio_played = True
                        print("✅ Startup chime completed")
                        break
                    except Exception as e:
                        print(f"⚠️ Could not play {audio_file}: {e}")
                        continue
            
            if not audio_played:
                # Fallback to system sounds
                play_system_chime()
                        
        except Exception as e:
            print(f"❌ Startup chime error: {e}")
            play_system_chime()
    
    # Play in background thread so it doesn't block startup
    chime_thread = threading.Thread(target=play_audio_thread, daemon=True)
    chime_thread.start()

def play_system_chime():
    """Play system notification sounds as fallback"""
    try:
        print("🔊 Playing system notification sounds...")
        if sys.platform == "win32":
            import winsound
            # Play Windows startup-like chimes
            winsound.Beep(800, 200)   # High beep
            time.sleep(0.1)
            winsound.Beep(600, 200)   # Mid beep
            time.sleep(0.1)
            winsound.Beep(400, 300)   # Low beep
            print("✅ Windows startup chime completed")
        elif sys.platform == "darwin":  # macOS
            os.system("afplay /System/Library/Sounds/Glass.aiff")
            print("✅ macOS startup chime completed")
        else:  # Linux
            os.system("paplay /usr/share/sounds/alsa/Front_Left.wav 2>/dev/null || echo '\a'")
            print("✅ Linux startup chime completed")
            
    except Exception as e:
        print(f"⚠️ System beep failed: {e}")
        # Ultimate fallback - terminal bell
        print("\a" * 3)  # Terminal bell
        print("🔔 Terminal bell chime completed")

def generate_startup_chime_audio(assistant):
    """Generate a nice startup chime using ElevenLabs"""
    if not assistant or not hasattr(assistant, 'use_elevenlabs') or not assistant.use_elevenlabs:
        return None
    
    try:
        # Generate a pleasant startup message
        startup_text = "Chime... Connected to Futures Link. System ready."
        
        print("🎵 Generating startup chime with ElevenLabs...")
        audio_content = asyncio.run(assistant.generate_elevenlabs_audio(startup_text))
        
        if audio_content:
            # Save the audio file
            os.makedirs('temp_audio', exist_ok=True)
            chime_path = 'temp_audio/startup_chime.mp3'
            
            with open(chime_path, 'wb') as f:
                f.write(audio_content)
            
            print(f"✅ Startup chime generated: {chime_path}")
            return chime_path
        else:
            print("⚠️ Could not generate startup chime audio")
            return None
            
    except Exception as e:
        print(f"❌ Failed to generate startup chime: {e}")
        return None

# Initialize Flask-Limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# 🔧 ENHANCED LOGGING SETUP - Fixed and More Robust
def setup_logging():
    """Setup enhanced logging with proper error handling"""
    try:
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # File handler
        try:
            file_handler = logging.FileHandler('logs/futures_link.log')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(detailed_formatter)
            root_logger.addHandler(file_handler)
            print("✅ File logging enabled: logs/futures_link.log")
        except Exception as e:
            print(f"⚠️ Could not setup file logging: {e}")
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
        
        # Test logging
        logging.info("Logging system initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Logging setup failed: {e}")
        return False

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

class EnhancedChurchAssistant:
    def parse_month_range(self, text: str) -> Optional[tuple]:
        """Extract a month range and optional year from text like 'from February to April 2023'"""
        import calendar
        text = text.lower()
        months = list(calendar.month_name)
        month_indices = []

        for i, month in enumerate(months):
            if month and month.lower() in text:
                month_indices.append((i, text.index(month.lower())))

        if len(month_indices) >= 2:
            # Sort by position in text to maintain natural order
            month_indices.sort(key=lambda x: x[1])
            start_month = month_indices[0][0]
            end_month = month_indices[1][0]

            # Try to find a year
            tokens = text.split()
            year = None
            for token in tokens:
                if token.isdigit() and 2000 <= int(token) <= 2100:
                    year = int(token)
                    break
            return (start_month, end_month, year)
        return None

    def is_asking_for_data(self, text: str) -> bool:
        """🔥 ENHANCED: Determine if user is ASKING for data vs PROVIDING data"""
        text = text.lower()
        
        # Clear question indicators
        question_words = [
            'how many', 'what were', 'what are', 'tell me', 'show me', 'what was',
            'which campus', 'average attendance', 'what is the average', 'give me stats',
            'any idea', 'do you know', 'compare', 'how is', 'summary', 'what about',
            'can you tell me', 'do we have', 'what do we have', 'what\'s the'
        ]
        if any(q in text for q in question_words):
            return True
            
        # Question marks
        if '?' in text:
            return True
            
        # Providing data indicators (they're giving us stats, not asking)
        providing_indicators = [
            'had', 'got', 'we had', 'there were', 'attendance was', 'np', 'nc',
            'was', 'were', 'today we had', 'this week', 'sunday we had'
        ]
        if any(p in text for p in providing_indicators):
            return False
            
        # Numbers with campus names usually means providing
        for campus in self.campuses:
            if campus.lower() in text and any(char.isdigit() for char in text):
                return False
                
        return False

    def handle_stat_query(self, text: str) -> Optional[str]:
        """🔥 ENHANCED: Handle queries like 'new Christians in March at South' - ONLY when user asks"""
        
        # 🚨 CRITICAL FIX: Only respond if they're explicitly asking for data
        if not self.is_asking_for_data(text):
            return None
            
        stat_keywords = {
            'new christians': 'new_christians',
            'youth salvations': 'new_youth_christians',
            'kids salvations': 'kids_salvations',
            'total attendance': 'total_attendance',
            'new people': 'new_people',
            'youth attendance': 'youth_attendance',
            'new youth': 'new_youth',
            'new kids': 'new_kids',
            'kids total': 'kids_total',
            'connect groups': 'connect_groups'
        }

        text_lower = text.lower()

        # Check for month range like "from February to April"
        month_range = self.parse_month_range(text)
        if month_range:
            start_month, end_month, year = month_range
            campus = self.extract_campus_enhanced(text)
            summaries = []
            for m in range(start_month, end_month + 1):
                summaries.append(self.get_annual_summary(campus, year=year, month=m))
            return "\n".join(summaries)

        # --- Salvation Health Queries (church-wide) ---
        if any(phrase in text_lower for phrase in [
            "how many people have given their lives",
            "how many salvations",
            "how many people got saved",
            "how many people became christians"
        ]):
            year = None
            for token in text.split():
                if token.isdigit() and 2000 <= int(token) <= 2100:
                    year = int(token)
                    break
            year = year or datetime.now().year
            total = sum(self.get_stat_total(c, "new_christians", year) or 0 for c in self.campuses)
            return f"In {year}, {total} people have given their lives to Jesus across all campuses."

        # Parse explicit month and year from text for summary/statistics summary queries
        import calendar
        month = None
        year = None
        for i, m in enumerate(calendar.month_name):
            if m and f"in {m.lower()}" in text_lower:
                month = i
                break
        for token in text.split():
            if token.isdigit() and 2000 <= int(token) <= 2100:
                year = int(token)
                break
        if "summary" in text_lower or "how is" in text_lower:
            campus = self.extract_campus_enhanced(text)
            return self.get_annual_summary(campus, year=year, month=month)

        stat_key = next((k for k, v in stat_keywords.items() if k in text_lower), None)
        if not stat_key:
            return None

        key = stat_keywords[stat_key]
        campus = self.extract_campus_enhanced(text) or self.current_campus

        # Support whole-church year-over-year comparisons if no campus is mentioned and phrases like "this year vs last year" or "year over year" are used
        year_over_year_phrases = [
            "compared to last year",
            "compare to last year",
            "this year vs last year",
            "year over year",
            "year-on-year",
            "year on year"
        ]
        now = datetime.now()
        year = now.year
        month = None
        if any(phrase in text_lower for phrase in year_over_year_phrases):
            # If no campus in text and no campus in context, do whole-church comparison
            if campus is None:
                # All campuses
                this_year_total = sum(self.get_stat_total(c, key, year) or 0 for c in self.campuses)
                last_year_total = sum(self.get_stat_total(c, key, year - 1) or 0 for c in self.campuses)
                if this_year_total is None or last_year_total is None or (this_year_total == 0 and last_year_total == 0):
                    return f"Sorry, I couldn't find enough data to compare {stat_key} across all campuses year over year."
                if last_year_total == 0:
                    return f"Last year's {stat_key} for all campuses was zero, so I can't calculate a comparison."
                change_percent = ((this_year_total - last_year_total) / last_year_total) * 100
                direction = "up" if change_percent > 0 else "down"
                return f"Across all campuses, there were {this_year_total} {stat_key} this year, {direction} {abs(change_percent):.1f}% from last year's {last_year_total}."
            else:
                this_year_total = self.get_stat_total(campus, key, year)
                last_year_total = self.get_stat_total(campus, key, year - 1)
                if this_year_total is None or last_year_total is None:
                    return f"Sorry, I couldn't find enough data to compare {stat_key} for {campus} year over year."
                if last_year_total == 0:
                    return f"Last year's {stat_key} for {campus} was zero, so I can't calculate a comparison."
                change_percent = ((this_year_total - last_year_total) / last_year_total) * 100
                direction = "up" if change_percent > 0 else "down"
                return f"{campus} had {this_year_total} {stat_key} this year so far, {direction} {abs(change_percent):.1f}% from last year's {last_year_total}."

        # Check if asking for top campus
        if "which campus" in text_lower and ("most" in text_lower or "highest" in text_lower):
            for label, key2 in stat_keywords.items():
                if label in text_lower or (label == "new christians" and "salvation" in text_lower):
                    now = datetime.now()
                    year2 = now.year
                    month2 = now.month - 1 or 12
                    if month2 == 12:
                        year2 -= 1
                    return self.get_top_campus_for_stat(key2, year2, month2)

        # Check for "last month"
        if "last month" in text_lower:
            month = now.month - 1 or 12
            if month == 12:
                year -= 1
        else:
            import calendar
            for i, m in enumerate(calendar.month_name):
                if m and f"in {m.lower()}" in text_lower:
                    month = i
                    break

        # Monthly trend/trending and new trend phrases
        if any(term in text_lower for term in ["trending", "trend", "going up", "improving", "getting better", "on the rise"]):
            trend_summary = self.get_monthly_trend_summary(campus, key, year, month)
            if trend_summary:
                if "increased" in trend_summary or "up" in trend_summary:
                    trend_summary += " Keep it up—momentum is building!"
                return trend_summary
            else:
                return f"Sorry, I couldn't determine the trend for {campus} {stat_key}."

        # If no campus still, prompt for campus
        if not campus:
            return "Which campus are you referring to?"

        total = self.get_stat_total(campus, key, year, month)
        import calendar
        when = f"{calendar.month_name[month]} {year}" if month else str(year)
        if total is not None:
            return f"Here's the summary for {campus} in {when}: {total} {stat_key}."

        # Detect celebration or breakthrough queries
        if any(phrase in text_lower for phrase in [
            "breakthrough month",
            "celebration",
            "any spikes",
            "spike in salvations",
            "breakout",
            "surge"
        ]):
            best_campus = None
            best_increase = 0
            best_month = None
            now = datetime.now()
            for campus in self.campuses:
                for month in range(1, 13):
                    current_total = self.get_stat_total(campus, "new_christians", now.year, month)
                    prev_month = month - 1 or 12
                    prev_year = now.year if month > 1 else now.year - 1
                    previous_total = self.get_stat_total(campus, "new_christians", prev_year, prev_month)
                    if current_total is None or previous_total is None or previous_total == 0:
                        continue
                    increase = (current_total - previous_total) / previous_total
                    if increase > best_increase and current_total >= 5:
                        best_increase = increase
                        best_campus = campus
                        best_month = month
            if best_campus:
                import calendar
                return f"{best_campus} had a breakthrough month in {calendar.month_name[best_month]} with a {best_increase*100:.1f}% spike in salvations!"
            else:
                return "No major spikes or breakthrough months found recently."

        return f"Sorry, I couldn't find any {stat_key} data for {campus} in {when}."

    def get_monthly_trend_summary(self, campus: Optional[str], stat_key: str, year: Optional[int] = None, month: Optional[int] = None) -> Optional[str]:
        """Compare this month's stat with last month's and return a summary if data is sufficient"""
        if not self.sheets_client or not self.spreadsheet or not campus:
            return None

        try:
            now = datetime.now()
            year = year or now.year
            month = month or now.month

            # Calculate previous month and year
            prev_month = month - 1 or 12
            prev_year = year - 1 if prev_month == 12 else year

            current_total = self.get_stat_total(campus, stat_key, year, month)
            previous_total = self.get_stat_total(campus, stat_key, prev_year, prev_month)

            if current_total is None or previous_total is None:
                return None

            if previous_total == 0:
                return f"No {stat_key.replace('_', ' ')} were recorded in {prev_month}/{prev_year} to compare."

            percent_change = ((current_total - previous_total) / previous_total) * 100
            direction = "increased" if percent_change > 0 else "decreased"
            return f"{campus}'s {stat_key.replace('_', ' ')} has {direction} by {abs(percent_change):.1f}% compared to last month."
        except Exception as e:
            logger.error(f"❌ Monthly trend comparison failed: {e}")
            return None

    def get_annual_summary(self, campus: Optional[str] = None, year: Optional[int] = None, month: Optional[int] = None) -> str:
        """Summarize stats for a campus or all campuses in a year or month"""
        if not self.sheets_client or not self.spreadsheet:
            return "Stats summary is unavailable at the moment."

        try:
            import calendar
            year = year or datetime.now().year
            worksheet = self.spreadsheet.sheet1
            records = worksheet.get_all_records()

            campuses = [campus] if campus else self.campuses
            summary = []

            for camp in campuses:
                camp_normalized = str(camp).strip().lower()
                totals = {
                    'attendance': 0,
                    'new_people': 0,
                    'new_christians': 0,
                    'youth_salvations': 0,
                    'kids_salvations': 0
                }

                for row in records:
                    row_campus = str(row.get('Campus', '')).strip().lower()
                    if row_campus != camp_normalized:
                        continue
                    try:
                        date = datetime.strptime(row.get('Sunday Date', ''), '%Y-%m-%d')
                        if date.year != year:
                            continue
                        if month and date.month != month:
                            continue
                    except Exception:
                        continue

                    totals['attendance'] += int(row.get('Total Attendance') or 0)
                    totals['new_people'] += int(row.get('New People') or 0)
                    totals['new_christians'] += int(row.get('New Christians') or 0)
                    totals['youth_salvations'] += int(row.get('New Youth Christians') or 0)
                    totals['kids_salvations'] += int(row.get('Kids Salvations') or 0)

                time_label = f"{calendar.month_name[month]} {year}" if month else str(year)
                summary.append(f"{camp}: {totals['attendance']} attendance, {totals['new_people']} new, "
                               f"{totals['new_christians']} salvations, {totals['youth_salvations']} youth saved, "
                               f"{totals['kids_salvations']} kids saved ({time_label})")

            time_label = f"{calendar.month_name[month]} {year}" if month else str(year)
            if campus:
                return f"Here's how {campus} has been doing in {time_label}: {summary[0]}"
            else:
                return f"Here's a summary for all campuses in {time_label}:\n" + "\n".join(summary)

        except Exception as e:
            logger.error(f"❌ Failed to generate summary: {e}")
            return "There was an error generating the summary."

    def get_top_campus_for_stat(self, stat_key: str, year: Optional[int] = None, month: Optional[int] = None) -> Optional[str]:
        """Return the campus with the highest value for a given stat in a given month/year"""
        if not self.sheets_client or not self.spreadsheet:
            return None
        try:
            worksheet = self.spreadsheet.sheet1
            records = worksheet.get_all_records()
            campus_totals = {}

            for row in records:
                campus = row.get('Campus')
                if not campus:
                    continue
                date_str = row.get('Sunday Date')
                if not date_str:
                    continue
                try:
                    row_date = datetime.strptime(date_str, '%Y-%m-%d')
                    if year and row_date.year != year:
                        continue
                    if month and row_date.month != month:
                        continue
                except ValueError:
                    continue

                value = row.get(stat_key.replace('_', ' ').title())
                if isinstance(value, int):
                    campus_totals[campus] = campus_totals.get(campus, 0) + value
                elif isinstance(value, str) and value.isdigit():
                    campus_totals[campus] = campus_totals.get(campus, 0) + int(value)

            if not campus_totals:
                return None

            top_campus = max(campus_totals.items(), key=lambda x: x[1])
            return f"{top_campus[0]} had the most {stat_key.replace('_', ' ')} with {top_campus[1]} logged."
        except Exception as e:
            logger.error(f"❌ Failed to compute top campus for {stat_key}: {e}")
            return None

    def __init__(self):
        """Initialize enhanced voice assistant with Claude AI"""
        print("🚀 Starting ENHANCED Futures Link Voice Assistant with Claude...")
        print("=" * 60)

        # Validate environment variables (warnings only)
        required_env_vars = ['ANTHROPIC_API_KEY', 'ELEVENLABS_API_KEY']
        for var in required_env_vars:
            if not os.getenv(var):
                logger.warning(f"⚠️ Missing environment variable: {var}")

        # Core settings
        self.current_campus = None
        self.conversation_history = {}
        self.session_stats = {}

        # Previous stat memory (used for long-term trend analysis)
        self.previous_stats_by_campus = {}

        # Performance optimizations
        self.thread_pool = ThreadPoolExecutor(max_workers=5)

        # Create directories
        self.ensure_directories()

        # Setup all services
        self.setup_claude()
        if ELEVENLABS_AVAILABLE:
            self.elevenlabs_client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))
        else:
            self.elevenlabs_client = None
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

        print("✅ Enhanced Voice Assistant with Claude initialized!")
        print("✅ ALL features preserved + Claude integration!")
        print("=" * 60)
    
    def ensure_directories(self):
        """Ensure required directories exist"""
        directories = ['temp_audio', 'logs', 'data', 'static']
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"✅ Directory ensured: {directory}")
            except Exception as e:
                logger.error(f"❌ Failed to create directory {directory}: {e}")
    
    def setup_claude(self):
        """Setup Claude (Anthropic) AI"""
        if not ANTHROPIC_AVAILABLE:
            self.claude_client = None
            logger.warning("❌ Anthropic Claude not available")
            return
            
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            logger.warning("❌ ANTHROPIC_API_KEY not found")
            self.claude_client = None
            return
        
        try:
            self.claude_client = anthropic.Anthropic(api_key=api_key)
            
            # Test connection with a simple message
            test_response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                messages=[{"role": "user", "content": "Test"}],
                timeout=10
            )
            logger.info("✅ Claude AI connected successfully")
            self.has_claude = True
        except Exception as e:
            logger.error(f"❌ Claude setup failed: {e}")
            self.claude_client = None
            self.has_claude = False
    
    def setup_elevenlabs(self):
        """Setup ElevenLabs with bulletproof configuration"""
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        self.elevenlabs_voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'pNInz6obpgDQGcFmaJgB')
        
        if self.elevenlabs_api_key and ELEVENLABS_AVAILABLE:
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
            logger.warning("⚠️ ElevenLabs not available or API key missing")
            self.use_elevenlabs = False
    
    def setup_google_sheets(self):
        """Setup Google Sheets"""
        if not GSPREAD_AVAILABLE:
            self.sheets_client = None
            logger.warning("❌ Google Sheets not available")
            return
            
        try:
            credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
            if os.path.exists(credentials_path):
                scope = [
                    'https://www.googleapis.com/auth/spreadsheets',
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
                logger.warning(f"⚠️ No credentials file found at {credentials_path}")
                self.sheets_client = None
                self.spreadsheet = None
        except Exception as e:
            logger.error(f"❌ Google Sheets setup failed: {e}")
            self.sheets_client = None
            self.spreadsheet = None
    
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
                    self.conversation_history = data.get('conversations', {})[-10:]
                    self.session_stats = data.get('session_stats', {})
                logger.info(f"✅ Loaded {len(self.conversation_history)} conversation(s)")
        except Exception as e:
            logger.error(f"❌ Failed to load memory: {e}")
            self.conversation_history = {}
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
        """🔥 SUPER ENHANCED: Campus extraction - handles ALL natural variations"""
        if not text:
            return None
            
        text = text.lower().strip()
        logger.info(f"🔍 Analyzing text for campus: '{text}'")
        
        # ENHANCED patterns - order by specificity to avoid conflicts
        campus_patterns = [
            # Multi-word campuses first (most specific)
            (r'\b(adelaide city|adel city|city campus|adelaide)\b', 'Adelaide City'),
            (r'\bcity\b', 'Adelaide City'),
            (r'\b(clare valley|clare)\b', 'Clare Valley'),
            (r'\b(mount barker|mt barker|barker)\b', 'Mount Barker'),
            (r'\b(victor harbour|victor harbor|victor)\b', 'Victor Harbour'),
            (r'\b(copper coast|copper)\b', 'Copper Coast'),
            
            # Single word campuses with variations
            (r'\b(paradise|para|par)\b', 'Paradise'),
            (r'\b(salisbury|sal|sali|sbury)\b', 'Salisbury'),
            (r'\bsouth\b', 'South'),  # EXACT match for "south" only
            
            # Handle common speech patterns
            (r'\bat (paradise|para|par)\b', 'Paradise'),
            (r'\bat (salisbury|sal|sali)\b', 'Salisbury'),
            (r'\bat (adelaide city|city)\b', 'Adelaide City'),
            (r'\bat south\b', 'South'),
            (r'\bat (clare valley|clare)\b', 'Clare Valley'),
            (r'\bat (mount barker|barker)\b', 'Mount Barker'),
            (r'\bat (victor harbour|victor)\b', 'Victor Harbour'),
            (r'\bat (copper coast|copper)\b', 'Copper Coast'),
        ]
        
        for pattern, campus_name in campus_patterns:
            if re.search(pattern, text):
                logger.info(f"✅ Campus detected: '{text}' → {campus_name} (pattern: {pattern})")
                return campus_name
        
        logger.info(f"🔍 No campus detected in: '{text}'")
        return None
    
    def parse_stats_enhanced(self, text: str) -> Dict:
        """🔥 SUPER ENHANCED: Statistics parsing - handles ALL natural speech patterns"""
        if not text:
            return {}

        stats = {}
        text_original = text
        text = text.lower()
        
        logger.info(f"📊 Parsing stats from: '{text_original}'")

        # Preserve context of current campus and last stats
        if hasattr(self, 'last_spoken_stats') and isinstance(self.last_spoken_stats, dict):
            current_context = self.last_spoken_stats.get(self.current_campus, {})
            stats.update(current_context)

        campus = self.extract_campus_enhanced(text)
        if campus:
            stats['campus'] = campus
            logger.info(f"🏫 Campus identified: {campus}")

        # ENHANCED patterns for natural speech
        patterns = {
            'total_attendance': [
                # Standard patterns
                r'(?:had|got|there were|total of|attendance was|we had)\s*(\d+)\s*(?:people|total|attendance)',
                r'(\d+)\s*(?:people|total|attendance)',
                r'attendance\s*(?:was|is|of)?\s*(\d+)',
                
                # Natural speech patterns
                r'(\d+)\s*(?:at|in)\s*(?:church|service|the service)',
                r'(?:about|around|roughly)\s*(\d+)\s*people',
                r'we had\s*(\d+)',
                r'there were\s*(\d+)',
                r'(\d+)\s*showed up',
                r'(\d+)\s*came',
                r'(\d+)\s*were there',
                r'(\d+)\s*in total',
                r'total was\s*(\d+)',
            ],
            'new_people': [
                # Standard patterns
                r'(\d+)\s*(?:new|first.?time|visitors|guests|newcomers)',
                r'(?:new|first.?time|visitors|guests)\s*(\d+)',
                r'(\d+)\s*new\s*(?:people|visitors|guests)',
                
                # Natural speech patterns
                r'(\d+)\s*(?:first time|first.time)',
                r'(\d+)\s*(?:visitor|visitors)',
                r'(\d+)\s*new\s*(?:folks|friends)',
                r'(\d+)\s*(?:guest|guests)',
                
                # Abbreviations
                r'(\d+)\s*np\b',  # "5 np" 
                r'\bnp\s*(\d+)',  # "np 5"
                r'(\d+)\s*new',   # Just "5 new"
            ],
            'new_christians': [
                # Standard patterns
                r'(\d+)\s*(?:salvation|decision|new christian|saved)',
                r'(?:salvation|decision|saved)\s*(\d+)',
                r'(\d+)\s*(?:decisions?|salvations?)',
                
                # Natural speech patterns
                r'(\d+)\s*(?:gave their life|gave their lives|got saved|became christian|became christians)',
                r'(\d+)\s*(?:accepted christ|accepted jesus)',
                r'(\d+)\s*(?:came to christ|came to jesus)',
                r'(\d+)\s*(?:prayed the prayer|said the prayer)',
                
                # Abbreviations
                r'(\d+)\s*nc\b',  # "3 nc"
                r'\bnc\s*(\d+)',  # "nc 3"
                r'(\d+)\s*sal\b',  # "3 sal" (salvations)
            ],
            'youth_attendance': [
                r'(\d+)\s*(?:youth\s+attending|youth\s+attendance|young people)',
                r'youth\s+attendance\s*(?:was|is|of)?\s*(\d+)',
                r'(\d+)\s*youth',
                r'(\d+)\s*young\s*(?:people|adults)',
                r'(\d+)\s*in\s*youth',
            ],
            'new_youth': [
                r'(\d+)\s*(?:new\s+youth|first time youth|youth visitors)',
                r'new\s+youth\s*(?:was|is|of)?\s*(\d+)',
                r'(\d+)\s*new\s*(?:young people|youth)',
            ],
            'new_youth_christians': [
                r'(\d+)\s*(?:youth\s+saved|youth\s+salvations|youth\s+decisions)',
                r'youth\s+salvations\s*(?:was|is|of)?\s*(\d+)',
                r'(\d+)\s*youth\s*(?:got saved|gave their lives)',
            ],
            'kids_total': [
                r'(\d+)\s*(?:kids\s+attending|kids\s+total|children\s+present)',
                r'kids\s+attendance\s*(?:was|is|of)?\s*(\d+)',
                r'(\d+)\s*kids',
                r'(\d+)\s*children',
                r'(\d+)\s*in\s*(?:kids|children)',
            ],
            'new_kids': [
                r'(\d+)\s*(?:new\s+kids|first time kids|kids visitors)',
                r'new\s+kids\s*(?:was|is|of)?\s*(\d+)',
                r'(\d+)\s*new\s*(?:kids|children)',
            ],
            'kids_salvations': [
                r'(\d+)\s*(?:kids\s+saved|kids\s+salvations|kids\s+decisions)',
                r'kids\s+salvations\s*(?:was|is|of)?\s*(\d+)',
                r'(\d+)\s*kids\s*(?:got saved|gave their lives)',
            ],
            'connect_groups': [
                r'(\d+)\s*(?:connect\s+groups|small\s+groups|life\s+groups)',
                r'connect\s+groups\s*(?:was|is|of)?\s*(\d+)',
                r'(\d+)\s*(?:cg|connect|groups)',
            ]
        }

        # Track which stat fields are detected in this utterance
        new_fields = set()
        for field, field_patterns in patterns.items():
            for pattern in field_patterns:
                try:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        number = int(match.group(1))
                        if 0 <= number <= 10000:
                            stats[field] = number
                            new_fields.add(field)
                            logger.info(f"📊 Found {field}: {number} (pattern: {pattern})")
                            break
                except (ValueError, IndexError, AttributeError) as e:
                    logger.debug(f"Pattern match error: {e}")
                    continue

        # Auto-fill prediction if missing key stats
        if campus and 'total_attendance' in stats and 'new_people' not in stats:
            avg_new = self.get_average_stat(campus, 'new_people') or 5  # Default fallback
            stats['new_people'] = avg_new  # Predict based on average

        # Store last spoken stats per campus
        if 'campus' in stats:
            self.last_spoken_stats = getattr(self, 'last_spoken_stats', {})
            self.last_spoken_stats[stats['campus']] = stats

        logger.info(f"📊 Final parsed stats: {stats}")
        return stats
    
    def generate_trend_insight(self, campus: str, stat_key: str) -> Optional[str]:
        """Generate insight if stat trend shows consistent growth or decline"""
        if campus not in self.session_stats or len(self.session_stats[campus]) < 3:
            return None

        recent = [s.get(stat_key) for s in self.session_stats[campus] if stat_key in s][-4:]
        if len(recent) < 3 or not all(isinstance(x, int) for x in recent):
            return None

        changes = [recent[i+1] - recent[i] for i in range(len(recent) - 1)]
        avg_change = sum(changes) / len(changes)
        if abs(avg_change) / max(recent[-2], 1) >= 0.1:  # 10% threshold
            direction = "increased" if avg_change > 0 else "decreased"
            percent = abs(avg_change) / max(recent[-2], 1) * 100
            return f"{stat_key.replace('_', ' ').title()} has {direction} {percent:.1f}% on average the last few weeks."
        return None

    def generate_claude_response(self, user_input: str, stats: Dict, context: str = "") -> str:
        """🔥 ENHANCED: Claude AI response generation with better conversational flow"""
        if not self.claude_client:
            return self.generate_fallback_response(user_input, stats)

        try:
            # Build conversation history for Claude
            messages = []

            # Add recent conversation history for context
            campus_history = self.conversation_history.get(self.current_campus, [])[-3:]
            for conv in campus_history:
                if conv.get('user') and conv.get('assistant'):
                    messages.append({"role": "user", "content": conv['user']})
                    messages.append({"role": "assistant", "content": conv['assistant']})

            # Build current context
            current_context = f"User said: {user_input}"
            if stats:
                current_context += f"\nDetected data: {stats}"
            if context:
                current_context += f"\nContext: {context}"
            if self.current_campus:
                current_context += f"\nCurrent campus: {self.current_campus}"

            messages.append({"role": "user", "content": current_context})

            # Get Claude response
            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=150,
                temperature=0.7,  # Slightly higher for more natural responses
                system="""You are Link, a friendly church assistant helping pastors log stats. 
                Be conversational, helpful, and encouraging. Keep responses under 30 words when possible.
                
                Campus names: Paradise, Adelaide City, Salisbury, South, Clare Valley, Mount Barker, Victor Harbour, Copper Coast
                
                🔥 ENHANCED GUIDELINES:
                - When they give you numbers, acknowledge them warmly and ask what else you can log
                - Be encouraging about growth and salvations - this is ministry!
                - Use natural, conversational language like a helpful friend
                - If they switch topics, follow their lead naturally
                - ABBREVIATIONS: "nc" = new Christians, "np" = new people
                - Always end with a question or invitation to continue the conversation
                - Guide for missing data like attendance or youth if not provided. Be encouraging.
                
                BE WARM, ENCOURAGING, AND CONVERSATIONAL!""",
                messages=messages
            )

            response_text = response.content[0].text.strip()
            
            # Only use fallback if Claude response is empty or too short
            if not response_text or len(response_text.strip()) < 5:
                response_text = self.generate_fallback_response(user_input, stats)
            
            logger.info(f"🤖 Claude Response: {response_text}")
            return response_text

        except Exception as e:
            logger.error(f"❌ Claude response failed: {e}")
            return self.generate_fallback_response(user_input, stats)

    def compare_to_last_week(self, campus: str, stat_key: str) -> Optional[str]:
        """Compare current stat to last week's and return an insight if difference > 3%"""
        if not self.sheets_client or not self.spreadsheet:
            return None
        try:
            worksheet = self.spreadsheet.sheet1
            records = worksheet.get_all_records()
            campus_records = [r for r in records if r['Campus'] == campus and r.get(stat_key.replace('_', ' ').title())]

            if len(campus_records) < 2:
                return None  # Not enough data

            last_week_record = campus_records[-2]  # Assuming newest are at the end
            current_record = campus_records[-1]

            last_value = int(last_week_record.get(stat_key.replace('_', ' ').title(), 0))
            current_value = int(current_record.get(stat_key.replace('_', ' ').title(), 0))

            if last_value == 0:
                return None  # Avoid division by zero

            change_percent = ((current_value - last_value) / last_value) * 100

            if abs(change_percent) < 3:
                return None  # Not significant enough

            direction = "up" if change_percent > 0 else "down"
            return f"{stat_key.replace('_', ' ').title()} is {direction} {abs(change_percent):.1f}% from last week."
        except Exception as e:
            logger.error(f"❌ Failed to compare {stat_key}: {e}")
            return None
    
    def generate_fallback_response(self, user_input: str, stats: Dict) -> str:
        """🔥 ENHANCED: Fallback response - more natural and contextual"""
        # 🔥 At the very start, block fallback logic for queries/questions
        if self.is_asking_for_data(user_input):
            return "Let me check that for you..."

        campus = stats.get('campus') or self.extract_campus_enhanced(user_input)

        # If they provided stats, acknowledge them warmly
        if stats and len(stats) > 1:  # More than just campus
            if campus:
                stat_summary = []
                if 'total_attendance' in stats:
                    stat_summary.append(f"{stats['total_attendance']} people")
                if 'new_people' in stats:
                    stat_summary.append(f"{stats['new_people']} new")
                if 'new_christians' in stats:
                    stat_summary.append(f"{stats['new_christians']} salvations")

                if stat_summary:
                    encouragement = ""
                    if 'new_christians' in stats and stats['new_christians'] > 0:
                        encouragement = " Praise God! "
                    return f"Great! {campus}: {', '.join(stat_summary)}.{encouragement}What else can I log?"
                else:
                    return f"Perfect! Logged stats for {campus}. Anything else?"
            else:
                return "Awesome numbers! Which campus was that for?"

        # If campus mentioned but no stats
        if campus and len(stats) <= 1:
            return f"Ready for {campus}! What were your numbers today?"

        # Default friendly response
        if campus:
            return f"Perfect! Ready for {campus} stats."

        self.current_campus = None
        return "Hey! Which campus are you reporting for today?"
    
    def get_stat_total(self, campus: str, stat_key: str, year: Optional[int] = None, month: Optional[int] = None) -> Optional[int]:
        """Return total stat value for a campus optionally filtered by year and month"""
        if not self.sheets_client or not self.spreadsheet:
            return None
        try:
            worksheet = self.spreadsheet.sheet1
            records = worksheet.get_all_records()
            total = 0
            for row in records:
                if row.get('Campus') != campus:
                    continue
                date_str = row.get('Sunday Date')
                if not date_str:
                    continue
                try:
                    row_date = datetime.strptime(date_str, '%Y-%m-%d')
                    if year and row_date.year != year:
                        continue
                    if month and row_date.month != month:
                        continue
                except ValueError:
                    continue
                
                # Map stat_key to actual column name
                column_mapping = {
                    'total_attendance': 'Total Attendance',
                    'new_people': 'New People',
                    'new_christians': 'New Christians',
                    'youth_attendance': 'Youth Attendance',
                    'new_youth': 'New Youth',
                    'new_youth_christians': 'New Youth Christians',
                    'kids_total': 'Kids Total',
                    'new_kids': 'New Kids',
                    'kids_salvations': 'Kids Salvations',
                    'connect_groups': 'Connect Groups'
                }
                
                column_name = column_mapping.get(stat_key, stat_key.replace('_', ' ').title())
                value = row.get(column_name)
                
                if isinstance(value, int):
                    total += value
                elif isinstance(value, str) and value.isdigit():
                    total += int(value)
            return total if total > 0 else None
        except Exception as e:
            logger.error(f"❌ Failed to fetch totals for {campus}, {stat_key}: {e}")
            return None
    
    @lru_cache(maxsize=100)
    def get_all_sheets_data_cached(self, cache_key: str) -> List[Dict]:
        """Cached method to get all sheets data - reduces API calls"""
        if not self.sheets_client or not self.spreadsheet:
            return []
        try:
            worksheet = self.spreadsheet.sheet1
            return worksheet.get_all_records()
        except Exception as e:
            logger.error(f"❌ Failed to get cached sheets data: {e}")
            return []

    def get_stat_total_optimized(self, campus: str, stat_key: str, year: Optional[int] = None, month: Optional[int] = None) -> Optional[int]:
        """Optimized version using cached data"""
        try:
            cache_key = f"stats_{int(time.time() // 300)}"  # 5-minute cache
            records = self.get_all_sheets_data_cached(cache_key)
            
            total = 0
            column_mapping = {
                'total_attendance': 'Total Attendance',
                'new_people': 'New People',
                'new_christians': 'New Christians',
                'youth_attendance': 'Youth Attendance',
                'new_youth': 'New Youth',
                'new_youth_christians': 'New Youth Christians',
                'kids_total': 'Kids Total',
                'new_kids': 'New Kids',
                'kids_salvations': 'Kids Salvations',
                'connect_groups': 'Connect Groups'
            }
            
            column_name = column_mapping.get(stat_key, stat_key.replace('_', ' ').title())
            
            for row in records:
                if row.get('Campus') != campus:
                    continue
                    
                if year or month:
                    date_str = row.get('Sunday Date')
                    if date_str:
                        try:
                            row_date = datetime.strptime(date_str, '%Y-%m-%d')
                            if year and row_date.year != year:
                                continue
                            if month and row_date.month != month:
                                continue
                        except ValueError:
                            continue
                
                value = row.get(column_name)
                if isinstance(value, int):
                    total += value
                elif isinstance(value, str) and value.isdigit():
                    total += int(value)
            
            return total if total > 0 else None
        except Exception as e:
            logger.error(f"❌ Failed to get optimized total for {campus}: {e}")
            return self.get_stat_total(campus, stat_key, year, month)  # Fallback
    
    def get_average_stat(self, campus, stat_key):
        if not self.spreadsheet:
            return None
        records = self.spreadsheet.sheet1.get_all_records()
        values = [int(r.get(stat_key.replace('_', ' ').title(), 0)) for r in records if r['Campus'] == campus]
        return sum(values) / len(values) if values else None
    
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
                
                headers = [
                    'Timestamp', 'Sunday Date', 'Campus', 'Total Attendance',
                    'New People', 'New Christians', 'Youth Attendance',
                    'New Youth', 'New Youth Christians', 'Kids Total',
                    'New Kids', 'Connect Groups', 'Kids Salvations'
                ]
                row = [
                    timestamp,
                    sunday_date,
                    stats.get('campus', ''),
                    stats.get('total_attendance', ''),
                    stats.get('new_people', ''),
                    stats.get('new_christians', ''),
                    stats.get('youth_attendance', ''),
                    stats.get('new_youth', ''),
                    stats.get('new_youth_christians', ''),
                    stats.get('kids_total', ''),
                    stats.get('new_kids', ''),
                    stats.get('connect_groups', ''),
                    stats.get('kids_salvations', '')
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

        campus = stats.get('campus') or self.current_campus
        if campus:
            if campus not in self.conversation_history:
                self.conversation_history[campus] = []
            self.conversation_history[campus].append(conversation_entry)

        self.conversation_history.append(conversation_entry)

        if stats and 'campus' in stats:
            campus = stats['campus']
            if campus not in self.session_stats:
                self.session_stats[campus] = []
            # Only append if this stats dict is not a duplicate of the last one for this campus
            if not self.session_stats[campus] or self.session_stats[campus][-1] != stats:
                self.session_stats[campus].append(stats)

        # Store most recent stat snapshot for long-term comparisons
        if stats and 'campus' in stats:
            campus = stats['campus']
            self.previous_stats_by_campus[campus] = stats

        # Save memory every 3 conversations or if the conversation is a stats submission (len(stats) > 2)
        if len(self.conversation_history) % 3 == 0 or (stats and 'campus' in stats and len(stats) > 2):
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
    
    def get_insights_data(self) -> Dict:
        """Generate insights data for the dashboard"""
        if not self.sheets_client or not self.spreadsheet:
            return {}
        
        try:
            worksheet = self.spreadsheet.sheet1
            records = worksheet.get_all_records()
            current_year = datetime.now().year
            
            # Calculate insights
            insights = {
                'top_growing_campus': None,
                'total_salvations_this_year': 0,
                'attendance_trend': 'stable',
                'youth_growth_percentage': 0
            }
            
            # Find top growing campus this month
            campus_growth = {}
            for campus in self.campuses:
                current_month_attendance = self.get_stat_total(campus, 'total_attendance', current_year, datetime.now().month)
                last_month_attendance = self.get_stat_total(campus, 'total_attendance', current_year, datetime.now().month - 1)
                
                if current_month_attendance and last_month_attendance and last_month_attendance > 0:
                    growth = ((current_month_attendance - last_month_attendance) / last_month_attendance) * 100
                    campus_growth[campus] = growth
            
            if campus_growth:
                insights['top_growing_campus'] = max(campus_growth.items(), key=lambda x: x[1])
            
            # Total salvations this year
            insights['total_salvations_this_year'] = sum(
                self.get_stat_total(campus, 'new_christians', current_year) or 0 
                for campus in self.campuses
            )
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Failed to generate insights: {e}")
            return {}
    
    def cleanup_on_exit(self):
        """Cleanup on exit"""
        try:
            self.save_memory()
            self.cleanup_old_audio_files()
            self.thread_pool.shutdown(wait=False)
            logger.info("✅ Application cleanup completed")
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")

    def check_for_nudges(self):
        today = datetime.now().date()
        for campus in self.campuses:
            if not self.get_stat_total(campus, 'total_attendance', today.year, today.month):
                logger.info(f"Nudge: {campus} stats missing today")
                # Extend to email/SMS later
                return f"Reminder: Log stats for {campus}!"

# Initialize global assistant variable
assistant = None

# CSP configuration
csp = {
    'default-src': "'self'",
    'script-src': ["'self'", "'unsafe-inline'"],  # Allow inline scripts
    'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
    'font-src': ["'self'", "https://fonts.gstatic.com"],
    'connect-src': ["'self'", 'https://api.elevenlabs.io', 'https://api.anthropic.com'],
    'media-src': ["'self'", 'blob:'],
    'img-src': ["'self'", 'data:']
}
Talisman(app, force_https=False, strict_transport_security=False, content_security_policy=csp)

@app.route('/')
def index():
    """Serve the main dashboard"""
    nonce = base64.b64encode(os.urandom(16)).decode('utf-8')
    try:
        return render_template("index.html", nonce=nonce)
    except Exception as e:
        logger.error(f"❌ Failed to render template: {e}")
        return f"Template error: {e}", 500

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    try:
        favicon_path = os.path.join(app.static_folder, 'favicon.ico')
        if os.path.exists(favicon_path):
            return send_from_directory(app.static_folder, 'favicon.ico')
        else:
            return '', 204
    except Exception as e:
        logger.error(f"Error serving favicon.ico: {str(e)}")
        return '', 204

@app.route('/api/stats', methods=['GET'])
def get_all_stats():
    """Return all available stats from Google Sheets"""
    global assistant
    if not assistant or not assistant.sheets_client or not assistant.spreadsheet:
        return jsonify({'error': 'Assistant or Sheets not initialized'}), 500

    try:
        worksheet = assistant.spreadsheet.sheet1
        records = worksheet.get_all_records()

        stats_list = []
        for row in records:
            try:
                # Convert sheet row into stat dict
                row_date_str = row.get('Sunday Date')
                # Updated date parsing to handle datetime strings with time portion
                row_date = None
                if row_date_str:
                    try:
                        row_date = datetime.strptime(row_date_str.split(' ')[0], '%Y-%m-%d')
                    except Exception:
                        row_date = None
                stat = {
                    'date': row.get('Sunday Date'),
                    'campus': row.get('Campus'),
                    'total_attendance': int(row.get('Total Attendance') or 0),
                    'new_people': int(row.get('New People') or 0),
                    'new_christians': int(row.get('New Christians') or 0),
                    'youth_attendance': int(row.get('Youth Attendance') or 0),
                    'kids_total': int(row.get('Kids Total') or 0),
                    'connect_groups': int(row.get('Connect Groups') or 0)
                }
                stats_list.append(stat)
            except Exception as row_error:
                logger.warning(f"⚠️ Skipped row due to error: {row_error}")

        return jsonify({'stats': stats_list})
    except Exception as e:
        logger.error(f"❌ Failed to load all stats: {e}")
        return jsonify({'error': 'Failed to retrieve stats from sheets'}), 500

@app.route('/api/process_voice', methods=['POST'])
def process_voice():
    """🔥 ENHANCED: Voice processing endpoint with Claude AI + Auto-Mic"""
    global assistant
    if not assistant:
        return jsonify({'error': 'Assistant not initialized'}), 500

    try:
        data = request.json
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing text input'}), 400

        text = data['text'].strip()
        if not text:
            return jsonify({'error': 'Empty input'}), 400

        logger.info(f"🎙️ Voice input received: {text}")

        # Session reset check
        if 'new session' in text.lower():
            assistant.current_campus = None
            return jsonify({
                'text': 'Futures Link with Claude is live. How can I help you today?',
                'campus': None,
                'audio_url': None,
                'stats': {},
                'session_summary': None,
                'insights': assistant.get_insights_data(),
                'auto_listen': True  # 🔥 NEW: Signal frontend to auto-restart listening
            })

        # Parse stats once
        stats = assistant.parse_stats_enhanced(text)
        campus = stats.get('campus', assistant.current_campus)
        
        if campus:
            stats['campus'] = campus
            if campus != assistant.current_campus:
                logger.info(f"🔁 Switching campus from {assistant.current_campus} to {campus}")
            assistant.current_campus = campus

        # Manual campus switch
        if "switch to" in text.lower() or "reporting for" in text.lower():
            potential_campus = assistant.extract_campus_enhanced(text)
            if potential_campus:
                logger.info(f"🔀 Manual campus switch to: {potential_campus}")
                assistant.current_campus = potential_campus
                return jsonify({
                    'text': f"Switched to {potential_campus}. Ready for your stats.",
                    'campus': potential_campus,
                    'audio_url': None,
                    'stats': {},
                    'campus_switched': True,
                    'insights': assistant.get_insights_data(),
                    'auto_listen': True  # 🔥 NEW: Keep conversation going
                })

        # 🔥 ENHANCED: Check if they're asking for data vs providing data
        context = f"Voice request for {campus}" if campus else "Voice request"
        stat_query_response = None
        
        # Only do data lookup if they're asking questions
        if assistant.is_asking_for_data(text):
            stat_query_response = assistant.handle_stat_query(text)
        
        # Generate response using Claude
        if stat_query_response:
            response_text = stat_query_response
        else:
            # They're providing data or having normal conversation
            response_text = assistant.generate_claude_response(text, stats, context)

        # Update memory
        assistant.update_conversation_memory(text, response_text, stats)

        # Log to sheets if needed
        if stats and 'campus' in stats and len(stats) > 2:
            assistant.log_to_sheets_background(stats)

        # Check nudges
        nudge = assistant.check_for_nudges()
        if nudge:
            response_text += f"\n{nudge}"

        # Generate audio response
        audio_url = None
        if assistant.use_elevenlabs and response_text:
            audio_content = asyncio.run(assistant.generate_elevenlabs_audio(response_text))
            if audio_content:
                filename = f"speech_{uuid.uuid4().hex[:8]}.mp3"
                path = os.path.join('temp_audio', filename)
                with open(path, 'wb') as f:
                    f.write(audio_content)
                audio_url = f"/api/audio/{filename}"

        # 🔥 NEW: Auto-restart listening for conversational flow
        return jsonify({
            'text': response_text,
            'campus': campus,
            'stats': stats,
            'audio_url': audio_url,
            'session_summary': assistant.get_session_summary(),
            'insights': assistant.get_insights_data(),
            'auto_listen': True  # 🔥 NEW: Signal frontend to restart listening automatically
        })

    except Exception as e:
        logger.error(f"❌ Voice processing failed: {e}", exc_info=True)
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/stats/<campus>')
def get_campus_stats(campus):
    """Get current stats for a specific campus - BULLETPROOF VERSION"""
    global assistant
    if not assistant:
        return jsonify({'error': 'Assistant not initialized'}), 500
    
    try:
        # Simple fallback stats if Sheets unavailable
        fallback_stats = {
            'total_attendance': 0,
            'new_people': 0, 
            'new_christians': 0,
            'youth_attendance': 0,
            'kids_total': 0,
            'connect_groups': 0,
            'attendance_change_percentage': 0
        }
        
        # If no sheets client, return fallback
        if not assistant.sheets_client or not assistant.spreadsheet:
            logger.warning(f"⚠️ No sheets client available for {campus}")
            return jsonify(fallback_stats)
        
        # Try to get real data with error handling
        try:
            current_year = datetime.now().year
            
            # Use the optimized method
            stats = {
                'total_attendance': assistant.get_stat_total_optimized(campus, 'total_attendance', current_year) or 0,
                'new_people': assistant.get_stat_total_optimized(campus, 'new_people', current_year) or 0,
                'new_christians': assistant.get_stat_total_optimized(campus, 'new_christians', current_year) or 0,
                'youth_attendance': assistant.get_stat_total_optimized(campus, 'youth_attendance', current_year) or 0,
                'kids_total': assistant.get_stat_total_optimized(campus, 'kids_total', current_year) or 0,
                'connect_groups': assistant.get_stat_total_optimized(campus, 'connect_groups', current_year) or 0
            }
            
            # Try to add trend data (optional)
            try:
                last_year_attendance = assistant.get_stat_total_optimized(campus, 'total_attendance', current_year - 1) or 0
                if last_year_attendance > 0 and stats['total_attendance'] > 0:
                    attendance_change = ((stats['total_attendance'] - last_year_attendance) / last_year_attendance) * 100
                    stats['attendance_change_percentage'] = round(attendance_change, 1)
                else:
                    stats['attendance_change_percentage'] = 0
            except Exception as trend_error:
                logger.warning(f"⚠️ Could not calculate trend for {campus}: {trend_error}")
                stats['attendance_change_percentage'] = 0
            
            logger.info(f"✅ Retrieved stats for {campus}: {stats}")
            return jsonify(stats)
            
        except Exception as data_error:
            logger.error(f"❌ Failed to get real data for {campus}: {data_error}")
            # Return fallback stats instead of error
            logger.info(f"📊 Returning fallback stats for {campus}")
            return jsonify(fallback_stats)
            
    except Exception as e:
        logger.error(f"❌ Endpoint error for {campus}: {e}")
        return jsonify({
            'error': f'Failed to retrieve stats for {campus}',
            'campus': campus,
            'total_attendance': 0,
            'new_people': 0,
            'new_christians': 0,
            'youth_attendance': 0,
            'kids_total': 0,
            'connect_groups': 0
        }), 200  # Return 200 instead of 500 to avoid frontend errors

@app.route('/api/insights')
def get_insights():
    """Get dashboard insights"""
    global assistant
    if not assistant:
        return jsonify({'error': 'Assistant not initialized'}), 500
    
    try:
        insights = assistant.get_insights_data()
        return jsonify(insights)
    except Exception as e:
        logger.error(f"❌ Failed to get insights: {e}")
        return jsonify({'error': 'Failed to retrieve insights'}), 500

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
                conditional=True
            )
        else:
            logger.warning(f"Audio file not found: {filename}")
            return "Audio file not found", 404
    except Exception as e:
        logger.error(f"❌ Error serving audio: {e}")
        return "Error serving audio", 500

@app.route('/api/session', methods=['GET'])
def get_session_summary():
    """Get current session summary with enhanced data"""
    global assistant
    if assistant:
        insights = assistant.get_insights_data()
        return jsonify({
            'summary': assistant.get_session_summary(),
            'conversation_count': len(assistant.conversation_history),
            'current_campus': assistant.current_campus,
            'available_campuses': assistant.campuses,
            'insights': insights
        })
    return jsonify({
        'summary': 'No active session', 
        'conversation_count': 0,
        'error': 'assistant_not_initialized'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Enhanced health check endpoint"""
    global assistant
    
    health_status = {
        'status': 'healthy' if assistant else 'unhealthy',
        'timestamp': datetime.now().isoformat(),
        'services': {},
        'version': '3.0-claude-enhanced-automic'
    }
    
    if assistant:
        health_status['services'] = {
            'claude': assistant.claude_client is not None,
            'elevenlabs': assistant.use_elevenlabs,
            'google_sheets': assistant.sheets_client is not None,
            'memory_system': os.path.exists(assistant.memory_file)
        }
        
        # Add system metrics
        health_status['metrics'] = {
            'campuses_configured': len(assistant.campuses),
            'conversations_this_session': len(assistant.conversation_history),
            'active_campus': assistant.current_campus
        }
    
    status_code = 200 if assistant else 503
    return jsonify(health_status), status_code

@app.route('/api/summary/weekend', methods=['GET'])
def weekend_summary():
    """Get weekend summary across all campuses"""
    global assistant
    if not assistant or not assistant.sheets_client or not assistant.spreadsheet:
        return jsonify({'error': 'Assistant or Sheets not initialized'}), 500

    try:
        worksheet = assistant.spreadsheet.sheet1
        records = worksheet.get_all_records()

        today = datetime.now()
        days_since_sunday = (today.weekday() + 1) % 7
        last_sunday = (today - timedelta(days=days_since_sunday)).strftime('%Y-%m-%d')

        summary = []
        total_attendance = 0
        total_salvations = 0
        total_new_people = 0
        
        for campus in assistant.campuses:
            campus_data = [r for r in records if r.get('Campus') == campus and r.get('Sunday Date') == last_sunday]
            if not campus_data:
                continue
            row = campus_data[-1]
            attendance = int(row.get('Total Attendance', 0))
            new_people = int(row.get('New People', 0))
            salvations = int(row.get('New Christians', 0))
            
            total_attendance += attendance
            total_new_people += new_people
            total_salvations += salvations
            
            summary.append({
                'campus': campus,
                'attendance': attendance,
                'new_people': new_people,
                'salvations': salvations
            })

        if not summary:
            return jsonify({'summary': 'No data found for the last Sunday.'})

        return jsonify({
            'summary': summary,
            'totals': {
                'attendance': total_attendance,
                'new_people': total_new_people,
                'salvations': total_salvations
            },
            'date': last_sunday
        })
    except Exception as e:
        logger.error(f"❌ Weekend summary failed: {e}")
        return jsonify({'error': 'Failed to generate summary'}), 500

@app.route('/api/startup_chime')
def trigger_startup_chime():
    """Trigger startup chime manually"""
    play_startup_chime()
    return jsonify({'message': 'Startup chime triggered', 'status': 'playing'})

@app.route('/api/nudges', methods=['GET'])
def get_nudges():
    global assistant
    if not assistant:
        return jsonify({'error': 'Assistant not initialized'}), 500
    
    nudge = assistant.check_for_nudges()
    return jsonify({'nudges': nudge or 'All good!'})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

def main():
    """🚀 Main application entry point with Claude + Auto-Mic"""
    global assistant
    
    print("\n🎯 STARTING FUTURES LINK ASSISTANT WITH CLAUDE + AUTO-MIC")
    print("=" * 50)
    
    # Initialize assistant with error handling
    try:
        assistant = EnhancedChurchAssistant()
        print("✅ Assistant with Claude initialized successfully")
        
        # 🎵 Generate and play startup chime (if available)
        if hasattr(assistant, 'use_elevenlabs') and assistant.use_elevenlabs:
            try:
                print("\n🎵 Initializing startup chime...")
                chime_path = generate_startup_chime_audio(assistant)
                if chime_path:
                    print(f"✅ Startup chime generated: {chime_path}")
            except Exception as e:
                print(f"⚠️ Startup chime failed: {e}")
                
        # Still play a chime even if assistant failed
        print("🎵 Playing startup chime...")
        play_startup_chime()
                
    except Exception as e:
        logger.error(f"❌ Assistant initialization failed: {e}")
        print("⚠️ Assistant will run in basic mode")
        # Create minimal assistant for fallback
        assistant = type('obj', (object,), {
            'demo_stats': {
                'Paradise': {'attendance': 320, 'new': 12, 'salvations': 4},
                'Adelaide City': {'attendance': 450, 'new': 18, 'salvations': 6},
                'Salisbury': {'attendance': 280, 'new': 9, 'salvations': 3},
            },
            'current_campus': None,
            'conversation_history': [],
            'campuses': ['Paradise', 'Adelaide City', 'Salisbury', 'South'],
            'has_sheets': False,
            'has_voice': False,
            'has_claude': False
        })()
        
        # Still play a chime even if assistant failed
        print("🎵 Playing basic startup chime...")
        play_startup_chime()
    
    print("\n🎉 FUTURES LINK WITH CLAUDE + AUTO-MIC READY!")
    print("=" * 50)
    print("🔥 NEW FEATURES:")
    print("✅ Enhanced natural language understanding")
    print("✅ Better phrasing recognition")
    print("✅ Auto-microphone for conversational flow")
    print("✅ Fixed logging system")
    print("✅ More encouraging responses")
    print("=" * 50)
    
    # 🚀 RAILWAY DEPLOYMENT CONFIGURATION
    port = int(os.getenv('PORT', 5001))  # Railway sets PORT automatically
    host = '0.0.0.0'  # Required for Railway
    
    # Determine if we're in production
    is_production = os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('PORT')
    
    if is_production:
        print(f"\n🌐 PRODUCTION MODE: Railway deployment")
        print(f"🔗 App will be available at your Railway URL")
        debug_mode = False
    else:
        print(f"\n💻 DEVELOPMENT MODE: Local testing")
        print(f"🔗 App running on: http://localhost:{port}")
        debug_mode = True
    
    print(f"🎯 Host: {host}, Port: {port}")
    print("🤖 AI: Claude 3.5 Sonnet (Enhanced)")
    print("🎤 Auto-Mic: Enabled")
    print("=" * 50)
    
    try:
        app.run(
            host=host,
            port=port,            debug=debug_mode,
            threaded=True,
            use_reloader=False  # Disable reloader for production
        )
    except Exception as e:
        logger.error(f"❌ Server failed to start: {e}")
        print(f"❌ Server error: {e}")
        if not is_production:
            print("💡 Try a different port or check if another app is running")
        raise

if __name__ == '__main__':
    main()