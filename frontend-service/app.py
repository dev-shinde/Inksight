from flask import Flask, render_template, jsonify, request, session, redirect
import os
from dotenv import load_dotenv
import requests
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

CALCULATOR_SERVICE_URL = os.getenv('CALCULATOR_SERVICE_URL', 'http://calculator-service:5002')

@app.route('/health')
def health_check():
   return jsonify({"status": "healthy", "service": "frontend"})

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
           json=request.get_json()
       )
       return response.json(), response.status_code
   except Exception as e:
       logger.error(f"Calculator error: {str(e)}")
       return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5001)