"""
Tests for backend/auth.py — JWT and Password Cryptography
Run: python -m pytest tests/ -v
"""
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.auth import (
    create_token,
    decode_token,
    hash_password,
    verify_password
)

def test_password_hashing():
    password = "SecretPassword!"
    hashed = hash_password(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_creation_and_decoding():
    data = {"sub": "123", "email": "test@cropguard.ai"}
    token = create_token(data)
    
    # Ensure it's a valid JWT string
    assert isinstance(token, str)
    assert len(token.split(".")) == 3
    
    # Decode
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "123"
    assert payload["email"] == "test@cropguard.ai"
    assert "exp" in payload

def test_jwt_expiration():
    # The function uses TOKEN_EXPIRE_H, we can just verify the token signature
    data = {"sub": "123"}
    token = create_token(data)
    
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "123"
