"""TDD tests for the Tagging System feature.

These tests were written first following the TDD approach,
then the implementation was built to make them pass.
"""

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from app.models import Tag, TagCreate, TagList, PromptTagsResponse


class TestTagModels:
    """Tests for tag Pydantic models."""

    def test_tag_create_valid(self):
        tag = TagCreate(name="python")
        assert tag.name == "python"
        assert tag.description is None

    def test_tag_create_with_description(self):
        tag = TagCreate(name="python", description="Python related prompts")
        assert tag.description == "Python related prompts"

    def test_tag_name_too_short(self):
        with pytest.raises(ValidationError):
            TagCreate(name="ab")

    def test_tag_name_too_long(self):
        with pytest.raises(ValidationError):
            TagCreate(name="x" * 51)

    def test_tag_name_min_length(self):
        tag = TagCreate(name="abc")
        assert tag.name == "abc"

    def test_tag_name_max_length(self):
        tag = TagCreate(name="x" * 50)
        assert len(tag.name) == 50

    def test_tag_name_invalid_chars_spaces(self):
        with pytest.raises(ValidationError):
            TagCreate(name="has spaces")

    def test_tag_name_invalid_chars_special(self):
        with pytest.raises(ValidationError):
            TagCreate(name="tag@name")

    def test_tag_name_valid_with_hyphens(self):
        tag = TagCreate(name="creative-writing")
        assert tag.name == "creative-writing"

    def test_tag_name_valid_with_underscores(self):
        tag = TagCreate(name="machine_learning")
        assert tag.name == "machine_learning"

    def test_tag_name_valid_alphanumeric(self):
        tag = TagCreate(name="python3")
        assert tag.name == "python3"

    def test_tag_defaults(self):
        tag = Tag(name="test-tag")
        assert tag.id is not None
        assert tag.usage_count == 0
        assert tag.created_at is not None

    def test_tag_list_model(self):
        t = Tag(name="test-tag")
        tl = TagList(tags=[t], total=1)
        assert len(tl.tags) == 1
        assert tl.total == 1

    def test_tag_list_empty(self):
        tl = TagList(tags=[], total=0)
        assert tl.tags == []

    def test_prompt_tags_response(self):
        t = Tag(name="test-tag")
        ptr = PromptTagsResponse(prompt_id="p-1", tags=[t], total_tags=1)
        assert ptr.prompt_id == "p-1"
        assert len(ptr.tags) == 1


