from cryptography.fernet import Fernet, InvalidToken
from .config import settings
import logging

logger = logging.getLogger("uvicorn")

try:
    cipher = Fernet(settings.ENCRYPTION_KEY)
except Exception as e:
    logger.error(f"CRITICAL: Encryption Key is invalid! {e}")
    raise e

def encrypt_text(plain_text: str) -> str:
    if not plain_text:
        return ""
    return cipher.encrypt(plain_text.encode()).decode()

def decrypt_text(encrypted_text: str) -> str:
    if not encrypted_text:
        return ""
    
    try:
        return cipher.decrypt(encrypted_text.encode()).decode()
    except InvalidToken:
        return encrypted_text
        