from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from anthropic import Anthropic
from utils import process_document
from pdf2image import convert_from_bytes
import base64
import io

load_dotenv()
app = Flask(__name__)
anthropic = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

@app.route('/health')
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

        # Initialize Anthropic client
        anthropic = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

        # Convert PDF to image
        images = convert_from_bytes(file.read())
        first_page = images[0]
        
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        img_base64 = base64.b64encode(img_byte_arr).decode('utf-8')
        
        message = anthropic.messages.create(
            model="claude-3-sonnet-20240229",
         max_tokens=1024,                           
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please provide a summary of this document in 2-3 big paragraph."  # Simplified prompt 
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
        
        return jsonify({
            'status': 'success',
            'summary': message.content[0].text
        })
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Processing error: {str(e)}'
        }), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
