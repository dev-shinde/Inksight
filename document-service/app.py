# document-service/app.py
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from utils import process_document, get_drive_credentials
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
load_dotenv()
app = Flask(__name__)

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

        summary = process_document(file.read())
        return jsonify({
            'status': 'success',
            'summary': summary
        })
    except Exception as e:
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
            redirect_uri='http://localhost:5000/api/document/oauth2callback'
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return jsonify({'auth_url': authorization_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/oauth2callback')
def oauth2callback():
    try:
        flow = Flow.from_client_secrets_file(
            'credentials.json',
            scopes=['https://www.googleapis.com/auth/drive.readonly'],
            redirect_uri='http://localhost:5000/api/document/oauth2callback'
        )
        
        # Don't forget to set OAUTHLIB_INSECURE_TRANSPORT=1 for development
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        
        authorization_response = request.url.replace('http://', 'https://')  # Required for OAuth
        flow.fetch_token(authorization_response=authorization_response)
        
        credentials = {
            'token': flow.credentials.token,
            'refresh_token': flow.credentials.refresh_token,
            'token_uri': flow.credentials.token_uri,
            'client_id': flow.credentials.client_id,
            'client_secret': flow.credentials.client_secret,
            'scopes': flow.credentials.scopes
        }
        return jsonify({'status': 'success', 'credentials': credentials})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/list-drive-files')
def list_drive_files():
    try:
        credentials_data = request.get_json()
        credentials = get_drive_credentials(credentials_data)
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

@app.route('/get-drive-file/<file_id>', methods=['POST'])
def get_drive_file(file_id):
    try:
        credentials_data = request.get_json()
        credentials = get_drive_credentials(credentials_data)
        if not credentials:
            return jsonify({'error': 'Not authenticated'}), 401
                
        service = build('drive', 'v3', credentials=credentials)
        file_content = service.files().get_media(fileId=file_id).execute()
        
        summary = process_document(file_content)
        return jsonify({
            'status': 'success',
            'summary': summary
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Processing error: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)