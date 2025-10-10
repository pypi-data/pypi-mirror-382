"""
Extended Draft7Validator with custom handlers for Aether-specific types.

This module extends the standard JSON Schema validator to handle custom
types like 'media' and 'markdown' that are specific to the Aether framework.
"""

import os
import re
from typing import Dict, Any, Optional, List
from jsonschema import Draft7Validator, ValidationError
from jsonschema.validators import extend
import zipfile


def create_aether_validator(schema: Dict[str, Any], zip_ref: Optional[zipfile.ZipFile] = None) -> Draft7Validator:
    """
    Create an extended Draft7Validator with custom handlers for Aether types.
    
    Args:
        schema: The JSON schema to validate against
        zip_ref: Optional ZipFile for validating media/markdown references
        
    Returns:
        Extended validator with custom type handlers
    """
    def validate_media(validator, media_type, instance, schema):
        """Validate media type fields."""
        if not isinstance(instance, str):
            yield ValidationError(f"Media path must be a string, got {type(instance)}")
            return
            
        # Check if media_type is defined in schema
        media_type_name = schema.get("media_type")
        if not media_type_name:
            yield ValidationError("Media type must specify 'media_type'")
            return
            
        # If we have a zipfile context, validate file existence and extension
        if zip_ref:
            for error in _validate_media_in_zip(validator, instance, media_type_name, schema, zip_ref):
                yield error
        else:
            # Basic validation without zip context
            if not instance.strip():
                yield ValidationError("Media path cannot be empty")
    
    def validate_markdown(validator, markdown_type, instance, schema):
        """Validate markdown type fields."""
        if not isinstance(instance, str):
            yield ValidationError(f"Markdown content must be a string, got {type(instance)}")
            return
            
        # Check if we have either path or inline content
        has_path = "path" in schema and schema["path"]
        has_inline = "inline" in schema and schema["inline"]
        
        if not has_path and not has_inline:
            yield ValidationError("Markdown must specify either 'path' or 'inline' content")
            return
            
        # If we have a zipfile context, validate file existence
        if zip_ref and has_path:
            for error in _validate_markdown_in_zip(validator, instance, schema, zip_ref):
                yield error
    
    # Create custom type validators by extending the existing ones
    # We need to use the correct jsonschema extension pattern
    from jsonschema.validators import extend
    
    def custom_type_checker(validator, types, instance, schema):
        """Custom type checker that handles media and markdown types."""
        if "media" in types:
            for error in validate_media(validator, "media", instance, schema):
                yield error
        elif "markdown" in types:
            for error in validate_markdown(validator, "markdown", instance, schema):
                yield error
        else:
            # For standard types, use the default checker
            for type_name in types:
                if not validator.is_type(instance, type_name):
                    yield ValidationError(f"{instance!r} is not of type {type_name!r}")
    
    # Create a custom type checker that handles our custom types
    def is_media_type(instance, type_name):
        """Check if instance is a valid media type."""
        return isinstance(instance, str) and type_name == "media"
    
    def is_markdown_type(instance, type_name):
        """Check if instance is a valid markdown type."""
        return isinstance(instance, str) and type_name == "markdown"
    
    # Create custom type checkers
    custom_type_checkers = {
        "media": is_media_type,
        "markdown": is_markdown_type,
    }
    
    # Extend the validator with custom type checkers
    AetherValidator = extend(Draft7Validator, type_checkers=custom_type_checkers)
    
    return AetherValidator(schema)


def validate_project(
    project_data: Dict[str, Any], 
    derived_schema: Dict[str, Any], 
    zip_ref: Optional[zipfile.ZipFile] = None
) -> None:
    """
    Validate an Aether project against its derived schema.
    
    Performs standard JSON Schema validation plus custom validation for
    media files (checking extensions against allowed_extensions) and
    markdown files.
    
    Args:
        project_data: The project data to validate
        derived_schema: The derived JSON schema for validation
        zip_ref: Optional ZipFile for validating media/markdown references
        
    Raises:
        ValidationError: If validation fails
    """
    # Use basic Draft7 validation for structure
    validator = Draft7Validator(derived_schema)
    
    try:
        validator.validate(project_data)
    except ValidationError as e:
        raise ValidationError(f"Project validation failed: {e.message}")
    
    # If we have a zip context and media_types defined, perform media validation
    if zip_ref and "x-aether-media-types" in derived_schema:
        media_types = derived_schema["x-aether-media-types"]
        _validate_media_files(project_data, derived_schema, media_types, zip_ref)


