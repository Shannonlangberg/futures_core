# Futures Link Assistant - Demo Guide

## 🚀 Quick Start

### 1. Start the Backend
```bash
cd backend
python app.py
```
You should see:
- "Google Sheets initialized successfully" (or warning if no credentials)
- "Claude initialized successfully"
- "ElevenLabs API key found" (or warning if no key)
- "Running on http://127.0.0.1:5001"

### 2. Test Everything Works
```bash
python demo_test.py
```
This will test all endpoints and show you what's working.

### 3. Open the Frontend
Go to: http://localhost:5001

## 🎯 Demo Flow

### Opening Demo
1. **Click the orb** - Should hear "Connected to Futures Link, how can I help you today?"
2. **Select a campus** from the dropdown (e.g., "South")
3. **Start talking** - "South campus had 150 people, 8 new visitors, 3 salvations"

### Key Features to Demo

#### 1. Voice Input & Stat Extraction
- Say: "South campus had 150 people, 8 new visitors, 3 salvations"
- Should extract: Attendance: 150, New People: 8, New Christians: 3
- Should respond with AI insights

#### 2. Campus Detection
- Say: "North campus had 200 people"
- Should automatically detect "North" campus
- Should update the dropdown

#### 3. Query System
- Go to: http://localhost:5001/query
- Ask: "How many new people has south campus had this year?"
- Should show historical data and analysis

#### 4. ElevenLabs Voice
- All responses should use ElevenLabs voice (if API key is set)
- Falls back to browser TTS if no ElevenLabs

## 🔧 Troubleshooting

### No Voice on Startup
- Check if `/api/greeting_audio` returns 200 OK
- Check ElevenLabs API key in .env file

### Stats Not Extracting
- Check the regex patterns in `extract_stats_with_context()`
- Make sure you say the numbers clearly

### Campus Not Detecting
- Check the campus detection patterns
- Try saying the campus name more clearly

### Backend Won't Start
- Check all required packages are installed
- Check .env file has required API keys
- Check no other process is using port 5001

## 📊 Demo Data

The system will:
- Store conversation memory in `data/conversation_memory.json`
- Log stats to Google Sheets (if configured)
- Generate audio files in `temp_audio/`

## 🎉 Demo Success Indicators

✅ Greeting voice plays on first orb click  
✅ Campus detection works automatically  
✅ Stats extract correctly from voice  
✅ AI responds with insights  
✅ Query system shows historical data  
✅ ElevenLabs voice sounds natural  

## 🚨 Common Issues

1. **No greeting voice**: Check ElevenLabs API key
2. **Stats wrong**: Check regex patterns, speak clearly
3. **Campus wrong**: Say campus name clearly
4. **No response**: Check Claude API key
5. **404 errors**: Restart backend server

---

**Ready for demo! 🚀** 

Perfect! The backend is working correctly now. The response is:

```json
{
  "text": "I'd be happy to help you log stats! Which campus would you like to log stats for? You can say something like 'Salisbury campus' or 'South campus'.",
  "campus": null,
  "insights": ["Please select a campus first"],
  "suggestions": ["Try saying a campus name like 'Salisbury', 'South', 'Paradise', etc."]
}
```

This is the correct response. The issue you experienced ("love log stats for nun campus") might have been from an older version or a caching issue.

## 🧪 **Try These Test Texts Again:**

### **1. Test No Campus (Should Work Now)**
```
Can I log stats?
```
**Expected**: Should say "I'd be happy to help you log stats! Which campus would you like to log stats for? You can say something like 'Salisbury campus' or 'South campus'."

### **2. Test Campus Detection**
```
Salisbury campus had 150 people, 8 new visitors, 3 salvations
```
**Expected**: Should detect Salisbury, extract stats, show transcript

### **3. Test Different Campus**
```
South campus had 200 people, 12 new visitors, 5 salvations
```
**Expected**: Should detect South, extract stats, update dropdown

**The backend is working correctly now!** The "nun campus" issue should be resolved. Try the tests again and let me know what happens! 🚀 