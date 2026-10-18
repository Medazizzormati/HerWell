"""
Tests for MCP server.
"""

import pytest
from app.mcp import get_mcp_server, HERwellMCPServer
from app.models import Resource
from app.database import SessionLocal


@pytest.fixture
def mcp_server():
    """Create MCP server instance."""
    return get_mcp_server()


@pytest.fixture
def sample_resources():
    """Create sample resources for testing."""
    db = SessionLocal()
    try:
        r1 = Resource(
            title="Stress Management Guide",
            category="wellbeing",
            content="This guide covers stress management techniques.",
            source_label="Test Source",
            source_url="https://example.com/stress",
            language="en",
            verification_status="internal",
            publication_date="2024-01-01"
        )
        r2 = Resource(
            title="Study Tips",
            category="academic",
            content="Effective study strategies for students.",
            source_label="Test Source",
            source_url="https://example.com/study",
            language="en",
            verification_status="internal",
            publication_date="2024-01-01"
        )
        db.add(r1)
        db.add(r2)
        db.commit()
        yield [r1, r2]
    finally:
        db.query(Resource).delete()
        db.commit()
        db.close()


def test_mcp_server_singleton():
    """Test that MCP server is a singleton."""
    server1 = get_mcp_server()
    server2 = get_mcp_server()
    assert server1 is server2


def test_get_tools(mcp_server):
    """Test that tools schema is returned correctly."""
    tools = mcp_server.get_tools()
    
    assert isinstance(tools, dict)
    assert "search_resources" in tools
    assert "get_resource_by_id" in tools
    assert "list_resource_categories" in tools
    assert "get_resource_count" in tools
    
    # Check tool schema structure
    search_tool = tools["search_resources"]
    assert "name" in search_tool
    assert "description" in search_tool
    assert "input_schema" in search_tool
    assert "properties" in search_tool["input_schema"]


def test_call_unknown_tool(mcp_server):
    """Test calling an unknown tool."""
    result = mcp_server.call_tool("unknown_tool", {})
    
    assert result["success"] is False
    assert "error" in result
    assert "available_tools" in result


def test_search_resources(mcp_server, sample_resources):
    """Test resource search."""
    result = mcp_server.call_tool("search_resources", {"query": "stress"})
    
    assert result["success"] is True
    assert "result" in result
    assert result["result"]["total_found"] >= 1
    assert len(result["result"]["results"]) >= 1


def test_search_resources_with_category(mcp_server, sample_resources):
    """Test resource search with category filter."""
    result = mcp_server.call_tool(
        "search_resources",
        {"query": "management", "category": "wellbeing"}
    )
    
    assert result["success"] is True
    assert "result" in result
    # Should filter to wellbeing category only
    for r in result["result"]["results"]:
        assert r["category"].lower() == "wellbeing"


def test_search_resources_limit(mcp_server, sample_resources):
    """Test resource search with limit."""
    result = mcp_server.call_tool(
        "search_resources",
        {"query": "test", "limit": 1}
    )
    
    assert result["success"] is True
    assert len(result["result"]["results"]) <= 1


def test_search_resources_limit_clamping(mcp_server):
    """Test that limit is clamped to valid range."""
    # Try with limit > 20
    result = mcp_server.call_tool(
        "search_resources",
        {"query": "stress", "limit": 100}
    )
    
    assert result["success"] is True
    assert len(result["result"]["results"]) <= 20
    
    # Try with limit < 1 (should be clamped to 1)
    result = mcp_server.call_tool(
        "search_resources",
        {"query": "stress", "limit": 0}
    )
    
    assert result["success"] is True
    # Just verify it doesn't crash, results may be 0 if no resources match


def test_get_resource_by_id(mcp_server, sample_resources):
    """Test getting resource by ID."""
    resource = sample_resources[0]
    result = mcp_server.call_tool(
        "get_resource_by_id",
        {"resource_id": resource.id}
    )
    
    assert result["success"] is True
    assert result["result"]["id"] == resource.id
    assert result["result"]["title"] == resource.title


def test_get_resource_by_id_not_found(mcp_server):
    """Test getting non-existent resource."""
    result = mcp_server.call_tool(
        "get_resource_by_id",
        {"resource_id": 99999}
    )
    
    assert result["success"] is True
    assert result["result"] is None


def test_list_resource_categories(mcp_server, sample_resources):
    """Test listing resource categories."""
    result = mcp_server.call_tool("list_resource_categories", {})
    
    assert result["success"] is True
    assert isinstance(result["result"], list)
    assert "wellbeing" in result["result"]
    assert "academic" in result["result"]


def test_get_resource_count(mcp_server, sample_resources):
    """Test getting resource count."""
    result = mcp_server.call_tool("get_resource_count", {})
    
    assert result["success"] is True
    assert "total_resources" in result["result"]
    assert result["result"]["total_resources"] >= 2


def test_tool_input_validation(mcp_server):
    """Test that tool input validation works."""
    # Missing required parameter
    result = mcp_server.call_tool("search_resources", {})
    
    assert result["success"] is False
    assert "error" in result


def test_search_resources_result_format(mcp_server, sample_resources):
    """Test that search results have correct format."""
    result = mcp_server.call_tool("search_resources", {"query": "stress"})
    
    assert result["success"] is True
    formatted = result["result"]["results"]
    
    if formatted:
        first = formatted[0]
        assert "title" in first
        assert "category" in first
        assert "content_preview" in first
        assert "source" in first
        assert "source_url" in first
        assert "language" in first
        assert "verification_status" in first
