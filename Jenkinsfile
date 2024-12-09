pipeline {
    agent any
    
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
        
        stage('Deploy using Ansible') {
            steps {
                sh 'ansible-playbook -i inventory.yaml deploy-k8s.yaml'
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