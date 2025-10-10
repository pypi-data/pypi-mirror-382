"""
Validation context for detailed error messages and debugging.
"""

from typing import Dict, Any, List, Optional, Tuple
import json
import re
from jsonschema import ValidationError


class ValidationContext:
    """Validation context with detailed error reporting."""
    
    def __init__(self, schema_data: Dict[str, Any], project_data: Dict[str, Any]):
        self.schema_data = schema_data
        self.project_data = project_data
        self.validation_path = []
        self.entity_context = {}
    
    def validate_with_context(self, derived_schema: Dict[str, Any], zip_ref=None) -> List[Dict[str, Any]]:
        """Validate project with enhanced context tracking."""
        from .validator import validate_project
        
        try:
            validate_project(self.project_data, derived_schema, zip_ref)
            return []
        except ValidationError as e:
            return self._enhance_validation_error(e)
    
    def _enhance_validation_error(self, error: ValidationError) -> List[Dict[str, Any]]:
        """Enhance a validation error with context and suggestions."""
        enhanced_errors = []
        
        # Get the path where the error occurred
        path_parts = list(error.absolute_path) if error.absolute_path else []
        field_path = " -> ".join(str(part) for part in path_parts) if path_parts else "root"
        
        # Determine the type of error and provide specific suggestions
        error_type = self._classify_error(error)
        suggestions = self._get_suggestions(error, path_parts)
        
        enhanced_error = {
            "message": str(error.message),
            "path": field_path,
            "error_type": error_type,
            "suggestions": suggestions,
            "context": self._get_error_context(path_parts)
        }
        
        enhanced_errors.append(enhanced_error)
        
        # Add related errors if this is a reference issue
        if "reference" in error_type.lower():
            related_errors = self._find_related_reference_errors(error, path_parts)
            enhanced_errors.extend(related_errors)
        
        return enhanced_errors
    
    def _classify_error(self, error: ValidationError) -> str:
        """Classify the type of validation error."""
        message = str(error.message).lower()
        
        if "is not of type" in message:
            return "Type Mismatch"
        elif "required" in message:
            return "Missing Required Field"
        elif "reference" in message or "$ref" in message:
            return "Invalid Reference"
        elif "format" in message:
            return "Invalid Format"
        elif "enum" in message:
            return "Invalid Enum Value"
        else:
            return "Validation Error"
    
    def _get_suggestions(self, error: ValidationError, path_parts: List[str]) -> List[str]:
        """Get actionable suggestions for fixing the error."""
        suggestions = []
        message = str(error.message)
        
        if "is not of type" in message:
            # Type mismatch - suggest correct type
            if "string" in message and "object" in message:
                suggestions.append("Expected a string but got an object. Did you mean to reference another entity?")
                suggestions.append("Try using: {$ref: '#/entity_type/entity_id'}")
            elif "object" in message and "string" in message:
                suggestions.append("Expected an object but got a string. Did you mean to use a reference?")
                suggestions.append("Try using: {$ref: '#/entity_type/entity_id'}")
        
        elif "required" in message:
            # Missing required field
            field_name = message.split("'")[1] if "'" in message else "field"
            suggestions.append(f"Add the required field '{field_name}' to this entity")
            suggestions.append("Check the schema definition for the correct field structure")
        
        elif "reference" in message or "$ref" in message:
            # Reference issue
            suggestions.append("Check that the referenced entity exists")
            suggestions.append("Verify the reference path format: #/collection_name/entity_id")
            suggestions.append("Make sure the referenced entity has the correct 'id' field")
        
        elif "format" in message:
            # Format issue
            if "media" in message:
                suggestions.append("Ensure the file exists in the project bundle")
                suggestions.append("Check that the file extension is supported")
            elif "markdown" in message:
                suggestions.append("Verify the markdown file path is correct")
                suggestions.append("Check that the file contains valid markdown content")
        
        return suggestions
    
    def _get_error_context(self, path_parts: List[str]) -> Dict[str, Any]:
        """Get context information about where the error occurred."""
        context = {
            "entity_type": None,
            "entity_id": None,
            "field_name": None,
            "available_entities": {}
        }
        
        if len(path_parts) >= 2:
            # Try to determine entity context
            collection_name = path_parts[0]
            if collection_name in self.project_data:
                collection = self.project_data[collection_name]
                if isinstance(collection, list) and len(collection) > 0:
                    context["entity_type"] = collection_name
                    context["available_entities"] = [
                        entity.get("id", entity.get("name", "unknown"))
                        for entity in collection[:5]  # First 5 entities
                    ]
        
        if len(path_parts) >= 1:
            context["field_name"] = path_parts[-1]
        
        return context
    
    def _find_related_reference_errors(self, error: ValidationError, path_parts: List[str]) -> List[Dict[str, Any]]:
        """Find related reference errors that might be connected."""
        related_errors = []
        
        # Look for other entities that might have similar reference issues
        if len(path_parts) >= 2:
            collection_name = path_parts[0]
            if collection_name in self.project_data:
                collection = self.project_data[collection_name]
                if isinstance(collection, list):
                    for i, entity in enumerate(collection):
                        if isinstance(entity, dict):
                            # Check if this entity has similar reference issues
                            for key, value in entity.items():
                                if isinstance(value, dict) and "$ref" in value:
                                    ref = value["$ref"]
                                    if not self._is_valid_reference(ref):
                                        related_errors.append({
                                            "message": f"Invalid reference in {collection_name}[{i}].{key}: {ref}",
                                            "path": f"{collection_name}[{i}].{key}",
                                            "error_type": "Invalid Reference",
                                            "suggestions": [
                                                "Check that the referenced entity exists",
                                                "Verify the reference path format"
                                            ],
                                            "context": {
                                                "entity_type": collection_name,
                                                "entity_id": entity.get("id", f"item_{i}"),
                                                "field_name": key
                                            }
                                        })
        
        return related_errors
    
    def _is_valid_reference(self, ref: str) -> bool:
        """Check if a reference is valid."""
        if not ref.startswith("#/"):
            return False
        
        # Basic validation - could be enhanced
        return len(ref.split("/")) >= 3


