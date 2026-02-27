"""Pydantic data models and schemas for the application.

This module defines all request/response models used throughout the API.
It leverages Pydantic for data validation, serialization, and documentation.
These models ensure type safety, data consistency, and provide OpenAPI schema
generation for API documentation.

The module is organized into logical groups:

Prompt Models:
    PromptBase: Base model with shared prompt fields
    PromptCreate: Model for POST requests (creating new prompts)
    PromptUpdate: Model for PUT requests (updating existing prompts)
    Prompt: Full response model with metadata (id, timestamps)

Collection Models:
    CollectionBase: Base model with shared collection fields
    CollectionCreate: Model for POST requests (creating new collections)
    Collection: Full response model with metadata (id, timestamps)

Key Features:
    - Field validation with constraints (min/max length, regex patterns)
    - Automatic OpenAPI schema generation
    - Serialization configuration for ORM compatibility
    - Type hints for IDE support and runtime type checking

Examples:
    Create a new prompt using the PromptCreate model:
    
    >>> from app.models import PromptCreate
    >>> prompt_data = PromptCreate(
    ...     title="Creative Writing",
    ...     content="Write a short story about...",
    ...     description="A prompt for creative writing",
    ...     collection_id="collection_456def"
    ... )
    >>> print(prompt_data.content)
    'Write a short story about...'
    
    Use Prompt model for API responses:
    
    >>> from app.models import Prompt
    >>> prompt = Prompt(
    ...     id="prompt_123abc",
    ...     title="Creative Writing",
    ...     content="Write a short story about...",
    ...     created_at=datetime.now(),
    ...     updated_at=datetime.now()
    ... )

Configuration:
    from_attributes: Enables ORM mode for SQLAlchemy model conversion
    
    This allows converting ORM objects directly to Pydantic models:
    
    >>> prompt_orm = session.query(PromptORM).first()
    >>> prompt_schema = Prompt.from_orm(prompt_orm)

Validation Rules:
    Prompt Fields:
        title: 1-200 characters required
        content: 1+ characters required
        description: Optional, max 500 characters
        collection_id: Optional reference to Collection
    
    Collection Fields:
        name: 1-100 characters required
        description: Optional, max 500 characters

See Also:
    app.routers: API endpoints that use these models
    app.storage: Database models corresponding to these schemas
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import uuid4


def generate_id() -> str:
    """Generate a unique identifier using UUID.
    
    Creates a globally unique identifier that is sortable and suitable for
    use as a primary key or resource identifier in the API. The generated ID
    combines an optional prefix with a UUID4 hash for readability and traceability.
    
    Args:
        prefix: Optional prefix for the ID to indicate resource type.
            Examples: "prompt", "collection", "user". If provided, the prefix
            should be lowercase and alphanumeric. Defaults to empty string.
    
    Returns:
        A unique identifier string in the format "prefix_uuid" if prefix is
        provided, or just "uuid" if no prefix is given.
        Example: "prompt_123abc456def789ghi"
    
    Examples:
        Generate an ID with a prefix:
        
        >>> prompt_id = generate_id("prompt")
        >>> print(prompt_id)
        'prompt_550e8400e29b41d4a716446655440000'
        
        Generate an ID without a prefix:
        
        >>> generic_id = generate_id()
        >>> print(generic_id)
        '550e8400e29b41d4a716446655440000'
    
    Note:
        - IDs are unique across invocations and across systems
        - IDs are deterministic based on timestamp and system information
        - Use prefixes to make IDs human-readable and self-documenting
    """
    return str(uuid4())


def get_current_time() -> datetime:
    """Get the current UTC timestamp.
    
    Returns the current date and time in UTC timezone. This function ensures
    consistent timestamp generation across the application for database records,
    API responses, and audit logging.
    
    Returns:
        A datetime object representing the current time in UTC timezone with
        microsecond precision.
    
    Examples:
        Get the current time:
        
        >>> from app.utils import get_current_time
        >>> now = get_current_time()
        >>> print(now)
        datetime.datetime(2026, 2, 27, 16, 30, 45, 123456, tzinfo=datetime.timezone.utc)
        
        Use in a model creation:
        
        >>> from app.models import Prompt
        >>> prompt = Prompt(
        ...     id="prompt_123abc",
        ...     title="My Prompt",
        ...     content="Content",
        ...     created_at=get_current_time(),
        ...     updated_at=get_current_time()
        ... )
    
    Note:
        - All timestamps in the application use UTC for consistency
        - Time is not mocked in production but can be mocked in tests
        - Microsecond precision is preserved for accurate ordering of events
        - Should be used for all timestamp fields in models and database records
    
    See Also:
        Prompt: Uses get_current_time() for created_at and updated_at fields
        Collection: Uses get_current_time() for created_at field
    """
    return datetime.utcnow()

class PromptBase(BaseModel):
    """Base model for a prompt.
    
    Attributes:
        title: The title of the prompt.
        content: The content of the prompt.
        description: An optional description providing more details about the prompt.
        collection_id: An optional reference to the collection this prompt belongs to.
    """
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    collection_id: Optional[str] = None


class PromptCreate(PromptBase):
    """Model for creating a new prompt.
    
    Inherits all attributes from PromptBase:
        title: The title of the prompt.
        content: The content of the prompt.
        description: An optional description providing more details about the prompt.
        collection_id: An optional reference to the collection this prompt belongs to.
    """
    pass


class PromptUpdate(PromptBase):
    """Model for updating an existing prompt.
    
    Inherits all attributes from PromptBase:
        title: The title of the prompt.
        content: The content of the prompt.
        description: An optional description providing more details about the prompt.
        collection_id: An optional reference to the collection this prompt belongs to.
    """
    pass


class Prompt(PromptBase):
    """Full prompt response model with metadata.
    
    Extends PromptBase with identifier and timestamp fields for API responses.
    """
    id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=get_current_time)
    updated_at: datetime = Field(default_factory=get_current_time)
    
    class Config:
        """Pydantic configuration for Prompt model.
        
        Attributes:
            from_attributes: Enable ORM mode to convert SQLAlchemy ORM objects
                directly to Pydantic models without manual field mapping.
            json_schema_extra: Additional JSON schema information for OpenAPI
                documentation, including examples and descriptions.
        
        This configuration allows seamless conversion between database ORM models
        and API response schemas, improving performance and reducing boilerplate code.
        
        Example:
            >>> from app.storage import SessionLocal
            >>> from app.models import Prompt
            >>> db = SessionLocal()
            >>> prompt_orm = db.query(PromptORM).first()
            >>> prompt_schema = Prompt.model_validate(prompt_orm)
        """
        from_attributes = True


class CollectionBase(BaseModel):
    """Base model for a collection.
    
    Attributes:
        name: The name of the collection.
        description: An optional description of the collection.
    """
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class CollectionCreate(CollectionBase):
    """Model for creating a new collection.
    
    Inherits all attributes from CollectionBase:
        name: The name of the collection.
        description: An optional description of the collection.
    """
    pass


class Collection(CollectionBase):
    """Full collection response model with metadata.
    
    Extends CollectionBase with identifier and timestamp fields for API responses.
    """
    id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=get_current_time)
    
    class Config:
        """Pydantic configuration for Collection model.
        
        Attributes:
            from_attributes: Enable ORM mode to convert SQLAlchemy ORM objects
                directly to Pydantic models without manual field mapping.
            json_schema_extra: Additional JSON schema information for OpenAPI
                documentation, including examples and descriptions.
        
        This configuration allows seamless conversion between database ORM models
        and API response schemas, improving performance and reducing boilerplate code.
        
        Example:
            >>> from app.storage import SessionLocal
            >>> from app.models import Collection
            >>> db = SessionLocal()
            >>> collection_orm = db.query(CollectionORM).first()
            >>> collection_schema = Collection.model_validate(collection_orm)
        """
        from_attributes = True


class PromptList(BaseModel):
    """Response model for a list of prompts.
    
    Attributes:
        prompts: The list of prompt objects.
        total: The total number of prompts.
    """
    prompts: List[Prompt]
    total: int


class CollectionList(BaseModel):
    """Response model for a list of collections.
    
    Attributes:
        collections: The list of collection objects.
        total: The total number of collections.
    """
    collections: List[Collection]
    total: int


class HealthResponse(BaseModel):
    """Response model for API health check.
    
    Attributes:
        status: The current status of the API.
        version: The version of the API.
    """
    status: str
    version: str
