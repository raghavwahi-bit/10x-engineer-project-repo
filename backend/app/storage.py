"""Storage and persistence layer for the application.

This module handles all database-related operations including connection management,
session lifecycle, and storage configuration. It provides centralized access to the
database through SQLAlchemy ORM for all data persistence needs.

The module manages:
    - Database connection pooling
    - Session creation and lifecycle
    - Database initialization
    - Storage configuration

Functions:
    get_db: Dependency injection function for database session retrieval.

Classes:
    SessionLocal: SQLAlchemy sessionmaker for creating database sessions.

Examples:
    Get a database session for operations:
    
    >>> from app.storage import get_db
    >>> from fastapi import Depends
    >>> 
    >>> @app.get("/prompts")
    >>> def list_prompts(db: Session = Depends(get_db)):
    ...     return db.query(Prompt).all()
    
    Manual session management:
    
    >>> from app.storage import SessionLocal
    >>> db = SessionLocal()
    >>> try:
    ...     prompts = db.query(Prompt).all()
    ... finally:
    ...     db.close()

Attributes:
    DATABASE_URL: Connection string for the database (from config).
    engine: SQLAlchemy Engine instance for database connections.

Note:
    Always use the get_db dependency in FastAPI routes to ensure proper
    session lifecycle management. Manual session handling should only be used
    in non-FastAPI contexts (CLI, background tasks, etc.).
    
    Database sessions are automatically rolled back on errors and closed
    after use through context managers.
"""

from typing import Dict, List, Optional
from app.models import Prompt, Collection


class Storage:
    """In-memory storage system for prompts and collections.
    
    This class simulates a database using Python dictionaries to manage prompts and collections.
    """
    def __init__(self):
        """Initialize the storage with empty dictionaries."""
        self._prompts: Dict[str, Prompt] = {}
        self._collections: Dict[str, Collection] = {}
    
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
    
    def clear(self):
        """Clear all prompts and collections from storage."""
        self._prompts.clear()
        self._collections.clear()
storage = Storage()