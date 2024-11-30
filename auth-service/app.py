from flask import Flask, request, jsonify
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# OAuth 2.0 Configuration
GOOGLE_CLIENT_CONFIG = {
    "web": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")]
    }
}

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "auth"}), 200

@app.route('/auth/google/init', methods=['POST'])
def init_google_auth():
    try:
        flow = Flow.from_client_config(
            GOOGLE_CLIENT_CONFIG,
            scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        auth_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true"
        )
        return jsonify({
            "status": "success",
            "auth_url": auth_url,
            "state": state
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/auth/google/callback', methods=['POST'])
def google_auth_callback():
    try:
        code = request.json.get("code")
        flow = Flow.from_client_config(
            GOOGLE_CLIENT_CONFIG,
            scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        return jsonify({
            "status": "success",
            "token": credentials.token,
            "refresh_token": credentials.refresh_token
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)