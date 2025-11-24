# 🔐 SecureNote API

REST API for secure note-taking and social sharing, built with **FastAPI**, **PostgreSQL**, and **Docker**.

The project implements **JWT Authentication** (Access + Refresh Token Rotation), **Argon2** password hashing, and **Alembic** for database version control.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)
![Alembic](https://img.shields.io/badge/Alembic-Migrations-red.svg)

## ✨ Key Features

* 🐳 **Fully Dockerized:** Seamless setup with `docker-compose`.
* 🔐 **Implemented Security:**
    * JWT Access Tokens (Short-lived).
    * **Refresh Token Rotation** (Old tokens are invalidated upon use to prevent replay attacks).
    * Password hashing with **Argon2**.
    * Email format validation using Pydantic.
* 🌍 **Social Features (Public Feed):** Users can mark notes as "Public". Other users can view these notes with the author's username attached (via SQL Joins).
* 🔍 **Search:** Filter notes by title or content using the search endpoint.
* 🧪 **Automated Testing (CI):** GitHub Actions pipeline running asynchronous **Pytest** suite on every push/pull request.
* 🏗️ **Database Migrations:** Schema changes are managed professionally using **Alembic**.
* ⚙️ **Configuration:** Centralized settings management using `pydantic-settings`.
* 💻 **CLI Client:** Includes a Python-based terminal client with session management for easy testing.

---

## 🛠 Tech Stack

* **Framework:** FastAPI
* **Database:** PostgreSQL 15
* **ORM:** SQLModel (SQLAlchemy + Pydantic)
* **Migrations:** Alembic
* **Authentication:** Python-JOSE & Passlib (Argon2)
* **Config:** Pydantic-Settings

---

## 🚀 Installation & Setup (Step-by-Step)

Follow these steps to run the project from scratch.

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/fastapi-docker-secure-note.git
cd fastapi-docker-secure-note
```

### 2. Create Environment Variables (.env)
For security reasons, the .env file is not included in the repository. Create a file named .env in the root directory and add the following content:
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=securenote_db
SECRET_KEY=change_this_to_a_very_long_random_secret_string
```

### 3. Start Containers
Build and start the services in detached mode:
```bash
docker-compose up -d --build
```

### 4. Create Database Tables (Crucial Step)
```bash
docker-compose exec web alembic upgrade head
```

&nbsp;

## 🧪 Usage & Testing
### Option A: Swagger UI (Browser)
* Visit http://localhost:8000/docs to explore the interactive API documentation.
* Use /auth/register to create a new user.
* Use /auth/token to login and copy the access_token.
* Click the Authorize button at the top right and paste the token.
* Use /notes/search to search for notes by keyword.

### Option B: CLI Client (Terminal)
You can use the included Python script to test the API interactively:
```bash
# Install requests if not already installed: pip install requests
python client_test_app.py
```
_The client saves your login tokens to a local session.json file, so you don't have to login every time._

&nbsp;

&nbsp;

## 🛠️ Developer Notes (Cheat Sheet)
### If you modify the database models (e.g., adding a new field in models.py), follow these commands:

* 1. Create a New Migration (Plan)
`docker-compose exec web alembic revision --autogenerate -m "description_of_changes"`
&nbsp;

* 2. Apply Changes to Database (Upgrade)
`docker-compose exec web alembic upgrade head`

&nbsp;


## 🛠️ DB Reset

If you want to wipe everything (including data) and start fresh:

* Delete old migration files inside alembic/versions/ (keep __pycache__).
* Remove the Docker volume: 
`docker-compose down -v`
* Restart containers: `docker-compose up -d --build`
* Create initial migration: `docker-compose exec web alembic revision --autogenerate -m "initial"`
* Apply migration: `docker-compose exec web alembic upgrade head`

&nbsp;

## 📂 Project Structure  
├── alembic/             # Database migration scripts  
├── app/  
│   ├── routers/         # API Endpoints (Auth, Notes)  
│   ├── models.py        # Database Models (User, Note, Token)  
│   ├── crud.py          # Database Operations (Create, Read...)  
│   ├── auth.py          # JWT, Hashing, and Security Logic  
│   ├── config.py        # Settings Management (.env reading)  
│   └── main.py          # Application Entry Point  
├── client_app.py        # Terminal Testing Client  
├── docker-compose.yml   # Docker Services Configuration  
└── Dockerfile           # Python Environment Definition  

&nbsp;

## 🗺️ Roadmap

This project is actively being developed. Here are the planned features for upcoming releases:

- [x] Core Backend API (FastAPI, SQLModel, PostgreSQL)
- [x] Advanced Security (JWT, Argon2, Rotation)
- [x] Docker & Compose Infrastructure
- [x] CLI Client
- [x] Refactored Async Codebase
- [x] Comprehensive Unit Tests (Pytest)
- [ ] **Frontend Web UI** (Planned: Streamlit Dashboard)
- [ ] Deployment to Cloud (Render)
