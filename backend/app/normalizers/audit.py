def normalize_audit_log_entry(entry):
    """Normalize an audit log entry for consistent output."""

    normalized_entry = {
        "id": entry.id,
        "action": entry.action,
        "timestamp": entry.timestamp.isoformat(),
        "user_id": entry.user_id,
        "details": entry.details,
        
    }
    return normalized_entry