#!/usr/bin/env python3
"""
Aether CLI - Command-line interface for Aether operations

Provides commands for:
- Validating schemas
- Validating projects
- Creating bundles
- Extracting bundles
- Inspecting bundles

All operations expect unified project structure:
    project-root/
    ├── name.aether
    └── project/
        └── project.yaml
"""

import argparse
import yaml
import sys
import io
from pathlib import Path
from typing import Dict, Any

from aether import (
    get_spec, load_schema, create_bundle, extract_bundle,
    resolve_project, validate_project, scaffold_project
)
from aether.scaffolding import _create_entity_from_object_def, _collection_has_content
from aether.schema_scaffolding import scaffold_schema
from jsonschema import Draft7Validator, ValidationError

# Fix for Windows Unicode handling
# Ensures CLI output works correctly with Unicode characters on Windows
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def validate_schema_cmd(args):
    """Validate a schema against the Aether Spec."""
    print(f"Validating schema: {args.schema}")
    
    # Validate file extension
    if not args.schema.endswith('.aether'):
        print(f"[FAIL] Schema file must have .aether extension")
        print(f"       Got: {args.schema}")
        print(f"       Aether uses .aether for schemas and .aetherpack for bundles")
        return False
    
    try:
        # Load schema
        with open(args.schema, 'r') as f:
            schema_data = yaml.safe_load(f)
        
        print(f"[OK] Schema loaded: {schema_data.get('title', 'Unknown')}")
        
        # Validate against spec
        spec = get_spec()
        validator = Draft7Validator(spec)
        errors = list(validator.iter_errors(schema_data))
        
        if errors:
            print(f"\n[FAIL] Schema validation failed:")
            for error in errors:
                print(f"  - {error.message}")
            return False
        
        print("[OK] Schema is valid against Aether Spec")
        
        # Try to derive
        derived_schema = load_schema(schema_data)
        print(f"[OK] Schema derivation successful")
        print(f"     Derived schema has {len(derived_schema.get('$defs', {}))} object definitions")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def bundle_cmd(args):
    """Create an Aether bundle from a project directory."""
    print(f"Creating bundle from: {args.project_dir}")
    
    try:
        project_dir = Path(args.project_dir)
        
        # Verify unified structure
        if not project_dir.exists():
            print(f"[FAIL] Directory does not exist: {project_dir}")
            return False
        
        aether_files = list(project_dir.glob('*.aether'))
        
        if not aether_files:
            print("[FAIL] No .aether schema file found in project root")
            print("\nExpected structure:")
            print("  project-root/")
            print("    ├── name.aether")
            print("    └── project/")
            print("        └── project.yaml")
            return False
        
        if len(aether_files) > 1:
            print(f"[FAIL] Multiple .aether files found: {[f.name for f in aether_files]}")
            print("       Only one schema file is allowed per project")
            return False
        
        schema_file = aether_files[0]
        print(f"[OK] Found schema: {schema_file.name}")
        
        # Check for project/ subdirectory
        project_subdir = project_dir / 'project'
        if not project_subdir.exists():
            print("[FAIL] No project/ subdirectory found")
            print(f"       Expected: {project_subdir}")
            return False
        
        # Check for project/project.yaml
        project_yaml = project_subdir / 'project.yaml'
        if not project_yaml.exists():
            print("[FAIL] No project.yaml found in project/ subdirectory")
            print(f"       Expected: {project_yaml}")
            return False
        
        print(f"[OK] Found project.yaml")
        
        # Create bundle
        output_path = args.output if args.output else f"{project_dir.name}.aetherpack"
        
        # Validate output file extension
        if not output_path.endswith('.aetherpack'):
            print(f"[FAIL] Bundle output must have .aetherpack extension")
            print(f"       Got: {output_path}")
            print(f"       Aether uses .aether for schemas and .aetherpack for bundles")
            return False
        
        print(f"[OK] Creating bundle...")
        bundle_bytes = create_bundle(str(project_dir), output_path)
        
        print(f"[OK] Bundle created: {len(bundle_bytes)} bytes")
        print(f"[OK] Saved to: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error creating bundle: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_project_cmd(args):
    """Validate a project directory against its schema."""
    print(f"Validating project: {args.project_dir}")
    
    try:
        project_dir = Path(args.project_dir)
        
        # Find schema
        if args.schema:
            schema_path = Path(args.schema)
        else:
            # Look for .aether file in project root
            aether_files = list(project_dir.glob('*.aether'))
            if not aether_files:
                print("[FAIL] No .aether schema file found")
                print("       Specify with --schema or place schema.aether in project root")
                return False
            schema_path = aether_files[0]
        
        print(f"[OK] Using schema: {schema_path}")
        
        # Load schema
        with open(schema_path, 'r') as f:
            schema_data = yaml.safe_load(f)
        print(f"[OK] Schema loaded: {schema_data.get('title', 'Unknown')}")
        
        # Derive schema
        derived_schema = load_schema(schema_data)
        print(f"[OK] Schema derived")
        
        # Load project
        project_yaml_path = project_dir / 'project' / 'project.yaml'
        if not project_yaml_path.exists():
            # Try root level for compatibility
            project_yaml_path = project_dir / 'project.yaml'
            if not project_yaml_path.exists():
                print(f"[FAIL] project.yaml not found")
                print(f"       Expected: {project_dir}/project/project.yaml")
                return False
        
        with open(project_yaml_path, 'r') as f:
            project_data = yaml.safe_load(f)
        print(f"[OK] Project loaded")
        
        # Create a temporary bundle for validation
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.aetherpack', delete=False) as tmp:
            temp_bundle = tmp.name
        
        try:
            create_bundle(str(project_dir), temp_bundle)
            schema, project, zip_ref = extract_bundle(temp_bundle)
            
            # Use enhanced validation with context
            from aether.validation_context import validate_with_context, format_validation_errors
            is_valid, errors = validate_with_context(project, derived_schema, zip_ref)
            
            # IMPORTANT: Close zip_ref before trying to delete on Windows
            zip_ref.close()
            
            if is_valid:
                print("[OK] Project validation passed!")
                return True
            else:
                # Output errors in both human-readable and JSON format
                print(f"[FAIL] Project validation failed with {len(errors)} error(s)")
                print("")
                
                # Human-readable format
                print(format_validation_errors(errors))
                
                # JSON format for tooling (on stderr for parsing)
                import json
                print("__AETHER_ERRORS_JSON__", file=sys.stderr)
                print(json.dumps(errors), file=sys.stderr)
                print("__AETHER_ERRORS_END__", file=sys.stderr)
                
                return False
            
        finally:
            # Ensure zip is closed before deletion
            try:
                if 'zip_ref' in locals() and zip_ref:
                    zip_ref.close()
            except:
                pass
            # Delete temp file
            try:
                Path(temp_bundle).unlink()
            except PermissionError:
                # On Windows, file might still be locked - ignore
                pass
        
    except ValidationError as e:
        print(f"[FAIL] Validation failed: {e.message}")
        print(f"       Path: {'.'.join(str(p) for p in e.path)}")
        return False
    except Exception as e:
        error_str = str(e)
        print(f"[FAIL] Error: {error_str}")
        
        # Try to extract file path from error message for better error reporting
        import re
        file_match = re.search(r'File: (project/[^\n]+\.yaml)', error_str)
        
        if file_match:
            file_path = file_match.group(1)
            
            # Format as structured error for VS Code
            errors = [{
                "message": error_str.split('\n')[0],  # First line of error
                "path": file_path,
                "error_type": "Validation Error",
                "suggestions": [line.strip() for line in error_str.split('\n')[1:] if line.strip() and not line.strip().startswith('File:')],
                "context": {"file": file_path}
            }]
            
            # Output JSON format for tooling
            import json
            print("__AETHER_ERRORS_JSON__", file=sys.stderr)
            print(json.dumps(errors), file=sys.stderr)
            print("__AETHER_ERRORS_END__", file=sys.stderr)
        else:
            import traceback
            traceback.print_exc()
        
        return False


def extract_cmd(args):
    """Extract an Aether bundle."""
    print(f"Extracting bundle: {args.bundle}")
    
    # Validate file extension
    if not args.bundle.endswith('.aetherpack'):
        print(f"[FAIL] Bundle file must have .aetherpack extension")
        print(f"       Got: {args.bundle}")
        print(f"       Aether uses .aether for schemas and .aetherpack for bundles")
        return False
    
    try:
        output_dir = Path(args.output) if args.output else Path('.')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract to inspect structure
        schema, project, zip_ref = extract_bundle(args.bundle)
        
        if args.list:
            # Just list contents
            print("\nBundle contents:")
            for name in sorted(zip_ref.namelist()):
                print(f"  {name}")
            zip_ref.close()
            return True
        
        # Extract all files
        print(f"[OK] Extracting to: {output_dir}")
        zip_ref.extractall(output_dir)
        zip_ref.close()
        
        print(f"[OK] Extracted {len(zip_ref.namelist())} files")
        print(f"[OK] Schema: {schema.get('title', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error extracting bundle: {e}")
        return False


def scaffold_schema_cmd(args):
    """Scaffold a new schema file with proper structure."""
    print(f"Creating schema: {args.output}")
    
    try:
        # Parse collections if provided
        collections = None
        if args.collections:
            collections = [c.strip() for c in args.collections.split(',')]
        
        # Scaffold the schema
        schema = scaffold_schema(
            schema_id=args.id,
            output_path=args.output,
            title=args.title,
            collections=collections,
            include_examples=not args.no_examples
        )
        
        print(f"[OK] Schema created: {args.output}")
        print(f"     ID: {schema['id']}")
        print(f"     Title: {schema['title']}")
        
        if collections:
            print(f"     Collections: {', '.join(collections)}")
        
        print()
        print("Next steps:")
        print(f"  1. Review and customize: {args.output}")
        print(f"  2. Scaffold project: aether scaffold {args.output} my-project")
        print(f"  3. Add content to my-project/")
        print(f"  4. Validate: aether validate-project my-project")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error creating schema: {e}")
        return False


def scaffold_cmd(args):
    """Scaffold a new project from a schema."""
    print(f"Scaffolding project from schema: {args.schema}")
    
    # Validate file extension
    if not args.schema.endswith('.aether'):
        print(f"[FAIL] Schema file must have .aether extension")
        print(f"       Got: {args.schema}")
        print(f"       Aether uses .aether for schemas and .aetherpack for bundles")
        return False
    
    try:
        schema_path = Path(args.schema)
        if not schema_path.exists():
            print(f"[FAIL] Schema file not found: {schema_path}")
            return False
        
        output_dir = Path(args.output)
        
        # Determine project name
        project_name = args.name if hasattr(args, 'name') and args.name else schema_path.stem
        
        print(f"[OK] Creating project: {project_name}")
        print(f"[OK] Output directory: {output_dir}")
        
        # Scaffold the project
        result = scaffold_project(
            schema_path=str(schema_path),
            output_dir=str(output_dir),
            include_examples=not args.no_examples,
            project_name=project_name
        )
        
        # Report results
        print(f"\n[OK] Project scaffolded successfully!")
        print(f"[OK] Created {len(result['created_files'])} files")
        print(f"[OK] Created {len(result['created_directories'])} directories")
        
        # Output created files for VS Code parsing
        for rel_path in result['created_files'].keys():
            print(f"Created file: {rel_path}")
        for dir_name in result['created_directories']:
            print(f"Created directory: {dir_name}")
        
        if args.verbose:
            print("\nDetailed structure:")
            for rel_path in result['created_files'].keys():
                print(f"  - {rel_path}")
            print("\nDirectories:")
            for dir_name in result['created_directories']:
                print(f"  - {dir_name}/")
        
        print(f"\nProject structure:")
        print(f"  {output_dir}/")
        print(f"  ├── {project_name}.aether")
        print(f"  └── project/")
        print(f"      └── project.yaml")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error scaffolding project: {e}")
        import traceback
        traceback.print_exc()
        return False


def new_entity_cmd(args):
    """Create a new entity in a collection (supports nested collections)."""
    print(f"Creating new entity: {args.entity_id}")
    
    try:
        project_dir = Path(args.project_dir)
        
        # Parse collection path - supports nested paths like "posts/my-post/images"
        collection_path_parts = args.collection.split('/')
        collection_name = collection_path_parts[0]  # Top-level collection
        
        # Build full path
        full_collection_path = project_dir / 'project' / args.collection
        
        # For nested collections, verify parent entity exists
        if len(collection_path_parts) > 1:
            # Extract parent path (e.g., "posts/my-travel-post" from "posts/my-travel-post/images")
            parent_path = project_dir / 'project' / '/'.join(collection_path_parts[:-1])
            if not parent_path.exists():
                print(f"[FAIL] Parent entity directory not found: {parent_path}")
                print(f"       Make sure the parent entity exists before creating nested collections")
                return False
            
            # Create the sub-collection directory if it doesn't exist
            if not full_collection_path.exists():
                full_collection_path.mkdir(parents=True, exist_ok=True)
                print(f"[OK] Created sub-collection directory: {full_collection_path}")
        else:
            # Top-level collection must already exist
            if not full_collection_path.exists():
                print(f"[FAIL] Collection directory not found: {full_collection_path}")
                print(f"       Run 'scaffold' command to create project structure first")
                return False
        
        # Find schema
        if args.schema:
            schema_path = Path(args.schema)
        else:
            aether_files = list(project_dir.glob('*.aether'))
            if not aether_files:
                print("[FAIL] No .aether schema file found")
                return False
            schema_path = aether_files[0]
        
        print(f"[OK] Using schema: {schema_path}")
        
        # Load schema
        with open(schema_path, 'r') as f:
            schema_data = yaml.safe_load(f)
        
        # Navigate through nested schema to find the target collection definition
        object_def = None
        object_name = None
        
        if len(collection_path_parts) == 1:
            # Top-level collection (e.g., "posts")
            structure = schema_data.get('structure', {})
            collection_def = structure.get(collection_name)
            
            if not collection_def or collection_def.get('type') != 'array':
                print(f"[FAIL] Collection '{collection_name}' not found in schema or is not an array")
                return False
            
            items_ref = collection_def.get('items', {}).get('$ref', '')
            if not items_ref.startswith('#/objects/'):
                print(f"[FAIL] Could not determine entity type from schema")
                return False
            
            object_name = items_ref.replace('#/objects/', '')
            object_def = schema_data.get('objects', {}).get(object_name)
        else:
            # Nested collection (e.g., "posts/my-post/images")
            # Path format: collection/entity-id/sub-collection/sub-entity-id/...
            # We need to skip entity IDs and only navigate through collection names
            
            # Start with top-level collection
            structure = schema_data.get('structure', {})
            top_collection_def = structure.get(collection_name)
            if not top_collection_def:
                print(f"[FAIL] Top-level collection '{collection_name}' not found in schema")
                return False
            
            items_ref = top_collection_def.get('items', {}).get('$ref', '')
            if not items_ref.startswith('#/objects/'):
                print(f"[FAIL] Could not determine entity type from schema")
                return False
            
            current_object_name = items_ref.replace('#/objects/', '')
            
            # Navigate through path: skip entity IDs, process collection names
            # For "posts/my-post/images", we skip "my-post" (entity) and process "images" (collection)
            for i in range(1, len(collection_path_parts)):
                part = collection_path_parts[i]
                
                # Get the current object definition
                current_object_def = schema_data.get('objects', {}).get(current_object_name)
                if not current_object_def:
                    print(f"[FAIL] Object '{current_object_name}' not found in schema")
                    return False
                
                properties = current_object_def.get('properties', {})
                
                # Check if this part is a collection (has array type in schema)
                if part in properties and properties[part].get('type') == 'array':
                    # This is a sub-collection
                    sub_prop_def = properties[part]
                    sub_items_ref = sub_prop_def.get('items', {}).get('$ref', '')
                    
                    if not sub_items_ref.startswith('#/objects/'):
                        print(f"[FAIL] Could not determine type for collection '{part}'")
                        return False
                    
                    current_object_name = sub_items_ref.replace('#/objects/', '')
                else:
                    # This part is an entity ID (e.g., "my-post"), not a collection
                    # Skip it - stay with current object type
                    pass
            
            object_name = current_object_name
            object_def = schema_data.get('objects', {}).get(object_name)
        
        if not object_def:
            print(f"[FAIL] Object definition '{object_name}' not found in schema")
            return False
        
        print(f"[OK] Creating {object_name} entity in {args.collection}")
        
        # Create entity directory
        entity_dir = full_collection_path / args.entity_id
        entity_dir.mkdir(parents=True, exist_ok=True)
        print(f"[OK] Created directory: {entity_dir}")
        
        # Generate metadata
        metadata = _create_entity_from_object_def(object_name, object_def)
        metadata_path = entity_dir / 'metadata.yaml'
        with open(metadata_path, 'w') as f:
            yaml.dump(metadata, f, default_flow_style=False, sort_keys=False)
        print(f"[OK] Created file: {metadata_path}")
        
        # Create content.md if applicable
        if _collection_has_content(collection_name, schema_data):
            content_path = entity_dir / 'content.md'
            with open(content_path, 'w') as f:
                f.write(f"# {args.entity_id}\n\nYour content here...\n")
            print(f"[OK] Created file: {content_path}")
        
        # Create sub-collection directories if defined in schema
        sub_collections_created = []
        properties = object_def.get('properties', {})
        for prop_name, prop_def in properties.items():
            # If property is an array with object items, it's a sub-collection
            if prop_def.get('type') == 'array':
                items_def = prop_def.get('items', {})
                if items_def.get('$ref') or items_def.get('type') == 'object':
                    # This is a sub-collection - create its directory
                    sub_collection_dir = entity_dir / prop_name
                    if not sub_collection_dir.exists():
                        sub_collection_dir.mkdir(parents=True, exist_ok=True)
                        sub_collections_created.append(prop_name)
                        print(f"[OK] Created sub-collection directory: {sub_collection_dir}")
        
        print(f"\n[OK] Entity created successfully!")
        print(f"[OK] Entity ID: {args.entity_id} (from directory name)")
        print(f"[OK] Location: project/{args.collection}/{args.entity_id}/")
        if sub_collections_created:
            print(f"[OK] Sub-collections ready: {', '.join(sub_collections_created)}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error creating entity: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Aether CLI - Structured content authoring and validation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate a schema
  aether validate-schema blog.aether
  
  # Validate a project
  aether validate-project examples/blog --schema examples/blog/blog.aether
  
  # Create a bundle
  aether bundle examples/blog -o blog.aetherpack
  
  # Extract a bundle
  aether extract blog.aetherpack --output extracted/
  
  # List bundle contents
  aether extract blog.aetherpack --list
  
  # Scaffold a new project from a schema
  aether scaffold blog.aether my-blog-project --name my-blog
  
  # Create a new entity in a top-level collection
  aether new-entity examples/blog posts my-new-post
  
  # Create a new entity in a nested collection
  aether new-entity examples/blog posts/my-new-post/images sunset-photo
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # validate-schema command
    validate_schema_parser = subparsers.add_parser(
        'validate-schema',
        help='Validate a schema against the Aether Spec'
    )
    validate_schema_parser.add_argument('schema', help='Path to schema (.aether file)')
    
    # validate-project command
    validate_project_parser = subparsers.add_parser(
        'validate-project',
        help='Validate a project against its schema'
    )
    validate_project_parser.add_argument('project_dir', help='Path to project directory')
    validate_project_parser.add_argument('--schema', help='Path to schema file (auto-detected if not specified)')
    
    # bundle command
    bundle_parser = subparsers.add_parser(
        'bundle',
        help='Create an Aether bundle from a project directory'
    )
    bundle_parser.add_argument('project_dir', help='Path to project root directory')
    bundle_parser.add_argument('-o', '--output', help='Output bundle path (default: <project-name>.aetherpack)')
    bundle_parser.add_argument('--schema', help='Path to schema file (auto-detected if not specified)')
    
    # extract command
    extract_parser = subparsers.add_parser(
        'extract',
        help='Extract an Aether bundle'
    )
    extract_parser.add_argument('bundle', help='Path to bundle file')
    extract_parser.add_argument('--output', help='Output directory (default: current directory)')
    extract_parser.add_argument('--list', action='store_true', help='List bundle contents without extracting')
    
    # scaffold-schema command
    scaffold_schema_parser = subparsers.add_parser(
        'scaffold-schema',
        help='Create a new schema file with proper structure'
    )
    scaffold_schema_parser.add_argument('id', help='Schema ID (e.g., "blog", "my-project")')
    scaffold_schema_parser.add_argument('output', help='Output file path (e.g., "blog.aether")')
    scaffold_schema_parser.add_argument('--title', help='Human-readable title (default: derived from ID)')
    scaffold_schema_parser.add_argument('--collections', help='Comma-separated list of collections (e.g., "posts,authors")')
    scaffold_schema_parser.add_argument('--no-examples', action='store_true', help='Do not include example comments')
    
    # scaffold command
    scaffold_parser = subparsers.add_parser(
        'scaffold',
        help='Scaffold a new project from a schema'
    )
    scaffold_parser.add_argument('schema', help='Path to schema file (.aether)')
    scaffold_parser.add_argument('output', help='Output directory')
    scaffold_parser.add_argument('--name', help='Project name (default: schema filename)')
    scaffold_parser.add_argument('--no-examples', action='store_true', help='Do not include example entities')
    scaffold_parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    
    # new-entity command
    new_entity_parser = subparsers.add_parser(
        'new-entity',
        help='Create a new entity in a collection (supports nested collections)'
    )
    new_entity_parser.add_argument('project_dir', help='Path to project root directory')
    new_entity_parser.add_argument('collection', help='Collection path (e.g., "posts" or "posts/my-post/images")')
    new_entity_parser.add_argument('entity_id', help='Entity ID (will be used as directory name)')
    new_entity_parser.add_argument('--schema', help='Path to schema file (auto-detected if not specified)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to command handler
    command_handlers = {
        'validate-schema': validate_schema_cmd,
        'validate-project': validate_project_cmd,
        'bundle': bundle_cmd,
        'extract': extract_cmd,
        'scaffold-schema': scaffold_schema_cmd,
        'scaffold': scaffold_cmd,
        'new-entity': new_entity_cmd
    }
    
    handler = command_handlers.get(args.command)
    if handler:
        success = handler(args)
        return 0 if success else 1
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())

