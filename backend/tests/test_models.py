"""Tests for Pydantic data models and helper functions."""

import pytest
from datetime import datetime
from uuid import UUID

from app.models import (
    generate_id,
    get_current_time,
    PromptBase,
    PromptCreate,
    PromptUpdate,
    Prompt,
    CollectionBase,
    CollectionCreate,
    Collection,
    PromptList,
    CollectionList,
    HealthResponse,
)


class TestGenerateId:
    """Tests for generate_id helper function."""

    def test_generate_id_returns_string(self):
        result = generate_id()
        assert isinstance(result, str)

    def test_generate_id_unique_values(self):
        ids = {generate_id() for _ in range(100)}
        assert len(ids) == 100

    def test_generate_id_valid_uuid_format(self):
        result = generate_id()
        UUID(result)  # Raises ValueError if invalid


class TestGetCurrentTime:
    """Tests for get_current_time helper function."""

    def test_get_current_time_returns_datetime(self):
        result = get_current_time()
        assert isinstance(result, datetime)

    def test_get_current_time_approximately_now(self):
        before = datetime.utcnow()
        result = get_current_time()
        after = datetime.utcnow()
        assert before <= result <= after


class TestPromptBase:
    """Tests for PromptBase model validation."""

    def test_prompt_base_valid(self):
        prompt = PromptBase(title="Test", content="Test content")
        assert prompt.title == "Test"
        assert prompt.content == "Test content"
        assert prompt.description is None
        assert prompt.collection_id is None

    def test_prompt_base_title_empty(self):
        with pytest.raises(Exception):
            PromptBase(title="", content="Test content")

    def test_prompt_base_title_too_long(self):
        with pytest.raises(Exception):
            PromptBase(title="x" * 201, content="Test content")

    def test_prompt_base_title_max_length(self):
        prompt = PromptBase(title="x" * 200, content="Test content")
        assert len(prompt.title) == 200

    def test_prompt_base_content_empty(self):
        with pytest.raises(Exception):
            PromptBase(title="Test", content="")

    def test_prompt_base_description_optional(self):
        prompt = PromptBase(title="Test", content="Content")
        assert prompt.description is None

    def test_prompt_base_description_set(self):
        prompt = PromptBase(
            title="Test", content="Content", description="A description"
        )
        assert prompt.description == "A description"

    def test_prompt_base_description_too_long(self):
        with pytest.raises(Exception):
            PromptBase(title="Test", content="Content", description="x" * 501)

    def test_prompt_base_collection_id_optional(self):
        prompt = PromptBase(title="Test", content="Content")
        assert prompt.collection_id is None

    def test_prompt_base_collection_id_set(self):
        prompt = PromptBase(title="Test", content="Content", collection_id="col-123")
        assert prompt.collection_id == "col-123"


class TestPromptCreate:
    """Tests for PromptCreate model."""

    def test_prompt_create_valid(self):
        prompt = PromptCreate(title="Test", content="Content")
        assert prompt.title == "Test"
        assert prompt.content == "Content"

    def test_prompt_create_inherits_prompt_base_fields(self):
        prompt = PromptCreate(
            title="Test",
            content="Content",
            description="Desc",
            collection_id="col-1",
        )
        assert prompt.description == "Desc"
        assert prompt.collection_id == "col-1"


class TestPromptUpdate:
    """Tests for PromptUpdate model."""

    def test_prompt_update_valid(self):
        prompt = PromptUpdate(title="Updated", content="Updated content")
        assert prompt.title == "Updated"

    def test_prompt_update_inherits_prompt_base_fields(self):
        prompt = PromptUpdate(
            title="Test",
            content="Content",
            description="Desc",
            collection_id="col-1",
        )
        assert prompt.description == "Desc"
        assert prompt.collection_id == "col-1"


