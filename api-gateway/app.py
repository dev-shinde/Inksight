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
    'document': os.getenv('DOCUMENT_SERVICE_URL', 'http://document-service:5003'),

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
@app.route('/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    try:
        # Default to frontend service for base routes
        service = 'frontend'
        service_url = SERVICES['frontend']

        # Route API calls to specific services
        if path.startswith('api/'):
            service_parts = path.split('/')
            service = service_parts[1]
            path = '/'.join(service_parts[2:])
            if service not in SERVICES:
                return jsonify({"error": "Service not found"}), 404
            service_url = SERVICES[service]

        target_url = f"{service_url}/{path}"
        logger.info(f"Forwarding request to: {target_url}")

        kwargs = {
            'method': request.method,
            'url': target_url,
            'headers': {key: value for key, value in request.headers if key != 'Host'},
            'params': request.args,
            'allow_redirects': False,
            'timeout': 30
        }

        # Handle different types of request data
        if request.is_json:
            kwargs['json'] = request.get_json()
        elif request.form:
            kwargs['data'] = request.form
        if request.files:
            kwargs['files'] = request.files

        response = requests.request(**kwargs)
        return response.content, response.status_code, response.headers.items()

    except requests.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Service temporarily unavailable"
        }), 503



@app.route('/api/<service>/<path:path>', methods=['GET', 'POST'])
def service_gateway(service, path):
    if service not in SERVICES:
        return jsonify({"error": "Service not found"}), 404
    
    try:
        service_url = f"{SERVICES[service]}/{path}"
        
        # Forward the request to the appropriate service
        response = requests.request(
            method=request.method,
            url=service_url,
            params=request.args,
            headers={key: value for key, value in request.headers if key != 'Host'},
            cookies=request.cookies,
            data=request.get_data() if request.method == 'POST' else None,
            allow_redirects=False
        )
        
        # Handle redirects
        if response.status_code in [301, 302, 303, 307, 308]:
            return redirect(response.headers['Location'])
            
        return response.content, response.status_code, response.headers.items()
    except requests.RequestException as e:
        print(f"Gateway error: {str(e)}")  # For debugging
        return jsonify({
            "error": f"Service request failed: {str(e)}"
        }), 503

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