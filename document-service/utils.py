from anthropic import Anthropic
import os
from pdf2image import convert_from_bytes
import base64
import io
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

def process_document(file_content):
    """Process document and return summary using Anthropic's Claude"""
    try:
        # Convert PDF to image
        images = convert_from_bytes(file_content)
        if not images:
            raise Exception("Failed to convert PDF to image")
            
        first_page = images[0]
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='PNG')
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        
        # Initialize Anthropic client
        anthropic = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        message = anthropic.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            timeout=70,  # Add timeout
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please provide a comprehensive technical summary of this document in two paragraphs."
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
        
        return message.content[0].text
    except Exception as e:
        raise Exception(f"Document processing failed: {str(e)}")

def get_drive_credentials(credentials_data):
    """Convert credentials dictionary to Credentials object and refresh if needed"""
    try:
        if credentials_data:
            credentials = Credentials(**credentials_data)
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            return credentials
        return None
    except Exception:
        return None