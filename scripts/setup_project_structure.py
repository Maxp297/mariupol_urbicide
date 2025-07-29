import os
import shutil
import hashlib
import json
from pathlib import Path
from datetime import datetime

def create_directory_structure():
    """Create standardized project directory structure with proper documentation"""
    
    # Project root structure
    directories = {
        "src": {
            "forensics": ["evidence_chain", "validation"],
            "processing": ["address", "telegram", "documents"],
            "analysis": ["claude", "geospatial"],
            "visualization": ["qgis_templates", "reports"]
        },
        "data": {
            "raw": ["telegram", "documents", "gis"],
            "processed": {
                "address_variants": None,
                "analysis_logs": None,
                "summary_stats": None,
                "validation_reports": None,
                "metadata": None
            },
            "interim": ["normalized", "validated"]
        },
        "tests": {
            "unit": None,
            "integration": None,
            "data": ["fixtures", "samples"]
        },
        "docs": {
            "api": None,
            "forensics": None,
            "workflows": None
        },
        "config": None,
        "notebooks": ["analysis", "validation"],
        "tools": ["forensics", "validation"],
        "templates": ["reports", "metadata"]
    }

    def create_dirs(base_path, structure):
        if structure is None:
            return
            
        for name, substructure in (structure.items() if isinstance(structure, dict) else [(d, None) for d in structure]):
            path = base_path / name
            path.mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py for Python packages
            if any(p in str(path) for p in ['src', 'tests']):
                (path / '__init__.py').touch()
            
            # Create README.md for each main directory
            if path.parent == Path('.'):
                create_readme(path)
                
            create_dirs(path, substructure)

    def create_readme(path):
        readme_content = f"""# {path.name.title()} Directory

## Purpose
Documentation for {path.name} components of the Mariupol Urbicide project.

## Contents
- List of key files and their purposes
- Usage guidelines
- Dependencies

## Forensic Requirements
- SHA-256 validation
- Chain of custody documentation
- Temporal metadata preservation
"""
        with open(path / 'README.md', 'w') as f:
            f.write(readme_content)

    # Create structure from project root
    root = Path('.')
    create_dirs(root, directories)
    
    print("✓ Project structure created")
    print("✓ README files generated")
    print("✓ Python packages initialized")

def move_existing_files():
    """Move existing files to new structure with forensic logging"""
    moves = {
        "process_data.py": "src/analysis/claude/",
        "analyze_geojson_addresses.py": "src/analysis/geospatial/",
        "batch_fuzzy_address_match.py": "src/processing/address/",
        "batch_inspect_pdfs.py": "src/processing/documents/"
    }
    
    log_entries = []
    for source, dest in moves.items():
        if os.path.exists(source):
            # Create hash before move
            with open(source, 'rb') as f:
                pre_hash = hashlib.sha256(f.read()).hexdigest()
                
            # Move file
            os.makedirs(dest, exist_ok=True)
            shutil.move(source, os.path.join(dest, os.path.basename(source)))
            
            # Verify hash after move
            with open(os.path.join(dest, os.path.basename(source)), 'rb') as f:
                post_hash = hashlib.sha256(f.read()).hexdigest()
                
            log_entries.append({
                "timestamp": datetime.now().isoformat(),
                "source": source,
                "destination": os.path.join(dest, os.path.basename(source)),
                "pre_move_hash": pre_hash,
                "post_move_hash": post_hash,
                "hash_verified": pre_hash == post_hash
            })
    
    # Write move log
    with open('data/processed/metadata/file_moves.json', 'w') as f:
        json.dump(log_entries, f, indent=2)

if __name__ == "__main__":
    create_directory_structure()
    move_existing_files()
    print("✓ Files moved with forensic logging")