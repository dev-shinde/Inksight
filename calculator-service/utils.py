import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import base64
import io

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def process_image(image_data):
    try:
        # Process base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        img = Image.open(io.BytesIO(image_bytes))
        
        # Initialize Gemini model
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        
        prompt = (
            "You have been given an image with mathematical expressions to solve. "
            "Return the answer in format: [{'expr': expression, 'result': calculated_answer, "
            "'explanation': 'Step by step solution'}]. For example: [{'expr': '2+2', "
            "'result': '4', 'explanation': 'Addition of 2 and 2'}]"
        )
        
        response = model.generate_content([prompt, img])
        
        try:
            # Clean and parse the response
            import json
            clean_text = response.text.strip()
            if clean_text.startswith('```') and clean_text.endswith('```'):
                clean_text = clean_text[3:-3]
            if clean_text.startswith('json'):
                clean_text = clean_text[4:]
            result = json.loads(clean_text.replace("'", '"'))
            return result
        except Exception as e:
            print(f"Parse error: {e}")
            return [{"expr": "Error", "result": "Could not process", "explanation": str(e)}]
            
    except Exception as e:
        print(f"Analysis error: {e}")
        return [{"expr": "Error", "result": "Processing failed", "explanation": str(e)}]