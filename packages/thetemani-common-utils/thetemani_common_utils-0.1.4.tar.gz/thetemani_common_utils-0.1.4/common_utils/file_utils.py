import os

def list_files_in_directory(base_path):
    files = []
    for root, dirs, filenames in os.walk(base_path):
        for filename in filenames:
            # Get the full path
            full_path = os.path.join(root, filename)
            # Get the relative path from the config directory
            rel_path = os.path.relpath(full_path, base_path)
            files.append(rel_path)
    return files