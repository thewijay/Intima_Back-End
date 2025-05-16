# 🐳 Intima Backend – Dockerized Development Setup

Welcome to the Intima backend project! This guide will help you get the development environment up and running using **Docker**.

---

## 🛠️ Prerequisites

Make sure you have the following installed:

- [Docker](https://www.docker.com/products/docker-desktop)
- Git

---

## 📦 Project Structure (Simplified)

Intima_Back-End/
│
├── backend/ # Django project
│ ├── Intima_BackEnd/
│ └── ...
├── .env.dev # Development environment variables
├── Dockerfile # Backend Docker build
├── docker-compose.yml # Compose setup
└── requirements.txt # Python dependencies

---

## 🚀 Setup Guide (Step-by-Step)

### 1. Clone the Repository

```bash
git clone https://github.com/thewijay/Intima_Back-End.git
cd Intima_Back-End
```

---

### 2. Add your .env.dev to the project folder

---

### 3. Start the Containers

This command will build the images and start the containers:
```bash
docker compose up -d
```

---

### 4. Login to the main container's bash

```bash
docker exec -it intima_back-end-web-1 bash 
```

---

### 5. Run migrations
```bash
python manage.py migrate
```

---

### 6. Create a Superuser

```bash
python manage.py createsuperuser
```
give your creditials and create a super user.
---

### 7. Access the App

Admin Panel: http://localhost:8000/admin/