class TestPrompt:
    """Tests for Prompt response model."""

    def test_prompt_id_auto_generated(self):
        prompt = Prompt(title="Test", content="Content")
        assert prompt.id is not None
        assert isinstance(prompt.id, str)
        assert len(prompt.id) > 0

    def test_prompt_timestamps_auto_generated(self):
        prompt = Prompt(title="Test", content="Content")
        assert isinstance(prompt.created_at, datetime)
        assert isinstance(prompt.updated_at, datetime)

    def test_prompt_unique_ids(self):
        p1 = Prompt(title="Test1", content="Content1")
        p2 = Prompt(title="Test2", content="Content2")
        assert p1.id != p2.id

    def test_prompt_from_attributes_config(self):
        assert Prompt.model_config.get("from_attributes") is True

    def test_prompt_model_dump_keys(self):
        prompt = Prompt(title="Test", content="Content")
        data = prompt.model_dump()
        expected_keys = {
            "id",
            "title",
            "content",
            "description",
            "collection_id",
            "created_at",
            "updated_at",
        }
        assert set(data.keys()) == expected_keys

    def test_prompt_with_all_fields(self):
        prompt = Prompt(
            title="Test",
            content="Content",
            description="Desc",
            collection_id="col-1",
        )
        assert prompt.description == "Desc"
        assert prompt.collection_id == "col-1"


class TestCollectionBase:
    """Tests for CollectionBase model validation."""

    def test_collection_base_valid(self):
        col = CollectionBase(name="Test Collection")
        assert col.name == "Test Collection"
        assert col.description is None

    def test_collection_base_name_empty(self):
        with pytest.raises(Exception):
            CollectionBase(name="")

    def test_collection_base_name_too_long(self):
        with pytest.raises(Exception):
            CollectionBase(name="x" * 101)

    def test_collection_base_name_max_length(self):
        col = CollectionBase(name="x" * 100)
        assert len(col.name) == 100

    def test_collection_base_description_optional(self):
        col = CollectionBase(name="Test")
        assert col.description is None

    def test_collection_base_description_set(self):
        col = CollectionBase(name="Test", description="A description")
        assert col.description == "A description"

    def test_collection_base_description_too_long(self):
        with pytest.raises(Exception):
            CollectionBase(name="Test", description="x" * 501)


class TestCollectionCreate:
    """Tests for CollectionCreate model."""

    def test_collection_create_valid(self):
        col = CollectionCreate(name="Test")
        assert col.name == "Test"

    def test_collection_create_inherits_collection_base(self):
        col = CollectionCreate(name="Test", description="Desc")
        assert col.description == "Desc"


class TestCollection:
    """Tests for Collection response model."""

    def test_collection_id_auto_generated(self):
        col = Collection(name="Test")
        assert col.id is not None
        assert isinstance(col.id, str)

    def test_collection_created_at_auto_generated(self):
        col = Collection(name="Test")
        assert isinstance(col.created_at, datetime)

    def test_collection_from_attributes_config(self):
        assert Collection.model_config.get("from_attributes") is True

    def test_collection_model_dump_keys(self):
        col = Collection(name="Test")
        data = col.model_dump()
        expected_keys = {"id", "name", "description", "created_at"}
        assert set(data.keys()) == expected_keys


class TestPromptList:
    """Tests for PromptList response model."""

    def test_prompt_list_empty(self):
        pl = PromptList(prompts=[], total=0)
        assert pl.prompts == []
        assert pl.total == 0

    def test_prompt_list_with_items(self):
        p1 = Prompt(title="Test1", content="Content1")
        p2 = Prompt(title="Test2", content="Content2")
        pl = PromptList(prompts=[p1, p2], total=2)
        assert len(pl.prompts) == 2
        assert pl.total == 2


class TestCollectionList:
    """Tests for CollectionList response model."""

    def test_collection_list_empty(self):
        cl = CollectionList(collections=[], total=0)
        assert cl.collections == []
        assert cl.total == 0

    def test_collection_list_with_items(self):
        c1 = Collection(name="Col1")
        c2 = Collection(name="Col2")
        cl = CollectionList(collections=[c1, c2], total=2)
        assert len(cl.collections) == 2
        assert cl.total == 2


class TestHealthResponse:
    """Tests for HealthResponse model."""

    def test_health_response_valid(self):
        hr = HealthResponse(status="healthy", version="1.0.0")
        assert hr.status == "healthy"
        assert hr.version == "1.0.0"
