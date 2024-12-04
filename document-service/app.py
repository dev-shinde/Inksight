# In document-service/app.py
import os
from dotenv import load_dotenv
from pathlib import Path
from flask import Flask, request, jsonify
from anthropic import Anthropic, APIError
import base64
import io
from pdf2image import convert_from_bytes
from PIL import Image

# Get path to .env file which is one level up
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)  # Load .env from parent directory

# Check if API key exists
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
   raise ValueError("ANTHROPIC_API_KEY environment variable is not set!")

# Initialize Anthropic client
try:
   anthropic = Anthropic(api_key=api_key)
except Exception as e:
   print(f"Failed to initialize Anthropic client: {str(e)}")
   raise

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
   return jsonify({
       "status": "healthy", 
       "service": "document",
       "api_key_present": bool(api_key)
   }), 200

@app.route('/upload', methods=['POST'])
def upload_file():
   try:
       if 'file' not in request.files:
           return jsonify({'status': 'error', 'message': 'No file provided'}), 400
       
       file = request.files['file']
       if file.filename == '':
           return jsonify({'status': 'error', 'message': 'No file selected'}), 400

       print(f"API Key present: {bool(api_key)}")
       print("Starting PDF conversion...")
       
       # Convert PDF to image
       images = convert_from_bytes(file.read())
       if not images:
           return jsonify({'status': 'error', 'message': 'Failed to convert PDF'}), 500
       
       first_page = images[0]
       print("PDF converted to image successfully")

       # Convert image to base64
       print("Converting image to base64...")
       img_byte_arr = io.BytesIO()
       first_page.save(img_byte_arr, format='PNG')
       img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
       print("Image converted to base64 successfully")

       try:
           print("Sending request to Anthropic API...")
           message = anthropic.messages.create(
               model="claude-3-sonnet-20240229",
               max_tokens=1024,
               messages=[{
                   "role": "user",
                   "content": [
                       {
                           "type": "text",
                           "text": "Please provide a summary of this document in 2-3 big paragraph."
                       },
                       {
                           "type": "image",
                           "source": {
                               "type": "base64",
                               "media_type": "image/png",
                               "data": img_base64
                           }
                       }
                   ]
               }]
           )
           print("Successfully received response from Anthropic")
           return jsonify({
               'status': 'success',
               'summary': message.content[0].text
           })
       except APIError as e:
           print(f"Anthropic API Error: {str(e)}")
           return jsonify({
               'status': 'error',
               'message': f'API Error: {str(e)}'
           }), 500
       except Exception as e:
           print(f"Unexpected error in Anthropic API call: {str(e)}")
           return jsonify({
               'status': 'error',
               'message': f'Unexpected error: {str(e)}'
           }), 500

   except Exception as e:
       print(f"Error processing file: {str(e)}")
       return jsonify({
           'status': 'error',
           'message': f'Processing error: {str(e)}'
       }), 500

if __name__ == '__main__':
   # Print the environment info at startup
   print(f"Starting document service...")
   print(f"Environment variables loaded from: {env_path}")
   print(f"API key present: {bool(api_key)}")
   app.run(host='0.0.0.0', port=5003)