pipeline {
    agent any
    
    environment {
        DOCKER_HUB = credentials('docker_hub')
        KUBE_CONFIG = credentials('kubernetes_config')
    }
    
    stages {
        stage('Clone Repository') {
            steps {
                git 'https://github.com/dev-shinde/Inksight.git'
            }
        }
        
        stage('Build Docker Images') {
            parallel {
                stage('API Gateway') {
                    steps {
                        sh '''
                            cd api-gateway
                            docker build -t devz19/inksight-api-gateway:latest .
                        '''
                    }
                }
                
                stage('Calculator Service') {
                    steps {
                        sh '''
                            cd calculator-service
                            docker build -t devz19/inksight-calculator:latest .
                        '''
                    }
                }
                
                stage('Document Service') {
                    steps {
                        sh '''
                            cd document-service
                            docker build -t devz19/inksight-document:latest .
                        '''
                    }
                }
                
                stage('Frontend Service') {
                    steps {
                        sh '''
                            cd frontend-service
                            docker build -t devz19/inksight-frontend:latest .
                        '''
                    }
                }
            }
        }
        
        stage('Push to DockerHub') {
            steps {
                sh '''
                    echo $DOCKER_HUB_PSW | docker login -u $DOCKER_HUB_USR --password-stdin
                    
                    docker push devz19/inksight-api-gateway:latest
                    docker push devz19/inksight-calculator:latest
                    docker push devz19/inksight-document:latest
                    docker push devz19/inksight-frontend:latest
                '''
            }
        }
        
        stage('Deploy to Kubernetes') {
            steps {
                script {
                    sh '''
                        # Create namespace if not exists
                        kubectl create namespace inksight --dry-run=client -o yaml | kubectl apply -f -
                        
                        # Apply configurations in order
                        kubectl apply -f k8/config/
                        
                        # Deploy services
                        kubectl apply -f k8/api-gateway/
                        kubectl apply -f k8/calculator/
                        kubectl apply -f k8/document/
                        kubectl apply -f k8/frontend/
                        
                        # Apply ingress last
                        kubectl apply -f k8/ingress/
                        
                        # Wait for deployments
                        kubectl rollout status deployment/api-gateway -n inksight
                        kubectl rollout status deployment/calculator-service -n inksight
                        kubectl rollout status deployment/document-service -n inksight
                        kubectl rollout status deployment/frontend -n inksight
                    '''
                }
            }
        }
        
        stage('Verify Deployment') {
            steps {
                sh '''
                    echo "Checking deployments..."
                    kubectl get deployments -n inksight
                    
                    echo "Checking services..."
                    kubectl get services -n inksight
                    
                    echo "Checking pods..."
                    kubectl get pods -n inksight
                    
                    echo "Checking HPAs..."
                    kubectl get hpa -n inksight
                    
                    echo "Checking ingress..."
                    kubectl get ingress -n inksight
                '''
            }
        }
    }
    
    post {
        always {
            sh '''
                docker logout
                docker system prune -f
            '''
        }
        success {
            echo 'Successfully deployed InkSight to Kubernetes!'
        }
        failure {
            echo 'Deployment failed! Check logs for details.'
        }
    }
}