"""
Custom field mappings for PWP Jira projects.

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
