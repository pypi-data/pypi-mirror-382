"""
Schema introspection helpers for understanding schema requirements and capabilities.
"""

from typing import Dict, List, Set, Any, Optional
import json


class SchemaIntrospector:
    """Helper class for introspecting Aether schemas."""
    
    def __init__(self, derived_schema: Dict[str, Any]):
        """Initialize with a derived JSON Schema."""
        self.schema = derived_schema
        self.properties = derived_schema.get("properties", {})
        self.definitions = derived_schema.get("$defs", {})
    
    def get_required_fields(self) -> List[str]:
        """Get list of required fields in the main structure."""
        return self.schema.get("required", [])
    
    def get_object_types(self) -> List[str]:
        """Get list of object types defined in the schema."""
        return list(self.definitions.keys())
    
    def get_entity_collections(self) -> List[str]:
        """Get list of entity collections (properties that are arrays of objects)."""
        collections = []
        for prop_name, prop_def in self.properties.items():
            if isinstance(prop_def, dict):
                # Check if it's an array of objects
                if (prop_def.get("type") == "array" and 
                    "items" in prop_def and 
                    isinstance(prop_def["items"], dict) and
                    "$ref" in prop_def["items"]):
                    collections.append(prop_name)
        return collections
    
    def get_media_types(self) -> List[str]:
        """Get list of media types used in the schema."""
        media_types = set()
        self._find_media_types(self.schema, media_types)
        return list(media_types)
    
    def _find_media_types(self, schema_part: Any, media_types: Set[str]) -> None:
        """Recursively find media types in schema."""
        if isinstance(schema_part, dict):
            if schema_part.get("type") == "string" and "format" in schema_part:
                if schema_part["format"] in ["media", "markdown"]:
                    media_types.add(schema_part["format"])
            
            for value in schema_part.values():
                self._find_media_types(value, media_types)
        elif isinstance(schema_part, list):
            for item in schema_part:
                self._find_media_types(item, media_types)
    
    def get_object_schema(self, object_type: str) -> Optional[Dict[str, Any]]:
        """Get the schema definition for a specific object type."""
        return self.definitions.get(object_type)
    
    def get_object_properties(self, object_type: str) -> Dict[str, Any]:
        """Get properties for a specific object type."""
        obj_schema = self.get_object_schema(object_type)
        if obj_schema:
            return obj_schema.get("properties", {})
        return {}
    
    def get_object_references(self, object_type: str) -> List[str]:
        """Get list of references (other object types) used by an object type."""
        references = []
        obj_schema = self.get_object_schema(object_type)
        if obj_schema:
            self._find_references(obj_schema, references)
        return references
    
    def _find_references(self, schema_part: Any, references: List[str]) -> None:
        """Recursively find $ref references in schema."""
        if isinstance(schema_part, dict):
            if "$ref" in schema_part:
                ref = schema_part["$ref"]
                if ref.startswith("#/$defs/"):
                    ref_type = ref.replace("#/$defs/", "")
                    if ref_type not in references:
                        references.append(ref_type)
            
            for value in schema_part.values():
                self._find_references(value, references)
        elif isinstance(schema_part, list):
            for item in schema_part:
                self._find_references(item, references)
    
    def get_collection_item_type(self, collection_name: str) -> Optional[str]:
        """Get the object type for items in a collection."""
        collection_def = self.properties.get(collection_name, {})
        if isinstance(collection_def, dict) and "items" in collection_def:
            items_def = collection_def["items"]
            if isinstance(items_def, dict) and "$ref" in items_def:
                ref = items_def["$ref"]
                if ref.startswith("#/$defs/"):
                    return ref.replace("#/$defs/", "")
        return None
    
    def get_field_type(self, field_name: str) -> Optional[str]:
        """Get the type of a field in the main structure."""
        field_def = self.properties.get(field_name, {})
        if isinstance(field_def, dict):
            return field_def.get("type")
        return None
    
    def is_required_field(self, field_name: str) -> bool:
        """Check if a field is required."""
        return field_name in self.get_required_fields()
    
    def get_schema_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the schema."""
        return {
            "required_fields": self.get_required_fields(),
            "object_types": self.get_object_types(),
            "entity_collections": self.get_entity_collections(),
            "media_types": self.get_media_types(),
            "total_properties": len(self.properties),
            "total_definitions": len(self.definitions)
        }


def introspect_schema(derived_schema: Dict[str, Any]) -> SchemaIntrospector:
    """Create a schema introspector for the given derived schema."""
    return SchemaIntrospector(derived_schema)
