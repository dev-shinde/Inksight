from flask import Flask, render_template, jsonify, request
import os
from dotenv import load_dotenv
import requests

load_dotenv()
app = Flask(__name__)

# Service URLs
CALCULATOR_SERVICE_URL = os.getenv('CALCULATOR_SERVICE_URL', 'http://calculator-service:5002')
DOCUMENT_SERVICE_URL = os.getenv('DOCUMENT_SERVICE_URL', 'http://document-service:5003')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "frontend"}), 200

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/calculator')
def calculator():
    return render_template('home.html')

@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    if request.method == 'GET':
        return render_template('home.html')
    
    # POST request handling for calculations
    try:
        calculator_response = requests.post(
            f'{CALCULATOR_SERVICE_URL}/calculate',
            json=request.get_json()
        )
        return calculator_response.json(), calculator_response.status_code
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/document')
def document():
    return render_template('document.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({'status': 'error', 'message': 'No file provided'}), 400

        # Forward the file to the document service
        files = {'file': (file.filename, file.read(), file.content_type)}
        response = requests.post(
            f'{DOCUMENT_SERVICE_URL}/upload',
            files=files
        )
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Google Drive routes
@app.route('/google-auth')
def google_auth():
    try:
        response = requests.get(f'{DOCUMENT_SERVICE_URL}/google-auth')
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/list-drive-files')
def list_drive_files():
    try:
        response = requests.get(f'{DOCUMENT_SERVICE_URL}/list-drive-files')
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-drive-file/<file_id>')
def get_drive_file(file_id):
    try:
        response = requests.get(f'{DOCUMENT_SERVICE_URL}/get-drive-file/{file_id}')
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)