from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

SERVICES = {
    'frontend': os.getenv('FRONTEND_SERVICE_URL', 'http://frontend-service:5001'),
    'calculator': os.getenv('CALCULATOR_SERVICE_URL', 'http://calculator-service:5002')
}

@app.route('/health', methods=['GET'])
def health_check():
    services_health = {}
    for service, url in SERVICES.items():
        try:
            response = requests.get(f"{url}/health")
            services_health[service] = "healthy" if response.status_code == 200 else "unhealthy"
        except:
            services_health[service] = "unreachable"
    
    return jsonify({
        "status": "healthy",
        "services": services_health
    })

@app.route('/<service>/<path:path>', methods=['GET', 'POST'])
def proxy(service, path):
    if service not in SERVICES:
        return jsonify({"error": "Service not found"}), 404
    
    try:
        response = requests.request(
            method=request.method,
            url=f"{SERVICES[service]}/{path}",
            headers={k: v for k, v in request.headers if k != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )
        
        return response.content, response.status_code, dict(response.headers)
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
