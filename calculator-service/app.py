from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from utils import process_image

load_dotenv()
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "calculator"}), 200

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({
                'status': 'error',
                'message': 'No image data provided'
            }), 400

        result = process_image(data['image'])
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
