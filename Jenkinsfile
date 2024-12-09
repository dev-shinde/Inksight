pipeline {
    agent any
    
    environment {
        VAULT_PASS_FILE = credentials('vault-pass')
    }
    
    stages {
        stage('Clone Repository') {
            steps {
                git credentialsId: 'gitconnect',
                    url: 'https://github.com/dev-shinde/Inksight.git',
                    branch: 'main'
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

        stage('Start Minikube') {
            steps {
                sh '''
                    minikube status || minikube start
                    minikube status
                '''
            }
        }
        
        stage('Deploy with Ansible') {
            steps {
                script {
                    withCredentials([file(credentialsId: 'vault-pass', variable: 'VAULT_PASS_FILE')]) {
                        sh """
                            # Verify vault file exists
                            ls -la vars/secrets.yml
                            
                            # Run ansible playbook with vault
                            ansible-playbook deploy-k8s.yaml --vault-password-file=\$VAULT_PASS_FILE
                        """
                    }
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