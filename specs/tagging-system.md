# Tagging System Feature Specification

## Overview

The tagging system enables users to categorize and organize prompts using flexible, user-defined tags. This allows users to:
- Quickly identify and categorize prompts by topic, difficulty, use case, etc.
- Search and filter prompts using tags
- Organize prompts across multiple dimensions (not limited to single collections)
- Build hierarchical tag structures (parent-child relationships)
- Reuse and discover tags across the system

### Key Objectives
- **Flexible Organization:** Tags are independent of collections; a prompt can have many tags
- **Discoverability:** Help users find related prompts through tag search
- **Reusability:** Encourage standardized tagging across team
- **Performance:** Efficient tag queries and filtering
- **Governance:** Prevent tag proliferation; suggest existing tags

### Target Users
- Content creators organizing large prompt libraries
- Teams sharing prompts and tag vocabularies
- Users searching for specific prompt categories
- Administrators managing tag standards

---

## User Stories

### Story 1: Add Tags to a Prompt
**As a** content creator
**I want to** add one or more tags to a prompt
**So that** I can organize and categorize my prompts

**Acceptance Criteria:**
- [ ] When editing a prompt, I can add tags via a text input or dropdown
- [ ] I can add multiple tags to a single prompt
- [ ] Tags are case-insensitive but case-preserved in storage
- [ ] Existing tags show as suggestions when I start typing
- [ ] I can create new tags that don't exist yet
- [ ] Changes are saved when I save the prompt
- [ ] A prompt can have between 0 and 50 tags
- [ ] Tag names can contain letters, numbers, hyphens, underscores (3-50 chars)

**Test Scenarios:**
- Add tag that already exists in system
- Create new tag
- Add multiple tags at once
- Edit prompt and modify tags
- Add 50 tags to single prompt (max)
- Attempt to add 51st tag (should fail)

---

### Story 2: Search Prompts by Tags
**As a** content creator
**I want to** search for prompts using tags
**So that** I can quickly find prompts in a specific category

**Acceptance Criteria:**
- [ ] On the prompts list, I can filter by one or more tags
- [ ] Multiple tags work with AND logic (prompt must have all selected tags)
- [ ] Results update in real-time as I select/deselect tags
- [ ] I can see the count of prompts matching each tag
- [ ] Search results show which tags matched
- [ ] I can combine tag search with text search
- [ ] Clear filters button resets all selections
- [ ] Tag filter persists in URL for sharing

**Test Scenarios:**
- Filter by single tag
- Filter by multiple tags (AND logic)
- Combine tag and text search
- Search with non-existent tag
- Filter with no matching results
- Clear and reapply filters

---

### Story 3: Browse Tag Suggestions
**As a** content creator
**I want to** see available tags and their usage frequency
**So that** I can standardize my tagging and avoid duplicate tags

**Acceptance Criteria:**
- [ ] A tag browser/explorer view shows all system tags
- [ ] Each tag displays its usage count (number of prompts)
- [ ] Tags are sorted by usage (most used first)
- [ ] I can search within the tag list
- [ ] Tags are grouped by category (if hierarchical tagging implemented)
- [ ] Clicking a tag shows all prompts with that tag
- [ ] I can see tag descriptions (if admin-provided)
- [ ] Last used date is visible

**Test Scenarios:**
- Browse tags with 0 prompts (orphaned tags)
- Search tag browser
- Click tag to see related prompts
- Sort by name vs. usage

---

### Story 4: View Tag Statistics
**As a** team lead
**I want to** view statistics about tag usage
**So that** I can understand tagging patterns and encourage consistency

**Acceptance Criteria:**
- [ ] A tag statistics dashboard shows:
  - Most used tags
  - Least used tags (orphaned)
  - Tags created over time
  - Average tags per prompt
  - Tag growth trend
- [ ] Statistics can be filtered by date range
- [ ] Ability to identify problematic tags (typos, duplicates)
- [ ] Export statistics as CSV or JSON

**Test Scenarios:**
- View stats for system with few tags
- View stats for system with many tags
- Filter stats by date range

---

### Story 5: Remove Tags from Prompt
**As a** content creator
**I want to** remove tags from a prompt
**So that** I can update prompt categorization as needed

**Acceptance Criteria:**
- [ ] When editing a prompt, I can remove individual tags
- [ ] Bulk remove tags from multiple prompts
- [ ] Confirmation prompt before removing all tags from a prompt
- [ ] Removed tags do not delete the tag itself (unless orphaned)
- [ ] Changes are saved immediately
- [ ] Undo available (optional, Phase 2)

**Test Scenarios:**
- Remove single tag
- Remove all tags
- Cancel removal
- Remove from multiple prompts

---

### Story 6: Auto-Complete Tag Input
**As a** content creator
**I want to** auto-complete tag names as I type
**So that** I don't have to remember exact tag names

**Acceptance Criteria:**
- [ ] As I type, suggestions appear below the input
- [ ] Suggestions match typed characters
- [ ] Most frequently used matching tags appear first
- [ ] Keyboard navigation (arrow keys) to select suggestions
- [ ] Enter key to select highlighted suggestion
- [ ] Escape key to dismiss suggestions
- [ ] Minimum 2 characters before suggestions appear

**Test Scenarios:**
- Type common tag prefix
- Type unique characters
- Navigate suggestions with keyboard
- No suggestions match input

---

### Story 7: Hierarchical Tags (Optional - Phase 2)
**As an** administrator
**I want to** create parent-child tag relationships
**So that** I can organize tags hierarchically for better navigation

**Acceptance Criteria:**
- [ ] Create parent tags and child tags (e.g., "Difficulty" → ["beginner", "intermediate", "advanced"])
- [ ] Display tags hierarchically in browser
- [ ] Filter by parent or child tags
- [ ] Prevent circular tag relationships
- [ ] Migrate existing flat tags to hierarchy (optional)

---

## Data Model Changes

### New Database Tables

#### `tags` table
```sql
CREATE TABLE tags (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(500),
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    created_by_user_id VARCHAR(36),  -- Future: link to User table
    usage_count INTEGER DEFAULT 0,
    parent_tag_id VARCHAR(36),  -- For hierarchical tags (Phase 2)
    
    INDEX idx_name (name),
    INDEX idx_usage_count (usage_count),
    FOREIGN KEY (parent_tag_id) REFERENCES tags(id) ON DELETE SET NULL
);
```

#### `prompt_tags` junction table
```sql
CREATE TABLE prompt_tags (
    prompt_id VARCHAR(36) NOT NULL,
    tag_id VARCHAR(36) NOT NULL,
    added_at DATETIME NOT NULL,
    added_by_user_id VARCHAR(36),  -- Future
    
    PRIMARY KEY (prompt_id, tag_id),
    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    INDEX idx_tag_id (tag_id),
    INDEX idx_added_at (added_at)
);
```

### Pydantic Models

```python
# Base tag model
class TagBase(BaseModel):
    """Base model for a tag."""
    name: str = Field(..., min_length=3, max_length=50, 
                      regex="^[a-zA-Z0-9_-]+$", 
                      description="Tag name (alphanumeric, dash, underscore)")
    description: Optional[str] = Field(None, max_length=500)
    parent_tag_id: Optional[str] = None

# Tag response model
class Tag(TagBase):
    """Model representing a tag."""
    id: str
    created_at: datetime
    usage_count: int
    created_by_user_id: Optional[str]

# Tag with prompts count
class TagWithStats(Tag):
    """Tag model with usage statistics."""
    prompt_count: int
    last_used_at: Optional[datetime]

# Tag browser model
class TagBrowser(BaseModel):
    """Model for tag browse/explorer view."""
    tags: List[TagWithStats]
    total_count: int
    most_used: List[Tag]
    least_used: List[Tag]
    orphaned_tags: List[Tag]

# Tag statistics
class TagStatistics(BaseModel):
    """Model for tag statistics."""
    total_unique_tags: int
    total_tag_assignments: int
    average_tags_per_prompt: float
    most_used_tags: List[TagWithStats]
    least_used_tags: List[TagWithStats]
    tags_created_in_period: int
    growth_trend: List[Dict[str, Any]]

# Prompt with tags
class PromptWithTags(BaseModel):
    """Extended prompt model including tags."""
    id: str
    title: str
    content: str
    description: Optional[str]
    collection_id: Optional[str]
    tags: List[Tag]
    created_at: datetime
    updated_at: datetime
```

### Modified Models