def _validate_media_files(
    data: Any, 
    schema: Dict[str, Any], 
    media_types: List[Dict[str, Any]], 
    zip_ref: zipfile.ZipFile,
    path: str = ""
) -> None:
    """
    Recursively validate all media files in the project data.
    
    Args:
        data: Project data or subset to validate
        schema: Current schema node
        media_types: List of media type definitions from the original schema
        zip_ref: ZipFile containing the project
        path: Current path in the data structure (for error messages)
    
    Raises:
        ValidationError: If any media validation fails
    """
    if isinstance(data, dict):
        for key, value in data.items():
            # Get the schema for this property
            prop_schema = None
            if "properties" in schema and key in schema["properties"]:
                prop_schema = schema["properties"][key]
            elif "$defs" in schema:
                # Might be in definitions
                for def_name, def_schema in schema["$defs"].items():
                    if isinstance(def_schema, dict) and "properties" in def_schema:
                        if key in def_schema["properties"]:
                            prop_schema = def_schema["properties"][key]
                            break
            
            # Check if this property is a media type
            if prop_schema and isinstance(prop_schema, dict):
                # Check for converted media type (now a string type with x-aether-media-type marker)
                if "x-aether-media-type" in prop_schema:
                    media_type_name = prop_schema["x-aether-media-type"]
                    _validate_single_media_file(value, media_type_name, media_types, zip_ref, f"{path}.{key}" if path else key)
                else:
                    # Recurse into nested structures
                    _validate_media_files(value, schema, media_types, zip_ref, f"{path}.{key}" if path else key)
    
    elif isinstance(data, list):
        for i, item in enumerate(data):
            _validate_media_files(item, schema, media_types, zip_ref, f"{path}[{i}]")


def _validate_single_media_file(
    media_path: str, 
    media_type_name: str, 
    media_types: List[Dict[str, Any]], 
    zip_ref: zipfile.ZipFile,
    field_path: str
) -> None:
    """
    Validate a single media file.
    
    Args:
        media_path: Path to the media file in the bundle
        media_type_name: Name of the media type (e.g., 'image', 'diagram')
        media_types: List of media type definitions
        zip_ref: ZipFile containing the project
        field_path: Path to this field in the project data (for error messages)
    
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(media_path, str):
        return  # Let JSON Schema validation handle type errors
    
    # Find the media type definition
    media_type_def = None
    for mt in media_types:
        if mt.get("name") == media_type_name:
            media_type_def = mt
            break
    
    if not media_type_def:
        # Media type not defined - this is a schema error, not a project error
        return
    
    # Check validation level
    validation_level = media_type_def.get("validation", "optional")
    
    if validation_level == "none":
        # No validation required
        return
    
    # Check if file exists in zip
    if media_path not in zip_ref.namelist():
        if validation_level == "required":
            raise ValidationError(f"Required media file not found in bundle: {media_path} (field: {field_path})")
        # For optional, missing file is acceptable
        return
    
    # Get file extension
    _, ext = os.path.splitext(media_path)
    if not ext:
        raise ValidationError(f"Media file must have an extension: {media_path} (field: {field_path})")
    
    # Validate extension against allowed_extensions
    allowed_extensions = media_type_def.get("allowed_extensions", [])
    if ext.lower() not in [e.lower() for e in allowed_extensions]:
        raise ValidationError(
            f"Invalid file extension '{ext}' for media type '{media_type_name}'. "
            f"Allowed extensions: {', '.join(allowed_extensions)} (file: {media_path}, field: {field_path})"
        )


def _validate_markdown_in_zip(validator, markdown_path: str, schema: Dict[str, Any], zip_ref: zipfile.ZipFile):
    """Validate markdown file within a ZIP archive."""
    try:
        # Check if file exists in zip
        if markdown_path not in zip_ref.namelist():
            yield ValidationError(f"Markdown file not found in archive: {markdown_path}")
            return
            
        # Validate file extension
        _, ext = os.path.splitext(markdown_path)
        if ext.lower() not in ['.md', '.markdown']:
            yield ValidationError(f"Markdown file must have .md or .markdown extension: {markdown_path}")
            return
            
    except Exception as e:
        yield ValidationError(f"Error validating markdown file {markdown_path}: {str(e)}")


def validate_media_types(media_types: List[Dict[str, Any]]) -> List[str]:
    """
    Validate media type definitions and return any errors.
    
    Args:
        media_types: List of media type definitions
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    for media_type in media_types:
        if "name" not in media_type:
            errors.append("Media type must have a 'name' field")
            continue
            
        if "allowed_extensions" not in media_type:
            errors.append(f"Media type '{media_type['name']}' must specify 'allowed_extensions'")
            continue
            
        extensions = media_type["allowed_extensions"]
        if not isinstance(extensions, list) or not extensions:
            errors.append(f"Media type '{media_type['name']}' must have non-empty 'allowed_extensions'")
            continue
            
        # Validate extension format
        for ext in extensions:
            if not re.match(r'^\.[a-z0-9]+$', ext):
                errors.append(f"Invalid extension format '{ext}' in media type '{media_type['name']}'")
    
    return errors
