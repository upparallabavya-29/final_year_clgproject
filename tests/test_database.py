"""
Tests for utils/database.py
Run: python -m pytest tests/ -v
"""
import os
import sys
import sqlite3
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import utils.database as db_module

@pytest.fixture(autouse=True)
def temp_db(tmp_path):
    """Redirect database to a temp file for each test."""
    original = db_module.DB_PATH
    db_module.DB_PATH = str(tmp_path / "test_scan_history.db")
    db_module.init_db()
    yield
    db_module.DB_PATH = original


def _sample_user(**overrides):
    base = {
        "email": "test@example.com",
        "phone": "9876543210",
        "name": "Test User",
        "password_hash": "hash123",
        "provider": "email"
    }
    base.update(overrides)
    return base

def _sample_scan(**overrides):
    base = {
        "user_id": 1,
        "crop": "Tomato",
        "disease": "Early Blight",
        "confidence": 87.5,
        "severity": "medium",
        "model": "vit",
        "filename": "leaf01.jpg",
        "inference_ms": 320.0,
    }
    base.update(overrides)
    return base


class TestUsers:
    def test_create_user(self):
        uid = db_module.create_user(_sample_user())
        assert uid >= 1

    def test_get_user_by_email(self):
        db_module.create_user(_sample_user(email="hello@world.com"))
        user = db_module.get_user_by_email("hello@world.com")
        assert user is not None
        assert user["name"] == "Test User"

    def test_get_user_by_phone(self):
        db_module.create_user(_sample_user(phone="1112223334"))
        user = db_module.get_user_by_phone("1112223334")
        assert user is not None
        assert user["email"] == "test@example.com"


class TestScansScoped:
    def test_insert_and_get_user_scans(self):
        uid = db_module.create_user(_sample_user())
        
        # Insert 3 scans for uid=1
        for i in range(3):
            db_module.insert_scan(_sample_scan(user_id=uid, disease=f"Disease {i}"))
            
        # Insert 2 scans for uid=2
        uid2 = db_module.create_user(_sample_user(email="user2@ext.com", phone="000"))
        for i in range(2):
            db_module.insert_scan(_sample_scan(user_id=uid2))
            
        # Fetch for uid=1
        res = db_module.get_user_scans(uid, page=1, page_size=10)
        assert res["total"] == 3
        assert len(res["scans"]) == 3
        
        # Fetch for uid=2
        res2 = db_module.get_user_scans(uid2, page=1, page_size=10)
        assert res2["total"] == 2
        
    def test_pagination(self):
        uid = db_module.create_user(_sample_user())
        for i in range(5):
            db_module.insert_scan(_sample_scan(user_id=uid, confidence=i))
            
        res = db_module.get_user_scans(uid, page=1, page_size=2)
        assert res["total"] == 5
        assert len(res["scans"]) == 2
        assert res["pages"] == 3

class TestOTP:
    def test_create_and_verify_otp(self):
        phone = "9998887776"
        otp = db_module.create_otp(phone)
        assert len(otp) == 6
        
        # Verify success
        assert db_module.verify_otp_db(phone, otp) is True
        
        # Consumed immediately
        assert db_module.verify_otp_db(phone, otp) is False

    def test_otp_expiration(self):
        phone = "1111"
        otp = db_module.create_otp(phone, expire_secs=-1) # Already expired
        assert db_module.verify_otp_db(phone, otp) is False