```python
# Updated PromptCreate
class PromptCreate(PromptBase):
    """Model for creating a new prompt."""
    tags: Optional[List[str]] = Field(None, description="List of tag names")

# Updated PromptUpdate
class PromptUpdate(PromptBase):
    """Model for updating a prompt."""
    tags: Optional[List[str]] = Field(None, description="List of tag names")

# Updated Prompt response
class Prompt(PromptBase):
    """Model representing a prompt."""
    id: str
    tags: List[Tag] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
```

---

## API Endpoint Specifications

### Base Paths
- Tag management: `/api/tags`
- Prompt tags: `/api/prompts/{prompt_id}/tags`
- Search: `/api/prompts/search`

### 1. List All Tags
**GET** `/api/tags`

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| skip | integer | 0 | Number of tags to skip |
| limit | integer | 50 | Maximum tags to return |
| sort | string | usage | Sort by: `usage`, `name`, `created` |
| order | string | desc | `asc` or `desc` |
| search | string | | Filter tags by name |

**Response (200 OK):**
```json
{
  "tags": [
    {
      "id": "tag_abc123",
      "name": "creative-writing",
      "description": "Prompts for creative writing tasks",
      "usage_count": 42,
      "created_at": "2026-02-20T10:00:00Z",
      "created_by_user_id": "user_xyz",
      "prompt_count": 42,
      "last_used_at": "2026-02-27T15:30:00Z"
    }
  ],
  "total_count": 156
}
```

---

### 2. Create Tag
**POST** `/api/tags`

**Request Body:**
```json
{
  "name": "creative-writing",
  "description": "Prompts for creative writing tasks",
  "parent_tag_id": null
}
```

**Response (201 Created):**
```json
{
  "id": "tag_abc123",
  "name": "creative-writing",
  "description": "Prompts for creative writing tasks",
  "usage_count": 0,
  "created_at": "2026-02-27T16:00:00Z",
  "created_by_user_id": "user_xyz"
}
```

**Error Responses:**
- 409: Tag name already exists
- 422: Invalid tag name format

---

### 3. Get Tag Details
**GET** `/api/tags/{tag_id}`

**Response (200 OK):**
```json
{
  "id": "tag_abc123",
  "name": "creative-writing",
  "description": "Prompts for creative writing tasks",
  "usage_count": 42,
  "created_at": "2026-02-20T10:00:00Z",
  "created_by_user_id": "user_xyz",
  "prompt_count": 42,
  "last_used_at": "2026-02-27T15:30:00Z",
  "related_tags": [
    {
      "id": "tag_def456",
      "name": "storytelling",
      "usage_count": 28
    }
  ]
}
```

---

### 4. Update Tag
**PUT** `/api/tags/{tag_id}`

**Request Body:**
```json
{
  "name": "creative-writing",
  "description": "Updated description for creative writing prompts"
}
```

**Response (200 OK):**
```json
{
  "id": "tag_abc123",
  "name": "creative-writing",
  "description": "Updated description for creative writing prompts",
  "updated_at": "2026-02-27T16:30:00Z"
}
```

---

### 5. Delete Tag
**DELETE** `/api/tags/{tag_id}`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| force | boolean | Force delete even if used by prompts |

**Response (204 No Content)**

**Error Responses:**
- 409: Tag is used by prompts (if force=false)

---

### 6. Get Prompts by Tag
**GET** `/api/tags/{tag_id}/prompts`

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| skip | integer | 0 | Number of prompts to skip |
| limit | integer | 20 | Maximum prompts to return |
| sort | string | created | Sort by: `created`, `updated`, `title` |

**Response (200 OK):**
```json
{
  "tag": {
    "id": "tag_abc123",
    "name": "creative-writing"
  },
  "prompts": [
    {
      "id": "prompt_123",
      "title": "Write a Story",
      "tags": ["creative-writing", "beginner"]
    }
  ],
  "total_count": 42
}
```

---

### 7. Add Tags to Prompt
**POST** `/api/prompts/{prompt_id}/tags`

**Request Body:**
```json
{
  "tag_names": ["creative-writing", "beginner", "fiction"]
}
```

**Response (200 OK):**
```json
{
  "prompt_id": "prompt_123",
  "tags": [
    {
      "id": "tag_abc123",
      "name": "creative-writing"
    },
    {
      "id": "tag_def456",
      "name": "beginner"
    }
  ],
  "total_tags": 2
}
```

**Error Responses:**
- 404: Prompt not found
- 422: Invalid tag names

