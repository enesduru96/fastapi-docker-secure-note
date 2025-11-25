import secrets
import base64
import os

def generate_env_file():
    file_path = ".env"
    
    if os.path.exists(file_path):
        return

    print("Generating .env file...")

    secret_key = secrets.token_urlsafe(64)
    encryption_key = base64.urlsafe_b64encode(os.urandom(32)).decode()


    env_content = f"""POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=securenote_db
REDIS_HOST=redis
REDIS_PORT=6379

# Security Keys (Auto Generated)
SECRET_KEY={secret_key}
ENCRYPTION_KEY={encryption_key}
"""

    with open(file_path, "w") as f:
        f.write(env_content)

    print(f"Generated '{file_path}' successfully")
    print("Generated Keys:")
    print(f"   -> SECRET_KEY: {secret_key[:10]}...")
    print(f"   -> ENCRYPTION_KEY: {encryption_key[:10]}...")
    print("\n🚀 You can run 'docker-compose up -d --build' now.")

if __name__ == "__main__":
    generate_env_file()