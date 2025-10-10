#!/usr/bin/env python3
"""
Aether MCP Server

Model Context Protocol server exposing Aether functions as tools for AI assistants.
Can be used by Claude Desktop, VS Code extensions, or any MCP-compatible client.

Usage:
    python -m aether.mcp_server

Configuration in Claude Desktop:
    Add to ~/.claude/config.json:
    {
      "mcpServers": {
        "aether": {
          "command": "python",
          "args": ["-m", "aether.mcp_server"]
        }
      }
    }
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import yaml

# MCP protocol implementation
class MCPServer:
    """Aether MCP Server implementing Model Context Protocol"""
    
    def __init__(self):
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define available tools for AI assistants"""
        return [
            {
                "name": "get_schema_structure",
                "description": "Get the structure of an Aether schema including collections, entity types, and required fields",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to Aether project root (containing .aether file)"
                        }
                    },
                    "required": ["project_path"]
                }
            },
            {
                "name": "get_required_fields",
                "description": "Get required fields for a specific entity type",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to Aether project root"
                        },
                        "entity_type": {
                            "type": "string",
                            "description": "Entity type name (e.g., 'BlogPost', 'Recipe')"
                        }
                    },
                    "required": ["project_path", "entity_type"]
                }
            },
            {
                "name": "get_available_references",
                "description": "Get list of available entity IDs in a collection for reference completion",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to Aether project root"
                        },
                        "collection_name": {
                            "type": "string",
                            "description": "Collection name (e.g., 'authors', 'categories')"
                        }
                    },
                    "required": ["project_path", "collection_name"]
                }
            },
            {
                "name": "validate_entity_yaml",
                "description": "Validate YAML content for an entity type against the schema",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to Aether project root"
                        },
                        "entity_type": {
                            "type": "string",
                            "description": "Entity type to validate against"
                        },
                        "yaml_content": {
                            "type": "string",
                            "description": "YAML content to validate"
                        }
                    },
                    "required": ["project_path", "entity_type", "yaml_content"]
                }
            },
            {
                "name": "create_entity_template",
                "description": "Generate a pre-filled YAML template for an entity type",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to Aether project root"
                        },
                        "entity_type": {
                            "type": "string",
                            "description": "Entity type to create template for"
                        }
                    },
                    "required": ["project_path", "entity_type"]
                }
            },
            {
                "name": "list_collections",
                "description": "List all collections in a project with entity counts",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to Aether project root"
                        }
                    },
                    "required": ["project_path"]
                }
            }
        ]
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP protocol requests"""
        method = request.get('method')
        params = request.get('params', {})
        
        if method == 'initialize':
            return {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "aether-mcp-server",
                    "version": "0.5.0"
                }
            }
        
        elif method == 'tools/list':
            return {
                "tools": self.tools
            }
        
        elif method == 'tools/call':
            tool_name = params.get('name')
            tool_args = params.get('arguments', {})
            
            try:
                result = self._execute_tool(tool_name, tool_args)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            except Exception as e:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error: {str(e)}"
                        }
                    ],
                    "isError": True
                }
        
        else:
            return {"error": f"Unknown method: {method}"}
    
    def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return results"""
        
        if tool_name == "get_schema_structure":
            return self._get_schema_structure(args['project_path'])
        
        elif tool_name == "get_required_fields":
            return self._get_required_fields(args['project_path'], args['entity_type'])
        
        elif tool_name == "get_available_references":
            return self._get_available_references(args['project_path'], args['collection_name'])
        
        elif tool_name == "validate_entity_yaml":
            return self._validate_entity_yaml(
                args['project_path'],
                args['entity_type'],
                args['yaml_content']
            )
        
        elif tool_name == "create_entity_template":
            return self._create_entity_template(args['project_path'], args['entity_type'])
        
        elif tool_name == "list_collections":
            return self._list_collections(args['project_path'])
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    def _get_schema_structure(self, project_path: str) -> Dict[str, Any]:
        """Get schema structure"""
        from aether import load_schema
        from aether.introspection import introspect_schema
        
        schema_file = self._find_schema_file(project_path)
        with open(schema_file) as f:
            schema_data = yaml.safe_load(f)
        
        derived = load_schema(schema_data)
        introspector = introspect_schema(derived)
        
        return {
            "title": schema_data.get('title'),
            "collections": introspector.get_entity_collections(),
            "entity_types": introspector.get_object_types(),
            "media_types": introspector.get_media_types()
        }
    
    def _get_required_fields(self, project_path: str, entity_type: str) -> Dict[str, Any]:
        """Get required fields for entity type"""
        from aether import load_schema
        from aether.introspection import introspect_schema
        
        schema_file = self._find_schema_file(project_path)
        with open(schema_file) as f:
            schema_data = yaml.safe_load(f)
        
        derived = load_schema(schema_data)
        introspector = introspect_schema(derived)
        
        required = introspector.get_required_fields(entity_type)
        object_schema = introspector.get_object_schema(entity_type)
        
        # Get field details
        fields = {}
        properties = object_schema.get('properties', {})
        for field_name in required:
            field_def = properties.get(field_name, {})
            fields[field_name] = {
                "type": field_def.get('type'),
                "description": field_def.get('description'),
                "enum": field_def.get('enum'),
                "x-aether-reference": field_def.get('x-aether-reference')
            }
        
        return {
            "entity_type": entity_type,
            "required_fields": required,
            "field_details": fields
        }
    
    def _get_available_references(self, project_path: str, collection_name: str) -> Dict[str, Any]:
        """Get available entity IDs in a collection"""
        project_dir = Path(project_path) / 'project' / collection_name
        
        if not project_dir.exists():
            return {"collection": collection_name, "entities": []}
        
        entities = []
        for item in project_dir.iterdir():
            if item.is_dir():
                # Directory-based entity
                entities.append(item.name)
            elif item.suffix == '.yaml':
                # Flat-file entity
                entities.append(item.stem)
        
        return {
            "collection": collection_name,
            "entities": sorted(entities),
            "count": len(entities)
        }
    
    def _validate_entity_yaml(self, project_path: str, entity_type: str, yaml_content: str) -> Dict[str, Any]:
        """Validate YAML content"""
        from aether import load_schema
        from jsonschema import Draft7Validator
        
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            return {
                "valid": False,
                "errors": [{"message": f"YAML syntax error: {str(e)}"}]
            }
        
        schema_file = self._find_schema_file(project_path)
        with open(schema_file) as f:
            schema_data = yaml.safe_load(f)
        
        derived = load_schema(schema_data)
        
        # Get the entity schema
        entity_schema = derived.get('$defs', {}).get(entity_type)
        if not entity_schema:
            return {
                "valid": False,
                "errors": [{"message": f"Entity type '{entity_type}' not found in schema"}]
            }
        
        # Validate
        validator = Draft7Validator(entity_schema)
        errors = list(validator.iter_errors(data))
        
        if errors:
            return {
                "valid": False,
                "errors": [{"message": e.message, "path": ".".join(str(p) for p in e.path)} for e in errors]
            }
        
        return {"valid": True, "errors": []}
    
    def _create_entity_template(self, project_path: str, entity_type: str) -> Dict[str, Any]:
        """Create entity template"""
        from aether import load_schema
        from aether.scaffolding import _create_entity_from_object_def
        
        schema_file = self._find_schema_file(project_path)
        with open(schema_file) as f:
            schema_data = yaml.safe_load(f)
        
        # Get object definition
        object_def = schema_data.get('objects', {}).get(entity_type)
        if not object_def:
            raise ValueError(f"Entity type '{entity_type}' not found in schema")
        
        # Generate template
        template = _create_entity_from_object_def(entity_type, object_def)
        
        return {
            "entity_type": entity_type,
            "template_yaml": yaml.dump(template, default_flow_style=False, sort_keys=False)
        }
    
    def _list_collections(self, project_path: str) -> Dict[str, Any]:
        """List collections with counts"""
        project_dir = Path(project_path) / 'project'
        
        if not project_dir.exists():
            return {"collections": {}}
        
        collections = {}
        for item in project_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Count entities
                entity_count = sum(1 for _ in item.iterdir())
                collections[item.name] = entity_count
        
        return {
            "collections": collections,
            "total_collections": len(collections)
        }
    
    def _find_schema_file(self, project_path: str) -> str:
        """Find .aether schema file in project"""
        project_dir = Path(project_path)
        aether_files = list(project_dir.glob('*.aether'))
        
        if not aether_files:
            raise ValueError(f"No .aether schema file found in {project_path}")
        
        if len(aether_files) > 1:
            raise ValueError(f"Multiple .aether files found: {[f.name for f in aether_files]}")
        
        return str(aether_files[0])
    
    def run(self):
        """Run MCP server (stdio transport)"""
        print("Aether MCP Server starting...", file=sys.stderr)
        print(f"Protocol: Model Context Protocol", file=sys.stderr)
        print(f"Tools available: {len(self.tools)}", file=sys.stderr)
        
        # MCP uses JSON-RPC over stdio
        for line in sys.stdin:
            try:
                request = json.loads(line)
                response = self.handle_request(request)
                
                # Send response
                print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError:
                error_response = {
                    "error": {"code": -32700, "message": "Parse error"}
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                error_response = {
                    "error": {"code": -32603, "message": str(e)}
                }
                print(json.dumps(error_response), flush=True)


def main():
    """Main entry point for MCP server"""
    server = MCPServer()
    server.run()


if __name__ == '__main__':
    main()