class TestTagStorage:
    """Tests for tag storage operations."""

    def setup_method(self):
        from app.storage import Storage

        self.store = Storage()

    def test_create_tag(self):
        tag = Tag(name="python")
        result = self.store.create_tag(tag)
        assert result.name == "python"
        assert result.id == tag.id

    def test_get_tag_existing(self):
        tag = Tag(name="python")
        self.store.create_tag(tag)
        result = self.store.get_tag(tag.id)
        assert result is not None
        assert result.name == "python"

    def test_get_tag_not_found(self):
        result = self.store.get_tag("nonexistent")
        assert result is None

    def test_get_tag_by_name(self):
        tag = Tag(name="Python")
        self.store.create_tag(tag)
        result = self.store.get_tag_by_name("python")
        assert result is not None
        assert result.name == "Python"

    def test_get_tag_by_name_case_insensitive(self):
        tag = Tag(name="MachineLearning")
        self.store.create_tag(tag)
        result = self.store.get_tag_by_name("machinelearning")
        assert result is not None

    def test_get_tag_by_name_not_found(self):
        result = self.store.get_tag_by_name("nonexistent")
        assert result is None

    def test_get_all_tags_empty(self):
        result = self.store.get_all_tags()
        assert result == []

    def test_get_all_tags_populated(self):
        self.store.create_tag(Tag(name="tag-one"))
        self.store.create_tag(Tag(name="tag-two"))
        result = self.store.get_all_tags()
        assert len(result) == 2

    def test_delete_tag_existing(self):
        tag = Tag(name="python")
        self.store.create_tag(tag)
        result = self.store.delete_tag(tag.id)
        assert result is True
        assert self.store.get_tag(tag.id) is None

    def test_delete_tag_not_found(self):
        result = self.store.delete_tag("nonexistent")
        assert result is False

    def test_add_tag_to_prompt(self):
        from app.models import Prompt

        prompt = Prompt(title="Test", content="Content")
        self.store.create_prompt(prompt)
        tag = Tag(name="python")
        self.store.create_tag(tag)

        result = self.store.add_tag_to_prompt(prompt.id, tag.id)
        assert result is True

    def test_add_duplicate_tag_to_prompt(self):
        from app.models import Prompt

        prompt = Prompt(title="Test", content="Content")
        self.store.create_prompt(prompt)
        tag = Tag(name="python")
        self.store.create_tag(tag)

        self.store.add_tag_to_prompt(prompt.id, tag.id)
        result = self.store.add_tag_to_prompt(prompt.id, tag.id)
        assert result is False

    def test_remove_tag_from_prompt(self):
        from app.models import Prompt

        prompt = Prompt(title="Test", content="Content")
        self.store.create_prompt(prompt)
        tag = Tag(name="python")
        self.store.create_tag(tag)
        self.store.add_tag_to_prompt(prompt.id, tag.id)

        result = self.store.remove_tag_from_prompt(prompt.id, tag.id)
        assert result is True

    def test_remove_tag_from_prompt_not_assigned(self):
        from app.models import Prompt

        prompt = Prompt(title="Test", content="Content")
        self.store.create_prompt(prompt)

        result = self.store.remove_tag_from_prompt(prompt.id, "bad-tag")
        assert result is False

    def test_get_tags_for_prompt(self):
        from app.models import Prompt

        prompt = Prompt(title="Test", content="Content")
        self.store.create_prompt(prompt)
        t1 = Tag(name="python")
        t2 = Tag(name="coding")
        self.store.create_tag(t1)
        self.store.create_tag(t2)
        self.store.add_tag_to_prompt(prompt.id, t1.id)
        self.store.add_tag_to_prompt(prompt.id, t2.id)

        result = self.store.get_tags_for_prompt(prompt.id)
        assert len(result) == 2
        names = {t.name for t in result}
        assert names == {"python", "coding"}

    def test_get_tags_for_prompt_none(self):
        from app.models import Prompt

        prompt = Prompt(title="Test", content="Content")
        self.store.create_prompt(prompt)

        result = self.store.get_tags_for_prompt(prompt.id)
        assert result == []

    def test_clear_includes_tags(self):
        self.store.create_tag(Tag(name="python"))
        self.store.clear()
        assert self.store.get_all_tags() == []


