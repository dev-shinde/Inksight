from pdf2image import convert_from_bytes
import io
import base64

def process_document(file, anthropic_client):
    try:
        # Convert PDF to image
        file_bytes = file.read()
        images = convert_from_bytes(file_bytes)
        first_page = images[0]
        
        # Convert to base64
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='PNG')
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        
        # Get summary from Claude
        message = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please provide a comprehensive summary of this document in two paragraphs."
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
