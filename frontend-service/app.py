from flask import Flask, render_template, jsonify, request, session, redirect, send_from_directory
import os
from dotenv import load_dotenv
import requests
import logging
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
    static_url_path='/static',
    static_folder='/app/static',  # Use absolute path
    template_folder='templates')

# Add proxy support
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

CALCULATOR_SERVICE_URL = os.getenv('CALCULATOR_SERVICE_URL', 'http://calculator-service:5002')
DOCUMENT_SERVICE_URL = os.getenv('DOCUMENT_SERVICE_URL', 'http://document-service:5003')

# Improved static file handling
@app.route('/static/<path:filename>')
def serve_static(filename):
    logger.info(f"Static file request received for: {filename}")
    try:
        # Handle CSS files
        if filename.startswith('css/'):
            logger.info(f"Serving CSS file: {filename}")
            return send_from_directory('/app/static', filename, mimetype='text/css')
        
        # Handle JavaScript files
        elif filename.startswith('js/'):
            logger.info(f"Serving JS file: {filename}")
            return send_from_directory('/app/static', filename, mimetype='application/javascript')
        
        # Handle other static files
        return send_from_directory('/app/static', filename)
    except Exception as e:
        logger.error(f"Error serving static file {filename}: {str(e)}")
        return f"Failed to serve static file: {str(e)}", 404

@app.route('/debug/static')
def debug_static():
    """Debug endpoint to check static files"""
    try:
        static_files = []
        for root, dirs, files in os.walk(app.static_folder):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, app.static_folder)
                static_files.append({
                    'path': relative_path,
                    'full_path': full_path,
                    'exists': os.path.exists(full_path),
                    'size': os.path.getsize(full_path) if os.path.exists(full_path) else None
                })
        return jsonify({
            'static_folder': app.static_folder,
            'files': static_files,
            'static_url_path': app.static_url_path
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Your existing routes...
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "frontend",
        "static_folder": app.static_folder,
        "static_url_path": app.static_url_path,
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


@app.after_request
def after_request(response):
    """Log all requests"""
    logger.info(f"{request.method} {request.path} - {response.status_code}")
    return response

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    logger.info(f"Static folder: {app.static_folder}")
    logger.info(f"Static URL path: {app.static_url_path}")
    logger.info(f"Template folder: {app.template_folder}")
    app.run(host='0.0.0.0', port=5001, debug=True)