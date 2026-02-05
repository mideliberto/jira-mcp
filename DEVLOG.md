# DEVLOG

## 2026-02-04

### Phase 1: Foundation - Auth and Connection
**Origin:** Chat decision
**Task:** Create repository structure, credential management, and basic Jira client
**Changes:**
- Created jira-mcp repository structure
- Implemented CredentialManager with Fernet+PBKDF2 encryption (adapted from google-mcp TokenManager)
- Implemented JiraClient with Basic Auth
- Created setup_credentials.py and test_connection.py scripts
- Verified connection to PWP Jira (pwphealth.atlassian.net)
**Commits:** e8f18bc
**Status:** Complete

### Phase 2: Read Operations - Search and Get Tools
**Origin:** Chat decision
**Task:** Implement search_issues and get_issue tools
**Changes:**
- Added search_issues() method using /rest/api/3/search/jql (old /search endpoint deprecated with 410)
- Added get_issue() method with full issue details
- Added _extract_description() for ADF to plain text conversion
- Created tools.py with search_issues_tool() and get_issue_tool() wrappers
- Created tests/test_search.py and tests/test_get.py
- Created scripts/test_phase2.py integration test
- Verified against ITHELP project (not IT as originally assumed)
**Commits:** 44a7aa1
**Status:** Complete
**Notes:** Jira API changed - /rest/api/3/search returns 410 Gone, must use /rest/api/3/search/jql

### Phase 3: Write Operations - Create, Update, Comment
**Origin:** Chat decision
**Task:** Implement create_issue, update_issue, and add_comment tools
**Changes:**
- Added create_issue() with epic/task/subtask hierarchy support
- Added update_issue() for field modifications
- Added add_comment() for issue comments
- Added _to_adf() helper for plain text to ADF conversion
- Epic link uses customfield_10014
- Parent for subtasks uses parent: {key: "..."}
- Created tests/test_create.py, test_update.py, test_comment.py
- Created scripts/test_phase3.py integration test
- Created docs/API-QUIRKS.md documenting field formats
- Verified full hierarchy creation in ITPROJ project
**Commits:** 150bdab
**Status:** Complete
**Notes:**
- Description field requires ADF format, not plain text
- ITHELP is service desk (no Epic/Task), ITPROJ has standard types
- Description is required in ITPROJ project

### Phase 4: Transitions - Workflow State Management
**Origin:** Chat decision
**Task:** Implement transition_issue tool for workflow state changes
**Changes:**
- Added get_transitions() method to discover available transitions
- Added transition_issue() with case-insensitive name matching
- Added get_transitions_tool() and transition_issue_tool() wrappers
- Created tests/test_transitions.py and scripts/test_phase4.py
- Updated API-QUIRKS.md with workflow documentation
- Verified full workflow: Backlog → To Do → In Progress → In Review → Done
**Commits:** e39cb5c
**Status:** Complete
**Notes:**
- Issues created in "Backlog" status by default
- Transitions require ID (API lookup by name)
- "Done" status has no available transitions (terminal state)

### Phase 5: MCP Server & Documentation - 8 Tools Complete
**Origin:** Chat decision
**Task:** Implement MCP server, complete documentation, add delete_issue
**Changes:**
- Created jira_mcp/server.py with FastMCP framework
- Registered 8 tools: search_issues, get_issue, create_issue, update_issue, add_comment, transition_issue, get_transitions, delete_issue
- Added delete_issue with confirm_delete safety check
- Created config/claude_desktop_config.json for Claude Desktop
- Created docs/USAGE.md with complete tool reference
- Updated README.md with setup instructions
- Created tests/integration/test_full_workflow.py
- Updated pyproject.toml with mcp dependency and jira-mcp entry point
**Commits:** ad8da4e
**Status:** Complete
**Notes:**
- get_transitions exposed as tool (deviation from 6-tool spec) for better UX
- delete_issue added as 8th tool per Mike's request
- Full integration test passes: Epic → Task → Subtask → Update → Comment → Transition → Done → Cleanup

### Phase 6: Vault Integration & GitHub
**Origin:** Chat decision
**Task:** Integrate with PWP vault, publish to GitHub
**Changes:**
- Created docs/jira-mcp.md tool reference (google-mcp format)
- Updated PWP vault .mcp.json with jira-pwp server config
- Updated PWP _claude/MCP-REFERENCE.md with Jira section
- Fixed mcp[cli] dependency (typer was missing)
- Removed spec file from git history (contained API token)
- Published to GitHub: github.com/mideliberto/jira-mcp
**Commits:** ff4bb79, 07adda9 (history rewritten)
**Status:** Complete
**Notes:**
- MCP config must use `.venv/bin/mcp run module:app` pattern (not uv)
- mcp[cli] extra required for typer dependency
- Spec file removed via git filter-branch to clear GitHub push protection

### Phase 7: Custom Fields Support
**Origin:** Chat decision
**Task:** Add custom_fields parameter for project-specific required fields
**Changes:**
- Added custom_fields parameter to create_issue() in jira_client.py
- Updated tools.py and server.py with custom_fields support
- Documented ITHELP Work Type (customfield_10055) example
- Custom field values require object format: {"value": "Software"}
**Commits:** fa301b6
**Status:** Complete
**Notes:**
- ITHELP requires Work Type field for ticket creation
- Work Type values: Hardware, Software, Access, Network, Security, Maintenance, Other
- Custom fields merge into Jira API request fields dict

### Phase 8: Friendly Field Name Mapping
**Origin:** GitHub Issue #1
**Task:** Map cryptic customfield_XXXXX IDs to friendly parameter names
**Changes:**
- Created jira_mcp/field_mappings.py with PROJECT_FIELDS mapping
- get_issue() returns work_type, risk_level, etc. instead of customfield_XXXXX
- create_issue() accepts work_type, risk_level, approvers, affected_systems,
  implementation_window_start/end, rollback_plan as named parameters
- Unknown custom fields preserved in 'custom_fields' dict
- Updated documentation with ITHELP and ITCM examples
**Commits:** 9d580d9
**Status:** Complete
**Notes:**
- ITHELP: work_type (customfield_10055)
- ITCM: work_type, risk_level, approvers, affected_systems, implementation_window_start/end, rollback_plan, approval_date
- custom_fields parameter remains as escape hatch for unmapped fields

### Phase 9: User Search Tool
**Origin:** GitHub Issue #2
**Task:** Add search_users tool for user lookup by name/email
**Changes:**
- Added search_users() to jira_client.py wrapping /rest/api/3/user/search
- Added search_users_tool() wrapper to tools.py
- Registered search_users MCP tool in server.py (now 9 tools)
- Updated documentation with usage examples
**Commits:** 5b08671
**Status:** Complete
**Notes:**
- Enables looking up account IDs for user fields (approvers, assignee)
- Search by full name, email, or partial match
- Returns accountId, displayName, emailAddress, active status
