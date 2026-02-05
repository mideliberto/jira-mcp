# Jira MCP Usage Guide

Complete reference for all Jira MCP tools.

## Tool Reference

### search_issues

Search for Jira issues using JQL (Jira Query Language).

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| jql | string | Yes | - | JQL query string |
| max_results | int | No | 50 | Maximum results (max 100) |
| fields | list[str] | No | key, summary, status, assignee, created, updated | Fields to return |

**Example JQL queries:**
```
project = ITHELP AND status = Open
assignee = currentUser() AND resolution = Unresolved
text ~ "email migration"
created >= -7d
project = ITPROJ AND type = Epic
```

**Returns:**
```json
{
  "total": 5,
  "issues": [
    {
      "key": "ITHELP-11",
      "summary": "Approve XL.net invoice",
      "status": "Open",
      "assignee": "Mike Deliberto",
      "created": "2026-02-04T10:00:00.000-0600",
      "updated": "2026-02-04T12:00:00.000-0600"
    }
  ]
}
```

---

### get_issue

Get full details for a specific issue.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| issue_key | string | Yes | Issue key like "ITPROJ-123" |

**Returns:**
```json
{
  "key": "ITPROJ-42",
  "summary": "Q1 Email Migration",
  "description": "Migrate all users to Google Workspace",
  "status": {"name": "In Progress", "id": "10014"},
  "issue_type": "Epic",
  "priority": "High",
  "assignee": "Mike Deliberto",
  "reporter": "Mike Deliberto",
  "created": "2026-02-04T10:00:00.000-0600",
  "updated": "2026-02-04T15:00:00.000-0600",
  "labels": ["q1-2026", "migration"],
  "components": ["Infrastructure"],
  "resolution": null
}
```

---

### create_issue

Create a new issue with optional hierarchy (Epic → Task → Subtask).

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| project | string | Yes | Project key (ITPROJ, ITHELP) |
| issue_type | string | Yes | Issue type name |
| summary | string | Yes | Issue title |
| description | string | No | Issue description |
| priority | string | No | "High", "Medium", "Low" (default: Medium) |
| assignee | string | No | Email or account ID |
| labels | list[str] | No | Label names |
| components | list[str] | No | Component names |
| parent_key | string | No | Parent issue for Sub-task |
| epic_link | string | No | Epic key for Task |

**Issue Types by Project:**

ITPROJ:
- `Epic` - Top-level project container
- `Task` - Work item (can link to Epic via epic_link)
- `Sub-task` - Child of Task (requires parent_key)

ITHELP:
- `[System] Service request`
- `[System] Incident`
- `Question`

**Example: Create Epic with Tasks and Subtasks:**
```python
# 1. Create Epic
epic = create_issue(
    project="ITPROJ",
    issue_type="Epic",
    summary="Q1 Email Migration",
    description="Migrate all users from Exchange to Google Workspace"
)
# Returns: {"key": "ITPROJ-42", "url": "https://..."}

# 2. Create Task under Epic
task = create_issue(
    project="ITPROJ",
    issue_type="Task",
    summary="Phase 1: Planning",
    description="Document current state and requirements",
    epic_link="ITPROJ-42"
)
# Returns: {"key": "ITPROJ-43", "url": "https://..."}

# 3. Create Subtask under Task
subtask = create_issue(
    project="ITPROJ",
    issue_type="Sub-task",
    summary="Document current mailbox sizes",
    parent_key="ITPROJ-43"
)
# Returns: {"key": "ITPROJ-44", "url": "https://..."}
```

---

### update_issue

Update fields on an existing issue.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| issue_key | string | Yes | Issue key |
| summary | string | No | New title |
| description | string | No | New description |
| priority | string | No | "High", "Medium", "Low" |
| assignee | string | No | Email or account ID |
| labels | list[str] | No | Replaces existing labels |
| components | list[str] | No | Replaces existing components |

**Note:** At least one field must be provided.

**Returns:**
```json
{
  "key": "ITPROJ-42",
  "updated": "2026-02-04T16:00:00.000-0600"
}
```

---

### add_comment

Add a comment to an issue.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| issue_key | string | Yes | Issue key |
| body | string | Yes | Comment text |

**Returns:**
```json
{
  "comment_id": "10067",
  "created": "2026-02-04T16:30:00.000-0600"
}
```

---

### transition_issue

Move an issue through its workflow.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| issue_key | string | Yes | Issue key |
| transition_name | string | Yes | Target status (case-insensitive) |

**ITPROJ Workflow:**
```
Backlog → To Do → In Progress → In Review → Done
```

From "In Review", additional transitions:
- `Needs Change` → back to In Progress
- `Blocked`

**Returns:**
```json
{
  "key": "ITPROJ-42",
  "new_status": "In Progress",
  "transitioned": "2026-02-04T17:00:00.000-0600"
}
```

**Error (invalid transition):**
```
ValueError: Transition 'Done' not available for ITPROJ-42. Available: To Do, In Progress
```

---

### get_transitions

Get available transitions for an issue's current status.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| issue_key | string | Yes | Issue key |

**Returns:**
```json
[
  {"id": "3", "name": "In Progress"},
  {"id": "4", "name": "In Review"}
]
```

---

### delete_issue

⚠️ **PERMANENTLY delete an issue. Cannot be undone.**

For normal workflow, use `transition_issue` to move to "Done" instead.
This is for cleanup and testing only.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| issue_key | string | Yes | Issue key |
| confirm_delete | boolean | Yes | Must be `true` (safety check) |

**Note:** Subtasks must be deleted before their parent tasks.

**Returns:**
```json
{
  "key": "ITPROJ-50",
  "deleted": true,
  "deleted_at": "2026-02-05T02:46:10.029156+00:00"
}
```

**Error (without confirmation):**
```
ValueError: delete_issue requires confirm_delete=True. This will permanently
delete ITPROJ-50 and cannot be undone. Consider transition_issue to 'Done' instead.
```

---

## Common Workflows

### Project Decomposition

Transform a project spec into Jira hierarchy:

```
1. Create Epic for the project
2. Create Tasks for each phase
3. Create Subtasks for specific deliverables
4. Add comments with context from specs
```

### Issue Triage

Handle an informal request:

```
1. Search for existing similar issues
2. If duplicate: add comment to existing issue
3. If new: create issue with appropriate type
4. Set priority based on urgency
5. Assign if owner is clear
```

### Status Updates

Track progress:

```
1. Get issue details
2. Update description with new information
3. Transition to next status
4. Add comment documenting the change
```

---

## Tips

### JQL Shortcuts
- `currentUser()` - Your account
- `-7d` - Last 7 days
- `text ~ "keyword"` - Full text search
- `ORDER BY updated DESC` - Sort by recently updated

### Project Selection
- Use **ITPROJ** for project work with hierarchy
- Use **ITHELP** for service requests and incidents

### Workflow Notes
- Issues start in **Backlog** status
- Can't skip workflow steps (must follow sequence)
- **Done** has no further transitions
