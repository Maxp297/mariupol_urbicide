import os
import fileinput

def update_imports():
    """Update import statements in all Python files after reorganization"""
    
    analysis_dir = os.path.join('scripts', 'analysis')
    processing_dir = os.path.join('scripts', 'processing')
    
    # Import patterns to update
    import_updates = {
        'from address_normalizer import': 'from ..processing.address_normalizer import',
        'from batch_fuzzy_address_match import': 'from ..processing.batch_fuzzy_address_match import',
        'from batch_inspect_pdfs import': 'from ..processing.batch_inspect_pdfs import',
        'import process_data': 'from . import process_data'
    }
    
    def process_file(filepath):
        print(f"Updating imports in {filepath}")
        with fileinput.FileInput(filepath, inplace=True) as file:
            for line in file:
                new_line = line
                for old, new in import_updates.items():
                    if old in line:
                        new_line = line.replace(old, new)
                print(new_line, end='')
    
    # Update files in analysis directory
    for root, _, files in os.walk(analysis_dir):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                process_file(os.path.join(root, file))
    
    print("✓ Import statements updated")

if __name__ == "__main__":
    update_imports()