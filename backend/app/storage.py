"""In-memory storage layer for prompts, collections, and tags.

This module provides a simple dict-based storage system using the Storage class.
A module-level singleton instance `storage` is used throughout the application.

Data is stored in Python dictionaries and does not persist across restarts.

Classes:
    Storage: In-memory storage with CRUD operations for all resource types.

Attributes:
    storage: Module-level Storage singleton instance.
"""

from typing import Dict, List, Optional, Set
from app.models import Prompt, Collection, Tag


class Storage:
    """In-memory storage system for prompts and collections.

    Uses Python dictionaries to manage prompts, collections, and tags.
    """

    def __init__(self):
        """Initialize the storage with empty dictionaries."""
        self._prompts: Dict[str, Prompt] = {}
        self._collections: Dict[str, Collection] = {}
        self._tags: Dict[str, Tag] = {}
        self._prompt_tags: Dict[str, Set[str]] = {}

    def create_prompt(self, prompt: Prompt) -> Prompt:
        """Create a new prompt in storage.

        Args:
            prompt: The prompt object to store.

        Returns:
            The created prompt object.
        """
        self._prompts[prompt.id] = prompt
        return prompt

    def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """Retrieve a prompt by its ID.

        Args:
            prompt_id: The unique identifier of the prompt to retrieve.

        Returns:
            The Prompt object if found, None otherwise.
        """
        return self._prompts.get(prompt_id)

    def get_all_prompts(self) -> List[Prompt]:
        """Retrieve all prompts.

        Returns:
            A list of all prompt objects in storage.
        """
        return list(self._prompts.values())

    def update_prompt(self, prompt_id: str, prompt: Prompt) -> Optional[Prompt]:
        """Update an existing prompt in storage.

        Args:
            prompt_id: The ID of the prompt to update.
            prompt: The new prompt data.

        Returns:
            The updated Prompt object if successful, None if the prompt ID is not found.
        """
        if prompt_id not in self._prompts:
            return None
        self._prompts[prompt_id] = prompt
        return prompt

    def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt from storage.

        Args:
            prompt_id: The unique identifier of the prompt to delete.

        Returns:
            True if the prompt was successfully deleted, False otherwise.
        """
        if prompt_id in self._prompts:
            del self._prompts[prompt_id]
            return True
        return False

    def create_collection(self, collection: Collection) -> Collection:
        """Create a new collection in storage.

        Args:
            collection: The collection object to store.

        Returns:
            The created collection object.
        """
        self._collections[collection.id] = collection
        return collection

    def get_collection(self, collection_id: str) -> Optional[Collection]:
        """Retrieve a collection by its ID.

        Args:
            collection_id: The unique identifier of the collection to retrieve.

        Returns:
            The Collection object if found, None otherwise.
        """
        return self._collections.get(collection_id)

    def get_all_collections(self) -> List[Collection]:
        """Retrieve all collections.

        Returns:
            A list of all collection objects in storage.
        """
        return list(self._collections.values())

    def delete_collection(self, collection_id: str) -> bool:
        """Delete a collection from storage.

        Args:
            collection_id: The unique identifier of the collection to delete.

        Returns:
            True if the collection was successfully deleted, False otherwise.
        """
        if collection_id in self._collections:
            del self._collections[collection_id]
            return True
        return False

    def get_prompts_by_collection(self, collection_id: str) -> List[Prompt]:
        """Retrieve prompts associated with a specific collection.

        Args:
            collection_id: The ID of the collection to filter prompts by.

        Returns:
            A list of prompts associated with the specified collection.
        """
        return [p for p in self._prompts.values() if p.collection_id == collection_id]

    # ============== Tag Operations ==============

    def create_tag(self, tag: Tag) -> Tag:
        """Create a new tag in storage.

        Args:
            tag: The tag object to store.

        Returns:
            The created tag object.
        """
        self._tags[tag.id] = tag
        return tag

    def get_tag(self, tag_id: str) -> Optional[Tag]:
        """Retrieve a tag by its ID.

        Args:
            tag_id: The unique identifier of the tag.

        Returns:
            The Tag object if found, None otherwise.
        """
        return self._tags.get(tag_id)

    def get_tag_by_name(self, name: str) -> Optional[Tag]:
        """Retrieve a tag by name (case-insensitive).

        Args:
            name: The tag name to search for.

        Returns:
            The Tag object if found, None otherwise.
        """
        name_lower = name.lower()
        for tag in self._tags.values():
            if tag.name.lower() == name_lower:
                return tag
        return None

    def get_all_tags(self) -> List[Tag]:
        """Retrieve all tags.

        Returns:
            A list of all tag objects in storage.
        """
        return list(self._tags.values())

    def delete_tag(self, tag_id: str) -> bool:
        """Delete a tag from storage and remove all prompt associations.

        Args:
            tag_id: The unique identifier of the tag to delete.

        Returns:
            True if the tag was successfully deleted, False otherwise.
        """
        if tag_id not in self._tags:
            return False
        del self._tags[tag_id]
        for prompt_id in self._prompt_tags:
            self._prompt_tags[prompt_id].discard(tag_id)
        return True

    def add_tag_to_prompt(self, prompt_id: str, tag_id: str) -> bool:
        """Associate a tag with a prompt.

        Args:
            prompt_id: The ID of the prompt.
            tag_id: The ID of the tag to add.

        Returns:
            True if the tag was added, False if already associated.
        """
        if prompt_id not in self._prompt_tags:
            self._prompt_tags[prompt_id] = set()
        if tag_id in self._prompt_tags[prompt_id]:
            return False
        self._prompt_tags[prompt_id].add(tag_id)
        return True

    def remove_tag_from_prompt(self, prompt_id: str, tag_id: str) -> bool:
        """Remove a tag association from a prompt.

        Args:
            prompt_id: The ID of the prompt.
            tag_id: The ID of the tag to remove.

        Returns:
            True if the tag was removed, False if not associated.
        """
        if prompt_id not in self._prompt_tags:
            return False
        if tag_id not in self._prompt_tags[prompt_id]:
            return False
        self._prompt_tags[prompt_id].discard(tag_id)
        return True

    def get_tags_for_prompt(self, prompt_id: str) -> List[Tag]:
        """Get all tags associated with a prompt.

        Args:
            prompt_id: The ID of the prompt.

        Returns:
            A list of Tag objects associated with the prompt.
        """
        tag_ids = self._prompt_tags.get(prompt_id, set())
        return [self._tags[tid] for tid in tag_ids if tid in self._tags]

    def get_prompts_by_tag(self, tag_id: str) -> List[Prompt]:
        """Get all prompts that have a specific tag.

        Args:
            tag_id: The ID of the tag.

        Returns:
            A list of prompts with the specified tag.
        """
        prompt_ids = [pid for pid, tids in self._prompt_tags.items() if tag_id in tids]
        return [self._prompts[pid] for pid in prompt_ids if pid in self._prompts]

    def clear(self):
        """Clear all data from storage."""
        self._prompts.clear()
        self._collections.clear()
        self._tags.clear()
        self._prompt_tags.clear()


storage = Storage()
