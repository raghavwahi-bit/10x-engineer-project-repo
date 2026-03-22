"""API tests for PromptLab

Comprehensive tests for all API endpoints including happy paths,
error cases, edge cases, and query parameter handling.
"""

import time

from fastapi.testclient import TestClient


class TestHealth:
    """Tests for health endpoint."""

    def test_health_check(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestCreatePrompt:
    """Tests for POST /prompts endpoint."""

    def test_create_prompt_success(self, client: TestClient, sample_prompt_data):
        response = client.post("/prompts", json=sample_prompt_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_prompt_data["title"]
        assert data["content"] == sample_prompt_data["content"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_prompt_minimal_fields(self, client: TestClient):
        response = client.post(
            "/prompts", json={"title": "Min", "content": "Minimal content"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["description"] is None
        assert data["collection_id"] is None

    def test_create_prompt_empty_title(self, client: TestClient):
        response = client.post("/prompts", json={"title": "", "content": "Content"})
        assert response.status_code == 422

    def test_create_prompt_empty_content(self, client: TestClient):
        response = client.post("/prompts", json={"title": "Title", "content": ""})
        assert response.status_code == 422

    def test_create_prompt_title_too_long(self, client: TestClient):
        response = client.post(
            "/prompts", json={"title": "x" * 201, "content": "Content"}
        )
        assert response.status_code == 422

    def test_create_prompt_invalid_collection_id(self, client: TestClient):
        response = client.post(
            "/prompts",
            json={
                "title": "Test",
                "content": "Content",
                "collection_id": "nonexistent-col",
            },
        )
        assert response.status_code == 400

    def test_create_prompt_with_valid_collection(
        self, client: TestClient, sample_prompt_data, sample_collection_data
    ):
        col = client.post("/collections", json=sample_collection_data).json()
        prompt_data = {**sample_prompt_data, "collection_id": col["id"]}
        response = client.post("/prompts", json=prompt_data)
        assert response.status_code == 201
        assert response.json()["collection_id"] == col["id"]

    def test_create_prompt_special_characters_in_title(self, client: TestClient):
        response = client.post(
            "/prompts",
            json={"title": "Test @#$%^&*()!", "content": "Content here"},
        )
        assert response.status_code == 201
        assert response.json()["title"] == "Test @#$%^&*()!"

    def test_create_prompt_with_description(self, client: TestClient):
        response = client.post(
            "/prompts",
            json={
                "title": "Test",
                "content": "Content",
                "description": "A detailed description",
            },
        )
        assert response.status_code == 201
        assert response.json()["description"] == "A detailed description"


class TestListPrompts:
    """Tests for GET /prompts endpoint."""

    def test_list_prompts_empty(self, client: TestClient):
        response = client.get("/prompts")
        assert response.status_code == 200
        data = response.json()
        assert data["prompts"] == []
        assert data["total"] == 0

    def test_list_prompts_with_data(self, client: TestClient, sample_prompt_data):
        client.post("/prompts", json=sample_prompt_data)
        response = client.get("/prompts")
        assert response.status_code == 200
        data = response.json()
        assert len(data["prompts"]) == 1
        assert data["total"] == 1

    def test_list_prompts_sorting_newest_first(self, client: TestClient):
        client.post("/prompts", json={"title": "First", "content": "Content1"})
        time.sleep(0.05)
        client.post("/prompts", json={"title": "Second", "content": "Content2"})

        response = client.get("/prompts")
        prompts = response.json()["prompts"]
        assert prompts[0]["title"] == "Second"
        assert prompts[1]["title"] == "First"

    def test_list_prompts_filter_by_collection(
        self, client: TestClient, sample_collection_data
    ):
        col = client.post("/collections", json=sample_collection_data).json()
        client.post(
            "/prompts",
            json={"title": "In Col", "content": "C1", "collection_id": col["id"]},
        )
        client.post("/prompts", json={"title": "No Col", "content": "C2"})

        response = client.get(f"/prompts?collection_id={col['id']}")
        data = response.json()
        assert data["total"] == 1
        assert data["prompts"][0]["title"] == "In Col"

    def test_list_prompts_search_by_title(self, client: TestClient):
        client.post("/prompts", json={"title": "Python Tutorial", "content": "Content"})
        client.post(
            "/prompts", json={"title": "JavaScript Guide", "content": "Content"}
        )

        response = client.get("/prompts?search=python")
        data = response.json()
        assert data["total"] == 1
        assert data["prompts"][0]["title"] == "Python Tutorial"

    def test_list_prompts_search_by_description(self, client: TestClient):
        client.post(
            "/prompts",
            json={
                "title": "Generic",
                "content": "Content",
                "description": "Machine learning basics",
            },
        )

        response = client.get("/prompts?search=machine")
        data = response.json()
        assert data["total"] == 1

    def test_list_prompts_search_no_results(self, client: TestClient):
        client.post("/prompts", json={"title": "Hello", "content": "World"})
        response = client.get("/prompts?search=nonexistent")
        assert response.json()["total"] == 0


class TestGetPrompt:
    """Tests for GET /prompts/{prompt_id} endpoint."""

    def test_get_prompt_success(self, client: TestClient, sample_prompt_data):
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]

        response = client.get(f"/prompts/{prompt_id}")
        assert response.status_code == 200
        assert response.json()["id"] == prompt_id

    def test_get_prompt_not_found(self, client: TestClient):
        response = client.get("/prompts/nonexistent-id")
        assert response.status_code == 404
        assert response.json()["detail"] == "Prompt not found"


class TestUpdatePrompt:
    """Tests for PUT /prompts/{prompt_id} endpoint."""

    def test_update_prompt_success(self, client: TestClient, sample_prompt_data):
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]

        updated_data = {
            "title": "Updated Title",
            "content": "Updated content for the prompt",
            "description": "Updated description",
        }

        response = client.put(f"/prompts/{prompt_id}", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["content"] == "Updated content for the prompt"

    def test_update_prompt_timestamp_changes(
        self, client: TestClient, sample_prompt_data
    ):
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]
        original_updated_at = create_response.json()["updated_at"]

        time.sleep(0.05)

        updated_data = {
            "title": "Updated",
            "content": "Updated content here",
        }
        response = client.put(f"/prompts/{prompt_id}", json=updated_data)
        assert response.json()["updated_at"] != original_updated_at

    def test_update_prompt_not_found(self, client: TestClient):
        response = client.put(
            "/prompts/nonexistent",
            json={"title": "T", "content": "C"},
        )
        assert response.status_code == 404

    def test_update_prompt_invalid_collection(
        self, client: TestClient, sample_prompt_data
    ):
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]

        response = client.put(
            f"/prompts/{prompt_id}",
            json={
                "title": "T",
                "content": "C",
                "collection_id": "bad-col",
            },
        )
        assert response.status_code == 400

    def test_update_prompt_preserves_created_at(
        self, client: TestClient, sample_prompt_data
    ):
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]
        original_created_at = create_response.json()["created_at"]

        response = client.put(
            f"/prompts/{prompt_id}",
            json={"title": "New", "content": "New content"},
        )
        assert response.json()["created_at"] == original_created_at


class TestPatchPrompt:
    """Tests for PATCH /prompts/{prompt_id} endpoint."""

    def test_patch_prompt_title_only(self, client: TestClient, sample_prompt_data):
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]
        original_content = create_response.json()["content"]

        response = client.patch(
            f"/prompts/{prompt_id}",
            json={"title": "New Title", "content": original_content},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"
        assert data["content"] == original_content

    def test_patch_prompt_not_found(self, client: TestClient):
        response = client.patch(
            "/prompts/nonexistent",
            json={"title": "T", "content": "C"},
        )
        assert response.status_code == 404

    def test_patch_prompt_timestamp_changes(
        self, client: TestClient, sample_prompt_data
    ):
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]
        original_updated_at = create_response.json()["updated_at"]

        time.sleep(0.05)

        response = client.patch(
            f"/prompts/{prompt_id}",
            json={"title": "Patched", "content": "Patched content"},
        )
        assert response.json()["updated_at"] != original_updated_at

    def test_patch_prompt_invalid_collection(
        self, client: TestClient, sample_prompt_data
    ):
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]

        response = client.patch(
            f"/prompts/{prompt_id}",
            json={
                "title": "T",
                "content": "C",
                "collection_id": "bad-col",
            },
        )
        assert response.status_code == 400


