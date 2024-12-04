from pdf2image import convert_from_bytes
import io
import base64
from anthropic import Anthropic
import os
from googleapiclient.discovery import build

def process_document(file):
    try:
        # Initialize Anthropic client without proxies
        anthropic = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

        # Convert PDF to image
        images = convert_from_bytes(file.read())
        first_page = images[0]
        
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='PNG')
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        
        # Create message with Claude
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
        
        return message.content[0].text
    except Exception as e:
        raise Exception(f"Document processing error: {str(e)}")

def process_drive_file(file_id, credentials):
    try:
        service = build('drive', 'v3', credentials=credentials)
        
        file_content = service.files().get_media(fileId=file_id).execute()
        
        # Convert PDF to image
        images = convert_from_bytes(file_content)
        if not images:
            return {
                'status': 'error',
                'message': 'Failed to convert PDF'
            }
            
        first_page = images[0]
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='PNG')
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        
        anthropic = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        message = anthropic.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
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
        
        return {
            'status': 'success',
            'summary': message.content[0].text
        }
    except Exception as e:
        raise Exception(f"Drive file processing error: {str(e)}")