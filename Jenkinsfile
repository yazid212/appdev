pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/yazid212/appdev.git'
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("yourdockerhub/todo-app:latest")
                }
            }
        }
    }
}