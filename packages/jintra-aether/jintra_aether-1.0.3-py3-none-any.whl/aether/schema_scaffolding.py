"""
Schema scaffolding functionality for generating Aether schemas.

Provides commands to create minimal valid schemas as starting points.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml


def scaffold_schema(
    schema_id: str,
    output_path: str,
    title: Optional[str] = None,
    collections: Optional[List[str]] = None,
    include_examples: bool = True
) -> Dict[str, Any]:
    """
    Generate a minimal valid Aether schema.
    
    Creates a properly structured schema with:
    - Required metadata (id, spec_version, version, title)
    - Optional collections with proper ID handling
    - Comments explaining the structure
    
    Args:
        schema_id: Unique identifier for the schema (e.g., "blog")
        output_path: Where to save the schema file
        title: Human-readable title (defaults to schema_id)
        collections: List of collection names to include (e.g., ["posts", "authors"])
        include_examples: Whether to include example comments
        
    Returns:
        Dictionary containing the generated schema
    """
    if not title:
        title = schema_id.replace('-', ' ').replace('_', ' ').title()
    
    if collections is None:
        collections = []
    
    schema = _create_minimal_schema(schema_id, title, collections, include_examples)
    
    # Save to file
    output_file = Path(output_path)
    with open(output_file, 'w', encoding='utf-8') as f:
        if include_examples:
            f.write(_generate_schema_with_comments(schema, collections))
        else:
            yaml.dump(schema, f, default_flow_style=False, sort_keys=False)
    
    return schema


def create_minimal_schema(schema_id: str, title: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a minimal valid Aether schema in memory.
    
    Args:
        schema_id: Unique identifier for the schema
        title: Human-readable title
        
    Returns:
        Dictionary containing minimal schema
    """
    if not title:
        title = schema_id.replace('-', ' ').replace('_', ' ').title()
    
    return {
        'id': schema_id,
        'spec_version': '1.0.0',
        'version': '1.0.0',
        'title': title,
        'structure': {},
        'objects': {}
    }


def add_collection_to_schema(
    schema: Dict[str, Any],
    collection_name: str,
    object_name: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Add a collection to an existing schema.
    
    Args:
        schema: Existing schema dictionary
        collection_name: Name of the collection (e.g., "posts")
        object_name: Name of the object type (defaults to singular of collection_name)
        properties: Additional properties for the object
        
    Returns:
        Updated schema
    """
    if object_name is None:
        object_name = _singularize(collection_name).title()
    
    if properties is None:
        properties = {}
    
    # Add collection to structure
    schema['structure'][collection_name] = {
        'type': 'array',
        'items': {'$ref': f'#/objects/{object_name}'}
    }
    
    # Create object definition with proper ID handling
    # Note: For directory-based entities, id is auto-injected from directory name
    # We include it in the schema so validation passes
    object_def = {
        'type': 'object',
        'properties': {
            'id': {'type': 'string'},  # Required for validation
            **properties
        },
        'required': ['id'] + [k for k, v in properties.items() if isinstance(v, dict) and v.get('required', False)]
    }
    
    schema['objects'][object_name] = object_def
    
    return schema


def _create_minimal_schema(
    schema_id: str,
    title: str,
    collections: List[str],
    include_examples: bool
) -> Dict[str, Any]:
    """Create minimal schema with optional collections."""
    schema = create_minimal_schema(schema_id, title)
    
    # Add collections if specified
    for collection_name in collections:
        object_name = _singularize(collection_name).title()
        
        # Add basic properties based on collection type
        properties = _get_default_properties(collection_name, include_examples)
        
        add_collection_to_schema(schema, collection_name, object_name, properties)
    
    return schema


def _get_default_properties(collection_name: str, include_examples: bool) -> Dict[str, Any]:
    """Generate sensible default properties based on collection name."""
    # Common properties for most entities
    base_properties = {
        'title': {'type': 'string'},
    }
    
    # Add type-specific properties
    if any(word in collection_name.lower() for word in ['post', 'article', 'page', 'document']):
        base_properties.update({
            'content': {'type': 'string'},
            'published': {'type': 'boolean'}
        })
    elif any(word in collection_name.lower() for word in ['author', 'user', 'person']):
        base_properties.update({
            'name': {'type': 'string'},
            'email': {'type': 'string'}
        })
    elif any(word in collection_name.lower() for word in ['product', 'item']):
        base_properties.update({
            'description': {'type': 'string'},
            'price': {'type': 'number'}
        })
    else:
        # Generic fallback
        base_properties['description'] = {'type': 'string'}
    
    return base_properties


def _generate_schema_with_comments(schema: Dict[str, Any], collections: List[str]) -> str:
    """Generate schema YAML with helpful comments."""
    lines = []
    
    # Header comment
    lines.append("# Aether Schema")
    lines.append("# Generated by: aether scaffold-schema")
    lines.append("#")
    lines.append("# This schema defines the structure for your Aether project.")
    lines.append("# See: https://github.com/jintra-jayce/aether for documentation")
    lines.append("")
    
    # Required metadata
    lines.append("# Schema metadata (required)")
    lines.append(f"id: {schema['id']}")
    lines.append(f"spec_version: {schema['spec_version']}")
    lines.append(f"version: {schema['version']}")
    lines.append(f"title: {schema['title']}")
    lines.append("")
    
    # Structure section
    lines.append("# Project structure - defines root-level collections")
    lines.append("structure:")
    
    if not schema['structure']:
        lines.append("  # Add your collections here, e.g.:")
        lines.append("  # posts:")
        lines.append("  #   type: array")
        lines.append("  #   items: { $ref: \"#/objects/Post\" }")
    else:
        for coll_name, coll_def in schema['structure'].items():
            lines.append(f"  {coll_name}:")
            lines.append(f"    type: {coll_def['type']}")
            items_ref = coll_def['items']['$ref']
            lines.append(f"    items: {{ $ref: \"{items_ref}\" }}")
    
    lines.append("")
    
    # Objects section
    lines.append("# Object definitions - defines entity types")
    lines.append("objects:")
    
    if not schema['objects']:
        lines.append("  # Define your entity types here")
    else:
        for obj_name, obj_def in schema['objects'].items():
            lines.append(f"  {obj_name}:")
            lines.append(f"    type: {obj_def['type']}")
            lines.append("    properties:")
            
            for prop_name, prop_def in obj_def['properties'].items():
                if prop_name == 'id':
                    lines.append(f"      {prop_name}: {{ type: {prop_def['type']} }}  # Auto-set from directory name")
                else:
                    lines.append(f"      {prop_name}: {{ type: {prop_def['type']} }}")
            
            if 'required' in obj_def:
                req_fields = ', '.join(obj_def['required'])
                lines.append(f"    required: [{req_fields}]")
            lines.append("")
    
    # Footer comment
    lines.append("# Next steps:")
    lines.append("# 1. Customize the collections and objects above")
    lines.append("# 2. Run: aether scaffold <schema-file> <output-dir>")
    lines.append("# 3. Add your content to the generated project")
    lines.append("# 4. Run: aether validate-project <project-dir>")
    
    return '\n'.join(lines)


def _singularize(word: str) -> str:
    """Simple singularization for common English plurals."""
    if word.endswith('ies'):
        return word[:-3] + 'y'
    elif word.endswith('ses'):
        return word[:-2]
    elif word.endswith('s'):
        return word[:-1]
    return word

