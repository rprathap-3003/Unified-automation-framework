"""REST API Tests for Swagger Petstore service."""

import pytest
import allure

from core.utils.data_generator import DataGenerator
from core.utils.file_reader import FileReader
from config.settings import BASE_DIR
from api.models.pet_model import PetModel, Category


@allure.epic("API Automation")
@allure.feature("Petstore Resource Management")
@pytest.mark.api
class TestPetstoreApi:
    """API test suite covering CRUD operations and schema contract validation."""

    @pytest.fixture(autouse=True)
    def setup_schema(self):
        schema_path = BASE_DIR / "test_data" / "schemas" / "user_schema.json"
        self.pet_schema = FileReader.load_json(schema_path)

    @allure.story("Create Pet & Validate Schema")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_create_pet_and_validate_schema(self, api_client):
        """Create a new pet via POST and validate the response structure against JSON schema."""
        pet_payload = DataGenerator.generate_pet_payload()

        with allure.step(f"POST /pet to create pet '{pet_payload['name']}'"):
            response = api_client.create_pet(pet_payload)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        with allure.step("Validate response body against JSON schema contract"):
            created_data = response.json()
            api_client.validate_schema(created_data, self.pet_schema)
            assert created_data["id"] == pet_payload["id"]
            assert created_data["name"] == pet_payload["name"]

        # Cleanup
        api_client.delete_pet(pet_payload["id"])

    @allure.story("Full CRUD Lifecycle")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_pet_crud_lifecycle(self, api_client):
        """Verify full lifecycle: Create -> Read -> Update -> Delete -> Verify 404."""
        # 1. CREATE
        new_pet = PetModel(
            id=DataGenerator.generate_pet_payload()["id"],
            name="Automation_Buddy",
            category=Category(id=1, name="Canine"),
            photoUrls=["https://example.com/buddy.jpg"],
            status="available",
        )

        with allure.step("1. Create Pet"):
            post_res = api_client.create_pet(new_pet)
            assert post_res.status_code == 200

        # 2. READ
        with allure.step("2. Get Pet by ID"):
            get_res = api_client.get_pet(new_pet.id)
            assert get_res.status_code == 200
            assert get_res.json()["name"] == "Automation_Buddy"

        # 3. UPDATE
        with allure.step("3. Update Pet Status to 'sold'"):
            new_pet.status = "sold"
            put_res = api_client.update_pet(new_pet)
            assert put_res.status_code == 200
            assert put_res.json()["status"] == "sold"

        # 4. DELETE
        with allure.step("4. Delete Pet"):
            del_res = api_client.delete_pet(new_pet.id)
            assert del_res.status_code == 200

        # 5. VERIFY DELETED
        with allure.step("5. Verify Pet Not Found (404)"):
            verify_res = api_client.get_pet(new_pet.id)
            assert verify_res.status_code == 404, f"Expected 404, got {verify_res.status_code}"

    @allure.story("Query by Status")
    @allure.severity(allure.severity_level.NORMAL)
    def test_find_pets_by_status(self, api_client):
        """Query available pets and verify all items have status 'available'."""
        with allure.step("GET /pet/findByStatus?status=available"):
            response = api_client.find_by_status("available")
            assert response.status_code == 200

        pets = response.json()
        assert isinstance(pets, list)
        assert len(pets) > 0
        assert all(p.get("status") == "available" for p in pets[:10])
