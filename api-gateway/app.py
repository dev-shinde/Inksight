from flask import Flask, request, jsonify, send_from_directory
import requests
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
app = Flask(__name__)

SERVICES = {
    'frontend': os.getenv('FRONTEND_SERVICE_URL', 'http://frontend-service:5001'),
    'calculator': os.getenv('CALCULATOR_SERVICE_URL', 'http://calculator-service:5002'),
    'document': os.getenv('DOCUMENT_SERVICE_URL', 'http://document-service:5003')
}

@app.route('/health', methods=['GET'])
def health_check():
    service_status = {}
    for service, url in SERVICES.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            service_status[service] = "healthy" if response.status_code == 200 else "unhealthy"
        except:
            service_status[service] = "unreachable"
    
    return jsonify({
        "status": "healthy",
        "service": "gateway",
        "dependencies": service_status
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """Handle all frontend routes"""
    try:
        frontend_url = f"{SERVICES['frontend']}/{path}"
        response = requests.request(
            method=request.method,
            url=frontend_url,
            headers={key: value for key, value in request.headers if key != 'Host'},
            params=request.args,
            cookies=request.cookies,
            allow_redirects=False
        )
        return response.content, response.status_code, dict(response.headers)
    except Exception as e:
        logger.error(f"Frontend routing error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/<service>/<path:path>', methods=['GET', 'POST'])
def service_gateway(service, path):
    """Handle service-specific routes"""
    if service not in SERVICES:
        return jsonify({"error": "Service not found"}), 404
    
    try:
        service_url = f"{SERVICES[service]}/{path}"
        logger.info(f"Forwarding request to: {service_url}")

        # Prepare the request
        kwargs = {
            'method': request.method,
            'url': service_url,
            'headers': {key: value for key, value in request.headers if key != 'Host'},
            'params': request.args,
            'cookies': request.cookies,
            'timeout': 30
        }

        # Handle different types of request data
        if request.is_json:
            kwargs['json'] = request.get_json()
        elif request.form:
            kwargs['data'] = request.form
        elif request.files:
            kwargs['files'] = request.files

        # Make the request
        response = requests.request(**kwargs)
        
        return response.content, response.status_code, response.headers.items()
    except requests.RequestException as e:
        logger.error(f"Service request failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Service request failed: {str(e)}"
        }), 503
    except Exception as e:
        logger.error(f"Gateway error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files from frontend service"""
    try:
        response = requests.get(f"{SERVICES['frontend']}/static/{filename}")
        if response.status_code == 200:
            return response.content, 200, {'Content-Type': response.headers['Content-Type']}
        return "File not found", 404
    except Exception as e:
        logger.error(f"Static file error: {str(e)}")
        return "Error serving static file", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)