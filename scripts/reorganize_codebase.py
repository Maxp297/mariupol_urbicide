import os
import shutil

def setup_directory_structure():
    """Create optimized directory structure"""
    
    # Create new directories
    dirs = [
        'scripts/processing',
        'scripts/analysis'
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        with open(os.path.join(dir_path, '__init__.py'), 'w') as f:
            pass

    # Move existing analysis scripts
    analysis_files = [
        'process_data.py',
        'analyze_geojson_addresses.py'
    ]
    
    for file in analysis_files:
        if os.path.exists(file):
            shutil.move(file, f'scripts/analysis/{file}')

    # Move processing scripts
    processing_files = [
        'batch_fuzzy_address_match.py',
        'batch_inspect_pdfs.py'
    ]
    
    for file in processing_files:
        if os.path.exists(file):
            shutil.move(file, f'scripts/processing/{file}')

if __name__ == "__main__":
    setup_directory_structure()
    print("✓ Code reorganization complete")