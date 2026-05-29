# FEVA

Modern full-stack platform built for scalable web applications.

FEVA combines a powerful backend, modern frontend architecture, realtime capabilities, and production-ready infrastructure into one developer-friendly project.

---

# Overview

FEVA is designed to provide:

* Fast and scalable backend APIs
* Modern responsive frontend
* Secure authentication system
* Realtime communication
* Background task processing
* Production-ready deployment architecture

---

# Tech Stack

| Layer            | Technology      |
| ---------------- | --------------- |
| Frontend         | Next.js / React |
| Backend          | Django + DRF    |
| Database         | PostgreSQL      |
| Cache & Queue    | Redis           |
| Realtime         | WebSockets      |
| Background Jobs  | Celery          |
| Containerization | Docker          |
| Authentication   | JWT             |

---

# Project Structure

```bash
FEVA/
├── backend/           # Django backend
├── frontend/          # Next.js frontend
├── mobile/            # Mobile app (optional)
├── docker-compose.yml
├── README.md
└── .env.example
```

---

# Features

* Multi-user authentication
* REST API architecture
* Realtime updates
* Role-based access control
* Responsive dashboard
* Background task processing
* Scalable deployment setup
* Docker development environment

---

# Getting Started

## Clone the repository

```bash
git clone https://github.com/Dagolde/Feva-proje.git
cd Feva-proje
```

---

# Environment Variables

Create your environment file:

```bash
cp .env.example .env
```

Example configuration:

```env
SECRET_KEY=your_secret_key
DEBUG=True

DATABASE_URL=postgres://user:password@localhost:5432/feva
REDIS_URL=redis://localhost:6379/0

JWT_SECRET=your_jwt_secret
```

---

# Run With Docker

```bash
docker-compose up --build
```

---

# Backend Setup

```bash
cd backend

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver
```

---

# Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

# Application URLs

| Service     | URL                         |
| ----------- | --------------------------- |
| Frontend    | http://localhost:3000       |
| Backend API | http://localhost:8000       |
| Admin Panel | http://localhost:8000/admin |

---

# Production Deployment

Recommended production stack:

* Ubuntu 22.04
* Nginx
* PostgreSQL
* Redis
* Docker
* HTTPS with Let's Encrypt

---

# Docker Services

| Service    | Purpose            |
| ---------- | ------------------ |
| PostgreSQL | Primary database   |
| Redis      | Cache & queue      |
| Backend    | Django API         |
| Frontend   | Next.js app        |
| Celery     | Background workers |

---

# API Authentication

Protected endpoints use JWT authentication:

```http
Authorization: Bearer <token>
```

---

# Development Commands

## Run migrations

```bash
python manage.py migrate
```

## Create migrations

```bash
python manage.py makemigrations
```

## Run Celery worker

```bash
celery -A config worker -l info
```

---

# Deployment Checklist

* [ ] Set `DEBUG=False`
* [ ] Configure allowed hosts
* [ ] Enable HTTPS
* [ ] Configure production database
* [ ] Configure Redis
* [ ] Secure environment variables
* [ ] Set up backups
* [ ] Configure Nginx reverse proxy

---

# License

MIT License

---

# Author

Built by Dagolde.
