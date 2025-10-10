"""
Reference resolution and Markdown placeholder handling for Aether projects.

This module handles expanding $ref references and resolving Markdown placeholders
with support for different resolution scopes (global vs contextual).
"""

import re
import json
from typing import Dict, Any, List, Set, Optional
from jsonschema import Draft7Validator
import zipfile


def resolve_project(
    project_data: Dict[str, Any], 
    derived_schema: Dict[str, Any], 
    zip_ref: zipfile.ZipFile
) -> Dict[str, Any]:
    """
    Resolve all references and Markdown placeholders in an Aether project.
    
    Args:
        project_data: The project data to resolve
        derived_schema: The derived JSON schema
        zip_ref: ZipFile containing the project resources
        
    Returns:
        Fully resolved project data with expanded references and resolved Markdown
    """
    # Create a deep copy to avoid modifying the original
    resolved_data = json.loads(json.dumps(project_data))
    
    # Resolve $ref references within the project data itself
    resolved_data = _resolve_project_refs(resolved_data)
    
    # Resolve string ID references using schema hints (x-aether-reference)
    resolved_data = _resolve_string_references(resolved_data, derived_schema, project_data)
    
    # Resolve Markdown placeholders
    resolved_data = _resolve_markdown_placeholders(resolved_data, derived_schema, zip_ref)
    
    return resolved_data


