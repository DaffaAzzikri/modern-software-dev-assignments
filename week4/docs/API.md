# API Documentation

## Overview
This document describes all available endpoints in the Modern Software Dev Backend API (Week 4).

## Endpoints

| Method | Endpoint | Description | Test Coverage |
|--------|----------|-------------|---|
| GET | `/` | Serves the frontend homepage (index.html) | ✅ |
| **Notes** | | | |
| GET | `/notes/` | List all notes | ✅ |
| POST | `/notes/` | Create a new note | ✅ |
| GET | `/notes/{note_id}` | Get a specific note by ID | ❌ |
| GET | `/notes/search/` | Search notes by keyword (query parameter `q`) | ✅ |
| **Action Items** | | | |
| GET | `/action-items/` | List all action items | ✅ |
| POST | `/action-items/` | Create a new action item | ✅ |
| PUT | `/action-items/{item_id}/complete` | Mark an action item as completed | ✅ |

## Request/Response Schema

### Notes
**NoteCreate (POST payload)**
```json
{
  "title": "string",
  "content": "string"
}
```

**NoteRead (Response)**
```json
{
  "id": "integer",
  "title": "string",
  "content": "string"
}
```

### Action Items
**ActionItemCreate (POST payload)**
```json
{
  "description": "string"
}
```

**ActionItemRead (Response)**
```json
{
  "id": "integer",
  "description": "string",
  "completed": "boolean"
}
```

## Status Codes
- `200` - OK
- `201` - Created
- `404` - Not Found
- `400` - Bad Request
