from flask import Flask, render_template, jsonify, request
import os
from dotenv import load_dotenv
import requests

load_dotenv()
app = Flask(__name__)

CALCULATOR_SERVICE_URL = os.getenv('CALCULATOR_SERVICE_URL', 'http://calculator-service:5002')
API_GATEWAY_URL = os.getenv('API_GATEWAY_URL', 'http://api-gateway:5000/upload')

# API_GATEWAY_URL = 'http://api-gateway:5000/upload'

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "frontend"}), 200

@app.route('/')
def home():
    return render_template('welcome.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Forward the request to calculator service
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
    file = request.files.get('file')
    if not file:
        return jsonify({'status': 'error', 'message': 'No file provided'}), 400

    # Forward the file to the API Gateway
    files = {'file': (file.filename, file.read(), file.content_type)}
    response = requests.post(API_GATEWAY_URL, files=files)
    return jsonify(response.json())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

