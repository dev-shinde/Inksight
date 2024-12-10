# InkSight: AI-Powered Mathematical Recognition & Document Analysis

## Overview
InkSight is a microservices-based application that combines intelligent mathematical expression recognition and document analysis capabilities. The system utilizes Google's Gemini API for mathematical expression interpretation and Claude AI for document summarization.

## Features
- Real-time handwritten mathematical expression recognition
- Interactive drawing canvas with color options
- Document upload and analysis with comprehensive summarization
- Microservices architecture for scalability
- Kubernetes orchestration with automated scaling
- CI/CD pipeline with Jenkins
- Secure configuration management with Ansible Vault

## Architecture
The application consists of four microservices:
- **API Gateway**: Routes requests and handles service orchestration
- **Calculator Service**: Processes mathematical expressions using Gemini AI
- **Document Service**: Analyzes documents using Claude AI
- **Frontend Service**: Provides user interface and drawing capabilities

## Technologies Used
- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **AI/ML**: Google Gemini API, Anthropic Claude API
- **DevOps**: Docker, Kubernetes, Jenkins, Ansible
- **Version Control**: Git, GitHub

## Setup and Installation
1. Clone the repository
```bash
git clone https://github.com/yourusername/InkSight.git
cd InkSight
```

2. Build Docker images
```bash
docker-compose build
```

3. Deploy to Kubernetes
```bash
ansible-playbook -i inventory ansible/deploy.yml --ask-vault-pass
```

## Environment Variables
Create a `.env` file with:
```
GEMINI_API_KEY=your_gemini_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
SECRET_KEY=your_secret_key
```

## Directory Structure
```
InkSight/
├── api-gateway/
├── calculator-service/
├── document-service/
├── frontend-service/
├── k8/
├── ansible/
├── jenkins/
└── docker-compose.yml
```

## API Documentation
### Calculator Service
- POST `/calculate`: Processes mathematical expressions
- GET `/health`: Service health check

### Document Service
- POST `/upload`: Analyzes uploaded documents
- GET `/health`: Service health check

## CI/CD Pipeline
The project uses Jenkins for continuous integration and deployment:
1. Automatic builds on code push
2. Docker image creation and push
3. Kubernetes deployment with rolling updates
4. Automated testing and verification

## Monitoring and Logging
- Kubernetes pod health monitoring
- Service-level logging with date-based organization
- Performance metrics tracking
- Auto-scaling based on CPU usage

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Open a pull request

## License
This project is licensed under the MIT License

## Authors
- Dev Shinde

## Acknowledgments
- Google Cloud Platform for Gemini API
- Anthropic for Claude API
- Open source community

## Contact
For any queries, reach out to [shindedev64@gmail.com](mailto:shindedev64@gmail.com)