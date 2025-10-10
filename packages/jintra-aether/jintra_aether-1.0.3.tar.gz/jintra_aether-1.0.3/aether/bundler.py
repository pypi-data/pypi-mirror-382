"""
ZIP bundling and extraction for Aether projects.

Unified Structure Convention:
- Project root contains exactly one .aether schema file and a project/ subdirectory
- Bundles preserve this structure exactly (no file renaming or transformation)
- Development, bundled, and extracted structures are identical

Project Structure:
    project-root/
    ├── name.aether      ← Schema file
    └── project/         ← Project directory
        ├── project.yaml ← Root project data
        └── entities/    ← Entity collections (directories or YAML files)

Supports both flat (single-file) and hierarchical (directory-based) entity structures.
"""

import zipfile
import yaml
import datetime
from typing import Dict, Any, Tuple, Optional
from io import BytesIO
from pathlib import Path
from contextlib import contextmanager


def _convert_dates_to_strings(data: Any) -> Any:
    """
    Recursively convert date/datetime objects to ISO format strings.
    
    YAML parsers auto-convert ISO date strings to date objects, but our schemas
    expect strings. This function walks the data structure and converts them back.
    """
    if isinstance(data, (datetime.date, datetime.datetime)):
        return data.isoformat()
    elif isinstance(data, dict):
        return {key: _convert_dates_to_strings(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_convert_dates_to_strings(item) for item in data]
    else:
        return data


def create_bundle(root_dir: str, output_path: str = None) -> bytes:
    """
    Create an Aether bundle by zipping a project directory.
    
    The directory must contain exactly one .aether schema file and a project/ subdirectory.
    
    Unified Structure:
        project-root/
        ├── name.aether      ← Schema file
        └── project/         ← Project directory
            ├── project.yaml ← Root project data
            └── entities/    ← Entity collections
    
    Args:
        root_dir: Path to project root directory
        output_path: Optional output path for bundle file (.aetherpack)
        
    Returns:
        ZIP archive as bytes
        
    Raises:
        ValueError: If directory structure is invalid or doesn't follow unified format
    """
    root_path = Path(root_dir)
    
    if not root_path.exists():
        raise ValueError(f"Directory does not exist: {root_dir}")
    
    # Find .aether schema file
    aether_files = list(root_path.glob('*.aether'))
    
    if len(aether_files) == 0:
        raise ValueError(f"No .aether schema file found in {root_dir}")
    elif len(aether_files) > 1:
        raise ValueError(
            f"Multiple .aether files found in {root_dir}: {[f.name for f in aether_files]}. "
            f"Only one schema file is allowed per project."
        )
    
    # Verify project/ directory exists
    project_dir = root_path / 'project'
    if not project_dir.exists():
        raise ValueError(
            f"No project/ subdirectory found in {root_dir}. "
            f"Expected structure: {root_dir}/project/project.yaml"
        )
    
    # Verify project/project.yaml exists
    project_yaml = project_dir / 'project.yaml'
    if not project_yaml.exists():
        raise ValueError(
            f"No project.yaml found in {project_dir}. "
            f"Expected: {project_dir}/project.yaml"
        )
    
    # Create bundle
    buffer = BytesIO()
    
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add all files, preserving structure
        for file_path in root_path.rglob('*'):
            if file_path.is_file():
                # Skip output file if bundling in place
                if output_path and Path(output_path).exists():
                    try:
                        if file_path.samefile(Path(output_path)):
                            continue
                    except (OSError, ValueError):
                        pass
                
                # Calculate relative path from root
                arcname = file_path.relative_to(root_path)
                zip_file.write(file_path, arcname)
    
    buffer.seek(0)
    bundle_bytes = buffer.getvalue()
    
    # Save to file if output_path specified
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(bundle_bytes)
    
    return bundle_bytes


def extract_bundle(bundle_path: str) -> Tuple[Dict[str, Any], Dict[str, Any], zipfile.ZipFile]:
    """
    Extract an Aether project bundle from a ZIP file.
    
    Expects unified structure with .aether schema file and project/ subdirectory.
    Automatically loads hierarchical entity structures from project/ directory.
    
    Expected Structure:
        name.aether       ← Schema file
        project/          ← Project directory
          project.yaml    ← Root project data
          entities/       ← Entity collections
    
    Args:
        bundle_path: Path to the .aetherpack bundle file
        
    Returns:
        Tuple of (schema_data, project_data, zip_file) where zip_file is open for reading
        
    Raises:
        ValueError: If the bundle is invalid or doesn't follow unified structure
    """
    try:
        zip_file = zipfile.ZipFile(bundle_path, 'r')
    except zipfile.BadZipFile:
        raise ValueError(f"Invalid ZIP file: {bundle_path}")
    
    zip_contents = zip_file.namelist()
    
    # Find .aether schema file at root
    aether_files = [f for f in zip_contents if f.endswith('.aether') and '/' not in f]
    
    if not aether_files:
        zip_file.close()
        raise ValueError(
            f"No .aether schema file found in bundle root.\n"
            f"Expected unified structure:\n"
            f"  name.aether\n"
            f"  project/\n"
            f"    project.yaml\n"
            f"    entities/"
        )
    
    if len(aether_files) > 1:
        zip_file.close()
        raise ValueError(
            f"Multiple .aether files found in bundle: {aether_files}.\n"
            f"Only one schema file is allowed per project."
        )
    
    try:
        schema_file = aether_files[0]
        project_file = 'project/project.yaml'
        
        # Verify project/project.yaml exists
        if project_file not in zip_contents:
            zip_file.close()
            raise ValueError(
                f"Missing {project_file}.\n"
                f"Bundle must contain project/ subdirectory with project.yaml"
            )
        
        # Load schema from .aether file
        schema_bytes = zip_file.read(schema_file)
        schema_data = yaml.safe_load(schema_bytes)
        schema_data = _convert_dates_to_strings(schema_data)
        
        # Load project.yaml from project/ subdirectory
        project_bytes = zip_file.read(project_file)
        project_data = yaml.safe_load(project_bytes)
        project_data = _convert_dates_to_strings(project_data)
        
        # Load hierarchical entities from project/ directory
        project_data = _load_hierarchical_entities(zip_file, schema_data, project_data)
        
        return schema_data, project_data, zip_file
        
    except yaml.YAMLError as e:
        zip_file.close()
        raise ValueError(f"Error parsing YAML in bundle: {e}")
    except Exception as e:
        zip_file.close()
        raise ValueError(f"Error extracting bundle: {e}")


def _load_hierarchical_entities(
    zip_file: zipfile.ZipFile,
    schema_data: Dict[str, Any],
    project_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Load hierarchical entity structures from project/ subdirectory.
    
    Auto-detects entity collection directories within project/ and loads their contents.
    Supports nested sub-collections within entities (e.g., posts/my-post/images/).
    
    Args:
        zip_file: Open ZipFile object
        schema_data: Schema definition
        project_data: Base project data from project/project.yaml
        
    Returns:
        Updated project_data with entity collections populated
    """
    # Get all files in the ZIP
    zip_contents = zip_file.namelist()
    
    # Find all potential entity collection directories within project/
    potential_collections = set()
    project_prefix = 'project/'
    reserved_files = {'project/project.yaml'}
    
    for file_path in zip_contents:
        # Skip reserved files
        if file_path in reserved_files:
            continue
        
        # Only look at files within project/ directory
        if not file_path.startswith(project_prefix):
            continue
            
        # Remove project/ prefix
        relative_path = file_path[len(project_prefix):]
        parts = relative_path.split('/')
        
        if len(parts) >= 2:  # At least collection/something
            collection_name = parts[0]
            # Skip if it's a dot file or hidden
            if not collection_name.startswith('.'):
                potential_collections.add(collection_name)
    
    # Load entities from each detected collection directory
    for collection_name in sorted(potential_collections):
        collection_dir = f"project/{collection_name}/"
        
        # Find all entities - either in subdirectories or as direct files
        entity_items = set()
        
        for file_path in zip_contents:
            if file_path.startswith(collection_dir):
                remainder = file_path[len(collection_dir):]
                parts = remainder.split('/')
                
                if len(parts) == 1 and remainder.endswith('.yaml'):
                    # Direct file: project/authors/jane.yaml
                    entity_id = parts[0].replace('.yaml', '')
                    if entity_id:
                        entity_items.add(('file', entity_id))
                elif len(parts) >= 2:
                    # Subdirectory: project/posts/post1/metadata.yaml
                    entity_id = parts[0]
                    if entity_id:
                        entity_items.add(('dir', entity_id))
        
        # Load entities
        if entity_items:
            entities = []
            seen_ids = set()
            for item_type, entity_id in sorted(entity_items):
                entity_data = _load_entity_from_directory(
                    zip_file,
                    collection_dir,
                    entity_id
                )
                if entity_data:
                    # Strict ID policy: For directory-based entities, the 'id' field is not allowed
                    # The directory name IS the ID to prevent confusion and ensure consistency
                    if item_type == 'dir' and 'id' in entity_data:
                        # Determine the file path for better error message
                        metadata_file = f"{collection_dir}{entity_id}/metadata.yaml"
                        raise ValueError(
                            f"The 'id' field is not allowed in directory-based entities.\n"
                            f"File: {metadata_file}\n"
                            f"Directory name '{entity_id}' is automatically used as the entity ID.\n"
                            f"This ensures consistency between file structure and references.\n"
                            f"Solution: Remove the 'id: {entity_data['id']}' line from the metadata file."
                        )
                    
                    # For flat-file entities (direct .yaml files), id field is required
                    if item_type == 'file' and 'id' not in entity_data:
                        raise ValueError(
                            f"Missing 'id' field in flat-file entity: {collection_dir}{entity_id}.yaml"
                        )
                    
                    # Set the ID from directory name (for dir-based) or use existing (for flat files)
                    if item_type == 'dir':
                        entity_data['id'] = entity_id
                    
                    # Check for duplicate IDs
                    entity_actual_id = entity_data.get('id')
                    if entity_actual_id in seen_ids:
                        raise ValueError(
                            f"Duplicate ID '{entity_actual_id}' found in collection '{collection_name}'. "
                            f"Each entity must have a unique ID within its collection for reference resolution to work correctly."
                        )
                    seen_ids.add(entity_actual_id)
                    
                    # Load nested sub-collections within this entity (if any)
                    if item_type == 'dir':
                        entity_data = _load_nested_collections(
                            zip_file,
                            schema_data,
                            entity_data,
                            f"{collection_dir}{entity_id}/",
                            collection_name
                        )
                    
                    entities.append(entity_data)
            
            # Add collection to project_data 
            # Override if the collection is empty (e.g., from project.yaml having [])
            # but preserve if there's actual data
            if entities and (collection_name not in project_data or not project_data[collection_name]):
                project_data[collection_name] = entities
            # If there's existing data but also directory entities, merge them
            elif entities and project_data.get(collection_name):
                existing_ids = {e.get('id') for e in project_data[collection_name] if isinstance(e, dict) and 'id' in e}
                for entity in entities:
                    if isinstance(entity, dict) and entity.get('id') not in existing_ids:
                        project_data[collection_name].append(entity)
    
    return project_data


def _load_nested_collections(
    zip_file: zipfile.ZipFile,
    schema_data: Dict[str, Any],
    entity_data: Dict[str, Any],
    entity_dir: str,
    parent_collection_name: str
) -> Dict[str, Any]:
    """
    Load nested sub-collections within an entity directory.
    
    Example: project/posts/my-post/images/ would load images into entity_data['images']
    
    Args:
        zip_file: Open ZipFile object
        schema_data: Schema definition
        entity_data: The entity data to populate with sub-collections
        entity_dir: Path to entity directory (e.g., "project/posts/my-post/")
        parent_collection_name: Name of parent collection (e.g., "posts")
        
    Returns:
        Updated entity_data with nested collections loaded
    """
    # Find the object definition for this entity type from schema
    structure = schema_data.get('structure', {})
    parent_coll_def = structure.get(parent_collection_name, {})
    
    if not parent_coll_def or parent_coll_def.get('type') != 'array':
        return entity_data
    
    items_ref = parent_coll_def.get('items', {}).get('$ref', '')
    if not items_ref.startswith('#/objects/'):
        return entity_data
    
    object_name = items_ref.replace('#/objects/', '')
    object_def = schema_data.get('objects', {}).get(object_name, {})
    object_properties = object_def.get('properties', {})
    
    # Find which properties are arrays (potential sub-collections)
    zip_contents = zip_file.namelist()
    
    for prop_name, prop_def in object_properties.items():
        if not isinstance(prop_def, dict):
            continue
            
        # Check if this property is an array type
        if prop_def.get('type') == 'array' and '$ref' in prop_def.get('items', {}):
            # This is a potential sub-collection
            sub_collection_dir = f"{entity_dir}{prop_name}/"
            
            # Check if this directory exists in the bundle
            has_entities = any(f.startswith(sub_collection_dir) for f in zip_contents)
            
            if has_entities:
                # Load entities from this sub-collection
                sub_entities = []
                sub_entity_items = set()
                
                for file_path in zip_contents:
                    if file_path.startswith(sub_collection_dir):
                        remainder = file_path[len(sub_collection_dir):]
                        parts = remainder.split('/')
                        
                        if len(parts) >= 2:
                            # Directory-based entity
                            sub_entity_id = parts[0]
                            if sub_entity_id:
                                sub_entity_items.add(sub_entity_id)
                
                # Load each sub-entity
                for sub_entity_id in sorted(sub_entity_items):
                    sub_entity_data = _load_entity_from_directory(
                        zip_file,
                        sub_collection_dir,
                        sub_entity_id
                    )
                    if sub_entity_data:
                        # Apply strict ID policy
                        if 'id' in sub_entity_data:
                            metadata_file = f"{sub_collection_dir}{sub_entity_id}/metadata.yaml"
                            raise ValueError(
                                f"The 'id' field is not allowed in directory-based entities.\n"
                                f"File: {metadata_file}\n"
                                f"Directory name '{sub_entity_id}' is automatically used as the entity ID.\n"
                                f"This ensures consistency between file structure and references.\n"
                                f"Solution: Remove the 'id: {sub_entity_data['id']}' line from the metadata file."
                            )
                        
                        sub_entity_data['id'] = sub_entity_id
                        
                        # Recursively load nested collections within this sub-entity
                        sub_object_ref = prop_def.get('items', {}).get('$ref', '')
                        if sub_object_ref.startswith('#/objects/'):
                            sub_entity_data = _load_nested_collections_recursive(
                                zip_file,
                                schema_data,
                                sub_entity_data,
                                f"{sub_collection_dir}{sub_entity_id}/",
                                sub_object_ref.replace('#/objects/', '')
                            )
                        
                        sub_entities.append(sub_entity_data)
                
                # Add the loaded sub-collection to entity
                if sub_entities:
                    entity_data[prop_name] = sub_entities
    
    return entity_data


def _load_nested_collections_recursive(
    zip_file: zipfile.ZipFile,
    schema_data: Dict[str, Any],
    entity_data: Dict[str, Any],
    entity_dir: str,
    object_name: str
) -> Dict[str, Any]:
    """
    Recursively load nested collections for any depth.
    
    Args:
        zip_file: Open ZipFile object
        schema_data: Schema definition
        entity_data: Entity data to populate
        entity_dir: Entity directory path
        object_name: Name of the object definition in schema
        
    Returns:
        Updated entity_data with nested collections loaded
    """
    object_def = schema_data.get('objects', {}).get(object_name, {})
    object_properties = object_def.get('properties', {})
    zip_contents = zip_file.namelist()
    
    for prop_name, prop_def in object_properties.items():
        if not isinstance(prop_def, dict):
            continue
            
        if prop_def.get('type') == 'array' and '$ref' in prop_def.get('items', {}):
            sub_collection_dir = f"{entity_dir}{prop_name}/"
            has_entities = any(f.startswith(sub_collection_dir) for f in zip_contents)
            
            if has_entities:
                sub_entities = []
                sub_entity_items = set()
                
                for file_path in zip_contents:
                    if file_path.startswith(sub_collection_dir):
                        remainder = file_path[len(sub_collection_dir):]
                        parts = remainder.split('/')
                        if len(parts) >= 2:
                            sub_entity_items.add(parts[0])
                
                for sub_entity_id in sorted(sub_entity_items):
                    sub_entity_data = _load_entity_from_directory(
                        zip_file,
                        sub_collection_dir,
                        sub_entity_id
                    )
                    if sub_entity_data:
                        if 'id' in sub_entity_data:
                            raise ValueError(
                                f"The 'id' field is not allowed in directory-based entities.\n"
                                f"File: {sub_collection_dir}{sub_entity_id}/metadata.yaml\n"
                                f"Directory name '{sub_entity_id}' is automatically used as the entity ID."
                            )
                        
                        sub_entity_data['id'] = sub_entity_id
                        
                        # Continue recursion
                        sub_object_ref = prop_def.get('items', {}).get('$ref', '')
                        if sub_object_ref.startswith('#/objects/'):
                            sub_entity_data = _load_nested_collections_recursive(
                                zip_file,
                                schema_data,
                                sub_entity_data,
                                f"{sub_collection_dir}{sub_entity_id}/",
                                sub_object_ref.replace('#/objects/', '')
                            )
                        
                        sub_entities.append(sub_entity_data)
                
                if sub_entities:
                    entity_data[prop_name] = sub_entities
    
    return entity_data


def _load_entity_from_directory(
    zip_file: zipfile.ZipFile,
    collection_dir: str,
    entity_id: str
) -> Optional[Dict[str, Any]]:
    """
    Load a single entity from its directory in the ZIP.
    
    Supports multiple patterns:
    - collection/entity_id/metadata.yaml (with optional additional files)
    - collection/entity_id.yaml (flat file)
    - collection/entity_id/process.md (markdown-only entities)
    
    Args:
        zip_file: Open ZipFile object
        collection_dir: Collection directory path (e.g., "project/posts/")
        entity_id: Entity identifier
        
    Returns:
        Entity data dictionary or None if not found
    """
    # Try flat file first: collection/entity_id.yaml
    flat_file = f"{collection_dir}{entity_id}.yaml"
    if flat_file in zip_file.namelist():
        try:
            entity_bytes = zip_file.read(flat_file)
            entity_data = yaml.safe_load(entity_bytes)
            entity_data = _convert_dates_to_strings(entity_data)
            if isinstance(entity_data, dict):
                return entity_data
        except yaml.YAMLError as e:
            # YAML parsing errors should fail validation
            error_msg = f"YAML syntax error in {flat_file}:\n{str(e)}"
            raise ValueError(error_msg)
    
    # Try hierarchical: collection/entity_id/metadata.yaml
    metadata_file = f"{collection_dir}{entity_id}/metadata.yaml"
    if metadata_file in zip_file.namelist():
        try:
            entity_bytes = zip_file.read(metadata_file)
            entity_data = yaml.safe_load(entity_bytes)
            entity_data = _convert_dates_to_strings(entity_data)
            if isinstance(entity_data, dict):
                return entity_data
        except yaml.YAMLError as e:
            # YAML parsing errors should fail validation
            error_msg = f"YAML syntax error in {metadata_file}:\n{str(e)}"
            raise ValueError(error_msg)
    
    # Try markdown-only: collection/entity_id/process.md (or other .md files)
    entity_dir_prefix = f"{collection_dir}{entity_id}/"
    entity_files = [f for f in zip_file.namelist() if f.startswith(entity_dir_prefix)]
    
    if entity_files:
        # Has directory with files, try to construct entity from markdown
        md_files = [f for f in entity_files if f.endswith('.md')]
        if md_files:
            # Create entity with markdown reference
            # NOTE: Don't add 'id' field here - directory name will be used (handled by caller)
            md_file = md_files[0]  # Use first markdown file
            md_filename = md_file.split('/')[-1]
            return {
                md_filename.replace('.md', ''): md_file
            }
    
    return None


@contextmanager
def open_bundle(bundle_path: str):
    """
    Context manager for safely opening and closing Aether bundles.
    
    Ensures the ZIP file is properly closed after use, preventing
    file locking issues on Windows.
    
    Args:
        bundle_path: Path to the .aetherpack bundle file
        
    Yields:
        Tuple of (schema_data, project_data, zip_file)
        
    Example:
        with open_bundle("project.aetherpack") as (schema, project, zip_ref):
            resolved = resolve_project(project, derived_schema, zip_ref)
            validate_project(resolved, derived_schema, zip_ref)
    """
    zip_file = None
    try:
        schema_data, project_data, zip_file = extract_bundle(bundle_path)
        yield schema_data, project_data, zip_file
    finally:
        if zip_file is not None:
            zip_file.close()


def list_bundle_contents(bundle_path: str) -> list:
    """
    List all files in an Aether bundle.
    
    Args:
        bundle_path: Path to the .aetherpack bundle file
        
    Returns:
        List of file paths in the bundle
    """
    try:
        with zipfile.ZipFile(bundle_path, 'r') as zip_file:
            return zip_file.namelist()
    except zipfile.BadZipFile:
        return []


def validate_bundle_structure(bundle_path: str) -> bool:
    """
    Validate that a bundle follows the unified structure.
    
    Args:
        bundle_path: Path to the .aetherpack bundle file
        
    Returns:
        True if structure is valid, False otherwise
    """
    try:
        with zipfile.ZipFile(bundle_path, 'r') as zip_file:
            contents = zip_file.namelist()
            
            # Check for .aether file at root
            aether_files = [f for f in contents if f.endswith('.aether') and '/' not in f]
            if len(aether_files) != 1:
                return False
            
            # Check for project/project.yaml
            if 'project/project.yaml' not in contents:
                return False
            
            return True
    except:
        return False


def get_bundle_info(bundle_path: str) -> Dict[str, Any]:
    """
    Get information about an Aether bundle.
    
    Args:
        bundle_path: Path to the .aetherpack bundle file
        
    Returns:
        Dictionary containing bundle information
    """
    try:
        with zipfile.ZipFile(bundle_path, 'r') as zip_file:
            contents = zip_file.namelist()
            
            # Find schema file
            aether_files = [f for f in contents if f.endswith('.aether') and '/' not in f]
            schema_file = aether_files[0] if aether_files else None
            
            # Try to get schema info
            schema_info = {}
            if schema_file:
                try:
                    schema_bytes = zip_file.read(schema_file)
                    schema_data = yaml.safe_load(schema_bytes)
                    schema_info = {
                        'id': schema_data.get('id'),
                        'version': schema_data.get('version'),
                        'title': schema_data.get('title'),
                        'schema_file': schema_file
                    }
                except:
                    pass
            
            # Get bundle size
            bundle_size = Path(bundle_path).stat().st_size if Path(bundle_path).exists() else 0
            
            return {
                'files': contents,
                'file_count': len(contents),
                'bundle_size': bundle_size,
                'schema_info': schema_info,
                'is_valid': validate_bundle_structure(bundle_path)
            }
    except zipfile.BadZipFile:
        return {
            'files': [],
            'file_count': 0,
            'bundle_size': 0,
            'schema_info': {},
            'is_valid': False
        }