class TestTagAPI:
    """Tests for tag API endpoints."""

    def test_create_tag_success(self, client: TestClient):
        response = client.post("/tags", json={"name": "python"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "python"
        assert "id" in data
        assert data["usage_count"] == 0

    def test_create_tag_with_description(self, client: TestClient):
        response = client.post(
            "/tags",
            json={"name": "python", "description": "Python prompts"},
        )
        assert response.status_code == 201
        assert response.json()["description"] == "Python prompts"

    def test_create_tag_duplicate_name(self, client: TestClient):
        client.post("/tags", json={"name": "python"})
        response = client.post("/tags", json={"name": "python"})
        assert response.status_code == 409

    def test_create_tag_duplicate_name_case_insensitive(self, client: TestClient):
        client.post("/tags", json={"name": "Python"})
        response = client.post("/tags", json={"name": "python"})
        assert response.status_code == 409

    def test_create_tag_invalid_name(self, client: TestClient):
        response = client.post("/tags", json={"name": "bad name"})
        assert response.status_code == 422

    def test_create_tag_name_too_short(self, client: TestClient):
        response = client.post("/tags", json={"name": "ab"})
        assert response.status_code == 422

    def test_list_tags_empty(self, client: TestClient):
        response = client.get("/tags")
        assert response.status_code == 200
        data = response.json()
        assert data["tags"] == []
        assert data["total"] == 0

    def test_list_tags_with_data(self, client: TestClient):
        client.post("/tags", json={"name": "python"})
        client.post("/tags", json={"name": "javascript"})
        response = client.get("/tags")
        assert response.status_code == 200
        assert response.json()["total"] == 2

    def test_get_tag_success(self, client: TestClient):
        create_response = client.post("/tags", json={"name": "python"})
        tag_id = create_response.json()["id"]

        response = client.get(f"/tags/{tag_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "python"

    def test_get_tag_not_found(self, client: TestClient):
        response = client.get("/tags/nonexistent")
        assert response.status_code == 404

    def test_delete_tag_success(self, client: TestClient):
        create_response = client.post("/tags", json={"name": "python"})
        tag_id = create_response.json()["id"]

        response = client.delete(f"/tags/{tag_id}")
        assert response.status_code == 204

    def test_delete_tag_not_found(self, client: TestClient):
        response = client.delete("/tags/nonexistent")
        assert response.status_code == 404

    def test_add_tags_to_prompt(self, client: TestClient, sample_prompt_data):
        prompt = client.post("/prompts", json=sample_prompt_data).json()
        client.post("/tags", json={"name": "python"})
        client.post("/tags", json={"name": "coding"})

        response = client.post(
            f"/prompts/{prompt['id']}/tags",
            json={"tag_names": ["python", "coding"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["prompt_id"] == prompt["id"]
        assert data["total_tags"] == 2

    def test_add_tags_to_nonexistent_prompt(self, client: TestClient):
        client.post("/tags", json={"name": "python"})
        response = client.post(
            "/prompts/nonexistent/tags",
            json={"tag_names": ["python"]},
        )
        assert response.status_code == 404

    def test_add_nonexistent_tag_to_prompt(
        self, client: TestClient, sample_prompt_data
    ):
        prompt = client.post("/prompts", json=sample_prompt_data).json()
        response = client.post(
            f"/prompts/{prompt['id']}/tags",
            json={"tag_names": ["nonexistent"]},
        )
        assert response.status_code == 404

    def test_remove_tag_from_prompt(self, client: TestClient, sample_prompt_data):
        prompt = client.post("/prompts", json=sample_prompt_data).json()
        tag = client.post("/tags", json={"name": "python"}).json()
        client.post(
            f"/prompts/{prompt['id']}/tags",
            json={"tag_names": ["python"]},
        )

        response = client.delete(f"/prompts/{prompt['id']}/tags/{tag['id']}")
        assert response.status_code == 204

    def test_get_prompt_tags(self, client: TestClient, sample_prompt_data):
        prompt = client.post("/prompts", json=sample_prompt_data).json()
        client.post("/tags", json={"name": "python"})
        client.post(
            f"/prompts/{prompt['id']}/tags",
            json={"tag_names": ["python"]},
        )

        response = client.get(f"/prompts/{prompt['id']}/tags")
        assert response.status_code == 200
        data = response.json()
        assert data["total_tags"] == 1
        assert data["tags"][0]["name"] == "python"

    def test_get_prompt_tags_empty(self, client: TestClient, sample_prompt_data):
        prompt = client.post("/prompts", json=sample_prompt_data).json()
        response = client.get(f"/prompts/{prompt['id']}/tags")
        assert response.status_code == 200
        assert response.json()["total_tags"] == 0

    def test_filter_prompts_by_single_tag(self, client: TestClient, sample_prompt_data):
        p1 = client.post("/prompts", json=sample_prompt_data).json()
        client.post(
            "/prompts",
            json={"title": "Other", "content": "Other content"},
        )
        client.post("/tags", json={"name": "python"})
        client.post(
            f"/prompts/{p1['id']}/tags",
            json={"tag_names": ["python"]},
        )

        response = client.get("/prompts?tags=python")
        data = response.json()
        assert data["total"] == 1
        assert data["prompts"][0]["id"] == p1["id"]

    def test_filter_prompts_by_multiple_tags_and_logic(self, client: TestClient):
        p1 = client.post(
            "/prompts",
            json={"title": "P1", "content": "Content1"},
        ).json()
        p2 = client.post(
            "/prompts",
            json={"title": "P2", "content": "Content2"},
        ).json()

        client.post("/tags", json={"name": "python"})
        client.post("/tags", json={"name": "beginner"})

        # p1 gets both tags
        client.post(
            f"/prompts/{p1['id']}/tags",
            json={"tag_names": ["python", "beginner"]},
        )
        # p2 gets only python
        client.post(
            f"/prompts/{p2['id']}/tags",
            json={"tag_names": ["python"]},
        )

        response = client.get("/prompts?tags=python,beginner")
        data = response.json()
        assert data["total"] == 1
        assert data["prompts"][0]["id"] == p1["id"]

    def test_filter_prompts_by_tag_no_results(self, client: TestClient):
        client.post(
            "/prompts",
            json={"title": "Test", "content": "Content"},
        )
        response = client.get("/prompts?tags=nonexistent")
        assert response.json()["total"] == 0

    def test_delete_tag_cleans_prompt_associations(
        self, client: TestClient, sample_prompt_data
    ):
        prompt = client.post("/prompts", json=sample_prompt_data).json()
        tag = client.post("/tags", json={"name": "python"}).json()
        client.post(
            f"/prompts/{prompt['id']}/tags",
            json={"tag_names": ["python"]},
        )

        client.delete(f"/tags/{tag['id']}")

        tags_response = client.get(f"/prompts/{prompt['id']}/tags")
        assert tags_response.json()["total_tags"] == 0
