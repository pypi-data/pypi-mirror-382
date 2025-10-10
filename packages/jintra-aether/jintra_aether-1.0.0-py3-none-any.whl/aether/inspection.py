"""
Project inspection functionality for analyzing project structure and content.
"""

import os
import zipfile
from typing import Dict, Any, List, Optional
from pathlib import Path
from .bundler import extract_bundle


def describe_project(project_path: str) -> Dict[str, Any]:
    """
    Get a comprehensive description of a project.
    
    Args:
        project_path: Path to project directory or .aetherpack bundle
    
    Returns:
        Dictionary with project description and statistics
    """
    # Support both .aetherpack (new) and .aether (legacy bundles)
    if project_path.endswith('.aetherpack') or project_path.endswith('.aether'):
        return _describe_bundle(project_path)
    else:
        return _describe_directory(project_path)


def _describe_bundle(bundle_path: str) -> Dict[str, Any]:
    """Describe a .aether bundle project."""
    try:
        schema_data, project_data, zip_ref = extract_bundle(bundle_path)
        
        # Get basic info
        project_name = project_data.get("project_name", "Unknown Project")
        schema_id = schema_data.get("id", "unknown-schema")
        schema_version = schema_data.get("version", "1.0.0")
        
        # Analyze files in bundle
        file_stats = _analyze_bundle_files(zip_ref)
        
        # Analyze entities
        entity_stats = _analyze_entities(project_data)
        
        zip_ref.close()
        
        return {
            "type": "bundle",
            "project_name": project_name,
            "schema": {
                "id": schema_id,
                "version": schema_version,
                "title": schema_data.get("title", "")
            },
            "files": file_stats,
            "entities": entity_stats,
            "bundle_size": os.path.getsize(bundle_path)
        }
        
    except Exception as e:
        return {
            "type": "bundle",
            "error": f"Failed to analyze bundle: {str(e)}"
        }


def _describe_directory(project_path: str) -> Dict[str, Any]:
    """Describe a directory-based project with unified structure."""
    try:
        project_dir = Path(project_path)
        
        if not project_dir.exists():
            return {"error": f"Project directory does not exist: {project_path}"}
        
        # Look for schema file (.aether) and project/ subdirectory
        # Unified structure: project_root/name.aether and project_root/project/project.yaml
        schema_files = list(project_dir.glob("*.aether"))
        schema_file = schema_files[0] if schema_files else project_dir / "schema.yaml"  # Fallback for old structure
        project_file = project_dir / "project" / "project.yaml"
        
        # Fallback to old structure if project/ doesn't exist
        if not project_file.exists():
            project_file = project_dir / "project.yaml"
        
        schema_data = {}
        project_data = {}
        
        if schema_file.exists():
            import yaml
            with open(schema_file, 'r') as f:
                schema_data = yaml.safe_load(f)
        
        if project_file.exists():
            import yaml
            with open(project_file, 'r') as f:
                project_data = yaml.safe_load(f)
        
        # Analyze directory structure
        file_stats = _analyze_directory_files(project_dir)
        
        # Analyze entities
        entity_stats = _analyze_entities(project_data)
        
        return {
            "type": "directory",
            "project_name": project_data.get("project_name", project_dir.name),
            "schema": {
                "id": schema_data.get("id", "unknown-schema"),
                "version": schema_data.get("version", "1.0.0"),
                "title": schema_data.get("title", "")
            },
            "files": file_stats,
            "entities": entity_stats,
            "directory_size": _get_directory_size(project_dir)
        }
        
    except Exception as e:
        return {
            "type": "directory",
            "error": f"Failed to analyze directory: {str(e)}"
        }


def _analyze_bundle_files(zip_ref: zipfile.ZipFile) -> Dict[str, Any]:
    """Analyze files in a bundle."""
    files = []
    total_size = 0
    file_types = {}
    
    for file_info in zip_ref.filelist:
        if not file_info.is_dir():
            files.append({
                "name": file_info.filename,
                "size": file_info.file_size,
                "type": _get_file_type(file_info.filename)
            })
            total_size += file_info.file_size
            
            file_type = _get_file_type(file_info.filename)
            file_types[file_type] = file_types.get(file_type, 0) + 1
    
    return {
        "total_files": len(files),
        "total_size": total_size,
        "file_types": file_types,
        "files": files[:10]  # First 10 files as sample
    }


def _analyze_directory_files(project_dir: Path) -> Dict[str, Any]:
    """Analyze files in a directory."""
    files = []
    total_size = 0
    file_types = {}
    
    for file_path in project_dir.rglob("*"):
        if file_path.is_file():
            file_size = file_path.stat().st_size
            relative_path = file_path.relative_to(project_dir)
            
            files.append({
                "name": str(relative_path),
                "size": file_size,
                "type": _get_file_type(str(relative_path))
            })
            total_size += file_size
            
            file_type = _get_file_type(str(relative_path))
            file_types[file_type] = file_types.get(file_type, 0) + 1
    
    return {
        "total_files": len(files),
        "total_size": total_size,
        "file_types": file_types,
        "files": files[:10]  # First 10 files as sample
    }


def _analyze_entities(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze entities in project data."""
    entity_stats = {}
    
    for key, value in project_data.items():
        if isinstance(value, list):
            # This looks like a collection
            entities = [item for item in value if isinstance(item, dict)]
            entity_stats[key] = {
                "count": len(entities),
                "sample_ids": [entity.get("id", entity.get("name", "unknown")) for entity in entities[:3]]
            }
    
    return entity_stats


def _get_file_type(filename: str) -> str:
    """Get file type from filename."""
    ext = Path(filename).suffix.lower()
    
    if ext in ['.yaml', '.yml']:
        return 'yaml'
    elif ext in ['.md', '.markdown']:
        return 'markdown'
    elif ext in ['.json']:
        return 'json'
    elif ext in ['.txt']:
        return 'text'
    elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
        return 'image'
    elif ext in ['.pdf']:
        return 'pdf'
    else:
        return 'other'


def _get_directory_size(directory: Path) -> int:
    """Get total size of directory in bytes."""
    total_size = 0
    for file_path in directory.rglob("*"):
        if file_path.is_file():
            total_size += file_path.stat().st_size
    return total_size


def format_project_description(description: Dict[str, Any]) -> str:
    """Format project description as a readable string."""
    if "error" in description:
        return f"Error: {description['error']}"
    
    lines = []
    
    # Project info
    lines.append(f"{description['project_name']} ({description['type'].title()} Project)")
    
    # Schema info
    schema = description.get('schema', {})
    if schema.get('id'):
        lines.append(f"Schema: {schema['id']} v{schema.get('version', '1.0.0')}")
    
    # Files info
    files = description.get('files', {})
    if files:
        lines.append(f"Files: {files.get('total_files', 0)} total ({files.get('total_size', 0)} bytes)")
        
        file_types = files.get('file_types', {})
        if file_types:
            type_parts = [f"{count} {file_type}" for file_type, count in file_types.items()]
            lines.append(f"  └── {', '.join(type_parts)}")
    
    # Entities info
    entities = description.get('entities', {})
    if entities:
        lines.append("Entities:")
        for entity_type, stats in entities.items():
            lines.append(f"  ├── {entity_type}: {stats.get('count', 0)} items")
            sample_ids = stats.get('sample_ids', [])
            if sample_ids:
                lines.append(f"      └── Examples: {', '.join(sample_ids)}")
    
    return "\n".join(lines)