---

### 8. Remove Tag from Prompt
**DELETE** `/api/prompts/{prompt_id}/tags/{tag_id}`

**Response (204 No Content)**

---

### 9. Replace All Tags for Prompt
**PUT** `/api/prompts/{prompt_id}/tags`

**Request Body:**
```json
{
  "tag_names": ["new-tag-1", "new-tag-2"]
}
```

**Response (200 OK):**
```json
{
  "prompt_id": "prompt_123",
  "tags": [
    {
      "id": "tag_xyz789",
      "name": "new-tag-1"
    }
  ],
  "total_tags": 1
}
```

---

### 10. Search Prompts by Tags
**GET** `/api/prompts`

**Extended Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| tags | string | Comma-separated tag IDs or names (AND logic) |
| tags_any | string | Comma-separated tags (OR logic, optional Phase 2) |
| exclude_tags | string | Exclude prompts with these tags |
| q | string | Text search in title/content |

**Response (200 OK):**
```json
{
  "prompts": [
    {
      "id": "prompt_123",
      "title": "Write a Story",
      "tags": [
        {
          "id": "tag_abc123",
          "name": "creative-writing"
        }
      ]
    }
  ],
  "matching_tags": ["creative-writing"],
  "total_count": 5,
  "filters_applied": {
    "tags": ["creative-writing"]
  }
}
```

---

### 11. Get Tag Statistics
**GET** `/api/tags/statistics`

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| date_from | string | 30 days ago | Start date for statistics |
| date_to | string | today | End date for statistics |

**Response (200 OK):**
```json
{
  "total_unique_tags": 156,
  "total_tag_assignments": 2847,
  "average_tags_per_prompt": 3.2,
  "most_used_tags": [
    {
      "id": "tag_abc123",
      "name": "creative-writing",
      "usage_count": 127
    }
  ],
  "least_used_tags": [
    {
      "id": "tag_xyz789",
      "name": "niche-topic",
      "usage_count": 1
    }
  ],
  "orphaned_tags": [...],
  "tags_created_in_period": 12,
  "growth_trend": [
    {
      "date": "2026-02-20",
      "count": 150
    }
  ]
}
```

---

### 12. Get Tag Suggestions
**GET** `/api/tags/suggest`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| q | string | Partial tag name |
| limit | integer | Max suggestions (default: 10) |
| used_only | boolean | Only show tags already in use |

**Response (200 OK):**
```json
{
  "suggestions": [
    {
      "id": "tag_abc123",
      "name": "creative-writing",
      "usage_count": 42
    },
    {
      "id": "tag_def456",
      "name": "creative-nonfiction",
      "usage_count": 15
    }
  ]
}
```

---

## Search/Filter Requirements

### Search Functionality

1. **Tag Search (Basic)**
   - Filter by single tag: `/api/prompts?tags=creative-writing`
   - Filter by multiple tags (AND): `/api/prompts?tags=creative-writing,beginner`
   - Show count of results

2. **Combined Search**
   - Text + tags: `/api/prompts?q=story&tags=creative-writing`
   - Exclude tags: `/api/prompts?tags=creative-writing&exclude_tags=advanced`

3. **Advanced Filters (Phase 2)**
   - OR logic: `/api/prompts?tags_any=creative-writing,technical`
   - Tag hierarchy: `/api/prompts?tags=difficulty:beginner`
   - Date range: `/api/prompts?tags=creative-writing&created_after=2026-02-01`

### Filtering Features

1. **UI Filters**
   - Multi-select dropdown for tags
   - Live count updates as selections change
   - Clear all filters button
   - Save filter presets

2. **Filter Persistence**
   - Store filters in URL for shareability
   - Remember filters in session
   - Save favorite filter combinations (Phase 2)

3. **Search Performance**
   - Index `prompt_tags` table for fast queries
   - Cache tag usage counts
   - Lazy load counting on large result sets
   - Limit result set to 1000 prompts

### Filter Logic

```
Single Tag: Prompt must have tag
Multiple Tags: Prompt must have ALL tags (AND logic)
Exclude Tags: Prompt must NOT have these tags
Text + Tags: Prompt must match text AND have tags

Examples:
- tags: creative-writing → filters to prompts with this tag
- tags: creative-writing,beginner → only prompts having BOTH tags
- tags: creative-writing & exclude_tags: advanced → prompts with creative-writing but WITHOUT advanced
- q: story & tags: creative-writing → prompts containing "story" AND tagged with creative-writing
```

