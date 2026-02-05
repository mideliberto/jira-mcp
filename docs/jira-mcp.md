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
| `create_issue` | Create epic/task/subtask | `project`, `issue_type`, `summary`, `description`, `priority`, `assignee`, `labels`, `components`, `parent_key`, `epic_link` |
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

## Notes

- Priority values: "High", "Medium", "Low"
- Labels and components arrays replace existing values on update
- `delete_issue` requires `confirm_delete=True` (safety check)
- Subtasks must be deleted before their parent tasks