class TestDeletePrompt:
    """Tests for DELETE /prompts/{prompt_id} endpoint."""

    def test_delete_prompt_success(self, client: TestClient, sample_prompt_data):
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]

        response = client.delete(f"/prompts/{prompt_id}")
        assert response.status_code == 204

        get_response = client.get(f"/prompts/{prompt_id}")
        assert get_response.status_code == 404

    def test_delete_prompt_not_found(self, client: TestClient):
        response = client.delete("/prompts/nonexistent")
        assert response.status_code == 404


class TestCreateCollection:
    """Tests for POST /collections endpoint."""

    def test_create_collection_success(
        self, client: TestClient, sample_collection_data
    ):
        response = client.post("/collections", json=sample_collection_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_collection_data["name"]
        assert "id" in data
        assert "created_at" in data

    def test_create_collection_empty_name(self, client: TestClient):
        response = client.post("/collections", json={"name": ""})
        assert response.status_code == 422

    def test_create_collection_name_too_long(self, client: TestClient):
        response = client.post("/collections", json={"name": "x" * 101})
        assert response.status_code == 422

    def test_create_collection_with_description(self, client: TestClient):
        response = client.post(
            "/collections",
            json={"name": "Test", "description": "A description"},
        )
        assert response.status_code == 201
        assert response.json()["description"] == "A description"


class TestListCollections:
    """Tests for GET /collections endpoint."""

    def test_list_collections_empty(self, client: TestClient):
        response = client.get("/collections")
        assert response.status_code == 200
        data = response.json()
        assert data["collections"] == []
        assert data["total"] == 0

    def test_list_collections_with_data(
        self, client: TestClient, sample_collection_data
    ):
        client.post("/collections", json=sample_collection_data)
        response = client.get("/collections")
        assert response.status_code == 200
        assert len(response.json()["collections"]) == 1


class TestGetCollection:
    """Tests for GET /collections/{collection_id} endpoint."""

    def test_get_collection_success(self, client: TestClient, sample_collection_data):
        create_response = client.post("/collections", json=sample_collection_data)
        col_id = create_response.json()["id"]

        response = client.get(f"/collections/{col_id}")
        assert response.status_code == 200
        assert response.json()["id"] == col_id

    def test_get_collection_not_found(self, client: TestClient):
        response = client.get("/collections/nonexistent-id")
        assert response.status_code == 404


class TestDeleteCollection:
    """Tests for DELETE /collections/{collection_id} endpoint."""

    def test_delete_collection_success(
        self, client: TestClient, sample_collection_data
    ):
        create_response = client.post("/collections", json=sample_collection_data)
        col_id = create_response.json()["id"]

        response = client.delete(f"/collections/{col_id}")
        assert response.status_code == 204

    def test_delete_collection_not_found(self, client: TestClient):
        response = client.delete("/collections/nonexistent")
        assert response.status_code == 404

    def test_delete_collection_with_prompts_blocked(
        self, client: TestClient, sample_collection_data, sample_prompt_data
    ):
        col = client.post("/collections", json=sample_collection_data).json()
        prompt_data = {**sample_prompt_data, "collection_id": col["id"]}
        client.post("/prompts", json=prompt_data)

        response = client.delete(f"/collections/{col['id']}")
        assert response.status_code == 400
        assert "associated with existing prompts" in response.json()["detail"]

    def test_delete_collection_without_prompts_succeeds(
        self, client: TestClient, sample_collection_data
    ):
        col = client.post("/collections", json=sample_collection_data).json()
        response = client.delete(f"/collections/{col['id']}")
        assert response.status_code == 204
