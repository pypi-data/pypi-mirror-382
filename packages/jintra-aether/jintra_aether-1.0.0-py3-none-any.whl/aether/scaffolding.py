"""
Project scaffolding functionality for generating project structure from schemas.
"""

import os
import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path


def _singularize(word: str) -> str:
    """
    Simple singularization for common English plurals.
    
    Handles common cases like:
    - categories → category
    - posts → post  
    - items → item
    """
    if word.endswith('ies'):
        return word[:-3] + 'y'  # categories → category
    elif word.endswith('ses'):
        return word[:-2]  # processes → process
    elif word.endswith('s'):
        return word[:-1]  # posts → post
    return word


def scaffold_project(
    schema_path: str, 
    output_dir: str, 
    include_examples: bool = True,
    project_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a project structure from a schema.
    
    Creates unified Aether project structure:
        output_dir/
        ├── <project_name>.aether    ← Schema file
        └── project/                  ← Project directory
            ├── project.yaml
            └── collections/          ← Entity collections
    
    Args:
        schema_path: Path to the schema file
        output_dir: Directory to create the project in
        include_examples: Whether to include example/template data
        project_name: Name for the project (defaults to schema name)
    
    Returns:
        Dictionary with created files and directories
    """
    # Load schema
    with open(schema_path, 'r') as f:
        schema_data = yaml.safe_load(f)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get project name
    if not project_name:
        project_name = schema_data.get("id", "my-project")
    
    # Copy schema file to output directory with .aether extension
    schema_filename = f"{project_name}.aether"
    schema_dest = output_path / schema_filename
    with open(schema_path, 'r') as src:
        with open(schema_dest, 'w') as dst:
            dst.write(src.read())
    
    # Create project/ subdirectory
    project_dir = output_path / "project"
    project_dir.mkdir(exist_ok=True)
    
    # Create main project file
    main_project = _create_main_project(schema_data, project_name, include_examples)
    project_yaml_path = project_dir / "project.yaml"
    with open(project_yaml_path, 'w') as f:
        yaml.dump(main_project, f, default_flow_style=False, sort_keys=False)
    
    # Create entity directories and templates
    created_files = {
        schema_filename: str(schema_dest),
        "project/project.yaml": str(project_yaml_path)
    }
    created_dirs = ["project"]
    
    # Get entity collections from schema
    structure = schema_data.get("structure", {})
    for collection_name, collection_def in structure.items():
        if isinstance(collection_def, dict) and collection_def.get("type") == "array":
            # Create directory for this collection inside project/
            collection_dir = project_dir / collection_name
            collection_dir.mkdir(exist_ok=True)
            created_dirs.append(f"project/{collection_name}")
            
            # Create example entity if requested
            if include_examples:
                example_entity = _create_example_entity(collection_name, schema_data)
                entity_singular = _singularize(collection_name)
                example_path = collection_dir / f"example-{entity_singular}"
                example_path.mkdir(exist_ok=True)
                
                # Create metadata file
                metadata_file = example_path / "metadata.yaml"
                with open(metadata_file, 'w') as f:
                    yaml.dump(example_entity, f, default_flow_style=False, sort_keys=False)
                created_files[f"project/{collection_name}/example-{entity_singular}/metadata.yaml"] = str(metadata_file)
                
                # Create content file if needed
                if _collection_has_content(collection_name, schema_data):
                    content_file = example_path / "content.md"
                    with open(content_file, 'w') as f:
                        f.write(f"# Example {entity_singular.title()}\n\nThis is an example {entity_singular}.\n")
                    created_files[f"project/{collection_name}/example-{entity_singular}/content.md"] = str(content_file)
    
    # Create Cursor AI integration files for IDE support
    _create_cursor_integration_files(output_path, created_files)
    
    return {
        "project_name": project_name,
        "output_dir": str(output_path),
        "created_files": created_files,
        "created_directories": created_dirs,
        "schema_info": {
            "id": schema_data.get("id"),
            "version": schema_data.get("version"),
            "title": schema_data.get("title")
        }
    }


def _create_main_project(schema_data: Dict[str, Any], project_name: str, include_examples: bool) -> Dict[str, Any]:
    """Create the main project file content that matches the schema structure."""
    main_project = {}
    
    # Only add fields defined in the schema structure
    structure = schema_data.get("structure", {})
    for field_name, field_def in structure.items():
        if isinstance(field_def, dict):
            if field_def.get("type") == "array":
                # Add empty array for collections
                main_project[field_name] = []
            elif include_examples:
                # Add example values for non-array fields
                field_type = field_def.get("type")
                
                if field_type == "string":
                    # Add example string values
                    if "title" in field_name.lower():
                        main_project[field_name] = f"My {field_name.replace('_', ' ').title()}"
                    elif "description" in field_name.lower():
                        main_project[field_name] = f"A description for {field_name.replace('_', ' ')}"
                    elif "url" in field_name.lower():
                        main_project[field_name] = f"https://example.com"
                    else:
                        main_project[field_name] = f"example-{field_name.replace('_', '-')}"
                        
                elif field_type == "object":
                    # Create object with fields from schema properties
                    properties = field_def.get("properties", {})
                    obj = {}
                    for prop_name, prop_def in properties.items():
                        prop_type = prop_def.get("type") if isinstance(prop_def, dict) else None
                        if prop_type == "string":
                            obj[prop_name] = f"example-{prop_name.replace('_', '-')}"
                        elif prop_type == "boolean":
                            obj[prop_name] = True
                        elif prop_type == "array":
                            obj[prop_name] = []
                    if obj:  # Only add object if it has properties
                        main_project[field_name] = obj
                        
                elif field_type == "boolean":
                    main_project[field_name] = True
                elif field_type == "number" or field_type == "integer":
                    main_project[field_name] = 0
    
    return main_project


def _create_example_entity(collection_name: str, schema_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create an example entity for a collection."""
    entity_name = _singularize(collection_name)
    
    # Get object definition for this collection
    structure = schema_data.get("structure", {})
    collection_def = structure.get(collection_name, {})
    
    if isinstance(collection_def, dict) and "items" in collection_def:
        items_def = collection_def["items"]
        if isinstance(items_def, dict) and "$ref" in items_def:
            ref = items_def["$ref"]
            if ref.startswith("#/objects/"):
                object_name = ref.replace("#/objects/", "")
                objects = schema_data.get("objects", {})
                object_def = objects.get(object_name, {})
                
                if isinstance(object_def, dict):
                    return _create_entity_from_object_def(object_name, object_def)
    
    # Fallback: create basic entity
    return {
        "id": f"example-{entity_name}",
        "name": f"Example {entity_name.title()}",
        "description": f"This is an example {entity_name}."
    }


def _create_entity_from_object_def(object_name: str, object_def: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create an entity from an object definition - only includes properties defined in schema.
    
    NOTE: For directory-based entities, the 'id' field is intentionally skipped.
    The directory name serves as the ID to ensure consistency.
    """
    entity = {}
    
    properties = object_def.get("properties", {})
    for prop_name, prop_def in properties.items():
        if isinstance(prop_def, dict):
            prop_type = prop_def.get("type", "string")
            
            if prop_type == "string":
                # Generate appropriate example values based on property name
                if prop_name == "id":
                    # Skip 'id' field for directory-based entities
                    # The directory name will be used as the ID
                    continue
                elif "title" in prop_name.lower():
                    entity[prop_name] = f"Example {prop_name.replace('_', ' ').title()}"
                elif "description" in prop_name.lower():
                    entity[prop_name] = f"This is an example {prop_name.replace('_', ' ')}."
                elif "name" in prop_name.lower():
                    entity[prop_name] = f"example-{prop_name.replace('_', '-')}"
                elif "url" in prop_name.lower() or "link" in prop_name.lower():
                    entity[prop_name] = "https://example.com"
                elif "email" in prop_name.lower():
                    entity[prop_name] = "example@example.com"
                else:
                    entity[prop_name] = f"example-{prop_name.replace('_', '-')}"
            elif prop_type == "array":
                entity[prop_name] = []
            elif prop_type == "boolean":
                entity[prop_name] = True
            elif prop_type == "number" or prop_type == "integer":
                entity[prop_name] = 0
            elif prop_type == "object":
                # Create object with fields from schema properties
                obj_properties = prop_def.get("properties", {})
                obj = {}
                for obj_prop_name, obj_prop_def in obj_properties.items():
                    obj_prop_type = obj_prop_def.get("type") if isinstance(obj_prop_def, dict) else "string"
                    if obj_prop_type == "string":
                        obj[obj_prop_name] = f"example-{obj_prop_name.replace('_', '-')}"
                    elif obj_prop_type == "boolean":
                        obj[obj_prop_name] = True
                    elif obj_prop_type == "array":
                        obj[obj_prop_name] = []
                    elif obj_prop_type == "number" or obj_prop_type == "integer":
                        obj[obj_prop_name] = 0
                entity[prop_name] = obj if obj else {}
    
    return entity


def _collection_has_content(collection_name: str, schema_data: Dict[str, Any]) -> bool:
    """Check if a collection typically has content files."""
    # This is a heuristic - collections that might have content
    content_collections = ["posts", "articles", "pages", "documents", "content"]
    return any(content_name in collection_name.lower() for content_name in content_collections)


def scaffold_from_bundle(bundle_path: str, output_dir: str) -> Dict[str, Any]:
    """
    Scaffold a project structure from an existing bundle.
    
    Args:
        bundle_path: Path to the .aether bundle file
        output_dir: Directory to create the project in
    
    Returns:
        Dictionary with created files and directories
    """
    from .bundler import extract_bundle
    
    # Extract bundle to get schema and project data
    schema_data, project_data, zip_ref = extract_bundle(bundle_path)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save schema
    schema_path = output_path / "schema.yaml"
    with open(schema_path, 'w') as f:
        yaml.dump(schema_data, f, default_flow_style=False, sort_keys=False)
    
    # Save main project file
    project_path = output_path / "project.yaml"
    with open(project_path, 'w') as f:
        yaml.dump(project_data, f, default_flow_style=False, sort_keys=False)
    
    # Extract all files from bundle
    created_files = {
        "schema.yaml": str(schema_path),
        "project.yaml": str(project_path)
    }
    
    for file_info in zip_ref.filelist:
        if not file_info.is_dir():
            file_path = Path(file_info.filename)
            if file_path.name not in ["schema.yaml", "project.yaml"]:
                # Extract file content
                content = zip_ref.read(file_info.filename)
                
                # Create directory structure
                target_path = output_path / file_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write file
                with open(target_path, 'wb') as f:
                    f.write(content)
                
                created_files[file_info.filename] = str(target_path)
    
    zip_ref.close()
    
    return {
        "project_name": project_data.get("project_name", "extracted-project"),
        "output_dir": str(output_path),
        "created_files": created_files,
        "schema_info": {
            "id": schema_data.get("id"),
            "version": schema_data.get("version"),
            "title": schema_data.get("title")
        }
    }


def _create_cursor_integration_files(output_path: Path, created_files: Dict[str, str]) -> None:
    """
    Create Cursor AI integration files (.cursorrules and .cursorcontext)
    to enable AI-assisted development in IDEs like Cursor.
    """
    cursor_rules_content = """# Aether Framework - Cursor AI Rules

## Project Context

This workspace contains Aether projects - a content management framework with schema-driven validation.

## File Structure

- `*.aether` files: Schema definitions (YAML format)
- `project/` directory: Content entities organized in collections
- `*.aetherpack` files: Bundled projects (ZIP archives)

## Key Concepts

### 1. Strict ID Policy
- **Directory-based entities**: The directory name IS the entity ID
- **NEVER** include `id` field in `metadata.yaml` for directory-based entities
- **Flat-file entities**: CAN have `id` field in the YAML file

### 2. Collections & Entities
- Collections are defined in schema `structure` section
- Entities are directories within collections (e.g., `project/posts/my-post/`)
- Each entity has `metadata.yaml` with required fields from schema

### 3. Nested Collections
- Collections can nest indefinitely (e.g., `posts/my-post/images/photo1/`)
- Sub-collections are defined as array properties in entity schemas
- Automatically created when using `new-entity` command

### 4. Reference Resolution
- Use `x-aether-reference: "#/collection-name"` in schema
- String IDs (e.g., `author: "jane"`) auto-resolve to full objects
- References must point to existing entity IDs (directory names)

## Common Validation Errors

### Error: "The 'id' field is not allowed in directory-based entities"
**Fix**: Remove `id:` line from metadata.yaml. The directory name is used as the ID.

### Error: "Additional properties are not allowed"
**Fix**: Remove any fields not defined in the schema's object definition.

### Error: "Missing required field: X"
**Fix**: Add the required field to metadata.yaml with appropriate value type.

### Error: "Entity with ID 'X' not found in collection 'Y'"
**Fix**: Ensure the referenced entity directory exists in `project/Y/`.

## When Helping with Aether Projects

1. **Check the Schema**: Always look at the `.aether` file to understand structure
2. **Respect ID Policy**: Never suggest adding `id` field to directory-based entities
3. **Validate References**: Ensure referenced entity IDs match existing directory names
4. **Follow Schema Types**: Match field types exactly (string, integer, array, etc.)
5. **Use Available Collections**: Only reference collections defined in schema

## Diagnostics Integration

- Aether validation errors appear in Problems panel with `aether` source
- Errors include suggestions for fixes
- Related information shows context about the issue
- All errors are file-specific and highlight the problematic field

## CLI Commands

- `aether validate-project <dir>` - Validate entire project
- `aether validate-schema <file>` - Validate schema file
- `aether new-entity <dir> <collection> <id>` - Create new entity
- `aether bundle <dir>` - Create .aetherpack bundle
- `aether scaffold <schema> <output>` - Create new project from schema

## Example Workflow

1. **Find Schema**: Locate `.aether` file to understand structure
2. **Check Collections**: Look at `structure` section for available collections
3. **Review Entity Type**: Find object definition in `objects` section
4. **Create Entity**: Use directory name as ID, add required fields
5. **Validate**: Save file to trigger validation, check Problems panel

## When User Reports Validation Errors

1. Read the error message carefully - it contains the fix
2. Check if error relates to ID policy, references, or schema compliance
3. Look at schema definition for the entity type
4. Suggest specific fix based on schema requirements
5. If fixing references, check what entities exist in that collection

## Important Notes

- Aether uses YAML format for all configuration and content
- Schema uses JSON Schema-compatible syntax
- Validation is schema-driven and strict
- Entity IDs must be lowercase with hyphens/underscores only
- All paths use forward slashes, even on Windows
"""

    cursor_context_content = """# Aether Project Context

## Active Schema Validation

This project uses the Aether framework for content management. Validation errors from the Aether extension appear in the Problems panel with source "aether".

## How to Help with Aether Errors

When you see validation errors:

1. **Read the full error message** - It contains specific fix instructions
2. **Check error suggestions** - Related information provides actionable advice
3. **Consult the schema** - Look at the `.aether` file for structure
4. **Verify entity references** - Check that referenced entity directories exist

## Common Fixes

- **"id field not allowed"** → Remove `id:` line (directory name is the ID)
- **"Additional properties"** → Remove fields not in schema
- **"Missing required field"** → Add the field with correct type
- **"Entity not found"** → Create the referenced entity directory

## Reference Pattern

When fixing entity references:
- Use directory names as IDs (e.g., `author: "jane"` references `project/authors/jane/`)
- Check available entities by looking at collection directories
- References auto-resolve to full objects at runtime
"""

    # Create .cursorrules
    cursorrules_path = output_path / ".cursorrules"
    with open(cursorrules_path, 'w', encoding='utf-8') as f:
        f.write(cursor_rules_content)
    created_files[".cursorrules"] = str(cursorrules_path)
    
    # Create .cursorcontext
    cursorcontext_path = output_path / ".cursorcontext"
    with open(cursorcontext_path, 'w', encoding='utf-8') as f:
        f.write(cursor_context_content)
    created_files[".cursorcontext"] = str(cursorcontext_path)
