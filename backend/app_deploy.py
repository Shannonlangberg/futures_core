# app_deploy.py - Production deployment version
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the main app
from app import app

# Production configuration
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    app.run(host="0.0.0.0", port=port, debug=False) 