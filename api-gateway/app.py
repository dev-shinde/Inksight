from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

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

@app.route('/<service>/<path:path>', methods=['GET', 'POST'])
def gateway(service, path):
    if service not in SERVICES:
        return jsonify({"error": "Service not found"}), 404
    
    try:
        service_url = f"{SERVICES[service]}/{path}"
        response = requests.request(
            method=request.method,
            url=service_url,
            headers={key: value for key, value in request.headers if key != 'Host'},
            params=request.args,
            json=request.get_json() if request.is_json else None,
            data=request.form if request.form else None,
            files=request.files if request.files else None,
            cookies=request.cookies,
            allow_redirects=False
        )
        
        return response.content, response.status_code, response.headers.items()
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)