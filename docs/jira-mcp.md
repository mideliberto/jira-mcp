# jira-mcp Tool Reference

Jira Cloud integration server with 8 tools for managing work items.

## Prerequisites

- Jira Cloud account (pwphealth.atlassian.net)
- API token from https://id.atlassian.com/manage-profile/security/api-tokens
- See [README.md](../README.md) for setup instructions

---

## Search & Read (2 tools)

| Tool | Description | Parameters |
|------|-------------|------------|
| `search_issues` | Search with JQL | `jql`, `max_results`, `fields` |
| `get_issue` | Get full issue details | `issue_key` |

---

## Create & Update (3 tools)

| Tool | Description | Parameters |
|------|-------------|------------|
| `create_issue` | Create epic/task/subtask | `project`, `issue_type`, `summary`, `description`, `priority`, `assignee`, `labels`, `components`, `parent_key`, `epic_link`, `work_type`, `risk_level`, `approvers`, `affected_systems`, `implementation_window_start`, `implementation_window_end`, `rollback_plan`, `custom_fields` |
| `update_issue` | Update issue fields | `issue_key`, `summary`, `description`, `priority`, `assignee`, `labels`, `components` |
| `add_comment` | Add comment to issue | `issue_key`, `body` |

---

## Workflow (2 tools)

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_transitions` | Get available transitions | `issue_key` |
| `transition_issue` | Move through workflow | `issue_key`, `transition_name` |

---

## Delete (1 tool)

| Tool | Description | Parameters |
|------|-------------|------------|
| `delete_issue` | Permanently delete issue | `issue_key`, `confirm_delete` |

---

## Projects

| Project | Purpose | Issue Types |
|---------|---------|-------------|
| ITPROJ | IT Projects | Epic, Task, Sub-task |
| ITHELP | IT Help Desk | Service request, Incident, Question |
| ITCM | Change Management | (varies) |

---

## Workflows

### ITPROJ Workflow

```
Backlog → To Do → In Progress → In Review → Done
```

Additional transitions from In Review:
- `Needs Change` → back to In Progress
- `Blocked`

### Notes

- Issues start in **Backlog** status
- Can't skip workflow steps (must follow sequence)
- **Done** has no further transitions (terminal state)

---

## JQL Examples

```
project = ITHELP AND status = Open
assignee = currentUser() AND resolution = Unresolved
text ~ "email migration"
created >= -7d
project = ITPROJ AND type = Epic
ORDER BY updated DESC
```

---

## Issue Hierarchy

```
Epic (ITPROJ)
└── Task (epic_link → Epic key)
    └── Sub-task (parent_key → Task key)
```

**Creating hierarchy:**

```python
# 1. Create Epic
create_issue(project="ITPROJ", issue_type="Epic", summary="Q1 Migration")

# 2. Create Task under Epic
create_issue(project="ITPROJ", issue_type="Task", summary="Phase 1", epic_link="ITPROJ-42")

# 3. Create Subtask under Task
create_issue(project="ITPROJ", issue_type="Sub-task", summary="Document requirements", parent_key="ITPROJ-43")
```

---

## Custom Fields

PWP Jira projects use custom fields that vary by project. Use friendly parameter names instead of cryptic `customfield_XXXXX` IDs.

### ITHELP

| Parameter | Description | Values |
|-----------|-------------|--------|
| `work_type` | Work Type (required) | Hardware, Software, Access, Network, Security, Maintenance, Other |

```python
create_issue(
    project="ITHELP",
    issue_type="[System] Service request",
    summary="Printer not working",
    work_type="Hardware"
)
```

### ITCM (Change Management)

| Parameter | Description | Values |
|-----------|-------------|--------|
| `work_type` | Work Type | Hardware, Software, Access, Network, Security, Maintenance, Other |
| `risk_level` | Risk Level | Low, Medium, High |
| `approvers` | Approvers list | `[{"accountId": "..."}]` |
| `affected_systems` | Affected Systems | List of strings |
| `implementation_window_start` | Start time | ISO datetime |
| `implementation_window_end` | End time | ISO datetime |
| `rollback_plan` | Rollback Plan | Plain text |

```python
create_issue(
    project="ITCM",
    issue_type="Standard Change",
    summary="Deploy new monitoring agent",
    work_type="Software",
    risk_level="Low",
    rollback_plan="Uninstall agent via MDM"
)
```

### get_issue Returns Friendly Names

```python
issue = get_issue("ITCM-1")
# Returns:
{
    'key': 'ITCM-1',
    'summary': '...',
    'work_type': {'value': 'Software'},
    'risk_level': {'value': 'Low'},
    'custom_fields': {  # Unknown fields preserved here
        'customfield_10099': '...'
    }
}
```

### Escape Hatch

For unmapped fields, use `custom_fields` parameter with raw field IDs:

```python
create_issue(
    project="ITCM",
    issue_type="Standard Change",
    summary="...",
    custom_fields={"customfield_10099": {"value": "something"}}
)
```

---

## Notes

- Priority values: "High", "Medium", "Low"
- Labels and components arrays replace existing values on update
- `delete_issue` requires `confirm_delete=True` (safety check)
- Subtasks must be deleted before their parent tasks
