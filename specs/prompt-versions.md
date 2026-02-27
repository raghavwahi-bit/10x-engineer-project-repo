# Prompt Versions Feature Specification

## Overview

The prompt versions feature enables users to track changes made to prompts over time. This allows users to:
- View the complete history of edits to a prompt
- Restore previous versions of a prompt
- Compare different versions to see what changed
- Understand who made changes and when
- Maintain an audit trail of prompt modifications

### Key Objectives
- **Non-destructive edits:** Preserve all previous versions of prompts
- **Easy restoration:** Quickly revert to any previous version
- **Change tracking:** Understand what changed between versions
- **Audit compliance:** Maintain complete history for compliance purposes

### Target Users
- Content creators who need to track prompt evolution
- Teams collaborating on prompt sets
- Administrators requiring audit trails
- Users who accidentally deleted content

---

## User Stories

### Story 1: View Prompt Version History
**As a** content creator
**I want to** view the complete version history of a prompt
**So that** I can understand how the prompt has evolved over time

**Acceptance Criteria:**
- [ ] When viewing a prompt, I can access a "Version History" tab
- [ ] The version history displays all versions in reverse chronological order (newest first)
- [ ] Each version entry shows: timestamp, version number, editor name, and change summary
- [ ] I can see the current (active) version is clearly marked
- [ ] The version list supports pagination for prompts with many versions

**Test Scenarios:**
- View history of prompt with 0 versions (current only)
- View history of prompt with 100+ versions
- Verify sorting and pagination work correctly

---

### Story 2: Compare Two Prompt Versions
**As a** content creator
**I want to** compare two different versions of a prompt side-by-side
**So that** I can understand exactly what changed between versions

**Acceptance Criteria:**
- [ ] I can select "Compare" from the version history
- [ ] A side-by-side diff view appears showing the two versions
- [ ] Changes are highlighted (additions in green, deletions in red, modifications in yellow)
- [ ] I can compare any version with any other version (not just consecutive)
- [ ] The diff view includes title, content, and description fields
- [ ] I can navigate back to the version history from the comparison view

**Test Scenarios:**
- Compare current version with first version
- Compare two middle versions
- Compare versions with identical content
- Compare versions with complete content replacement

---

### Story 3: Restore Previous Prompt Version
**As a** content creator
**I want to** restore a prompt to a previous version
**So that** I can undo unwanted changes quickly

