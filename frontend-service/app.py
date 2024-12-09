from flask import Flask, render_template, jsonify, request, session, redirect, send_from_directory, url_for
import os
from dotenv import load_dotenv
import requests
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__,
           static_url_path='',  # Changed this line
           static_folder='static',
           template_folder='templates')
           
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

CALCULATOR_SERVICE_URL = os.getenv('CALCULATOR_SERVICE_URL', 'http://calculator-service:5002')
DOCUMENT_SERVICE_URL = os.getenv('DOCUMENT_SERVICE_URL', 'http://document-service:5003')

# Explicit static file handling
@app.route('/static/<path:filename>')
def static_files(filename):
    logger.info(f"Serving static file: {filename}")
    try:
        return send_from_directory(app.static_folder, filename)
    except Exception as e:
        logger.error(f"Error serving static file {filename}: {str(e)}")
        return str(e), 404

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "frontend",
        "static_folder": app.static_folder,
        "template_folder": app.template_folder
    })

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    if request.method == 'GET':
        return render_template('home.html')
    
    try:
        response = requests.post(
            f'{CALCULATOR_SERVICE_URL}/calculate',
            json=request.get_json(),
            timeout=10  # Added timeout
        )
        return response.json(), response.status_code
    except requests.Timeout:
        logger.error("Calculator service timeout")
        return jsonify({'status': 'error', 'message': 'Service timeout'}), 504
    except Exception as e:
        logger.error(f"Calculator error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/document')
def document():
    return render_template('document.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file provided'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
            
        files = {'file': file}
        response = requests.post(
            f'{DOCUMENT_SERVICE_URL}/upload',
            files=files,
            timeout=30  # Added timeout for file upload
        )
        return response.json(), response.status_code
    except requests.Timeout:
        logger.error("Document service timeout")
        return jsonify({'status': 'error', 'message': 'Service timeout'}), 504
    except Exception as e:
        logger.error(f"Document upload error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Add debug route to check static files
@app.route('/debug/static')
def debug_static():
    static_files = []
    for root, dirs, files in os.walk(app.static_folder):
        for file in files:
            static_files.append(os.path.join(root, file))
    return jsonify({
        'static_folder': app.static_folder,
        'files': static_files
    })

if __name__ == '__main__':
    # Log important configurations
    logger.info(f"Static folder: {app.static_folder}")
    logger.info(f"Template folder: {app.template_folder}")
    
    # Run the app
    app.run(host='0.0.0.0', port=5001, debug=True)