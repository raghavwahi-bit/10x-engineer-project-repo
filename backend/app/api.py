"""FastAPI application with endpoints for prompts, collections, and tags.

This module defines all API endpoints for the PromptLab platform.

Endpoints:
    Health: GET /health
    Prompts: GET/POST /prompts, GET/PUT/PATCH/DELETE /prompts/{id}
    Prompt Run: POST /prompts/{id}/run
    Collections: GET/POST /collections, GET/DELETE /collections/{id}
    Tags: GET/POST /tags, GET/DELETE /tags/{id}
    Prompt-Tags: GET/POST /prompts/{id}/tags, DELETE /prompts/{id}/tags/{tag_id}
"""

import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app import __version__
from app.models import (
    Prompt,
    PromptCreate,
    PromptUpdate,
    Collection,
    CollectionCreate,
    PromptList,
    CollectionList,
    HealthResponse,
    Tag,
    TagCreate,
    TagList,
    PromptTagsResponse,
    AddTagsRequest,
    get_current_time,
)
from app.storage import storage
from app.utils import sort_prompts_by_date, filter_prompts_by_collection, search_prompts

app = FastAPI(
    title="PromptLab API",
    description="AI Prompt Engineering Platform",
    version=__version__,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== Helper Functions ==============


def _get_prompt_or_404(prompt_id: str) -> Prompt:
    """Retrieve a prompt or raise 404.

    Args:
        prompt_id: The unique identifier of the prompt.

    Returns:
        The Prompt object.

    Raises:
        HTTPException: 404 if prompt is not found.
    """
    if not prompt_id or not prompt_id.strip():
        raise HTTPException(status_code=404, detail="Prompt not found")
    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


def _validate_collection_exists(collection_id: Optional[str]) -> None:
    """Validate that a collection exists if an ID is provided.

    Args:
        collection_id: The collection ID to validate.

    Raises:
        HTTPException: 400 if collection is not found.
    """
    if collection_id:
        if not storage.get_collection(collection_id):
            raise HTTPException(status_code=400, detail="Collection not found")


# ============== Health Check ==============


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Check the API health status.

    Returns:
        HealthResponse: The current health status and version of the API.
    """
    return HealthResponse(status="healthy", version=__version__)


# ============== Prompt Endpoints ==============


@app.get("/prompts", response_model=PromptList)
def list_prompts(
    collection_id: Optional[str] = None,
    search: Optional[str] = None,
    tags: Optional[str] = None,
):
    """List all prompts with optional filters.

    Args:
        collection_id: Filter prompts by collection ID.
        search: Search term to filter prompts by title or content.
        tags: Comma-separated tag names to filter by (AND logic).

    Returns:
        PromptList: A list of prompts that match the filters.
    """
    prompts = storage.get_all_prompts()

    if collection_id:
        prompts = filter_prompts_by_collection(prompts, collection_id)

    if search:
        prompts = search_prompts(prompts, search)

    if tags:
        tag_names = [t.strip() for t in tags.split(",") if t.strip()]
        prompts = _filter_prompts_by_tags(prompts, tag_names)

    prompts = sort_prompts_by_date(prompts, descending=True)

    return PromptList(prompts=prompts, total=len(prompts))


def _filter_prompts_by_tags(prompts: list, tag_names: list) -> list:
    """Filter prompts that have ALL specified tags (AND logic).

    Args:
        prompts: List of prompts to filter.
        tag_names: List of tag names (case-insensitive).

    Returns:
        Filtered list of prompts having all specified tags.
    """
    tag_ids = set()
    for name in tag_names:
        tag = storage.get_tag_by_name(name)
        if tag:
            tag_ids.add(tag.id)
        else:
            return []

    result = []
    for prompt in prompts:
        prompt_tag_ids = {t.id for t in storage.get_tags_for_prompt(prompt.id)}
        if tag_ids.issubset(prompt_tag_ids):
            result.append(prompt)
    return result


@app.get("/prompts/{prompt_id}", response_model=Prompt)
def get_prompt(prompt_id: str):
    """Retrieve a specific prompt by its ID.

    Args:
        prompt_id: The unique identifier of the prompt.

    Returns:
        Prompt: The prompt object if found.

    Raises:
        HTTPException: 404 if the prompt is not found.
    """
    return _get_prompt_or_404(prompt_id)


@app.post("/prompts", response_model=Prompt, status_code=201)
def create_prompt(prompt_data: PromptCreate):
    """Create a new prompt.

    Args:
        prompt_data: Data for the new prompt.

    Returns:
        Prompt: The created prompt object.

    Raises:
        HTTPException: 400 if the specified collection is not found.
    """
    _validate_collection_exists(prompt_data.collection_id)
    prompt = Prompt(**prompt_data.model_dump())
    return storage.create_prompt(prompt)


@app.put("/prompts/{prompt_id}", response_model=Prompt)
def update_prompt(prompt_id: str, prompt_data: PromptUpdate):
    """Update an existing prompt (full replacement).

    Args:
        prompt_id: The ID of the prompt to update.
        prompt_data: The updated data for the prompt.

    Returns:
        Prompt: The updated prompt object.

    Raises:
        HTTPException: 404 if prompt not found, 400 if collection not found.
    """
    existing = _get_prompt_or_404(prompt_id)
    _validate_collection_exists(prompt_data.collection_id)

    updated_prompt = Prompt(
        id=existing.id,
        title=prompt_data.title,
        content=prompt_data.content,
        description=prompt_data.description,
        collection_id=prompt_data.collection_id,
        created_at=existing.created_at,
        updated_at=get_current_time(),
    )
    return storage.update_prompt(prompt_id, updated_prompt)


@app.patch("/prompts/{prompt_id}", response_model=Prompt)
def patch_prompt(prompt_id: str, prompt_data: PromptUpdate):
    """Partially update an existing prompt.

    Args:
        prompt_id: The ID of the prompt to update.
        prompt_data: The partial data for the prompt update.

    Returns:
        Prompt: The updated prompt object.

    Raises:
        HTTPException: 404 if prompt not found, 400 if collection not found.
    """
    existing = _get_prompt_or_404(prompt_id)
    _validate_collection_exists(prompt_data.collection_id)

    updated_prompt = Prompt(
        id=existing.id,
        title=prompt_data.title if prompt_data.title is not None else existing.title,
        content=(
            prompt_data.content if prompt_data.content is not None else existing.content
        ),
        description=(
            prompt_data.description
            if prompt_data.description is not None
            else existing.description
        ),
        collection_id=(
            prompt_data.collection_id
            if prompt_data.collection_id is not None
            else existing.collection_id
        ),
        created_at=existing.created_at,
        updated_at=get_current_time(),
    )
    return storage.update_prompt(prompt_id, updated_prompt)


@app.delete("/prompts/{prompt_id}", status_code=204)
def delete_prompt(prompt_id: str):
    """Delete a specific prompt.

    Args:
        prompt_id: The unique identifier of the prompt to delete.

    Raises:
        HTTPException: If the prompt is not found.
    """
    if not storage.delete_prompt(prompt_id):
        raise HTTPException(status_code=404, detail="Prompt not found")
    return None


@app.get("/collections", response_model=CollectionList)
def list_collections():
    """List all prompt collections.

    Returns:
        CollectionList: A list of available collections.
    """
    collections = storage.get_all_collections()
    return CollectionList(collections=collections, total=len(collections))


@app.get("/collections/{collection_id}", response_model=Collection)
def get_collection(collection_id: str):
    """Retrieve a specific collection by its ID.

    Args:
        collection_id: The unique identifier of the collection.

    Returns:
        Collection: The collection object if found.

    Raises:
        HTTPException: If the collection is not found.
    """
    collection = storage.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection


@app.post("/collections", response_model=Collection, status_code=201)
def create_collection(collection_data: CollectionCreate):
    """Create a new collection.

    Args:
        collection_data: Data for the new collection.

    Returns:
        Collection: The created collection object.
    """
    collection = Collection(**collection_data.model_dump())
    return storage.create_collection(collection)


@app.delete("/collections/{collection_id}", status_code=204)
def delete_collection(collection_id: str):
    """Delete a specific collection.

    Args:
        collection_id: The unique identifier of the collection to delete.

    Raises:
        HTTPException: If the collection is not found or is associated with prompts.
    """
    if not collection_id or not collection_id.strip():
        raise HTTPException(status_code=400, detail="Invalid collection ID")

    collection = storage.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    all_prompts = storage.get_all_prompts()
    prompts_in_collection = filter_prompts_by_collection(all_prompts, collection_id)

    if prompts_in_collection:
        raise HTTPException(
            status_code=400, detail="Collection is associated with existing prompts"
        )

    storage.delete_collection(collection_id)
    return None


# ============== Tag Endpoints ==============


@app.get("/tags", response_model=TagList)
def list_tags():
    """List all tags.

    Returns:
        TagList: A list of all available tags.
    """
    tags = storage.get_all_tags()
    return TagList(tags=tags, total=len(tags))


@app.post("/tags", response_model=Tag, status_code=201)
def create_tag(tag_data: TagCreate):
    """Create a new tag.

    Args:
        tag_data: Data for the new tag.

    Returns:
        Tag: The created tag object.

    Raises:
        HTTPException: 409 if a tag with the same name already exists.
    """
    existing = storage.get_tag_by_name(tag_data.name)
    if existing:
        raise HTTPException(status_code=409, detail="Tag already exists")

    tag = Tag(**tag_data.model_dump())
    return storage.create_tag(tag)


@app.get("/tags/{tag_id}", response_model=Tag)
def get_tag(tag_id: str):
    """Retrieve a specific tag by its ID.

    Args:
        tag_id: The unique identifier of the tag.

    Returns:
        Tag: The tag object if found.

    Raises:
        HTTPException: 404 if the tag is not found.
    """
    tag = storage.get_tag(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@app.delete("/tags/{tag_id}", status_code=204)
def delete_tag(tag_id: str):
    """Delete a specific tag.

    Args:
        tag_id: The unique identifier of the tag to delete.

    Raises:
        HTTPException: 404 if the tag is not found.
    """
    if not storage.delete_tag(tag_id):
        raise HTTPException(status_code=404, detail="Tag not found")
    return None


# ============== Prompt-Tag Endpoints ==============


@app.get("/prompts/{prompt_id}/tags", response_model=PromptTagsResponse)
def get_prompt_tags(prompt_id: str):
    """Get all tags associated with a prompt.

    Args:
        prompt_id: The unique identifier of the prompt.

    Returns:
        PromptTagsResponse: The tags associated with the prompt.

    Raises:
        HTTPException: 404 if the prompt is not found.
    """
    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    tags = storage.get_tags_for_prompt(prompt_id)
    return PromptTagsResponse(prompt_id=prompt_id, tags=tags, total_tags=len(tags))


@app.post("/prompts/{prompt_id}/tags", response_model=PromptTagsResponse)
def add_tags_to_prompt(prompt_id: str, request: AddTagsRequest):
    """Add tags to a prompt by tag names.

    Args:
        prompt_id: The unique identifier of the prompt.
        request: Request body containing tag names to add.

    Returns:
        PromptTagsResponse: The updated tags for the prompt.

    Raises:
        HTTPException: 404 if the prompt or any tag is not found.
    """
    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    for tag_name in request.tag_names:
        tag = storage.get_tag_by_name(tag_name)
        if not tag:
            raise HTTPException(status_code=404, detail=f"Tag '{tag_name}' not found")
        storage.add_tag_to_prompt(prompt_id, tag.id)

    tags = storage.get_tags_for_prompt(prompt_id)
    return PromptTagsResponse(prompt_id=prompt_id, tags=tags, total_tags=len(tags))


@app.delete("/prompts/{prompt_id}/tags/{tag_id}", status_code=204)
def remove_tag_from_prompt(prompt_id: str, tag_id: str):
    """Remove a tag from a prompt.

    Args:
        prompt_id: The unique identifier of the prompt.
        tag_id: The unique identifier of the tag to remove.

    Raises:
        HTTPException: 404 if the prompt is not found or tag is not associated.
    """
    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    if not storage.remove_tag_from_prompt(prompt_id, tag_id):
        raise HTTPException(status_code=404, detail="Tag not associated with prompt")
    return None


# ============== AI Run Endpoint ==============


class RunPromptRequest(BaseModel):
    """Request model for running a prompt with AI."""

    variables: Optional[dict] = None


class RunPromptResponse(BaseModel):
    """Response model for AI-generated output."""

    prompt_id: str
    output: str
    model: str


@app.post("/prompts/{prompt_id}/run", response_model=RunPromptResponse)
def run_prompt(prompt_id: str, request: RunPromptRequest = RunPromptRequest()):
    """Execute a prompt using the OpenAI API.

    Args:
        prompt_id: The unique identifier of the prompt.
        request: Optional variables to interpolate into the prompt content.

    Returns:
        RunPromptResponse: The AI-generated output.

    Raises:
        HTTPException: 404 if prompt not found, 500 if AI call fails,
                       400 if API key is not configured.
    """
    prompt = _get_prompt_or_404(prompt_id)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="OPENAI_API_KEY environment variable is not set",
        )

    content = prompt.content
    if request.variables:
        for key, value in request.variables.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": content}],
            max_tokens=1000,
        )
        output = response.choices[0].message.content
        return RunPromptResponse(prompt_id=prompt_id, output=output, model=model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI execution failed: {str(e)}")