def _classify_error(error: ValidationError) -> str:
    """Classify the type of validation error."""
    message = str(error.message).lower()
    
    if "is not of type" in message:
        return "Type Mismatch"
    elif "required" in message or "is a required property" in message:
        return "Missing Required Field"
    elif "additional properties" in message:
        return "Invalid Property"
    elif "reference" in message or "$ref" in message:
        return "Invalid Reference"
    elif "format" in message:
        return "Invalid Format"
    elif "enum" in message:
        return "Invalid Enum Value"
    else:
        return "Validation Error"


def _get_suggestions(error: ValidationError, path_parts: List[str], project_data: Dict[str, Any]) -> List[str]:
    """Get actionable suggestions for fixing the error."""
    suggestions = []
    message = str(error.message)
    
    if "additional properties" in message.lower():
        # Extract the invalid property name from the message
        match = re.search(r"'([^']+)' was unexpected", message)
        if match:
            invalid_prop = match.group(1)
            suggestions.append(f"Remove the '{invalid_prop}' property - it is not defined in the schema")
            suggestions.append("Check the schema definition to see which properties are allowed")
            suggestions.append("Aether enforces strict validation - only properties defined in the schema are permitted")
        else:
            suggestions.append("Remove any properties not defined in the schema")
            suggestions.append("Check the schema definition to see which properties are allowed")
    
    elif "is not of type" in message:
        # Extract expected and actual types
        expected_type = None
        if "'string'" in message:
            expected_type = "string"
        elif "'object'" in message:
            expected_type = "object"
        elif "'array'" in message:
            expected_type = "array"
        elif "'integer'" in message or "'number'" in message:
            expected_type = "number"
        elif "'boolean'" in message:
            expected_type = "boolean"
        
        if expected_type:
            suggestions.append(f"Expected type '{expected_type}'. Check the value type matches the schema.")
            
        if "'string'" in message and "object" in message:
            suggestions.append("Did you mean to use a reference? Try: {$ref: '#/collection/id'}")
        elif "'array'" in message:
            suggestions.append("This field should be an array. Try: field_name: []")
    
    elif "is a required property" in message or "required" in message.lower():
        # Extract field name from message
        match = re.search(r"'([^']+)'", message)
        if match:
            field_name = match.group(1)
            suggestions.append(f"Add the required field '{field_name}' to this entity")
            suggestions.append("Check the schema definition for required fields")
    
    elif "reference" in message or "$ref" in message:
        # Reference issue
        suggestions.append("Check that the referenced entity exists")
        suggestions.append("Verify the reference path format: #/collection_name/entity_id")
        suggestions.append("Make sure the referenced entity has the correct 'id' field")
    
    elif "format" in message:
        # Format issue
        if "media" in message:
            suggestions.append("Ensure the file exists in the project bundle")
            suggestions.append("Check that the file extension is supported")
        elif "markdown" in message:
            suggestions.append("Verify the markdown file path is correct")
            suggestions.append("Check that the file contains valid markdown content")
    
    return suggestions


