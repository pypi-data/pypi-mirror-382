"""
Aether Spec v1.0.0 - The foundational meta-standard

This module contains the official Aether Spec as a Python dict, loaded from
an embedded YAML string. The spec defines how all Aether Schemas must be
constructed and validated.
"""

import yaml
from typing import Dict, Any


def get_spec() -> Dict[str, Any]:
    """
    Get the official Aether Spec v1.0.0 as a Python dictionary.
    
    Returns:
        Dict containing the Aether Spec schema definition
    """
    return _AETHER_SPEC


# Embedded Aether Spec v1.0.0 as YAML string
_AETHER_SPEC_YAML = """
$schema: http://json-schema.org/draft-07/schema#
definitions:
  propertySchema:
    oneOf:
      - type: object  # Standard JSON Schema object with full Draft 7 support
        properties:
          type: { enum: [string, number, integer, boolean, array, object] }
          items: { $ref: "#/definitions/propertySchema" }  # Recursion for arrays
          properties: { type: object, additionalProperties: { $ref: "#/definitions/propertySchema" } }  # Recursion for objects
          required: { type: array, items: { type: string } }
          $ref: { type: string }  # For schema refs
          # Support standard JSON Schema Draft 7 keywords
          enum: { type: array, minItems: 1 }
          default: {}  # Can be any type
          description: { type: string }
          title: { type: string }
          examples: { type: array }
          # Numeric constraints
          minimum: { type: number }
          maximum: { type: number }
          exclusiveMinimum: { type: number }
          exclusiveMaximum: { type: number }
          multipleOf: { type: number }
          # String constraints
          minLength: { type: integer, minimum: 0 }
          maxLength: { type: integer, minimum: 0 }
          pattern: { type: string }
          format: { type: string }
          # Array constraints
          minItems: { type: integer, minimum: 0 }
          maxItems: { type: integer, minimum: 0 }
          uniqueItems: { type: boolean }
          # Object constraints
          minProperties: { type: integer, minimum: 0 }
          maxProperties: { type: integer, minimum: 0 }
          additionalProperties: { oneOf: [{ type: boolean }, { $ref: "#/definitions/propertySchema" }] }
          # Composition keywords
          allOf: { type: array, items: { $ref: "#/definitions/propertySchema" } }
          anyOf: { type: array, items: { $ref: "#/definitions/propertySchema" } }
          oneOf: { type: array, items: { $ref: "#/definitions/propertySchema" } }
          not: { $ref: "#/definitions/propertySchema" }
        # Allow additional properties for extensibility
        additionalProperties: true
      - type: object  # Custom: Markdown
        properties:
          type: { const: markdown }
          path: { type: string, format: uri-reference }
          inline: { type: string }
          ref_pattern: { type: string, default: '\\{(.+?)\\' }
          resolve_scope: { type: string, default: global }  # global or contextual (e.g., current object)
        required: [type]
        additionalProperties: true  # Allow JSON Schema keywords alongside custom properties
      - type: object  # Custom: Media
        properties:
          type: { const: media }
          media_type: { type: string }
        required: [type, media_type]
        additionalProperties: true  # Allow JSON Schema keywords alongside custom properties
type: object
properties:
  id:
    type: string
    pattern: ^[a-z0-9_-]+$
  spec_version:
    type: string
    pattern: ^\\d+\\.\\d+\\.\\d+$
    description: Version of the Aether Spec this schema conforms to
  version:
    type: string
    pattern: ^\\d+\\.\\d+\\.\\d+(-[a-z0-9]+)?$
    description: Version of this schema itself
  title: { type: string }
  description: { type: string }
  media_types:
    type: array
    items:
      type: object
      properties:
        name: { type: string }
        allowed_extensions:
          type: array
          items:
            type: string
            pattern: ^\\.[a-z0-9]+$
        validation: { type: string, enum: [required, optional, none], default: optional }
      required: [name, allowed_extensions]
      additionalProperties: false
  structure:
    type: object
    additionalProperties: { $ref: "#/definitions/propertySchema" }  # Recursive
  objects:
    type: object
    additionalProperties: { $ref: "#/definitions/propertySchema" }  # Recursive for custom objects
required: [id, spec_version, version, title, structure, objects]
additionalProperties: false
"""

# Load the spec from YAML string
_AETHER_SPEC = yaml.safe_load(_AETHER_SPEC_YAML)
