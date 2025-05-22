# 📝 Todo App 
*A containerized Flask application with Kubernetes deployment and CI/CD pipeline.*  

![Demo](https://via.placeholder.com/800x400?text=Todo+App+Demo) *(Replace with a real screenshot later)*  
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-purple)
![Docker](https://img.shields.io/badge/Docker-✓-lightblue)
![Kubernetes](https://img.shields.io/badge/Kubernetes-✓-326CE5)

---

## 🚀 Features
✅ **CRUD Operations**  
✔️ Add, view, complete, and delete tasks  
✔️ SQLite database with Flask backend  
✔️ Dockerized for easy deployment  
✔️ Kubernetes-ready with `k8s/` configs  
✔️ Jenkins CI/CD pipeline  

---

## 🛠️ Tech Stack
| Category      | Technologies                      |
|---------------|-----------------------------------|
| **Backend**   | Python 3.12, Flask                |
| **Frontend**  | HTML5, CSS3,                      |
| **Database**  | SQLite                            |
| **DevOps**    | Docker, Kubernetes, Jenkins       |

---

## 📂 Project Structure
```bash
.
├── k8s/                   # Kubernetes configs
│   ├── deployment.yaml
│   ├── service.yaml
│   └── pvc.yaml
├── static/                # CSS/JS
├── templates/             # Flask HTML templates
├── tests/                 # Unit tests
├── Dockerfile             # Container setup
├── Jenkinsfile            # CI/CD pipeline
└── app.py                 # Main Flask app
⚡ Quick Start
Prerequisites
Python 3.12+

Docker

Kubernetes (minikube for local testing)

Jenkins (optional)

Local Run
bash
git clone https://github.com/yazid212/appdev.git
cd appdev
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run
Access: http://localhost:5000

Docker Build & Run
bash
docker build -t todo-app .
docker run -p 5000:5000 todo-app
☸️ Kubernetes Deployment
bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
(Ensure your cluster is running!)

🔄 CI/CD Pipeline (Jenkins)
Pipeline stages defined in Jenkinsfile:

Build → Test → Dockerize → Deploy to K8s

🧪 Testing
Run unit tests:

bash
python -m unittest discover tests
