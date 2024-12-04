# frontend-service/app.py
from flask import Flask, render_template, jsonify, request, session, redirect
import os
from dotenv import load_dotenv
import requests

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

CALCULATOR_SERVICE_URL = os.getenv('CALCULATOR_SERVICE_URL', 'http://calculator-service:5002')
DOCUMENT_SERVICE_URL = os.getenv('DOCUMENT_SERVICE_URL', 'http://document-service:5003')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "frontend"}), 200

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    if request.method == 'GET':
        return render_template('home.html')
    
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
def upload_file():
    try:
        # Forward the file to document service
        files = {'file': request.files['file']}
        response = requests.post(f'{DOCUMENT_SERVICE_URL}/upload', files=files)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Google Drive Integration Routes
@app.route('/google-auth')
def google_auth():
    try:
        response = requests.get(f'{DOCUMENT_SERVICE_URL}/google-auth')
        auth_data = response.json()
        if 'auth_url' in auth_data:
            return redirect(auth_data['auth_url'])
        return jsonify(auth_data), response.status_code
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/oauth2callback')
def oauth2callback():
    try:
        response = requests.get(
            f'{DOCUMENT_SERVICE_URL}/oauth2callback',
            params=request.args
        )
        if response.status_code == 302:  # Handle redirects
            return redirect(response.headers['Location'])
        return response.content, response.status_code
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/list-drive-files')
def list_drive_files():
    try:
        response = requests.get(f'{DOCUMENT_SERVICE_URL}/list-drive-files')
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/get-drive-file/<file_id>')
def get_drive_file(file_id):
    try:
        response = requests.get(f'{DOCUMENT_SERVICE_URL}/get-drive-file/{file_id}')
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)