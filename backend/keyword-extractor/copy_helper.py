import shutil
import re
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
SOURCE_DIR = r'/path/to/your/main/folder'
DEST_DIR = r'/path/to/destination/folder'
# Regex pattern: matches any file containing 'job_description' (case-insensitive)
REGEX_PATTERN = re.compile(r'.*job_description.*', re.IGNORECASE)
# ==========================================

def collect_job_descriptions(source, destination, pattern):
    """
    Recursively walks through source, matches files via regex, 
    and copies them to destination.
    """
    src_path = Path(source)
    dest_path = Path(destination)

    # Create destination folder if it doesn't exist
    dest_path.mkdir(parents=True, exist_ok=True)

    print(f"--- Starting scan in: {src_path} ---")
    
    count = 0
    # .rglob('*') handles the "Recursive Walk" through all subfolders
    for file_path in src_path.rglob('*'):
        
        # Ensure we are looking at a file, not a directory
        if file_path.is_file():
            
            # Check if filename matches our Regex pattern
            if pattern.search(file_path.name):
                print(f"Match found: {file_path.name}")
                
                # Define the final destination path
                # (This will overwrite if a file with the same name exists)
                target_file = dest_path / file_path.name
                
                shutil.copy2(file_path, target_file)
                count += 1

    print("--- Scan Complete ---")
    print(f"Total files copied/overwritten: {count}")

if __name__ == "__main__":
    collect_job_descriptions(SOURCE_DIR, DEST_DIR, REGEX_PATTERN)