def _resolve_project_refs(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolve $ref references within project data.
    
    Args:
        project_data: The project data containing $ref references
        
    Returns:
        Project data with resolved references
    """
    # Create a lookup table for all entities by type and id
    lookup = {}
    
    # Build lookup table from project data
    # Look for all entity types (arrays of objects with 'id' or 'name' field)
    for key, value in project_data.items():
        if isinstance(value, list) and value and isinstance(value[0], dict):
            # This looks like an entity type (array of objects)
            for entity in value:
                if 'id' in entity:
                    lookup[f"#/{key}/{entity['id']}"] = entity
                elif 'name' in entity:
                    # Use name as the identifier (lowercase for consistency)
                    lookup[f"#/{key}/{entity['name'].lower()}"] = entity
    
    # Resolve references recursively
    return _resolve_refs_in_data(project_data, lookup)


def _resolve_string_references(
    data: Any,
    schema: Dict[str, Any],
    project_data: Dict[str, Any],
    current_schema_path: List[str] = None
) -> Any:
    """
    Resolve string ID references to full objects using x-aether-reference hints.
    
    This enables clean authoring (author: "jane") while providing full object
    resolution for applications (author: {id: "jane", name: "Jane Developer", ...}).
    
    Args:
        data: The data to resolve
        schema: The derived schema with x-aether-reference hints
        project_data: Full project data for entity lookup
        current_schema_path: Current path in schema (for tracking)
        
    Returns:
        Data with string IDs expanded to full objects
    """
    if current_schema_path is None:
        current_schema_path = []
    
    # Build entity lookup from project collections
    entity_lookup = _build_entity_lookup(project_data)
    
    # Build a map of collection names to their object types
    collection_to_type = {}
    root_properties = schema.get('properties', {})
    for collection_name, collection_def in root_properties.items():
        if isinstance(collection_def, dict) and collection_def.get('type') == 'array':
            items_ref = collection_def.get('items', {}).get('$ref', '')
            if items_ref.startswith('#/$defs/'):
                object_type = items_ref.replace('#/$defs/', '')
                collection_to_type[collection_name] = object_type
    
    # Resolve recursively
    return _resolve_data_with_hints(data, schema, entity_lookup, collection_to_type)


def _build_entity_lookup(project_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Build lookup table: {collection: {entity_id: entity_data}}
    """
    lookup = {}
    
    for key, value in project_data.items():
        if isinstance(value, list) and value:
            # This is a collection
            lookup[key] = {}
            for entity in value:
                if isinstance(entity, dict) and 'id' in entity:
                    lookup[key][entity['id']] = entity
    
    return lookup


def _resolve_data_with_hints(
    data: Any,
    schema: Dict[str, Any],
    entity_lookup: Dict[str, Dict[str, Any]],
    collection_to_type: Dict[str, str]
) -> Any:
    """
    Recursively resolve data using schema hints
    """
    if isinstance(data, dict):
        resolved = {}
        
        # Check if this dict has an 'id' - if so, it might be an entity
        # and we need to look up its type to find the right schema
        entity_type = None
        if 'id' in data:
            # Try to find which collection this entity belongs to
            for collection_name, entities in entity_lookup.items():
                if data['id'] in entities:
                    entity_type = collection_to_type.get(collection_name)
                    break
        
        for key, value in data.items():
            # Get the schema for this field
            field_schema = None
            
            if entity_type:
                # This is an entity, look up schema in $defs
                entity_def = schema.get('$defs', {}).get(entity_type, {})
                field_schema = entity_def.get('properties', {}).get(key)
            else:
                # Root-level property
                field_schema = schema.get('properties', {}).get(key)
            
            if field_schema and 'x-aether-reference' in field_schema:
                # This field is a reference
                ref_collection = field_schema['x-aether-reference'].strip('#/').strip('/')
                
                if isinstance(value, str):
                    # Single string reference
                    if ref_collection in entity_lookup and value in entity_lookup[ref_collection]:
                        resolved[key] = entity_lookup[ref_collection][value]
                    else:
                        resolved[key] = value
                elif isinstance(value, list):
                    # Array of string references - should not reach here for arrays
                    resolved[key] = value
                else:
                    resolved[key] = value
            elif field_schema and field_schema.get('type') == 'array' and isinstance(value, list):
                # Check if array items have x-aether-reference
                items_schema = field_schema.get('items', {})
                if items_schema.get('x-aether-reference'):
                    # Array items are references
                    ref_collection = items_schema['x-aether-reference'].strip('#/').strip('/')
                    resolved[key] = []
                    for item in value:
                        if isinstance(item, str) and ref_collection in entity_lookup and item in entity_lookup[ref_collection]:
                            resolved[key].append(entity_lookup[ref_collection][item])
                        elif isinstance(item, (dict, list)):
                            resolved[key].append(_resolve_data_with_hints(item, schema, entity_lookup, collection_to_type))
                        else:
                            resolved[key].append(item)
                else:
                    # Regular array, recurse
                    resolved[key] = [_resolve_data_with_hints(item, schema, entity_lookup, collection_to_type) for item in value]
            elif isinstance(value, (dict, list)):
                # Recurse into nested structures
                resolved[key] = _resolve_data_with_hints(value, schema, entity_lookup, collection_to_type)
            else:
                resolved[key] = value
        
        return resolved
    
    elif isinstance(data, list):
        return [_resolve_data_with_hints(item, schema, entity_lookup, collection_to_type) for item in data]
    
    else:
        return data


def _get_schema_at_path(schema: Dict[str, Any], path: List[str]) -> Dict[str, Any] | None:
    """Navigate schema to get definition at path"""
    current = schema
    
    for part in path:
        if isinstance(current, dict):
            if part in current:
                current = current[part]
            else:
                return None
        else:
            return None
    
    return current if isinstance(current, dict) else None


def _resolve_refs_in_data(data: Any, lookup: Dict[str, Any], visited: set = None) -> Any:
    """
    Recursively resolve $ref references in data using lookup table.
    
    Args:
        data: The data to resolve references in
        lookup: Dictionary mapping reference paths to resolved objects
        visited: Set of already visited references to prevent cycles
        
    Returns:
        Data with resolved references
    """
    if visited is None:
        visited = set()
    
    if isinstance(data, dict):
        if "$ref" in data:
            ref_path = data["$ref"]
            if ref_path in visited:
                # Cycle detected, return the original $ref
                return data
            if ref_path in lookup:
                visited.add(ref_path)
                resolved = _resolve_refs_in_data(lookup[ref_path], lookup, visited)
                visited.remove(ref_path)
                return resolved
            else:
                # If reference not found, return the original $ref
                return data
        else:
            # Recursively resolve all values
            return {key: _resolve_refs_in_data(value, lookup, visited)
                   for key, value in data.items()}
    elif isinstance(data, list):
        return [_resolve_refs_in_data(item, lookup, visited) for item in data]
    else:
        return data


def _resolve_refs(data: Any, schema: Dict[str, Any], visited: Optional[Set[str]] = None) -> Any:
    """
    Recursively resolve $ref references in data.
    
    Args:
        data: The data to resolve references in
        schema: The schema containing $defs for reference resolution
        visited: Set of already visited references (for cycle detection)
        
    Returns:
        Data with resolved references
    """
    if visited is None:
        visited = set()
    
    if isinstance(data, dict):
        if "$ref" in data:
            ref_path = data["$ref"]
            
            # Check for cycles
            if ref_path in visited:
                raise ValueError(f"Circular reference detected: {ref_path}")
            
            visited.add(ref_path)
            
            # Resolve the reference
            resolved_ref = _resolve_single_ref(ref_path, schema)
            return _resolve_refs(resolved_ref, schema, visited)
        else:
            # Recursively resolve all values
            return {key: _resolve_refs(value, schema, visited.copy()) 
                   for key, value in data.items()}
    elif isinstance(data, list):
        return [_resolve_refs(item, schema, visited.copy()) for item in data]
    else:
        return data


def _resolve_single_ref(ref_path: str, schema: Dict[str, Any]) -> Any:
    """
    Resolve a single $ref reference.
    
    Args:
        ref_path: The reference path (e.g., "#/objects/Person")
        schema: The schema containing $defs
        
    Returns:
        The resolved reference data
    """
    if not ref_path.startswith("#/"):
        raise ValueError(f"Invalid reference path: {ref_path}")
    
    # Remove the "#/" prefix and split by "/"
    path_parts = ref_path[2:].split("/")
    
    # Navigate to the referenced object
    current = schema
    for part in path_parts:
        if part in current:
            current = current[part]
        else:
            raise ValueError(f"Reference not found: {ref_path}")
    
    return current


def _resolve_markdown_placeholders(
    data: Any, 
    schema: Dict[str, Any], 
    zip_ref: zipfile.ZipFile
) -> Any:
    """
    Recursively resolve Markdown placeholders in data.
    
    Args:
        data: The data to resolve placeholders in
        schema: The schema containing Markdown field definitions
        zip_ref: ZipFile containing Markdown files
        
    Returns:
        Data with resolved Markdown placeholders
    """
    if isinstance(data, dict):
        # Check if this is a Markdown field
        if data.get("type") == "markdown":
            return _resolve_markdown_field(data, schema, zip_ref)
        else:
            # Recursively resolve all values
            return {key: _resolve_markdown_placeholders(value, schema, zip_ref) 
                   for key, value in data.items()}
    elif isinstance(data, list):
        return [_resolve_markdown_placeholders(item, schema, zip_ref) for item in data]
    else:
        return data


def _resolve_markdown_field(
    markdown_field: Dict[str, Any], 
    schema: Dict[str, Any], 
    zip_ref: zipfile.ZipFile
) -> Dict[str, Any]:
    """
    Resolve a single Markdown field with placeholders.
    
    Args:
        markdown_field: The Markdown field definition
        schema: The schema for context
        zip_ref: ZipFile containing Markdown files
        
    Returns:
        Resolved Markdown field
    """
    resolved_field = markdown_field.copy()
    
    # Get Markdown content
    if "path" in markdown_field and markdown_field["path"]:
        # Load from file
        try:
            content = zip_ref.read(markdown_field["path"]).decode('utf-8')
        except KeyError:
            raise ValueError(f"Markdown file not found: {markdown_field['path']}")
    elif "inline" in markdown_field and markdown_field["inline"]:
        content = markdown_field["inline"]
    else:
        return resolved_field
    
    # Get resolution parameters
    ref_pattern = markdown_field.get("ref_pattern", r'\{(.+?)\}')
    resolve_scope = markdown_field.get("resolve_scope", "global")
    
    # Resolve placeholders
    if resolve_scope == "global":
        resolved_content = _resolve_placeholders_global(content, ref_pattern, schema)
    elif resolve_scope == "contextual":
        resolved_content = _resolve_placeholders_contextual(content, ref_pattern, schema)
    else:
        raise ValueError(f"Invalid resolve_scope: {resolve_scope}")
    
    # Update the field with resolved content
    resolved_field["resolved_content"] = resolved_content
    
    return resolved_field


def _resolve_placeholders_global(
    content: str, 
    pattern: str, 
    schema: Dict[str, Any]
) -> str:
    """
    Resolve placeholders using global scope (full schema context).
    
    Args:
        content: The Markdown content with placeholders
        pattern: The regex pattern for placeholders
        schema: The full schema for context
        
    Returns:
        Content with resolved placeholders
    """
    def replace_placeholder(match):
        placeholder = match.group(1)
        # Try to resolve the placeholder from the schema
        try:
            return _resolve_placeholder_value(placeholder, schema)
        except ValueError:
            return match.group(0)  # Return original if not found
    
    return re.sub(pattern, replace_placeholder, content)


def _resolve_placeholders_contextual(
    content: str, 
    pattern: str, 
    schema: Dict[str, Any]
) -> str:
    """
    Resolve placeholders using contextual scope (limited to current object).
    
    Args:
        content: The Markdown content with placeholders
        pattern: The regex pattern for placeholders
        schema: The schema for context
        
    Returns:
        Content with resolved placeholders
    """
    # For contextual scope, we would need to know the current object context
    # This is a simplified implementation - in practice, this would need
    # the current object's data to resolve placeholders
    return _resolve_placeholders_global(content, pattern, schema)


def _resolve_placeholder_value(placeholder: str, schema: Dict[str, Any]) -> str:
    """
    Resolve a single placeholder value from the schema.
    
    Args:
        placeholder: The placeholder to resolve (e.g., "Role.title")
        schema: The schema containing the data
        
    Returns:
        The resolved value as a string
    """
    # Split the placeholder by dots to navigate the schema
    parts = placeholder.split(".")
    
    # Navigate to the referenced value
    current = schema
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise ValueError(f"Placeholder not found: {placeholder}")
    
    # Convert to string
    if isinstance(current, (str, int, float, bool)):
        return str(current)
    else:
        return str(current)


def sanitize_path(path: str) -> str:
    """
    Sanitize a file path to prevent directory traversal attacks.
    
    Args:
        path: The path to sanitize
        
    Returns:
        Sanitized path
    """
    # Normalize the path
    normalized = os.path.normpath(path)
    
    # Check for directory traversal attempts
    if ".." in normalized or normalized.startswith("/"):
        raise ValueError(f"Invalid path: {path}")
    
    return normalized


def detect_cycles(refs: List[str]) -> List[str]:
    """
    Detect circular references in a list of reference paths.
    
    Args:
        refs: List of reference paths to check
        
    Returns:
        List of circular reference paths found
    """
    cycles = []
    visited = set()
    
    for ref in refs:
        if ref in visited:
            cycles.append(ref)
        visited.add(ref)
    
    return cycles
