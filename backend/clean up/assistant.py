import os, json, re, logging, time, uuid, base64, difflib, asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from functools import lru_cache
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False