---

## Edge Cases to Handle

### Data Integrity
1. **Duplicate Tags:** Users create tags: "creative-writing", "Creative-Writing", "CREATIVE-WRITING"
   - Solution: Case-insensitive unique constraint; normalize to lowercase internally, display original case

2. **Orphaned Tags:** Tags with 0 prompts after prompt deletion
   - Solution: Allow orphaned tags; provide tag cleanup utility; show in statistics

3. **Circular Dependencies:** Creating parent-child tag relationships that create cycles
   - Solution: Validate hierarchy in create/update; prevent circular references

### Search Edge Cases
4. **Special Characters in Tag Names:** Users attempt "tag@name", "tag#1", spaces
   - Solution: Restrict to alphanumeric, dash, underscore only; enforce via regex

5. **Tag Name Normalization:** "Python" vs "python" vs "PYTHON"
   - Solution: Store in lowercase; display original; handle case-insensitive matching

6. **Very Long Queries:** User selects 50 tags for filtering
   - Solution: Limit to 20 tags in single query; handle via URL properly

### Performance
7. **High-Volume Tag Assignment:** Creating prompt with 50 tags simultaneously
   - Solution: Batch insert into prompt_tags; transaction handling

8. **Tag Count Accuracy:** Concurrent tag additions/removals affecting usage_count
   - Solution: Use atomic database operations; eventual consistency acceptable

### User Experience
9. **Tag Suggestions Overload:** System has 10,000 tags and user types "t"
   - Solution: Require minimum 2 characters before suggestions; limit to 20 suggestions

10. **Accidental Tag Deletion:** User deletes tag that many prompts use
    - Solution: Require confirmation; show impact count; option to reassign

### Migration
11. **Existing Data Without Tags:** Adding tags to system with existing prompts
    - Solution: Allow prompts with 0 tags; no migration required

12. **Tag Naming Conflicts:** Creating system with 100K tags, legacy system has different names
    - Solution: Merge/alias feature for tag consolidation

---

## Implementation Timeline

### Phase 1 (MVP - Sprint 1-2)
- [ ] Database schema (tags, prompt_tags tables)
- [ ] Pydantic models
- [ ] Endpoints 1-9 (CRUD operations)
- [ ] Basic search (single tag filter)
- [ ] Tag suggestions
- [ ] Unit tests

### Phase 2 (Sprint 3-4)
- [ ] Endpoint 10-12 (statistics, advanced search)
- [ ] Tag browser UI
- [ ] Advanced filters (OR logic, exclusions)
- [ ] Hierarchical tags (parent-child)
- [ ] Integration tests

### Phase 3 (Future)
- [ ] Tag aliases/synonyms
- [ ] Tag hierarchies UI
- [ ] Advanced analytics
- [ ] Tag-based prompt recommendations
- [ ] Bulk tagging operations

---

## Testing Strategy

### Unit Tests
- Tag name validation (regex, length, uniqueness)
- Duplicate tag prevention
- Orphaned tag detection

### Integration Tests
- Full workflow: create tag → add to prompt → search by tag
- Multiple tag filtering (AND logic)
- Remove tag from prompt
- Delete tag with related prompts

### Performance Tests
- Search with 10,000+ tags
- Filter 1000+ prompts by tags
- Concurrent tag modifications
- Tag suggestion performance

### Data Integrity Tests
- Cascade delete when tag removed
- Usage count accuracy
- Orphaned tag cleanup

---

## Monitoring and Metrics

- Number of unique tags created
- Average tags per prompt
- Tag search usage frequency
- Most/least used tags
- Orphaned tag count
- Tag mutation rate (new/modified/deleted)
- Search query performance
- Usage count accuracy

---

## Future Enhancements

1. **Tag Aliases:** Map multiple tag names to single tag
2. **Tag Hierarchy:** Parent-child relationships with depth limiting
3. **Tag Recommendations:** Suggest tags based on prompt content
4. **Bulk Operations:** Add tags to multiple prompts at once
5. **Tag Merging:** Combine similar/duplicate tags
6. **Team Tags:** Shared vs. personal tags
7. **Tag Permissions:** Control who can create/modify tags
8. **Tag Workflow:** Tags for status (in-review, approved, deprecated)
