from flask import Flask, request, jsonify, session
import os
from dotenv import load_dotenv
from utils import process_document, process_drive_file
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "document"}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400

        summary = process_document(file)
        return jsonify({
            'status': 'success',
            'summary': summary
        })
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Processing error: {str(e)}'
        }), 500

@app.route('/google-auth')
def google_auth():
    try:
        flow = Flow.from_client_secrets_file(
            'credentials.json',
            scopes=['https://www.googleapis.com/auth/drive.readonly'],
            redirect_uri='http://127.0.0.1:5173/oauth2callback'
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        session['state'] = state
        return jsonify({'auth_url': authorization_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/list-drive-files')
def list_drive_files():
    try:
        credentials = get_credentials()
        if not credentials:
            return jsonify({'error': 'Not authenticated'}), 401
            
        service = build('drive', 'v3', credentials=credentials)
        results = service.files().list(
            pageSize=10,
            fields="files(id, name, mimeType)",
            q="mimeType='application/pdf'"
        ).execute()
        return jsonify({'files': results.get('files', [])})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-drive-file/<file_id>')
def get_drive_file(file_id):
    try:
        credentials = get_credentials()
        if not credentials:
            return jsonify({'error': 'Not authenticated'}), 401
        
        summary = process_drive_file(file_id, credentials)
        return jsonify(summary)
            
    except Exception as e:
        print(f"Drive File Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Processing error: {str(e)}'
        }), 500

def get_credentials():
    """Helper function to get and refresh credentials"""
    try:
        if 'credentials' in session:
            creds = Credentials(**session['credentials'])
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                session['credentials']['token'] = creds.token
            return creds
        return None
    except Exception:
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)