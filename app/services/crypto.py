# app/services/crypto.py

import base64
from cryptography.fernet import Fernet
from app.core.config import settings

def get_fernet() -> Fernet:
    if not settings.FERNET_KEY_BASE64:
        # Agar key nahi mili to generate karo aur print karo (ya .env me set karo)
        key = Fernet.generate_key()
        print("Generated new FERNET_KEY_BASE64:", key.decode())
    else:
        key = settings.FERNET_KEY_BASE64.encode()
    return Fernet(key)

def encrypt_text(plaintext: str) -> str:
    f = get_fernet()
    token = f.encrypt(plaintext.encode())
    return token.decode()

def decrypt_text(token_str: str) -> str:
    f = get_fernet()
    return f.decrypt(token_str.encode()).decode()
