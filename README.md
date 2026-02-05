# Jira MCP

MCP server for Jira Cloud integration, enabling Claude to manage PWP work items.

## Features

- **Search issues** with JQL (Jira Query Language)
- **Get issue details** with full context
- **Create issues** with full hierarchy support (Epic → Task → Subtask)
- **Update issues** - modify fields, priority, assignee
- **Add comments** to document decisions and progress
- **Transition issues** through workflow states
- **Get transitions** - discover available workflow options
- **Delete issues** - cleanup with safety confirmation (⚠️ permanent)

## Installation

```bash
cd ~/dev/jira-mcp

# Create virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .
```

## Configuration

### 1. Set up credentials

Generate an encryption key:
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Set the environment variable:
```bash
export JIRA_ENCRYPTION_KEY='your-generated-key'
```

Run the setup script:
```bash
python scripts/setup_credentials.py
```

### 2. Configure Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "jira-pwp": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/mike/dev/jira-mcp",
        "run",
        "jira-mcp"
      ],
      "env": {
        "JIRA_ENCRYPTION_KEY": "your-encryption-key"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

The Jira tools will appear in the tools panel.

## Quick Start

### Search for issues
```
Search for open issues in ITHELP
```

### Create an issue
```
Create a task in ITPROJ to review the Q1 budget
```

### Update an issue
```
Set ITPROJ-42 to high priority
```

### Transition an issue
```
Move ITPROJ-42 to In Progress
```

## Projects

| Project | Purpose | Issue Types |
|---------|---------|-------------|
| ITPROJ | IT Projects | Epic, Task, Sub-task |
| ITHELP | IT Help Desk | Service request, Incident, Question |
| ITCM | Change Management | (varies) |

## Documentation

- [USAGE.md](docs/USAGE.md) - Complete tool reference with examples
- [API-QUIRKS.md](docs/API-QUIRKS.md) - Jira API gotchas and field formats

## Development

```bash
# Run tests
python -m pytest tests/

# Test connection
python scripts/test_connection.py

# Run server directly
python -m jira_mcp.server
```

## License

MIT
