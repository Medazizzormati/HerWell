"""
MCP (Model Context Protocol) Server for HERwell AI.
Exposes controlled, read-only tools for external agents.
"""

import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Resource, ResourceChunk
from app.ai.rag import retrieve_resources

logger = logging.getLogger(__name__)


class HERwellMCPServer:
    """
    MCP Server implementation for HERwell AI.
    
    Exposes read-only tools for educational resource access.
    Does not provide destructive operations or unrestricted data access.
    """
    
    def __init__(self):
        self.tools = {
            "search_resources": self.search_resources,
            "get_resource_by_id": self.get_resource_by_id,
            "list_resource_categories": self.list_resource_categories,
            "get_resource_count": self.get_resource_count
        }
    
    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        Return available tools with their schemas.
        
        Returns:
            Dictionary mapping tool names to their schemas
        """
        return {
            "search_resources": {
                "name": "search_resources",
                "description": "Search educational resources by query using semantic search or keyword matching",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (e.g., 'stress management', 'study tips')"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 5, max: 20)",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 20
                        },
                        "category": {
                            "type": "string",
                            "description": "Optional category filter (e.g., 'wellbeing', 'academic')"
                        }
                    },
                    "required": ["query"]
                }
            },
            "get_resource_by_id": {
                "name": "get_resource_by_id",
                "description": "Get a specific resource by its ID",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "resource_id": {
                            "type": "integer",
                            "description": "The resource ID"
                        }
                    },
                    "required": ["resource_id"]
                }
            },
            "list_resource_categories": {
                "name": "list_resource_categories",
                "description": "List all available resource categories",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "get_resource_count": {
                "name": "get_resource_count",
                "description": "Get the total count of resources in the database",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with the given arguments.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
        
        Returns:
            Tool execution result or error
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "available_tools": list(self.tools.keys())
            }
        
        try:
            result = self.tools[tool_name](**arguments)
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {"success": False, "error": str(e)}
    
    def search_resources(
        self,
        query: str,
        limit: int = 5,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search resources by query.
        
        Args:
            query: Search query
            limit: Maximum results (1-20)
            category: Optional category filter
        
        Returns:
            Search results with metadata
        """
        # Validate limit
        limit = max(1, min(20, limit))
        
        db = SessionLocal()
        try:
            results = retrieve_resources(db, query, limit=limit, use_semantic=False)
            
            # Filter by category if specified
            if category and results["results"]:
                results["results"] = [
                    r for r in results["results"]
                    if r.get("category", "").lower() == category.lower()
                ]
            
            # Format results for MCP
            formatted = []
            for r in results["results"][:limit]:
                formatted.append({
                    "title": r.get("title", ""),
                    "category": r.get("category", ""),
                    "content_preview": r.get("content", "")[:200] + "..." if len(r.get("content", "")) > 200 else r.get("content", ""),
                    "source": r.get("source_label", r.get("source", "")),
                    "source_url": r.get("source_url", ""),
                    "language": r.get("language", "unknown"),
                    "verification_status": r.get("verification_status", "unknown")
                })
            
            return {
                "method": results["method"],
                "total_found": len(formatted),
                "results": formatted
            }
        finally:
            db.close()
    
    def get_resource_by_id(self, resource_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a resource by ID.
        
        Args:
            resource_id: Resource ID
        
        Returns:
            Resource details or None if not found
        """
        db = SessionLocal()
        try:
            resource = db.query(Resource).filter(Resource.id == resource_id).first()
            if not resource:
                return None
            
            return {
                "id": resource.id,
                "title": resource.title,
                "category": resource.category,
                "content": resource.content,
                "source_label": resource.source_label,
                "source_url": resource.source_url,
                "language": resource.language,
                "verification_status": resource.verification_status,
                "publication_date": resource.publication_date
            }
        finally:
            db.close()
    
    def list_resource_categories(self) -> List[str]:
        """
        List all resource categories.
        
        Returns:
            List of unique category names
        """
        db = SessionLocal()
        try:
            categories = db.query(Resource.category).distinct().all()
            return [c[0] for c in categories if c[0]]
        finally:
            db.close()
    
    def get_resource_count(self) -> Dict[str, int]:
        """
        Get total resource count.
        
        Returns:
            Dictionary with count
        """
        db = SessionLocal()
        try:
            count = db.query(Resource).count()
            return {"total_resources": count}
        finally:
            db.close()


# Singleton instance
_mcp_server = None

def get_mcp_server() -> HERwellMCPServer:
    """Get the singleton MCP server instance."""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = HERwellMCPServer()
    return _mcp_server


if __name__ == "__main__":
    # Simple CLI for testing MCP server
    import json
    import sys
    
    server = get_mcp_server()
    
    if len(sys.argv) < 2:
        print("Available tools:")
        for name, schema in server.get_tools().items():
            print(f"  {name}: {schema['description']}")
        sys.exit(0)
    
    tool_name = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    
    result = server.call_tool(tool_name, args)
    print(json.dumps(result, indent=2))
