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
