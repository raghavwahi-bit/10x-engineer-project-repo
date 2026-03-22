# PromptLab

**Professional AI Prompt Engineering Platform**

---

## Welcome to the Team! 👋

Congratulations on joining the PromptLab engineering team! You've been brought on to help us build the next generation of prompt engineering tools.

## Project Overview & Purpose

PromptLab is a state-of-the-art platform designed for AI engineers to effectively store, organize, and manage their prompts. Inspired by tools like Postman but for prompts, PromptLab offers a unified workspace where teams can:

- Store and manage prompt templates
- Organize prompts into easily navigable collections
- Tag and search through prompts efficiently
- Track comprehensive version histories
- Test prompts with sample inputs

The platform aims to streamline the prompt engineering process and enhance productivity for AI-focused teams.
---

## Features

- **Prompt Template Storage**: Save prompts with placeholders for dynamic input.
- **Organized Collections**: Group related prompts together for easy access.
- **Tagging System**: Create tags, assign them to prompts, and filter prompts by tags with AND logic.
- **Search**: Case-insensitive search across prompt titles and descriptions.
- **Version Control**: Maintain a history of changes to refine and track prompt evolution.
- **CI/CD**: GitHub Actions pipeline with linting (flake8) and test coverage enforcement (80%+).
- **Docker Support**: Containerized with Docker and Docker Compose for easy development and deployment.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/prompts` | List prompts (supports `collection_id`, `search`, `tags` filters) |
| POST | `/prompts` | Create a prompt |
| GET | `/prompts/{id}` | Get a prompt |
| PUT | `/prompts/{id}` | Full update a prompt |
| PATCH | `/prompts/{id}` | Partial update a prompt |
| DELETE | `/prompts/{id}` | Delete a prompt |
| GET | `/collections` | List collections |
| POST | `/collections` | Create a collection |
| GET | `/collections/{id}` | Get a collection |
| DELETE | `/collections/{id}` | Delete a collection |
| GET | `/tags` | List all tags |
| POST | `/tags` | Create a tag |
| GET | `/tags/{id}` | Get a tag |
| DELETE | `/tags/{id}` | Delete a tag |
| GET | `/prompts/{id}/tags` | Get tags for a prompt |
| POST | `/prompts/{id}/tags` | Add tags to a prompt |
| DELETE | `/prompts/{id}/tags/{tag_id}` | Remove a tag from a prompt |

For full details, see [docs/API_REFERENCE.md](docs/API_REFERENCE.md).

---

## Prerequisites & Installation

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional, for containerized development)
- Git for version control

### Installation

1. Clone the repository:

