"""
Schema loading and derivation logic for Aether.

This module handles loading Aether schemas, validating them against the Aether Spec,
and deriving runtime JSON schemas for project validation.
"""

import json
from typing import Dict, Any, Optional
from jsonschema import Draft7Validator, ValidationError
from .spec import get_spec


def load_schema(schema_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load and validate an Aether schema, then derive a runtime JSON schema.
    
    Args:
        schema_data: Dictionary containing the Aether schema definition
        
    Returns:
        Derived JSON schema suitable for validating Aether projects
        
    Raises:
        ValidationError: If the schema doesn't conform to the Aether Spec
    """
    # Get the Aether Spec
    aether_spec = get_spec()
    
    # Validate the schema against the Aether Spec
    validator = Draft7Validator(aether_spec)
    try:
        validator.validate(schema_data)
    except ValidationError as e:
        raise ValidationError(f"Schema validation failed: {e.message}")
    
    # Derive runtime JSON schema
    derived_schema = _derive_runtime_schema(schema_data)
    
    return derived_schema


def _derive_runtime_schema(schema_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Derive a runtime JSON schema from an Aether schema.
    
    Maps the 'structure' properties to root properties and 'objects' to $defs
    for reference support.
    
    Args:
        schema_data: Validated Aether schema
        
    Returns:
        Derived JSON schema for project validation
    """
    derived = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,  # Strict validation: no extra properties allowed
        "$defs": {}
    }
    
    # Map structure properties to root properties
    if "structure" in schema_data:
        derived["properties"].update(_convert_custom_types(schema_data["structure"]))
    
    # Map objects to $defs for reference support
    if "objects" in schema_data:
        derived["$defs"] = _convert_custom_types(schema_data["objects"])
    
    # Add required fields from structure if they exist
    for prop_name, prop_def in schema_data.get("structure", {}).items():
        if isinstance(prop_def, dict) and prop_def.get("required", False):
            derived["required"].append(prop_name)
    
    # Fix references to point to $defs instead of objects
    derived = _fix_references(derived)
    
    # Preserve media_types for validation purposes
    if "media_types" in schema_data:
        derived["x-aether-media-types"] = schema_data["media_types"]
    
    return derived


def _convert_custom_types(schema_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert custom Aether types (media, markdown) to standard JSON Schema types.
    Also adds strict validation (additionalProperties: false) to all objects.
    Preserves x-aether-reference hints for string ID resolution.
    
    Args:
        schema_dict: Dictionary containing schema definitions
        
    Returns:
        Schema with custom types converted to standard types
    """
    converted = {}
    
    for key, value in schema_dict.items():
        if isinstance(value, dict):
            if value.get("type") == "media":
                # Convert media type to string with additional properties
                # Preserve media_type name for validation
                converted[key] = {
                    "type": "string",
                    "description": f"Media file path for {value.get('media_type', 'unknown')} type",
                    "x-aether-media-type": value.get('media_type', 'unknown')
                }
            elif value.get("type") == "markdown":
                # Convert markdown type to string with additional properties
                converted[key] = {
                    "type": "string",
                    "description": "Markdown content with placeholder resolution"
                }
            elif value.get("type") == "object":
                # For object types, add strict validation
                converted[key] = _convert_custom_types(value)
                if "properties" in converted[key]:
                    # Only add additionalProperties: false if this has defined properties
                    converted[key]["additionalProperties"] = False
            else:
                # Recursively convert nested objects
                converted[key] = _convert_custom_types(value)
            
            # Preserve x-aether-reference hints for reference resolution
            if "x-aether-reference" in value:
                converted[key]["x-aether-reference"] = value["x-aether-reference"]
        else:
            converted[key] = value
    
    return converted


def _fix_references(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fix references in the schema to point to $defs instead of objects.
    
    Args:
        schema: The schema to fix
        
    Returns:
        Schema with fixed references
    """
    import json
    import re
    
    # Convert to JSON string and replace references
    schema_str = json.dumps(schema)
    schema_str = re.sub(r'#/objects/', '#/$defs/', schema_str)
    
    return json.loads(schema_str)


def validate_schema_against_spec(schema_data: Dict[str, Any]) -> bool:
    """
    Validate that a schema conforms to the Aether Spec.
    
    Args:
        schema_data: Dictionary containing the schema to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        aether_spec = get_spec()
        validator = Draft7Validator(aether_spec)
        validator.validate(schema_data)
        return True
    except ValidationError:
        return False


def get_schema_info(schema_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract basic information from a schema.
    
    Args:
        schema_data: Dictionary containing the schema
        
    Returns:
        Dictionary with schema metadata (id, version, title, description)
    """
    return {
        "id": schema_data.get("id"),
        "version": schema_data.get("version"), 
        "title": schema_data.get("title"),
        "description": schema_data.get("description"),
        "media_types": schema_data.get("media_types", []),
    }
