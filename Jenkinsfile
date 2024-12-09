pipeline {
    agent any
    
    stages {
        stage('Clone Repository') {
            steps {
                git 'https://github.com/dev-shinde/Inksight.git'
            }
        }
        
        stage('Build and Push Docker Images') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'DockerHubCred', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                    sh """
                        echo \$DOCKER_PASSWORD | docker login -u \$DOCKER_USERNAME --password-stdin
                        
                        cd api-gateway
                        docker build -t devz19/inksight-api-gateway:latest .
                        docker push devz19/inksight-api-gateway:latest
                        cd ..
                        
                        cd calculator-service
                        docker build -t devz19/inksight-calculator:latest .
                        docker push devz19/inksight-calculator:latest
                        cd ..
                        
                        cd document-service
                        docker build -t devz19/inksight-document:latest .
                        docker push devz19/inksight-document:latest
                        cd ..
                        
                        cd frontend-service
                        docker build -t devz19/inksight-frontend:latest .
                        docker push devz19/inksight-frontend:latest
                        cd ..
                        
                        docker logout
                    """
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(credentialsId: 'kubernetes_config', variable: 'KUBECONFIG')]) {
                    sh """
                        kubectl create namespace inksight --dry-run=client -o yaml | kubectl apply -f -
                        
                        kubectl apply -f k8/config/
                        kubectl apply -f k8/api-gateway/
                        kubectl apply -f k8/calculator/
                        kubectl apply -f k8/document/
                        kubectl apply -f k8/frontend/
                        kubectl apply -f k8/ingress/
                    """
                }
            }
        }
    }
    
    post {
        success {
            echo 'Successfully deployed InkSight!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}