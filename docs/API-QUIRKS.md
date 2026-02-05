# Jira API Quirks

Discovered during jira-mcp implementation. These are deviations from documentation or unexpected behaviors.

## Endpoint Changes

### Search Endpoint Deprecated (410 Gone)
- **Old:** `/rest/api/3/search`
- **New:** `/rest/api/3/search/jql`
- **Discovered:** 2026-02-04
- **Impact:** Old endpoint returns 410 with migration message
- **Response format change:** New endpoint uses `nextPageToken` and `isLast` instead of `total` for pagination

Reference: https://developer.atlassian.com/changelog/#CHANGE-2046

## Field Formats

### Description (Atlassian Document Format)
Description field requires ADF, not plain text:
```json
{
  "description": {
    "type": "doc",
    "version": 1,
    "content": [
      {
        "type": "paragraph",
        "content": [
          {"type": "text", "text": "Your text here"}
        ]
      }
    ]
  }
}
```

### Comment Body
Same ADF format as description - plain text not accepted.

### Priority
Must be object with name, not just string:
```json
{"priority": {"name": "High"}}  // Correct
{"priority": "High"}            // Incorrect
```

### Assignee
Use `emailAddress` for email, `id` for account ID:
```json
{"assignee": {"emailAddress": "user@domain.com"}}
// or
{"assignee": {"id": "5f4dcc3b5aa765d61d8327deb882cf99"}}
```

## Custom Fields

### Epic Link
- Field ID: `customfield_10014`
- Value: Just the epic key as string
```json
{"customfield_10014": "ITPROJ-42"}
```

### Parent (for Subtasks)
- Field: `parent`
- Value: Object with key
```json
{"parent": {"key": "ITPROJ-43"}}
```

## Project-Specific

### ITHELP (Service Desk)
Issue types are service desk specific:
- `[System] Service request`
- `[System] Incident`
- `[System] Service request with approvals`
- `Question`
- `Scheduled Maintenance`

Does NOT have: Epic, Task, Sub-task, Bug, Story

### ITPROJ (Software Project)
Standard issue types:
- `Epic`
- `Task`
- `Sub-task`

Supports epic link and parent relationships.

### ITCM (Change Management)
Not explored yet.

## Required Fields

### ITPROJ
- `summary` - Required
- `description` - Required (will error if missing)
- `project` - Required
- `issuetype` - Required

## Response Codes

### Update Issue (PUT)
Returns `204 No Content` on success, not `200 OK` with body.

### Create Issue (POST)
Returns `201 Created` with:
```json
{
  "id": "10274",
  "key": "ITPROJ-38",
  "self": "https://..."
}
```

---

*Last updated: 2026-02-04*
