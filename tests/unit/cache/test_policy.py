from app.cache.policy import CachePolicy
from app.models.query import QueryRequest


def test_policy_classifies_query_types():
    assert CachePolicy.for_request(QueryRequest(query="What is Python?", tenant_id="a")).query_type == "stable"
    assert CachePolicy.for_request(QueryRequest(query="What is the latest price today?", tenant_id="a")).query_type == "time_sensitive"
    assert CachePolicy.for_request(QueryRequest(query="Classify this ticket", tenant_id="a")).query_type == "classification"
    assert CachePolicy.for_request(QueryRequest(query="Write a poem", tenant_id="a")).query_type == "creative"


def test_policy_isolates_namespace_and_key_context():
    from app.utils.hasher import generate_cache_key

    assert generate_cache_key("same", namespace="one") != generate_cache_key("same", namespace="two")
    assert generate_cache_key("same", model="a") != generate_cache_key("same", model="b")
    assert generate_cache_key("same", system_prompt_hash="a") != generate_cache_key("same", system_prompt_hash="b")
