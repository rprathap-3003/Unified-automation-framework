"""Domain-specific API Client for Swagger Petstore service."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import requests

from api.clients.base_api_client import BaseApiClient
from api.models.pet_model import PetModel


class PetStoreClient(BaseApiClient):
    """High-level client for Petstore REST API endpoints."""

    def __init__(self, base_url: Optional[str] = None):
        super().__init__(base_url=base_url)

    def create_pet(self, pet: PetModel | Dict[str, Any]) -> requests.Response:
        payload = pet.model_dump() if isinstance(pet, PetModel) else pet
        return self.post("pet", json_data=payload)

    def get_pet(self, pet_id: int) -> requests.Response:
        return self.get(f"pet/{pet_id}")

    def update_pet(self, pet: PetModel | Dict[str, Any]) -> requests.Response:
        payload = pet.model_dump() if isinstance(pet, PetModel) else pet
        return self.put("pet", json_data=payload)

    def delete_pet(self, pet_id: int, api_key: str = "special-key") -> requests.Response:
        headers = {"api_key": api_key}
        return self.delete(f"pet/{pet_id}", headers=headers)

    def find_by_status(self, status: str = "available") -> requests.Response:
        return self.get("pet/findByStatus", params={"status": status})
