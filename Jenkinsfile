pipeline {
    agent any
    environment {
        DOCKERHUB_CREDS = credentials('dockerhub-creds')  // Ensure you added these credentials in Jenkins
    }
    stages {
        // Stage 1: Clone repository
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/yazid212/appdev.git'
            }
        }

        // Stage 2: Run tests (replace with your test command)
        stage('Test') {
            steps {
                sh 'python -m pytest tests/'  // Example for Python
            }
        }

        // Stage 3: Build Docker image
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("yourdockerhub/todo-app:latest")
                }
            }
        }

        // Stage 4: Push to DockerHub
        stage('Push to DockerHub') {
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-creds') {
                        docker.image("yourdockerhub/todo-app:latest").push()
                    }
                }
            }
        }

        // Stage 5: Deploy to Kubernetes
        stage('Deploy to K8s') {
            steps {
                sh 'kubectl apply -f kubernetes/deployment.yaml'
                sh 'kubectl apply -f kubernetes/service.yaml'
            }
        }
    }
    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed! Check logs.'
        }
    }
}
