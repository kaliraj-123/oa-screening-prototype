"""
Archive generator to package oa-screening-prototype into a downloadable ZIP file.
"""

import os
import zipfile

def create_project_zip():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = base_dir
    parent_dir = os.path.dirname(project_root)
    
    zip_filename_in_parent = os.path.join(parent_dir, "oa-screening-prototype.zip")
    zip_filename_in_project = os.path.join(project_root, "oa-screening-prototype.zip")

    # Exclusions
    exclude_dirs = {"__pycache__", ".venv", "venv", ".git", ".pytest_cache"}
    exclude_extensions = {".pyc", ".pyo"}

    for zip_path in [zip_filename_in_parent, zip_filename_in_project]:
        print(f"Creating ZIP archive at: {zip_path}")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_root):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if d not in exclude_dirs]

                for file in files:
                    if file == "oa-screening-prototype.zip":
                        continue
                    if any(file.endswith(ext) for ext in exclude_extensions):
                        continue

                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, parent_dir)
                    zipf.write(file_path, rel_path)

        file_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
        print(f"Archive successfully generated: {zip_path} ({file_size_mb:.2f} MB)")

if __name__ == "__main__":
    create_project_zip()
