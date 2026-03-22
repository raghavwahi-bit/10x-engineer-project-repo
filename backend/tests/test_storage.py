"""Tests for the in-memory storage layer."""

from app.models import Prompt, Collection
from app.storage import Storage, storage


class TestStoragePrompts:
    """Tests for prompt storage operations."""

    def setup_method(self):
        """Create a fresh storage instance for each test."""
        self.store = Storage()

    def test_create_prompt_stores_and_returns(self):
        prompt = Prompt(title="Test", content="Content")
        result = self.store.create_prompt(prompt)
        assert result.id == prompt.id
        assert result.title == "Test"

    def test_get_prompt_existing(self):
        prompt = Prompt(title="Test", content="Content")
        self.store.create_prompt(prompt)
        result = self.store.get_prompt(prompt.id)
        assert result is not None
        assert result.id == prompt.id

    def test_get_prompt_not_found(self):
        result = self.store.get_prompt("nonexistent-id")
        assert result is None

    def test_get_all_prompts_empty(self):
        result = self.store.get_all_prompts()
        assert result == []

    def test_get_all_prompts_populated(self):
        p1 = Prompt(title="Test1", content="Content1")
        p2 = Prompt(title="Test2", content="Content2")
        self.store.create_prompt(p1)
        self.store.create_prompt(p2)
        result = self.store.get_all_prompts()
        assert len(result) == 2

    def test_update_prompt_existing(self):
        prompt = Prompt(title="Original", content="Content")
        self.store.create_prompt(prompt)
        updated = Prompt(
            id=prompt.id,
            title="Updated",
            content="New content",
            created_at=prompt.created_at,
        )
        result = self.store.update_prompt(prompt.id, updated)
        assert result is not None
        assert result.title == "Updated"

    def test_update_prompt_not_found(self):
        prompt = Prompt(title="Test", content="Content")
        result = self.store.update_prompt("nonexistent", prompt)
        assert result is None

    def test_delete_prompt_existing(self):
        prompt = Prompt(title="Test", content="Content")
        self.store.create_prompt(prompt)
        result = self.store.delete_prompt(prompt.id)
        assert result is True
        assert self.store.get_prompt(prompt.id) is None

    def test_delete_prompt_not_found(self):
        result = self.store.delete_prompt("nonexistent")
        assert result is False

    def test_get_prompts_by_collection(self):
        p1 = Prompt(title="T1", content="C1", collection_id="col-1")
        p2 = Prompt(title="T2", content="C2", collection_id="col-2")
        p3 = Prompt(title="T3", content="C3", collection_id="col-1")
        self.store.create_prompt(p1)
        self.store.create_prompt(p2)
        self.store.create_prompt(p3)
        result = self.store.get_prompts_by_collection("col-1")
        assert len(result) == 2

    def test_get_prompts_by_collection_no_match(self):
        p1 = Prompt(title="T1", content="C1", collection_id="col-1")
        self.store.create_prompt(p1)
        result = self.store.get_prompts_by_collection("col-999")
        assert result == []


class TestStorageCollections:
    """Tests for collection storage operations."""

    def setup_method(self):
        """Create a fresh storage instance for each test."""
        self.store = Storage()

    def test_create_collection_stores_and_returns(self):
        col = Collection(name="Test Collection")
        result = self.store.create_collection(col)
        assert result.id == col.id
        assert result.name == "Test Collection"

    def test_get_collection_existing(self):
        col = Collection(name="Test")
        self.store.create_collection(col)
        result = self.store.get_collection(col.id)
        assert result is not None
        assert result.name == "Test"

    def test_get_collection_not_found(self):
        result = self.store.get_collection("nonexistent")
        assert result is None

    def test_get_all_collections_empty(self):
        result = self.store.get_all_collections()
        assert result == []

    def test_get_all_collections_populated(self):
        c1 = Collection(name="Col1")
        c2 = Collection(name="Col2")
        self.store.create_collection(c1)
        self.store.create_collection(c2)
        result = self.store.get_all_collections()
        assert len(result) == 2

    def test_delete_collection_existing(self):
        col = Collection(name="Test")
        self.store.create_collection(col)
        result = self.store.delete_collection(col.id)
        assert result is True
        assert self.store.get_collection(col.id) is None

    def test_delete_collection_not_found(self):
        result = self.store.delete_collection("nonexistent")
        assert result is False


class TestStorageClear:
    """Tests for storage clear operation."""

    def test_clear_removes_all_data(self):
        store = Storage()
        store.create_prompt(Prompt(title="T", content="C"))
        store.create_collection(Collection(name="Col"))
        assert len(store.get_all_prompts()) == 1
        assert len(store.get_all_collections()) == 1

        store.clear()
        assert store.get_all_prompts() == []
        assert store.get_all_collections() == []


class TestStorageSingleton:
    """Tests for module-level storage instance."""

    def test_storage_instance_exists(self):
        assert storage is not None
        assert isinstance(storage, Storage)
