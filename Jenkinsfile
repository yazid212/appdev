pipeline {
    agent any

    triggers {
        githubPush()
        pollSCM('H/5 * * * *')
    }

    environment {
        DOCKER_HUB_REPO  = "cryptpi/todo-app"
        DOCKER_HUB_CREDS = credentials('dockerhub-creds')
        IMAGE_TAG        = "v${BUILD_NUMBER}"
    }

    stages {
        stage('Clone Repository') {
            steps {
                cleanWs()
                git branch: 'main',
                    url: 'https://github.com/yazid212/appdev.git',
                    credentialsId: 'github-credentials'
                sh 'git log -1'
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh 'python3 -m venv venv'

                sh '''
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install flask==2.0.1
                    pip install pytest
                    pip install -r requirements.txt
                '''

                sh 'mkdir -p tests'

                sh '''
                if [ ! -f tests/test_app.py ]; then
                    cat > tests/test_app.py << 'EOF'
from app import app
import pytest

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
EOF
                fi
                '''

                sh '''
                    . venv/bin/activate
                    python -m pytest tests/
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${DOCKER_HUB_REPO}:${IMAGE_TAG} -t ${DOCKER_HUB_REPO}:latest ."
                sh 'docker images | grep ${DOCKER_HUB_REPO}'
            }
        }

        stage('Push to DockerHub') {
            steps {
                sh "echo ${DOCKER_HUB_CREDS_PSW} | docker login -u ${DOCKER_HUB_CREDS_USR} --password-stdin"
                sh "docker push ${DOCKER_HUB_REPO}:${IMAGE_TAG}"
                sh "docker push ${DOCKER_HUB_REPO}:latest"
                sh 'docker logout'
            }
        }

        stage('Setup Kubernetes Config') {
            steps {
                withCredentials([file(credentialsId: 'kubeconfig-file', variable: 'KUBECONFIG')]) {
                    sh 'kubectl config current-context'
                    sh 'kubectl cluster-info'
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    kubectl config current-context
                    kubectl cluster-info
                    kubectl get nodes
                '''

                sh 'mkdir -p kubernetes'

                sh '''
                if [ ! -f kubernetes/deployment.yaml ]; then
                    cat > kubernetes/deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-app-deployment
  labels:
    app: todo-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-app
  template:
    metadata:
      labels:
        app: todo-app
    spec:
      containers:
      - name: todo-app
        image: PLACEHOLDER_IMAGE
        ports:
        - containerPort: 5000
        volumeMounts:
        - name: todo-db-storage
          mountPath: /app/data
      volumes:
      - name: todo-db-storage
        persistentVolumeClaim:
          claimName: todo-db-pvc
EOF
                fi
                '''

                sh '''
                if [ ! -f kubernetes/service.yaml ]; then
                    cat > kubernetes/service.yaml << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: todo-app-service
spec:
  selector:
    app: todo-app
  ports:
  - port: 80
    targetPort: 5000
  type: NodePort
EOF
                fi
                '''

                sh '''
                if [ ! -f kubernetes/pvc.yaml ]; then
                    cat > kubernetes/pvc.yaml << 'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: todo-db-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
EOF
                fi
                '''

                sh "sed -i 's|PLACEHOLDER_IMAGE|${DOCKER_HUB_REPO}:${IMAGE_TAG}|g' kubernetes/deployment.yaml"

                sh '''
                    kubectl apply -f kubernetes/pvc.yaml
                    kubectl apply -f kubernetes/deployment.yaml
                    kubectl apply -f kubernetes/service.yaml
                '''

                sh '''
                    kubectl get pods -l app=todo-app
                    kubectl get services todo-app-service
                '''

                sh '''
                    kubectl rollout status deployment/todo-app-deployment --timeout=300s
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
            echo "Application deployed with image: ${DOCKER_HUB_REPO}:${IMAGE_TAG}"

            script {
                try {
                    def serviceInfo = sh(
                        script: 'kubectl get service todo-app-service -o jsonpath="{.spec.ports[0].nodePort}"',
                        returnStdout: true
                    ).trim()
                    echo "Application accessible on NodePort: ${serviceInfo}"
                } catch (Exception e) {
                    echo "Could not retrieve service port information: ${e.getMessage()}"
                }
            }
        }

        failure {
            echo 'Pipeline failed!'

            echo 'Recent Docker images:'
            sh 'docker images | head -10 || true'

            echo 'Kubernetes pod status:'
            sh 'kubectl get pods -l app=todo-app || true'

            echo 'Kubernetes events:'
            sh 'kubectl get events --sort-by=.metadata.creationTimestamp | tail -10 || true'
        }

        always {
            sh "docker rmi ${DOCKER_HUB_REPO}:${IMAGE_TAG} || true"
            sh "docker rmi ${DOCKER_HUB_REPO}:latest || true"
            sh 'rm -rf venv || true'
            sh 'docker image prune -f || true'
        }
    }
}
