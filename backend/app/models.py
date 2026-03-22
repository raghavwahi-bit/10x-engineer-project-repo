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
    """Generate a unique identifier using UUID4.

    Returns:
        A unique identifier string.

    Example:
        >>> id_val = generate_id()
        >>> len(id_val) > 0
        True
    """
    return str(uuid4())


def get_current_time() -> datetime:
    """Get the current UTC timestamp.

    Returns:
        A datetime object representing the current time in UTC.
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


# ============== Tag Models ==============


class TagBase(BaseModel):
    """Base model for a tag.

    Attributes:
        name: The tag name (alphanumeric, hyphens, underscores, 3-50 chars).
        description: An optional description of the tag.
    """

    name: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    description: Optional[str] = Field(None, max_length=500)


class TagCreate(TagBase):
    """Model for creating a new tag.

    Inherits all attributes from TagBase.
    """

    pass


class Tag(TagBase):
    """Full tag response model with metadata.

    Attributes:
        id: Unique identifier for the tag.
        created_at: Timestamp when the tag was created.
        usage_count: Number of prompts using this tag.
    """

    id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=get_current_time)
    usage_count: int = 0

    class Config:
        """Pydantic configuration for Tag model."""

        from_attributes = True


class TagList(BaseModel):
    """Response model for a list of tags.

    Attributes:
        tags: The list of tag objects.
        total: The total number of tags.
    """

    tags: List[Tag]
    total: int


class PromptTagsResponse(BaseModel):
    """Response model for tags associated with a prompt.

    Attributes:
        prompt_id: The ID of the prompt.
        tags: List of tags associated with the prompt.
        total_tags: Total number of tags.
    """

    prompt_id: str
    tags: List[Tag]
    total_tags: int


class AddTagsRequest(BaseModel):
    """Request model for adding tags to a prompt.

    Attributes:
        tag_names: List of tag names to add.
    """

    tag_names: List[str]
