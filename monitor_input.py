#!/usr/bin/env python3
"""
Directory Monitoring Script for Mariupol Administrative Violence Documentation Project
- Watches input directories for new files
- Automatically processes new files
- Maintains logs of all processed files
"""

import os
import sys
import time
import yaml
import json
import argparse
import hashlib
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime
from process_assets import process_file, is_youtube_url

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("directory_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("directory_monitor")

# Constants
PROJECT_ROOT = Path(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = PROJECT_ROOT / "input"
PROCESSED_REGISTRY = PROJECT_ROOT / "data" / "processed_files_registry.json"


def load_processed_files_registry() -> Dict:
    """Load the registry of processed files"""
    if PROCESSED_REGISTRY.exists():
        try:
            with open(PROCESSED_REGISTRY, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading processed files registry: {str(e)}")
            return {"files": {}, "last_updated": datetime.now().isoformat()}
    else:
        return {"files": {}, "last_updated": datetime.now().isoformat()}


def save_processed_files_registry(registry: Dict):
    """Save the registry of processed files"""
    # Update the last_updated timestamp
    registry["last_updated"] = datetime.now().isoformat()
    
    try:
        # Ensure parent directory exists
        PROCESSED_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
        
        with open(PROCESSED_REGISTRY, 'w') as f:
            json.dump(registry, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving processed files registry: {str(e)}")


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating hash for {file_path}: {str(e)}")
        return ""


def scan_directory(directory: Path, registry: Dict) -> List[Path]:
    """Scan directory for new files"""
    new_files = []
    
    try:
        for item in directory.glob('**/*'):
            if item.is_file():
                # Calculate hash for the file
                file_hash = calculate_file_hash(item)
                
                # Check if this file (by hash) has been processed before
                if file_hash and file_hash not in registry["files"]:
                    new_files.append(item)
                    
                    # Register the file by its hash
                    registry["files"][file_hash] = {
                        "path": str(item),
                        "size": item.stat().st_size,
                        "discovered_at": datetime.now().isoformat(),
                        "processed": False
                    }
    except Exception as e:
        logger.error(f"Error scanning directory {directory}: {str(e)}")
    
    return new_files


def scan_url_file(url_file: Path, registry: Dict) -> List[str]:
    """Scan a file containing URLs for new YouTube URLs"""
    new_urls = []
    
    try:
        with open(url_file, 'r') as f:
            for line in f:
                url = line.strip()
                if url and is_youtube_url(url):
                    # Use the URL itself as the key in the registry
                    if url not in registry["files"]:
                        new_urls.append(url)
                        
                        # Register the URL
                        registry["files"][url] = {
                            "url": url,
                            "discovered_at": datetime.now().isoformat(),
                            "processed": False
                        }
    except Exception as e:
        logger.error(f"Error scanning URL file {url_file}: {str(e)}")
    
    return new_urls


def process_new_files(new_files: List[Path], registry: Dict):
    """Process new files"""
    for file_path in new_files:
        try:
            logger.info(f"Processing file: {file_path}")
            
            # Calculate hash for registry lookup
            file_hash = calculate_file_hash(file_path)
            
            # Process the file
            metadata = process_file(str(file_path))
            
            # Update registry
            if file_hash in registry["files"]:
                registry["files"][file_hash]["processed"] = True
                registry["files"][file_hash]["processed_at"] = datetime.now().isoformat()
                registry["files"][file_hash]["metadata_path"] = metadata.get("metadata_path", "")
            
            logger.info(f"Successfully processed: {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")


def main():
    """Main function to monitor directories and process new files"""
    registry = load_processed_files_registry()
    
    while True:
        try:
            # Scan input directory for new files
            new_files = scan_directory(INPUT_DIR, registry)
            
            # Process new files
            if new_files:
                process_new_files(new_files, registry)
            
            # Save the updated registry
            save_processed_files_registry(registry)
            
            # Sleep for a while before the next scan
            time.sleep(10)
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            time.sleep(10)  # Wait before retrying


if __name__ == "__main__":
    main()