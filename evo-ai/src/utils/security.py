"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: security.py                                                           │
│ Developed by: Davidson Gomes                                                 │
│ Creation date: May 13, 2025                                                  │
│ Contact: contato@evolution-api.com                                           │
├──────────────────────────────────────────────────────────────────────────────┤
│ @copyright © Evolution API 2025. All rights reserved.                        │
│ Licensed under the Apache License, Version 2.0                               │
└──────────────────────────────────────────────────────────────────────────────┘
"""

from passlib.context import CryptContext
from datetime import datetime, timedelta
import secrets
import string
from jose import jwt
from src.config.settings import settings
import logging
import bcrypt
from dataclasses import dataclass
from cryptography.fernet import Fernet
import base64
from hashlib import sha256

logger = logging.getLogger(__name__)

# Fix bcrypt error with passlib
if not hasattr(bcrypt, "__about__"):
    @dataclass
    class BcryptAbout:
        __version__: str = getattr(bcrypt, "__version__")
    setattr(bcrypt, "__about__", BcryptAbout())

# Context for password hashing using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Creates a password hash"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies if the provided password matches the stored hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_jwt_token(data: dict, expires_delta: timedelta = None) -> str:
    """Creates a JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_TIME)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def generate_token(length: int = 32) -> str:
    """Generates a secure token for email verification or password reset"""
    alphabet = string.ascii_letters + string.digits
    token = "".join(secrets.choice(alphabet) for _ in range(length))
    return token

# ═══════════════════════════════════════════════════════════════════════════
# ENCRYPTION/DECRYPTION (Fernet)
# ═══════════════════════════════════════════════════════════════════════════

def get_fernet_key() -> bytes:
    """Gera uma chave Fernet válida a partir do ENCRYPTION_KEY"""
    raw_key = settings.ENCRYPTION_KEY or settings.JWT_SECRET_KEY or "default-insecure-key"
    key_bytes = sha256(raw_key.encode()).digest()
    return base64.urlsafe_b64encode(key_bytes)

def encrypt_key(plain_text: str) -> str:
    """Criptografa uma string usando Fernet"""
    try:
        key = get_fernet_key()
        f = Fernet(key)
        encrypted = f.encrypt(plain_text.encode())
        return encrypted.decode()
    except Exception as e:
        logger.error(f"Erro ao criptografar: {e}")
        raise

def decrypt_key(encrypted_text: str) -> str:
    """Descriptografa uma string usando Fernet (com fallback)"""
    try:
        key = get_fernet_key()
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_text.encode())
        return decrypted.decode()
    except Exception as e:
        logger.warning(f"Falha ao descriptografar: {e}")
        return encrypted_text  # Fallback: retornar texto original

def is_encrypted(text: str) -> bool:
    """Verifica se um texto está criptografado"""
    try:
        if not text:
            return False
        key = get_fernet_key()
        f = Fernet(key)
        f.decrypt(text.encode())
        return True
    except:
        return False
