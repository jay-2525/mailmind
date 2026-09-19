"""
InboxGuard Chrome Extension Packager
Generates a distributable .zip file from the extension directory.
"""

import os
import zipfile
import shutil
from pathlib import Path

def package_extension():
    root_dir = Path(__file__).resolve().parent.parent
    extension_dir = root_dir / "extension"
    output_zip = root_dir / "inboxguard-chrome-extension.zip"

    if not extension_dir.exists():
        print(f"Error: {extension_dir} not found!")
        return

    print(f"Packaging extension from: {extension_dir}")
    print(f"Target archive: {output_zip}")

    if output_zip.exists():
        output_zip.unlink()

    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in extension_dir.rglob('*'):
            if file_path.is_file() and not file_path.name.endswith('.zip'):
                rel_path = file_path.relative_to(extension_dir)
                zf.write(file_path, arcname=str(rel_path))
                print(f"  + Added: {rel_path}")

    size_kb = output_zip.stat().st_size / 1024
    print(f"\nSuccessfully generated {output_zip.name} ({size_kb:.1f} KB)")
    print("Anyone can unzip this and install via chrome://extensions -> Load unpacked.")

if __name__ == "__main__":
    package_extension()
