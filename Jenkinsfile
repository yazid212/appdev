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
      }
    }

    stage('Run Unit Tests') {
      steps {
        sh 'python3 -m venv venv'
        sh '''
          . venv/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt pytest flask==2.0.1
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
    r = client.get('/')
    assert r.status_code == 200
EOF
          fi
        '''
        sh '''
          . venv/bin/activate
          pytest -q
        '''
      }
    }

    stage('Build Docker Image') {
      steps {
        // Ensure /app/data exists inside the image
        sh "docker build -t ${DOCKER_HUB_REPO}:${IMAGE_TAG} \\
           --build-arg BUILDKIT_INLINE_CACHE=1 ."
        sh "docker images | grep ${DOCKER_HUB_REPO}"
      }
    }

    stage('Push to DockerHub') {
      steps {
        sh "echo ${DOCKER_HUB_CREDS_PSW} | docker login -u ${DOCKER_HUB_CREDS_USR} --password-stdin"
        sh "docker push ${DOCKER_HUB_REPO}:${IMAGE_TAG}"
        sh "docker push ${DOCKER_HUB_REPO}:latest"
        sh "docker logout"
      }
    }

    stage('Deploy to Kubernetes') {
      steps {
        withCredentials([file(credentialsId: 'kubeconfig-file', variable: 'KUBECONFIG')]) {
          sh '''
            set -e

            mkdir -p kubernetes

            # PVC
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

            # Deployment with proper volumeMount
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
        imagePullPolicy: IfNotPresent
        env:
        - name: DATABASE
          value: /app/data/todo.db
        ports:
        - containerPort: 5000
        volumeMounts:
        - name: todo-db-storage
          mountPath: /app/data
        readinessProbe:
          httpGet:
            path: /
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /
            port: 5000
          initialDelaySeconds: 15
          periodSeconds: 20
      volumes:
      - name: todo-db-storage
        persistentVolumeClaim:
          claimName: todo-db-pvc
EOF

            # Service
            cat > kubernetes/service.yaml << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: todo-app-service
spec:
  selector:
    app: todo-app
  type: NodePort
  ports:
    - port: 80
      targetPort: 5000
      nodePort: 31885
EOF

            # Replace placeholder & apply
            sed -i "s|PLACEHOLDER_IMAGE|${DOCKER_HUB_REPO}:${IMAGE_TAG}|g" kubernetes/deployment.yaml

            kubectl apply -f kubernetes/pvc.yaml
            kubectl apply -f kubernetes/deployment.yaml
            kubectl apply -f kubernetes/service.yaml

            # Wait for rollout
            kubectl rollout status deployment/todo-app-deployment --timeout=300s
          '''
        }
      }
    }
  }

  post {
    success {
      echo "✅ Deployment succeeded: ${DOCKER_HUB_REPO}:${IMAGE_TAG}"
    }
    failure {
      echo "❌ Deployment failed – dumping pod status and logs:"
      sh 'kubectl get pods -l app=todo-app -o wide || true'
      sh 'kubectl describe pods -l app=todo-app || true'
      sh 'kubectl logs -l app=todo-app || true'
    }
    always {
      echo "🧹 Cleaning up local artifacts…"
      sh 'docker image prune -f || true'
      sh 'rm -rf venv || true'
    }
  }
}