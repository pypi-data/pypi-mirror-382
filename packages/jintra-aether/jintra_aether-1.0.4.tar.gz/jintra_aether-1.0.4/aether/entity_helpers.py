"""
Entity helper functions for navigating and manipulating project entities.
"""

from typing import Dict, List, Any, Optional, Tuple
import json


def find_entity(project_data: Dict[str, Any], collection_name: str, **filters) -> Optional[Dict[str, Any]]:
    """
    Find a specific entity in a collection based on filters.
    
    Args:
        project_data: The resolved project data
        collection_name: Name of the collection to search
        **filters: Key-value pairs to filter by (e.g., id="jane", name="Jane Doe")
    
    Returns:
        The first matching entity or None if not found
    """
    collection = project_data.get(collection_name, [])
    if not isinstance(collection, list):
        return None
    
    for entity in collection:
        if isinstance(entity, dict):
            # Check if all filter conditions match
            match = True
            for key, value in filters.items():
                if entity.get(key) != value:
                    match = False
                    break
            if match:
                return entity
    
    return None


def list_entities(project_data: Dict[str, Any], collection_name: str) -> List[Dict[str, Any]]:
    """
    Get all entities from a collection.
    
    Args:
        project_data: The resolved project data
        collection_name: Name of the collection
    
    Returns:
        List of entities in the collection
    """
    collection = project_data.get(collection_name, [])
    if isinstance(collection, list):
        return [entity for entity in collection if isinstance(entity, dict)]
    return []


def get_entity_references(project_data: Dict[str, Any], collection_name: str, entity_id: str) -> List[Tuple[str, str]]:
    """
    Find all entities that reference a specific entity.
    
    Args:
        project_data: The resolved project data
        collection_name: Name of the collection containing the referenced entity
        entity_id: ID of the entity to find references for
    
    Returns:
        List of (collection_name, entity_id) tuples that reference the entity
    """
    references = []
    
    # Check all collections for references
    for coll_name, collection in project_data.items():
        if not isinstance(collection, list):
            continue
            
        for entity in collection:
            if not isinstance(entity, dict):
                continue
                
            # Check if this entity references the target entity
            if _entity_references_target(entity, collection_name, entity_id):
                # Find the ID of the referencing entity
                ref_entity_id = entity.get("id") or entity.get("name")
                if ref_entity_id:
                    references.append((coll_name, ref_entity_id))
    
    return references


def _entity_references_target(entity: Dict[str, Any], target_collection: str, target_id: str) -> bool:
    """Check if an entity references a target entity."""
    for key, value in entity.items():
        if _value_references_target(value, target_collection, target_id):
            return True
    return False


def _value_references_target(value: Any, target_collection: str, target_id: str) -> bool:
    """Check if a value references a target entity."""
    if isinstance(value, dict):
        # Check for $ref
        if "$ref" in value:
            ref = value["$ref"]
            if ref.startswith("#/") and f"/{target_collection}/{target_id}" in ref:
                return True
        
        # Recursively check nested objects
        for nested_value in value.values():
            if _value_references_target(nested_value, target_collection, target_id):
                return True
    
    elif isinstance(value, list):
        # Check each item in the list
        for item in value:
            if _value_references_target(item, target_collection, target_id):
                return True
    
    return False


def get_entity_by_path(project_data: Dict[str, Any], path: str) -> Optional[Dict[str, Any]]:
    """
    Get an entity by its path (e.g., "posts/getting-started").
    
    Args:
        project_data: The resolved project data
        path: Path to the entity (collection/entity_id)
    
    Returns:
        The entity or None if not found
    """
    parts = path.split("/", 1)
    if len(parts) != 2:
        return None
    
    collection_name, entity_id = parts
    return find_entity(project_data, collection_name, id=entity_id)


def get_entity_metadata(project_data: Dict[str, Any], collection_name: str, entity_id: str) -> Optional[Dict[str, Any]]:
    """
    Get metadata for a specific entity.
    
    Args:
        project_data: The resolved project data
        collection_name: Name of the collection
        entity_id: ID of the entity
    
    Returns:
        Entity metadata or None if not found
    """
    entity = find_entity(project_data, collection_name, id=entity_id)
    if entity:
        # Return a copy without the main content fields
        metadata = {}
        for key, value in entity.items():
            if key not in ["content", "body", "text", "description"]:
                metadata[key] = value
        return metadata
    return None


def count_entities(project_data: Dict[str, Any], collection_name: str) -> int:
    """
    Count entities in a collection.
    
    Args:
        project_data: The resolved project data
        collection_name: Name of the collection
    
    Returns:
        Number of entities in the collection
    """
    collection = project_data.get(collection_name, [])
    if isinstance(collection, list):
        return len([entity for entity in collection if isinstance(entity, dict)])
    return 0


def get_collection_summary(project_data: Dict[str, Any], collection_name: str) -> Dict[str, Any]:
    """
    Get a summary of a collection.
    
    Args:
        project_data: The resolved project data
        collection_name: Name of the collection
    
    Returns:
        Summary with count, sample entities, and common fields
    """
    entities = list_entities(project_data, collection_name)
    
    if not entities:
        return {
            "count": 0,
            "sample_entities": [],
            "common_fields": []
        }
    
    # Get common fields across all entities
    all_fields = set()
    for entity in entities:
        all_fields.update(entity.keys())
    
    # Get sample entities (first 3)
    sample_entities = entities[:3]
    
    return {
        "count": len(entities),
        "sample_entities": sample_entities,
        "common_fields": sorted(list(all_fields))
    }
