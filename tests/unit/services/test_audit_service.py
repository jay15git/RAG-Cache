from app.services.audit_service import AuditService


def test_audit_redacts_pii_and_is_bounded():
    audit = AuditService(max_entries=1)
    event = audit.record({"query": "Email me at person@example.com; call +1 555-123-4567; key sk_test_123456789"})
    assert "person@example.com" not in event["query"]
    assert "555-123-4567" not in event["query"]
    assert "sk_test_123456789" not in event["query"]
    audit.record({"event": "second"})
    assert len(audit.recent()) == 1
