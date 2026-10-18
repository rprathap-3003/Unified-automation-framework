"""Synthetic and randomized test data generator."""

from __future__ import annotations

import random
import string
import uuid
from typing import Dict, Any

try:
    from faker import Faker

    fake = Faker()
except ImportError:
    fake = None


class DataGenerator:
    """Provides fake realistic test data for UI and API tests."""

    @staticmethod
    def random_string(length: int = 8) -> str:
        return "".join(random.choices(string.ascii_letters, k=length))

    @staticmethod
    def random_email(domain: str = "example.com") -> str:
        if fake:
            return fake.email()
        return f"user_{uuid.uuid4().hex[:8]}@{domain}"

    @staticmethod
    def random_username(prefix: str = "user_") -> str:
        if fake:
            return f"{prefix}{fake.user_name()}_{random.randint(100, 999)}"
        return f"{prefix}{uuid.uuid4().hex[:6]}"

    @staticmethod
    def random_password(length: int = 12) -> str:
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return "".join(random.choices(chars, k=length))

    @staticmethod
    def random_phone_number() -> str:
        if fake:
            return fake.phone_number()
        return f"+1{random.randint(2000000000, 9999999999)}"

    @staticmethod
    def generate_pet_payload() -> Dict[str, Any]:
        """Generates realistic Swagger Petstore pet payload."""
        pet_id = random.randint(100000, 999999)
        names = ["Shadow", "Bella", "Max", "Luna", "Charlie", "Oliver", "Milo", "Rocky"]
        categories = ["Dog", "Cat", "Bird", "Hamster"]
        statuses = ["available", "pending", "sold"]

        return {
            "id": pet_id,
            "category": {
                "id": random.randint(1, 10),
                "name": random.choice(categories),
            },
            "name": f"{random.choice(names)}_{random.randint(10, 99)}",
            "photoUrls": [
                f"https://images.example.com/pets/{pet_id}.jpg"
            ],
            "tags": [
                {"id": 1, "name": "friendly"},
                {"id": 2, "name": "vaccinated"},
            ],
            "status": random.choice(statuses),
        }