def _get_error_context(path_parts: List[str], project_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get context information about where the error occurred."""
    context = {
        "entity_type": None,
        "entity_id": None,
        "field_name": None,
        "available_entities": {}
    }
    
    if len(path_parts) >= 1:
        # Try to determine entity context
        collection_name = path_parts[0]
        if collection_name in project_data:
            collection = project_data[collection_name]
            if isinstance(collection, list):
                context["entity_type"] = collection_name
                # Get available entities
                available = []
                for entity in collection[:10]:  # First 10 entities
                    if isinstance(entity, dict):
                        entity_id = entity.get("id", entity.get("name", None))
                        if entity_id:
                            available.append(entity_id)
                context["available_entities"] = available
                
                # If path points to specific entity
                if len(path_parts) >= 2 and isinstance(path_parts[1], int):
                    entity_index = path_parts[1]
                    if 0 <= entity_index < len(collection):
                        entity = collection[entity_index]
                        if isinstance(entity, dict):
                            context["entity_id"] = entity.get("id", f"index_{entity_index}")
    
    if len(path_parts) >= 1:
        context["field_name"] = str(path_parts[-1])
    
    return context


def validate_with_context(
    project_data: Dict[str, Any], 
    derived_schema: Dict[str, Any], 
    zip_ref=None
) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Validate project with enhanced context and error reporting.
    
    Returns:
        Tuple of (is_valid, enhanced_errors)
    """
    from jsonschema import Draft7Validator, ValidationError as JsonSchemaValidationError
    
    # Create validator and collect all errors
    validator = Draft7Validator(derived_schema)
    errors_list = []
    
    # Collect all validation errors
    for error in validator.iter_errors(project_data):
        # Get the path where the error occurred
        path_parts = list(error.absolute_path) if error.absolute_path else []
        
        # For "additionalProperties" errors, extract the invalid field name from the message
        # and add it to the path so VS Code can highlight the correct line
        invalid_field = None
        if "additional properties" in str(error.message).lower():
            match = re.search(r"\('([^']+)'\s+was unexpected\)", str(error.message))
            if match:
                invalid_field = match.group(1)
                # Add the invalid field to the path for better error location
                path_parts_with_field = path_parts + [invalid_field]
                field_path = " -> ".join(str(part) for part in path_parts_with_field)
            else:
                field_path = " -> ".join(str(part) for part in path_parts) if path_parts else "root"
        else:
            field_path = " -> ".join(str(part) for part in path_parts) if path_parts else "root"
        
        # Determine the type of error and provide specific suggestions
        error_type = _classify_error(error)
        suggestions = _get_suggestions(error, path_parts, project_data)
        
        enhanced_error = {
            "message": str(error.message),
            "path": field_path,
            "error_type": error_type,
            "suggestions": suggestions,
            "context": _get_error_context(path_parts, project_data),
            "invalid_field": invalid_field  # Include for tooling to highlight the specific field
        }
        
        errors_list.append(enhanced_error)
    
    return len(errors_list) == 0, errors_list


def format_validation_errors(errors: List[Dict[str, Any]]) -> str:
    """Format validation errors as a readable string."""
    if not errors:
        return "No validation errors found."
    
    lines = []
    lines.append(f"Found {len(errors)} validation error(s):")
    lines.append("")
    
    for i, error in enumerate(errors, 1):
        lines.append(f"{i}. {error['error_type']} at {error['path']}")
        lines.append(f"   Message: {error['message']}")
        
        if error.get('suggestions'):
            lines.append("   Suggestions:")
            for suggestion in error['suggestions']:
                lines.append(f"     • {suggestion}")
        
        if error.get('context', {}).get('available_entities'):
            entities = error['context']['available_entities']
            lines.append(f"   Available entities: {', '.join(entities)}")
        
        lines.append("")
    
    return "\n".join(lines)
