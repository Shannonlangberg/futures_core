# 🔥 Futures Core - Voice Assistant

A comprehensive church management system with AI-powered voice interaction, designed to streamline church operations and provide intelligent insights.

## 🚀 Core Features

### Core Link - Voice-Driven Logging & Interaction Hub
- **Voice Interface Layer**: Real-time transcription with speaker diarization
- **Stat Parser Engine**: Intelligent interpretation of spoken input into structured data
- **Multi-Campus Router**: Smart campus detection and routing
- **Dynamic Prompter**: AI-generated follow-up questions for missing data
- **Memory Threading**: Conversational history across time periods
- **Smart Nudges**: Automatic reminders for incomplete stats

### Enhanced AI Integration
- **Natural Language Understanding**: Advanced pattern recognition for church statistics
- **Memory Chaining**: Context-aware responses based on historical data
- **Auto-filling**: Predictive stat completion
- **Context-aware Flows**: Intelligent conversation management

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8+
- Google Cloud Platform account
- Anthropic API key
- Google Sheets API credentials

### 1. Environment Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd church-voice-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 2. API Keys & Credentials

Create a `.env` file in the `backend` directory:

```bash
# Backend/.env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
```

### 3. Google Sheets Setup

1. **Create a Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Google Sheets API and Google Drive API

2. **Create Service Account**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Download the JSON key file
   - Rename it to `credentials.json` and place it in the `backend` directory

3. **Set up Google Sheet**:
   - Create a new Google Sheet named "Stats"
   - Share it with the service account email (found in credentials.json)
   - The sheet should have these columns:
     - Timestamp
     - Campus
     - Total Attendance
     - New People
     - New Christians
     - Youth Attendance
     - Kids Total
     - Connect Groups
     - Tithe Amount
     - Volunteers
     - Encouragement

### 4. Run the Application

```bash
# Start the backend server
cd backend
python app.py

# The application will be available at:
# Frontend: http://localhost:5001
# API: http://localhost:5001/api/
```

## 🎯 Usage Examples

### Voice Input Examples

**Basic Attendance Logging:**
```
"Hey, we had 150 people today at the main campus, 25 new visitors, and 3 salvations."
```

**Detailed Service Report:**
```
"North campus this morning: 200 total attendance, 15 new people, 5 salvations, 45 youth, 60 kids, 12 connect groups, and we had $15,000 in tithe."
```

**Auto-detected Campus:**
```
"South campus had 180 people, 20 new visitors, and 4 baptisms today."
```

### API Endpoints

- `GET /api/health` - System health check
- `GET /api/stats` - Retrieve recent statistics
- `POST /api/process_voice` - Process voice input
- `GET /api/memory/<campus>` - Get conversation history
- `GET /api/campuses` - List available campuses

## 🔧 Advanced Configuration

### Custom Campus Detection

Edit the `campus_patterns` in `backend/app.py`:

```python
campus_patterns = {
    "main": r"(?:main\s+campus|downtown|central)",
    "north": r"(?:north\s+campus|northside)",
    # Add your custom campuses here
}
```

### Enhanced Stat Patterns

Add custom stat recognition patterns:

```python
patterns = {
    "total_attendance": r"(\d+)\s+(?:people|attendance|total|adults?)",
    # Add your custom patterns here
}
```

## 🧠 AI Features

### Memory System
- **Conversation History**: Tracks interactions per campus
- **Context Awareness**: AI responses consider historical data
- **Trend Recognition**: Identifies patterns across time periods

### Smart Suggestions
- **Missing Data Detection**: Automatically identifies incomplete reports
- **Follow-up Questions**: AI-generated prompts for missing information
- **Predictive Assistance**: Suggests likely values based on patterns

### Multi-Campus Intelligence
- **Campus Auto-detection**: Identifies campus from voice input
- **Cross-campus Insights**: Compares performance across locations
- **Unified Dashboard**: Consolidated view of all campus data

## 🔮 Future Enhancements

### Planned Core Components

1. **Core Dashboard** - Real-time church health monitoring
2. **Core Connect** - Follow-up & assimilation flow engine
3. **Core Pulse** - Real-time engagement tracking
4. **Core Grow** - Discipleship pathway builder

### Advanced AI Features
- **Predictive Analytics**: Forecast attendance and giving trends
- **Burnout Detection**: Identify team member fatigue patterns
- **Engagement Scoring**: Quantify member participation levels
- **Automated Reporting**: Generate insights and recommendations

## 🐛 Troubleshooting

### Common Issues

**Voice Recognition Not Working:**
- Ensure HTTPS is enabled (required for microphone access)
- Check browser permissions for microphone access
- Try refreshing the page

**Google Sheets Connection Error:**
- Verify `credentials.json` is in the backend directory
- Check that the service account has access to the sheet
- Ensure the sheet name is exactly "Stats"

**Claude API Errors:**
- Verify your Anthropic API key is correct
- Check your API usage limits
- Ensure the API key has proper permissions

### Debug Mode

Enable debug logging by setting the log level in `backend/app.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Data Structure

### Conversation Memory Format

```json
{
  "main": [
    {
      "Campus": "main",
      "Timestamp": "2024-01-15T10:30:00",
      "Total Attendance": "150",
      "New People": "25",
      "Raw_Text": "We had 150 people today..."
    }
  ]
}
```

### Google Sheets Structure

| Column | Description | Example |
|--------|-------------|---------|
| Timestamp | When the entry was logged | 2024-01-15 10:30:00 |
| Campus | Campus identifier | main |
| Total Attendance | Number of attendees | 150 |
| New People | New visitors | 25 |
| New Christians | Salvations/decisions | 3 |
| Youth Attendance | Youth ministry count | 45 |
| Kids Total | Children's ministry | 60 |
| Connect Groups | Small group count | 12 |
| Tithe Amount | Giving amount | $15,000 |
| Volunteers | Team members | 35 |
| Encouragement | AI-generated response | "Great work!..." |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section above
- Review the API documentation

---

**🔥 Futures Core** - Transforming church management through intelligent voice interaction and AI-powered insights. 