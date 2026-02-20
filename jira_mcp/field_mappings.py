"""
Custom field mappings for Jira projects (PWP + CMA instances).

Maps cryptic customfield_XXXXX IDs to friendly names.
"""

from typing import Any

PROJECT_FIELDS = {
    'ITHELP': {
        'customfield_10055': 'work_type',
    },
    'ITCM': {
        'customfield_10055': 'work_type',
        'customfield_10059': 'risk_level',
        'customfield_10003': 'approvers',
        'customfield_10060': 'affected_systems',
        'customfield_10061': 'implementation_window_start',
        'customfield_10062': 'implementation_window_end',
        'customfield_10063': 'rollback_plan',
        'customfield_10068': 'approval_date',
    },
    'ITPROJ': {},
    'ITPMO': {},
    # =========================================================================
    # CMA instance — chicagomeat.atlassian.net
    # =========================================================================

    # IT — Service desk project (JSM)
    # Issue types: Task, Sub-task, Service request, Incident,
    #              Service request with approvals
    # Workflows:
    #   Task: Open → Work in progress → Pending → Done (also Reopened)
    #   Service request: Open → In Progress → Waiting for support →
    #     Waiting for customer → Escalated → Pending → Resolved → Closed → Canceled
    #   Incident: Open → Work in progress → Pending → Completed → Closed → Canceled
    'IT': {
        'customfield_10004': 'impact',                # Service desk impact level
        'customfield_10041': 'urgency',               # Service desk urgency
        'customfield_10048': 'severity',              # Incident severity
        'customfield_10087': 'category',              # Ticket categorization
        'customfield_10042': 'affected_services',     # Impacted services
        'customfield_10049': 'affected_hardware',     # Impacted hardware
        'customfield_10044': 'pending_reason',        # Why ticket is pending
        'customfield_10010': 'request_type',          # JSM request type
        'customfield_10002': 'organizations',         # Customer organizations
        'customfield_10034': 'request_participants',  # Additional participants
        'customfield_10045': 'major_incident',        # Major incident flag
        'customfield_10047': 'responders',            # Incident responders
        'customfield_10003': 'approvers',             # Approval chain
        'customfield_10035': 'satisfaction',           # CSAT rating
        'customfield_10021': 'flagged',               # Impediment flag
        'customfield_10001': 'team',                  # Team assignment
    },

    # ITPROJECT — Team-managed kanban project
    # Issue types: Task, Sub-task, Epic
    # Workflow: To Do → In Progress → Done
    #
    # IMPORTANT: ITPROJECT is team-managed. Epic hierarchy uses the `parent`
    # field, NOT customfield_10014 (epic_link). epic_link is not on the
    # ITPROJECT Task screen.
    # Use: create_issue(parent_key="ITPROJECT-XX") to link Tasks under an Epic.
    'ITPROJECT': {
        'customfield_10011': 'epic_name',     # Epic display name
        'customfield_10014': 'epic_link',     # NOT USED for team-managed — see note above
        'customfield_10015': 'start_date',    # Project start
        'customfield_10016': 'story_points',  # Estimation
        'customfield_10020': 'sprint',        # Sprint assignment
        'customfield_10021': 'flagged',       # Impediment flag
        'customfield_10001': 'team',          # Team assignment
    },
}


def get_field_mapping(project_key: str) -> dict[str, str]:
    """Get custom field mapping for a project."""
    return PROJECT_FIELDS.get(project_key, {})


def get_reverse_mapping(project_key: str) -> dict[str, str]:
    """Get reverse mapping (friendly name -> field ID) for a project."""
    mapping = get_field_mapping(project_key)
    return {v: k for k, v in mapping.items()}


def map_custom_fields(project_key: str, raw_fields: dict[str, Any]) -> dict[str, Any]:
    """
    Map custom fields from Jira response to friendly names.

    Args:
        project_key: Project the issue belongs to
        raw_fields: Raw fields dict from Jira API

    Returns:
        Dict with:
        - Mapped fields as top-level keys (work_type, risk_level, etc.)
        - Unknown custom fields in 'custom_fields' dict
    """
    mapping = get_field_mapping(project_key)
    result: dict[str, Any] = {}
    unmapped: dict[str, Any] = {}

    for field_id, value in raw_fields.items():
        if field_id.startswith('customfield_'):
            if value is not None:  # Skip null custom fields
                if field_id in mapping:
                    # Known field - use friendly name
                    result[mapping[field_id]] = value
                else:
                    # Unknown field - preserve raw
                    unmapped[field_id] = value

    if unmapped:
        result['custom_fields'] = unmapped

    return result


def reverse_map_fields(project_key: str, friendly_fields: dict[str, Any]) -> dict[str, Any]:
    """
    Map friendly field names back to customfield IDs for API calls.

    Used in create_issue and update_issue.
    """
    reverse = get_reverse_mapping(project_key)

    result: dict[str, Any] = {}
    for name, value in friendly_fields.items():
        if name in reverse:
            result[reverse[name]] = value
        else:
            # Pass through if not in mapping (could be raw customfield_XXXXX)
            result[name] = value

    return result
