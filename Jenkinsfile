pipeline {
    agent any
    
    environment {
        VAULT_PASS_FILE = credentials('vault-pass')
        KUBECONFIG = "/tmp/kube_config_${BUILD_NUMBER}"
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

        stage('Setup Minikube') {
            steps {
                sh '''
                    # Stop and delete existing cluster if any
                    minikube stop || true
                    minikube delete || true
                    
                    # Start fresh cluster
                    minikube start --driver=docker \
                        --kubernetes-version=v1.31.0 \
                        --cpus=4 \
                        --memory=4096
                    
                    # Wait for cluster to be ready
                    minikube status
                    kubectl wait --for=condition=Ready node/minikube --timeout=300s
                '''
            }
        }

         stage('Setup Kubernetes') {
            steps {
                sh '''
                    # Start minikube if not running
                    minikube status || minikube start --driver=docker
                    
                    # Export minikube's kubectl config
                    minikube kubectl config view > ${KUBECONFIG}
                    
                    # Test connection
                    kubectl --kubeconfig=${KUBECONFIG} get nodes
                '''
            }
        }

        stage('Deploy with Ansible') {
            steps {
                script {
                    withCredentials([file(credentialsId: 'vault-pass', variable: 'VAULT_PASS_FILE')]) {
                        sh """
                            # Verify files
                            ls -la vars/secrets.yml
                            ls -la inventory
                            
                            # Run ansible with inventory
                            ansible-playbook deploy-k8s.yaml -i inventory --vault-password-file=\$VAULT_PASS_FILE
                        """
                    }
                }
            }
        }
    }
    
    post {

         always {
            sh """
                # Cleanup
                rm -f ${KUBECONFIG} || true
            """
        }
        success {
            echo 'Successfully deployed InkSight!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}