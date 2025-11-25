# 🔐 SecureNote API

High-performance REST API for secure note-taking and social sharing, built with **FastAPI**, **PostgreSQL**, **Redis**, and **Docker**.

The project implements **JWT Authentication** (Access + Refresh Token Rotation), **Argon2** password hashing, **Encryption at Rest**, **Async Architecture**, and **Redis Caching** for scalability.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)
![Redis](https://img.shields.io/badge/Redis-Caching-DC382D.svg)
![Alembic](https://img.shields.io/badge/Alembic-Migrations-red.svg)
![Encryption](https://img.shields.io/badge/Encryption-Fernet%2FAES-success)

## ✨ Key Features

* 🐳 **Fully Dockerized:** Seamless setup with `docker-compose`.
* 🚀 **High Performance:** Asynchronous codebase (Asyncpg + Asyncio) with **Redis Caching** for public feed and user notes.
* 🔐 **Advanced Security:**
    * **Encryption at Rest:** Private notes are encrypted in the database (AES/Fernet). Even if the DB is compromised, content remains secure.
    * **JWT Access Tokens:** Short-lived stateless tokens.
    * **Refresh Token Rotation:** Old tokens are invalidated upon use to prevent replay attacks.
    * **Argon2:** State-of-the-art password hashing.
* 🌍 **Social Features (Public Feed):** Users can mark notes as "Public". Other users can view these notes with the author's username attached (via SQL Joins).
* 🔍 **Smart Search:** Full-Text Search functionality (filters public notes, protects private ones).
* 🧪 **Automated Testing (CI):** GitHub Actions pipeline running asynchronous **Pytest** suite.
* ⚙️ **Auto-Configuration:** Includes a script to auto-generate secure environment variables.

---

## 🛡️ Security Architecture

This project uses a **Hybrid Encryption Strategy** to balance security and performance:

**Public Notes** - stored as-is to allow Full-Text Search and high-performance indexing.

**Private Notes** -  Both Title and Content are encrypted with Fernet before saving. Only the owner can decrypt and read them.

**Passwords** - Hashed (Argon2)

---

## 🛠 Tech Stack

* **Framework:** FastAPI (Async)
* **Database:** PostgreSQL 15 (Asyncpg driver)
* **Caching:** Redis (Async)
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
For security reasons, secrets are not stored in the repository. You need to create a .env file. You have two options:

#### Option A: Automatic Setup (Recommended) ⚡ 
Run the included Python script to generate a secure .env file with cryptographically strong keys:
```bash
python generate_env.py
```

#### Option B: Manual Setup 🛠️ 
Create a file named .env in the root directory and paste the content below. (Note: You must generate your own secure values for SECRET_KEY and ENCRYPTION_KEY).
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=securenote_db
REDIS_HOST=redis
REDIS_PORT=6379

# Replace these with strong, random keys!
SECRET_KEY=change_this_to_a_very_long_random_secret_string
ENCRYPTION_KEY=change_this_to_a_valid_fernet_key
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
│   ├── redis_client.py  # Redis Connection Manager
│   ├── config.py        # Settings Management (.env reading)  
│   └── main.py          # Application Entry Point  
├── client_test_app.py   # Terminal Testing Client  
├── docker-compose.yml   # Docker Services Configuration  
└── Dockerfile           # Python Environment Definition  

&nbsp;

## 🗺️ Roadmap

This project is actively being developed. Here are the planned features for upcoming releases:

- [x] Core Backend API (FastAPI, SQLModel, PostgreSQL)
- [x] Advanced Security (JWT, Argon2, Rotation)
- [x] Encryption at Rest (AES/Fernet)
- [x] Docker & Compose Infrastructure
- [x] CLI Client
- [x] Refactored Async Codebase
- [x] Redis Caching Implementation
- [x] Comprehensive Unit Tests (Pytest)
- [ ] **Frontend Web UI** (Planned: Streamlit Dashboard)
- [ ] Deployment to Cloud (Render)
