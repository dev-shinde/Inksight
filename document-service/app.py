from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from anthropic import Anthropic
from utils import process_document

load_dotenv()
app = Flask(__name__)
anthropic = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "document"}), 200

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file provided'
            }), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400

        summary = process_document(file, anthropic)
        return jsonify({
            'status': 'success',
            'summary': summary
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
