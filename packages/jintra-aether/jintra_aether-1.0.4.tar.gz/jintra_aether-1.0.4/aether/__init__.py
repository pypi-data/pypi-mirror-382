"""
Aether Python Library

A lightweight, extensible framework for structured content authoring and validation.
"""

__version__ = "1.0.4"
__author__ = "Aether Project"

from .spec import get_spec
from .schema import load_schema
from .validator import validate_project
from .resolver import resolve_project
from .bundler import create_bundle, extract_bundle, open_bundle

# Project management features
from .introspection import introspect_schema, SchemaIntrospector
from .entity_helpers import (
    find_entity, list_entities, get_entity_references, 
    get_entity_by_path, get_entity_metadata, count_entities, get_collection_summary
)
from .scaffolding import scaffold_project, scaffold_from_bundle
from .schema_scaffolding import scaffold_schema, create_minimal_schema, add_collection_to_schema
from .inspection import describe_project, format_project_description
from .validation_context import validate_with_context, format_validation_errors

__all__ = [
    # Core functionality
    "get_spec",
    "load_schema", 
    "validate_project",
    "resolve_project",
    "create_bundle",
    "extract_bundle",
    "open_bundle",
    
    # Schema introspection
    "introspect_schema",
    "SchemaIntrospector",
    
    # Entity helpers
    "find_entity",
    "list_entities", 
    "get_entity_references",
    "get_entity_by_path",
    "get_entity_metadata",
    "count_entities",
    "get_collection_summary",
    
    # Project scaffolding
    "scaffold_project",
    "scaffold_from_bundle",
    
    # Schema scaffolding
    "scaffold_schema",
    "create_minimal_schema",
    "add_collection_to_schema",
    
    # Project inspection
    "describe_project",
    "format_project_description",
    
    # Enhanced validation
    "validate_with_context",
    "format_validation_errors",
]
