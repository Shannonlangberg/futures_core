import os
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a new Flask app for deployment
app = Flask(__name__)

# Enable CORS
CORS(app, origins=['*'])  # Configure this properly in production

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
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/session')
def session_info():
    return jsonify({
        'status': 'connected',
        'timestamp': datetime.now().isoformat(),
        'message': 'Church Voice Assistant API is running'
    })

@app.route('/api/stats')
def get_stats():
    # Return basic stats for demo
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
    try:
        data = request.get_json()
        text = data.get('text', '')
        campus = data.get('campus', 'Futures Church')
        
        # Simple response for demo
        response_text = f"I heard you say: '{text}' for {campus}. This is a demo response from the deployed app."
        
        return jsonify({
            'text': response_text,
            'campus': campus,
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error processing voice: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/query', methods=['POST'])
def query():
    try:
        data = request.get_json()
        question = data.get('text', '')
        campus = data.get('campus', 'Futures Church')
        
        # Simple response for demo
        response_text = f"Query: '{question}' for {campus}. This is a demo response from the deployed app."
        
        return jsonify({
            'text': response_text,
            'campus': campus,
            'status': 'success'
        })
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
    return jsonify({
        'campus': campus,
        'memory': {
            'last_visit': datetime.now().isoformat(),
            'encouragement_count': 0
        }
    })

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