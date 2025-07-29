#!/usr/bin/env python3
"""
Comprehensive codebase cleanup script for urbicide_project
Removes redundant files, moves misplaced files, and optimizes structure
"""

import os
import shutil
import glob
import hashlib
import json
from pathlib import Path
from collections import defaultdict

# Project root
ROOT = Path(__file__).parent

def get_file_hash(filepath):
    """Get SHA256 hash of file content"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return None

def cleanup_system_files():
    """Remove macOS system files (.DS_Store)"""
    print("🧹 Removing .DS_Store files...")
    removed_count = 0
    for ds_store in ROOT.rglob('.DS_Store'):
        print(f"  Removing: {ds_store}")
        ds_store.unlink()
        removed_count += 1
    print(f"  ✅ Removed {removed_count} .DS_Store files")

def cleanup_redundant_venvs():
    """Remove redundant virtual environments, keep only .venv"""
    print("🗂️  Cleaning up redundant virtual environments...")
    
    venv_dirs = ['venv', 'venv311']
    total_saved = 0
    
    for venv_dir in venv_dirs:
        venv_path = ROOT / venv_dir
        if venv_path.exists():
            # Calculate size before removal
            size = sum(f.stat().st_size for f in venv_path.rglob('*') if f.is_file())
            size_mb = size / (1024 * 1024)
            
            print(f"  Removing redundant venv: {venv_path} ({size_mb:.1f} MB)")
            shutil.rmtree(venv_path)
            total_saved += size_mb
    
    print(f"  ✅ Freed {total_saved:.1f} MB of disk space")

def move_misplaced_files():
    """Move files to appropriate directories"""
    print("📁 Moving misplaced files...")
    
    # Move session file to cache
    session_file = ROOT / 'mariupol_session.session'
    cache_dir = ROOT / 'cache'
    if session_file.exists():
        cache_dir.mkdir(exist_ok=True)
        target = cache_dir / 'mariupol_session.session'
        print(f"  Moving: {session_file} -> {target}")
        session_file.rename(target)
        print("  ✅ Session file moved to cache")
    
    # Move asset database to data/processed
    asset_db = ROOT / 'asset_database_full.csv'
    processed_dir = ROOT / 'data' / 'processed'
    if asset_db.exists():
        target = processed_dir / 'asset_database_full.csv'
        print(f"  Moving: {asset_db} -> {target}")
        asset_db.rename(target)
        print("  ✅ Asset database moved to data/processed")

def cleanup_duplicate_analysis_files():
    """Intelligently remove duplicate analysis files based on content and timestamps"""
    print("🔍 Cleaning up duplicate analysis files...")
    
    analysis_dir = ROOT / 'analysis'
    if not analysis_dir.exists():
        return
    
    # Group files by content hash
    file_groups = defaultdict(list)
    
    # Patterns for files that are likely duplicates
    csv_files = list(analysis_dir.glob('*.csv'))
    
    print(f"  Analyzing {len(csv_files)} CSV files for duplicates...")
    
    for csv_file in csv_files:
        file_hash = get_file_hash(csv_file)
        if file_hash:
            file_groups[file_hash].append(csv_file)
    
    removed_count = 0
    saved_space = 0
    
    # Process groups with duplicates
    for file_hash, files in file_groups.items():
        if len(files) > 1:
            # Sort by modification time (newest first)
            files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            newest = files[0]
            duplicates = files[1:]
            
            print(f"  Found {len(duplicates)} duplicate(s) of {newest.name}")
            
            for duplicate in duplicates:
                size = duplicate.stat().st_size
                print(f"    Removing older duplicate: {duplicate.name}")
                duplicate.unlink()
                removed_count += 1
                saved_space += size
    
    # Look for versioned files (e.g., file_v1.csv, file_v2.csv)
    versioned_patterns = [
        'damage_assessment_with_*',
        '*_crossref*',
        '*_normalized*',
        '*_enriched*'
    ]
    
    for pattern in versioned_patterns:
        matching_files = list(analysis_dir.glob(f'{pattern}.csv'))
        if len(matching_files) > 1:
            # Keep only the most recent
            matching_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            newest = matching_files[0]
            old_versions = matching_files[1:]
            
            if old_versions:
                print(f"  Keeping newest version: {newest.name}")
                for old_file in old_versions:
                    size = old_file.stat().st_size
                    print(f"    Removing old version: {old_file.name}")
                    old_file.unlink()
                    removed_count += 1
                    saved_space += size
    
    saved_mb = saved_space / (1024 * 1024)
    print(f"  ✅ Removed {removed_count} duplicate/obsolete files, freed {saved_mb:.1f} MB")

def create_vscode_config():
    """Create VSCode configuration files"""
    print("⚙️  Creating VSCode configuration...")
    
    vscode_dir = ROOT / '.vscode'
    vscode_dir.mkdir(exist_ok=True)
    
    # Settings
    settings = {
        "python.defaultInterpreterPath": "./.venv/bin/python",
        "python.terminal.activateEnvironment": True,
        "files.exclude": {
            "**/.DS_Store": True,
            "**/__pycache__": True,
            "**/*.pyc": True,
            ".venv/": True,
            "cache/": True
        },
        "python.analysis.extraPaths": ["./scripts", "./analysis"],
        "python.linting.enabled": True,
        "python.linting.pylintEnabled": True,
        "python.formatting.provider": "black",
        "files.associations": {
            "*.csv": "csv (semicolon)",
            "*.geojson": "json"
        },
        "csv-preview.separator": ",",
        "workbench.editorAssociations": {
            "*.csv": "default"
        }
    }
    
    settings_file = vscode_dir / 'settings.json'
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)
    print(f"  ✅ Created: {settings_file}")
    
    # Launch configuration
    launch_config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Current File",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {
                    "PYTHONPATH": "${workspaceFolder}/scripts:${workspaceFolder}/analysis"
                }
            },
            {
                "name": "Python: Forensic Analysis",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/analysis/${input:analysisScript}",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}"
            }
        ],
        "inputs": [
            {
                "id": "analysisScript",
                "description": "Analysis script to run",
                "type": "pickString",
                "options": [
                    "forensic_dissection_and_crossref.py",
                    "enrich_addresses.py",
                    "normalize_addresses.py"
                ]
            }
        ]
    }
    
    launch_file = vscode_dir / 'launch.json'
    with open(launch_file, 'w') as f:
        json.dump(launch_config, f, indent=2)
    print(f"  ✅ Created: {launch_file}")

def update_gitignore():
    """Update .gitignore with comprehensive exclusions"""
    print("📝 Updating .gitignore...")
    
    gitignore_path = ROOT / '.gitignore'
    
    # Read existing content
    existing_content = ""
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            existing_content = f.read()
    
    gitignore_additions = [
        "",
        "# === CLEANUP ADDITIONS ===",
        "# Virtual environments",
        "venv/",
        "venv311/",
        "",
        "# Cache and temporary files", 
        "cache/",
        "*.session",
        "*.tmp",
        "*.log",
        "",
        "# System files",
        ".DS_Store",
        "Thumbs.db",
        "",
        "# Python cache",
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        "",
        "# IDE files",
        ".vscode/settings.json",
        ".idea/",
        "",
        "# Large data files",
        "data/raw/downloaded_pdfs/*.pdf",
        "*.gpkg",
        "asset_database_full.csv"
    ]
    
    # Only add new entries
    new_entries = []
    for entry in gitignore_additions:
        if entry.strip() and entry not in existing_content:
            new_entries.append(entry)
    
    if new_entries:
        with open(gitignore_path, 'a') as f:
            f.write('\n'.join(new_entries))
        print(f"  ✅ Added {len([e for e in new_entries if e.strip()])} new entries to .gitignore")
    else:
        print("  ✅ .gitignore already up to date")

def main():
    """Run all cleanup operations"""
    print("🚀 Starting comprehensive codebase cleanup...")
    print(f"📍 Project root: {ROOT}")
    print()
    
    cleanup_system_files()
    print()
    
    cleanup_redundant_venvs()
    print()
    
    move_misplaced_files()
    print()
    
    cleanup_duplicate_analysis_files()
    print()
    
    create_vscode_config()
    print()
    
    update_gitignore()
    print()
    
    print("✅ Comprehensive cleanup complete!")
    print("🎯 Your codebase is now optimized for VSCode development")
    print("💡 Next steps:")
    print("   1. Open project in VSCode")
    print("   2. Install recommended extensions (Python, CSV Viewer)")
    print("   3. Verify .venv Python interpreter is selected")

if __name__ == "__main__":
    main()
