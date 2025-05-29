## 💡 Project Overview

**Intima** is an AI-Based Sexual and Wellness Healthcare Assistant developed to help individuals confidently discuss and explore sensitive health concerns related to sexual health, gynecology, and wellness. This backend service powers intelligent document retrieval and chat-based interaction, making healthcare information more accessible and private.

This project is developed as part of the **Capstone Project** in the 2nd year, 2nd semester by a group of undergraduate students at the [Sabaragamuwa University of Sri Lanka](https://sab.ac.lk/).

---

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
git checkout Dev
```

---

### 2. Add your .env.dev to the project folder

---

### 3. Add your local ip address to these files

- .env.dev -> DJANGO_ALLOWED_HOSTS -> add yourip after a comma
- settings.py -> CORS_ALLOWED_ORIGINS -> "yourip:8081,"
- In frontend -> hooks/api/auth.ts -> onst API_BASE_URL = 'http://yourip:8000/api';

### 3. Start the Containers

This command will build the images and start the containers:

```bash
docker compose --env-file .env.dev up -d
```

---

### 4. Login to the django_app container's bash

```bash
docker exec -it django_app bash
```

---

### 5. Create a Superuser

```bash
python manage.py createsuperuser
```

#### give your creditials and create a super user.

After you can exit from the django_app container using this:
```
exit
```

---

### 6. Access the App

Admin Panel: http://localhost:8000/admin/

---

## Useful commands:

### In Backend Terminal
```
# start your apps
docker compose --env-file .env.dev up -d

# Restart your apps
docker compose restart

# Rebuild to apply changes
docker compose --env-file .env.dev up -d --build

# To delete all image cache
docker builder prune
```

### In django_app container

#### Documents managing
```
# Process newly added documents
python manage.py process_documents

# List all processed documents
python manage.py list_documents

# Delete all documents
python manage.py delete_all_documents --confirm

# Delete a single document with UUID
python manage.py delete_document <uuid>

# Delete multiple documents with UUID
python manage.py delete_document <uuid> <uuid>
```

#### Chat Testing
```
# Test the chat API
curl -X POST http://localhost:8000/ai/chat/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic of document A?", "limit": 2, "model": "gpt-4o-mini"}'

curl -X POST http://localhost:8000/ai/search/ \
  -H "Content-Type: application/json" \
  -d '{"question": "machine learning", "limit": 5}'

# Test with gpt-4o-mini (default)
curl -X POST http://localhost:8000/ai/chat/ \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain AI in healthcare", "model": "gpt-4o-mini"}'

# Check system health
curl -X GET http://localhost:8000/ai/health/

# Get document statistics
curl -X GET http://localhost:8000/ai/stats/
```

---

## 🎓 Academic Acknowledgment

This project is a proud outcome of our **Capstone Project** module at the  
🌱 **[Sabaragamuwa University of Sri Lanka](https://sab.ac.lk/)** – where creativity meets real-world impact.

We thank our mentors and the Faculty of Computing for the continued support and academic inspiration.

