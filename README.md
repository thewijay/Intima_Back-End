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
docker compose up -d
```

---

### 4. Login to the djago_app container's bash

```bash
docker exec -it django_app bash
```

---

### 5. Create a Superuser

```bash
python manage.py createsuperuser
```

## give your creditials and create a super user.

---

### 6. Access the App

Admin Panel: http://localhost:8000/admin/

## You can exit from the main container using this:

```
exit
```

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
```
# Process newly added documents
python manage.py process_documents

# List all processed documents
python manage.py list_documents

# Delete all documents
python manage.py delete_all_documents --confirm

# Delete a single document with UUID
python manage.py delete_document 3776760f-90e1-41bf-bd10-d61c5951ef24

# Delete multiple documents with UUID
python manage.py delete_document 3776760f-90e1-41bf-bd10-d61c5951ef24 b5127c29-dc62-42b7-b683-bb5505d84f86
```