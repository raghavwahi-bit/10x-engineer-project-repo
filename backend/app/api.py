"""API router and endpoint configuration for the application.

This module serves as the main entry point for all API routes. It aggregates
routers from different feature modules and configures them with appropriate
prefixes and tags for the FastAPI application.

The module is responsible for:
    - Registering feature routers (prompts, collections, etc.)
    - Setting route prefixes and OpenAPI tags
    - Organizing API structure and documentation
    - Providing centralized route management

Routers:
    prompts: Router for prompt-related endpoints (/api/prompts)
    collections: Router for collection-related endpoints (/api/collections)

Examples:
    Include the API router in a FastAPI application:
    
    >>> from fastapi import FastAPI
    >>> from app.api import router
    >>> 
    >>> app = FastAPI()
    >>> app.include_router(router, prefix="/api")
    
    Access API endpoints:
    
    >>> # GET /api/prompts
    >>> # POST /api/prompts
    >>> # GET /api/collections
    >>> # POST /api/collections

Attributes:
    router: APIRouter instance containing all API routes.

Note:
    All routes are prefixed with `/api` when included in the main application.
    Each feature router maintains its own prefix relative to the API prefix.
    OpenAPI tags are automatically generated from router configurations
    for organized API documentation.
    
    To add a new feature router:
    1. Create router in feature module (e.g., routers/new_feature.py)
    2. Import router in this module
    3. Include router with: router.include_router(feature_router, prefix="/path", tags=["tag"])

See Also:
    app.routers: Individual router modules for each feature
    app.main: Main FastAPI application entry point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.models import (
    Prompt, PromptCreate, PromptUpdate,
    Collection, CollectionCreate,
    PromptList, CollectionList, HealthResponse,
    get_current_time
)
from app.storage import storage
from app.utils import sort_prompts_by_date, filter_prompts_by_collection, search_prompts
from app import __version__


app = FastAPI(
    title="PromptLab API",
    description="AI Prompt Engineering Platform",
    version=__version__
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== Health Check ==============)

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
    search: Optional[str] = None
):
    """List all prompts with optional filters.
    
    Args:
        collection_id: Filter prompts by collection ID.
        search: Search term to filter prompts by title or content.
        
    Returns:
        PromptList: A list of prompts that match the filters.
    """
    prompts = storage.get_all_prompts()
    
    if collection_id:
        prompts = filter_prompts_by_collection(prompts, collection_id)
    
    if search:
        prompts = search_prompts(prompts, search)
    
    prompts = sort_prompts_by_date(prompts, descending=True)
    
    return PromptList(prompts=prompts, total=len(prompts))


@app.get("/prompts/{prompt_id}", response_model=Prompt)
def get_prompt(prompt_id: str):
    """Retrieve a specific prompt by its ID.
    
    Args:
        prompt_id: The unique identifier of the prompt.
        
    Returns:
        Prompt: The prompt object if found.
        
    Raises:
        HTTPException: If the prompt is not found.
    """
    if not prompt_id or not prompt_id.strip():
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    prompt = storage.get_prompt(prompt_id)
    
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    return prompt


@app.post("/prompts", response_model=Prompt, status_code=201)
def create_prompt(prompt_data: PromptCreate):
    """Create a new prompt.
    
    Args:
        prompt_data: Data for the new prompt.
        
    Returns:
        Prompt: The created prompt object.
        
    Raises:
        HTTPException: If the specified collection is not found.
    """
    if prompt_data.collection_id:
        collection = storage.get_collection(prompt_data.collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")
    
    prompt = Prompt(**prompt_data.model_dump())
    return storage.create_prompt(prompt)


@app.put("/prompts/{prompt_id}", response_model=Prompt)
def update_prompt(prompt_id: str, prompt_data: PromptUpdate):
    """Update an existing prompt.
    
    Args:
        prompt_id: The ID of the prompt to update.
        prompt_data: The updated data for the prompt.
        
    Returns:
        Prompt: The updated prompt object.
        
    Raises:
        HTTPException: If the prompt or collection is not found.
    """
    if not prompt_id or not prompt_id.strip():
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    existing = storage.get_prompt(prompt_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    if prompt_data.collection_id:
        collection = storage.get_collection(prompt_data.collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")
    
    updated_prompt = Prompt(
        id=existing.id,
        title=prompt_data.title,
        content=prompt_data.content,
        description=prompt_data.description,
        collection_id=prompt_data.collection_id,
        created_at=existing.created_at,
        updated_at=get_current_time()
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
        HTTPException: If the prompt or collection is not found.
    """
    if not prompt_id or not prompt_id.strip():
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    existing = storage.get_prompt(prompt_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    if prompt_data.collection_id:
        collection = storage.get_collection(prompt_data.collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")
    
    updated_prompt = Prompt(
        id=existing.id,
        title=prompt_data.title if prompt_data.title is not None else existing.title,
        content=prompt_data.content if prompt_data.content is not None else existing.content,
        description=prompt_data.description if prompt_data.description is not None else existing.description,
        collection_id=prompt_data.collection_id if prompt_data.collection_id is not None else existing.collection_id,
        created_at=existing.created_at,
        updated_at=get_current_time()
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
        raise HTTPException(status_code=400, detail="Collection is associated with existing prompts")
    
    storage.delete_collection(collection_id)
    return None