**Acceptance Criteria:**
- [ ] In version history, each version has a "Restore" action button
- [ ] Clicking "Restore" shows a confirmation dialog with the version being restored
- [ ] Upon confirmation, the prompt is restored to that version
- [ ] Restoring creates a new version entry (doesn't overwrite history)
- [ ] The restoration is logged with my user ID and timestamp
- [ ] After restoration, the prompt is immediately updated in the UI
- [ ] A success message confirms the restoration

**Test Scenarios:**
- Restore from immediately previous version
- Restore from very old version
- Cancel restoration confirmation
- Verify new version is created on restore

---

### Story 4: Automatic Version Creation on Edit
**As a** system
**I want to** automatically create a new version when a prompt is modified
**So that** all changes are tracked without user effort

**Acceptance Criteria:**
- [ ] Each update to a prompt creates a new version automatically
- [ ] Version is created only if content actually changed (not on metadata-only changes initially)
- [ ] Version includes: timestamp, user ID, change summary
- [ ] Version numbering increments automatically (v1, v2, v3, etc.)
- [ ] Maximum 1000 versions per prompt (older versions can be archived)
- [ ] Version creation doesn't impact update performance

**Test Scenarios:**
- Update prompt title only
- Update prompt content only
- Update multiple fields simultaneously
- Rapid consecutive updates

---

### Story 5: View Version Details
**As a** content creator
**I want to** view all details of a specific version
**So that** I can see exactly what that version contained

**Acceptance Criteria:**
- [ ] Clicking a version in history shows its full content
- [ ] Version details include: all fields (title, content, description, collection_id)
- [ ] Version metadata includes: version number, timestamp, editor info
- [ ] A "Restore" button is available on the version detail view
- [ ] Navigation arrows allow moving between consecutive versions
- [ ] I can return to the current version easily

**Test Scenarios:**
- View current version details
- View oldest version details
- Navigate through versions sequentially

---

## Data Model Changes

### New Database Tables

#### `prompt_versions` table
```sql
CREATE TABLE prompt_versions (
    id VARCHAR(36) PRIMARY KEY,
    prompt_id VARCHAR(36) NOT NULL,
    version_number INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    content LONGTEXT NOT NULL,
    description VARCHAR(500),
    collection_id VARCHAR(36),
    created_by_user_id VARCHAR(36),  -- Future: link to User table
    created_at DATETIME NOT NULL,
    change_summary VARCHAR(255),  -- Auto-generated or user-provided
    
    -- Indexes for performance
    INDEX idx_prompt_id (prompt_id),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE
);
```

### Modified Database Tables

#### `prompts` table additions
```sql
ALTER TABLE prompts ADD COLUMN (
    version_count INTEGER DEFAULT 1,
    current_version_number INTEGER DEFAULT 1,
    is_version_controlled BOOLEAN DEFAULT TRUE
);
```

### New Pydantic Models

```python
# Base version model
class PromptVersionBase(BaseModel):
    """Base model for a prompt version."""
    version_number: int
    title: str
    content: str
    description: Optional[str]
    collection_id: Optional[str]
    change_summary: Optional[str]
    created_at: datetime
    created_by_user_id: Optional[str]

# Version response model
class PromptVersion(PromptVersionBase):
    """Model representing a prompt version."""
    id: str
    prompt_id: str

# Version list item (lightweight for history list)
class PromptVersionSummary(BaseModel):
    """Summary model for version history list."""
    version_number: int
    created_at: datetime
    created_by_user_id: Optional[str]
    change_summary: Optional[str]
    is_current: bool

# Version history list response
class PromptVersionHistory(BaseModel):
    """Response model for version history."""
    versions: List[PromptVersionSummary]
    total_versions: int
    prompt_id: str

# Version comparison
class VersionComparison(BaseModel):
    """Model for comparing two versions."""
    version_a: PromptVersion
    version_b: PromptVersion
    differences: Dict[str, Dict[str, Any]]  # Field -> {old, new}
```

---

## API Endpoint Specifications

### Base Path
All endpoints are prefixed with `/api/prompts/{prompt_id}/versions`

### 1. Get Version History
**GET** `/api/prompts/{prompt_id}/versions`

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| skip | integer | 0 | Number of versions to skip |
| limit | integer | 20 | Maximum versions to return (max 100) |
| order | string | desc | Sort order: `asc` or `desc` |

**Response (200 OK):**
```json
{
  "versions": [
    {
      "version_number": 3,
      "created_at": "2026-02-27T11:00:00Z",
      "created_by_user_id": "user_abc",
      "change_summary": "Updated content for clarity",
      "is_current": true
    },
    {
      "version_number": 2,
      "created_at": "2026-02-27T10:30:00Z",
      "created_by_user_id": "user_def",
      "change_summary": "Added examples",
      "is_current": false
    }
  ],
  "total_versions": 3,
  "prompt_id": "prompt_123abc"
}
```

**Error Responses:**
- 404: Prompt not found

---

### 2. Get Specific Version Details
**GET** `/api/prompts/{prompt_id}/versions/{version_number}`

**Response (200 OK):**
```json
{
  "id": "version_v3_prompt_123",
  "prompt_id": "prompt_123abc",
  "version_number": 3,
  "title": "Updated Prompt Title",
  "content": "This is the updated content...",
  "description": "Updated description",
  "collection_id": "collection_456def",
  "created_at": "2026-02-27T11:00:00Z",
  "created_by_user_id": "user_abc",
  "change_summary": "Updated content for clarity"
}
```

**Error Responses:**
- 404: Prompt or version not found

---

### 3. Compare Two Versions
**GET** `/api/prompts/{prompt_id}/versions/compare`

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| version_a | integer | true | First version number to compare |
| version_b | integer | true | Second version number to compare |

**Response (200 OK):**
```json
{
  "version_a": {
    "version_number": 2,
    "title": "Old Title",
    "content": "Old content here",
    "created_at": "2026-02-27T10:30:00Z"
  },
  "version_b": {
    "version_number": 3,
    "title": "Updated Title",
    "content": "Updated content here",
    "created_at": "2026-02-27T11:00:00Z"
  },
  "differences": {
    "title": {
      "old": "Old Title",
      "new": "Updated Title"
    },
    "content": {
      "old": "Old content here",
      "new": "Updated content here"
    }
  }
}
```

**Error Responses:**
- 404: Prompt or version not found
- 422: Invalid version numbers

---

### 4. Restore Prompt to Previous Version
**POST** `/api/prompts/{prompt_id}/versions/{version_number}/restore`

**Request Body:**
```json
{
  "reason": "Accidental deletion - restoring previous version"
}
```

**Response (200 OK):**
```json
{
  "id": "prompt_123abc",
  "title": "Restored Prompt Title",
  "content": "Restored content...",
  "description": "Restored description",
  "collection_id": "collection_456def",
  "created_at": "2026-02-27T09:00:00Z",
  "updated_at": "2026-02-27T12:00:00Z",
  "current_version_number": 4,
  "version_count": 4
}
```

**Response Headers:**
```
X-New-Version: 4
X-Restored-From-Version: 2
```

**Error Responses:**
- 404: Prompt or version not found
- 409: Cannot restore to current version

---

### 5. Get Current Version
**GET** `/api/prompts/{prompt_id}/versions/current`

**Response (200 OK):**
```json
{
  "id": "version_v3_prompt_123",
  "prompt_id": "prompt_123abc",
  "version_number": 3,
  "title": "Current Title",
  "content": "Current content...",
  "description": "Current description",
  "collection_id": "collection_456def",
  "created_at": "2026-02-27T11:00:00Z",
  "created_by_user_id": "user_abc",
  "change_summary": "Latest update"
}
```

---

### 6. Delete Version History (Admin)
**DELETE** `/api/prompts/{prompt_id}/versions`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| keep_latest | integer | Number of latest versions to keep (default: 10) |

**Response (204 No Content)**

---

## Edge Cases to Handle

### Data Integrity
1. **Version Number Gaps:** Ensure version numbers are sequential even if versions are deleted
   - Solution: Never expose gaps; renumber on cleanup

2. **Concurrent Edits:** Multiple users editing the same prompt simultaneously
   - Solution: Implement optimistic locking or last-write-wins with conflict detection

3. **Large Version History:** Prompts with 1000+ versions
   - Solution: Implement archival; support pagination; add query filters

### Restoration Scenarios
4. **Restore to Deleted Collection:** Restoring prompt to version with non-existent collection
   - Solution: Validate collection_id on restore; option to clear or update

5. **Restore Cycle:** User restores to old version, immediately restores back
   - Solution: Allow; each creates new version entry; provides full audit trail

6. **Concurrent Restoration:** Two users attempting restore simultaneously
   - Solution: Serialize with database transaction; second fails with conflict error

### Performance
7. **Large Content:** Versions with very large content (>10MB)
   - Solution: Compress versions in storage; implement lazy loading; consider archival

8. **Rapid Updates:** User makes 100 edits in 1 minute
   - Solution: Option for automatic version consolidation; batch processing

### Edge Cases in Comparison
9. **Compare Non-Existent Version:** User requests comparison with deleted version
   - Solution: Return 404 with clear error message

10. **Compare Same Version:** User compares version 3 with version 3
    - Solution: Return empty differences; show appropriate message in UI

### Data Migration
11. **Existing Prompts:** Adding versioning to prompts created before feature launch
    - Solution: Create v1 archive of all existing prompts; set current_version_number to 1

12. **User ID Missing:** Older prompts have NULL created_by_user_id
    - Solution: Allow NULL; display "Unknown" in UI; migrate when possible

### Cleanup and Maintenance
13. **Version Permanence:** Users concerned about storage/performance with many versions
    - Solution: Implement retention policy; allow selective deletion with warning

14. **Orphaned Versions:** Prompt deleted but versions remain in database
    - Solution: Foreign key cascade DELETE; versions automatically removed

### API Contract
15. **Backward Compatibility:** Existing API clients expect no version fields
    - Solution: Add version info only to new endpoints; maintain existing endpoint contracts

16. **Version Format Change:** Future need to change version numbering system
    - Solution: Use semantic versioning early (major.minor.patch) or alphanumeric IDs

---

## Implementation Timeline

### Phase 1 (MVP - Sprint 1)
- [ ] Database schema modifications
- [ ] Pydantic models for versioning
- [ ] Endpoints 1-4 (basic version CRUD)
- [ ] Automatic version creation on update

### Phase 2 (Sprint 2)
- [ ] Endpoint 5-6 (current version, cleanup)
- [ ] Version comparison logic
- [ ] UI for version history
- [ ] Basic tests

### Phase 3 (Sprint 3+)
- [ ] Performance optimization
- [ ] Advanced filtering/search
- [ ] Version tagging/labeling
- [ ] Comprehensive test coverage

---

## Testing Strategy

### Unit Tests
- Version number increment logic
- Change detection algorithm
- Restoration validation

### Integration Tests
- Full workflow: create → update → checkhistory → restore
- Concurrent edit handling
- Data integrity checks

### Performance Tests
- Handle 1000+ versions per prompt
- Comparison of large content
- Pagination performance

---

## Monitoring and Metrics

- Number of versions created per day
- Average history size per prompt
- Restoration frequency
- Performance of comparison queries
- Storage usage growth
