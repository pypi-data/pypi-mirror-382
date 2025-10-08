#!/usr/bin/env python3
"""
Version update script for Railtown AI Python SDK.

Updates version numbers in multiple files:
- src/railtownai/__init__.py: __version__ variable
- src/railtownai/handler.py: ClientVersion string

Usage:
    python scripts/version.py 2.0.4
    python scripts/version.py v2.0.4
"""

import argparse
import re
import sys
from pathlib import Path


def validate_version(version: str) -> str:
    """
    Validate and normalize version string.

    Args:
        version: Version string (with or without 'v' prefix)

    Returns:
        Normalized version string without 'v' prefix

    Raises:
        ValueError: If version format is invalid
    """
    # Remove 'v' prefix if present
    version = version.lstrip("v")

    # Validate semantic versioning format (x.y.z)
    pattern = r"^\d+\.\d+\.\d+$"
    if not re.match(pattern, version):
        raise ValueError(f"Invalid version format: {version}. Expected format: x.y.z (e.g., 2.0.4)")

    return version


def update_file_version(file_path: Path, old_version: str, new_version: str) -> bool:
    """
    Update version in a file.

    Args:
        file_path: Path to the file to update
        old_version: Current version to replace
        new_version: New version to set

    Returns:
        True if file was updated, False otherwise
    """
    try:
        # Read file content
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Update __version__ in __init__.py
        if file_path.name == "__init__.py":
            pattern = rf'__version__\s*=\s*["\']?{re.escape(old_version)}["\']?'
            replacement = f'__version__ = "{new_version}"'
            content = re.sub(pattern, replacement, content)

        # Update ClientVersion in handler.py
        elif file_path.name == "handler.py":
            pattern = rf'"ClientVersion":\s*"Python-{re.escape(old_version)}"'
            replacement = f'"ClientVersion": "Python-{new_version}"'
            content = re.sub(pattern, replacement, content)

        # Write back if content changed
        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return True
        else:
            return False

    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False


def get_current_version() -> str:
    """
    Get the current version from __init__.py.

    Returns:
        Current version string

    Raises:
        RuntimeError: If version cannot be determined
    """
    init_file = Path("src/railtownai/__init__.py")
    try:
        content = init_file.read_text(encoding="utf-8")
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
        else:
            raise RuntimeError("Could not find __version__ in __init__.py")
    except Exception as e:
        raise RuntimeError(f"Could not read current version: {e}")  # noqa: B904


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Update version numbers in Railtown AI Python SDK files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/version.py 2.0.4
  python scripts/version.py v2.0.4
        """,
    )

    parser.add_argument("version", help="New version number (e.g., 2.0.4 or v2.0.4)")

    parser.add_argument("--dry-run", action="store_true", help="Show what would be updated without making changes")

    args = parser.parse_args()

    try:
        # Validate and normalize version
        new_version = validate_version(args.version)

        # Get current version
        current_version = get_current_version()

        print(f"Current version: {current_version}")
        print(f"New version: {new_version}")

        if current_version == new_version:
            print("Version is already up to date!")
            return 0

        # Files to update
        files_to_update = [Path("src/railtownai/__init__.py"), Path("src/railtownai/handler.py")]

        if args.dry_run:
            print("\nDry run - would update the following files:")
            for file_path in files_to_update:
                if file_path.exists():
                    print(f"  ✓ {file_path}")
                else:
                    print(f"  ✗ {file_path} (file not found)")
            return 0

        # Update files
        print(f"\nUpdating version to {new_version}...")
        updated_files = []

        for file_path in files_to_update:
            if not file_path.exists():
                print(f"✗ {file_path} (file not found)")
                continue

            if update_file_version(file_path, current_version, new_version):
                print(f"✓ Updated {file_path}")
                updated_files.append(file_path)
            else:
                print(f"✗ No changes needed in {file_path}")

        if updated_files:
            print(f"\nVersion update complete! Updated {len(updated_files)} file(s).")
            return 0
        else:
            print("\nNo files were updated.")
            return 1

    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except RuntimeError as e:
        print(f"Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
