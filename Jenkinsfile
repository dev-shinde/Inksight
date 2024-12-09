pipeline {
    agent any
    
    environment {
        DOCKER_HUB = credentials('docker_hub')
        KUBE_CONFIG = credentials('kubernetes_config')
    }
    
    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/dev-shinde/Inksight.git'
            }
        }
        
        stage('Build Docker Images') {
            steps {
                script {
                    sh '''
                        cd api-gateway
                        docker build -t devz19/inksight-api-gateway:latest .
                        cd ../calculator-service
                        docker build -t devz19/inksight-calculator:latest .
                        cd ../document-service
                        docker build -t devz19/inksight-document:latest .
                        cd ../frontend-service
                        docker build -t devz19/inksight-frontend:latest .
                    '''
                }
            }
        }
        
        stage('Push to DockerHub') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'docker_hub', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        sh '''
                            echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
                            
                            docker push devz19/inksight-api-gateway:latest
                            docker push devz19/inksight-calculator:latest
                            docker push devz19/inksight-document:latest
                            docker push devz19/inksight-frontend:latest
                        '''
                    }
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            steps {
                script {
                    withCredentials([file(credentialsId: 'kubernetes_config', variable: 'KUBECONFIG')]) {
                        sh '''
                            # Create namespace if not exists
                            kubectl create namespace inksight --dry-run=client -o yaml | kubectl apply -f -
                            
                            # Apply configurations in order
                            kubectl apply -f k8/config/
                            kubectl apply -f k8/api-gateway/
                            kubectl apply -f k8/calculator/
                            kubectl apply -f k8/document/
                            kubectl apply -f k8/frontend/
                            kubectl apply -f k8/ingress/
                            
                            # Verify deployments
                            kubectl rollout status deployment/api-gateway -n inksight
                            kubectl rollout status deployment/calculator-service -n inksight
                            kubectl rollout status deployment/document-service -n inksight
                            kubectl rollout status deployment/frontend -n inksight
                        '''
                    }
                }
            }
        }
    }
    
    post {
        always {
            script {
                sh '''
                    docker logout || true
                    docker system prune -f || true
                '''
            }
        }
        success {
            echo 'Successfully deployed InkSight to Kubernetes!'
        }
        failure {
            echo 'Deployment failed! Check logs for details.'
        }
    }
}