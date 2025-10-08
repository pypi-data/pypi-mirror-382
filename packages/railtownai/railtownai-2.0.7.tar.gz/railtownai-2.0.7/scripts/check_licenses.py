#!/usr/bin/env python3

import os
import re
import subprocess
import sys

# Import TOML library with fallback for Python < 3.11
try:
    import tomllib  # Python 3.11+  # pyright: ignore[reportMissingImports]
except ImportError:
    try:
        import tomli as tomllib  # Python < 3.11
    except ImportError:
        print("Installing tomli for TOML parsing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "tomli"], check=True)
        import tomli as tomllib

# Configuration
DISALLOWED_PATTERN = re.compile(r"GPL|AGPL|EPL", re.IGNORECASE)
INPUT_FILE = "licenses.md"
OUTPUT_FILE = "licenses-analysis.md"
GENERATE_LICENSES = os.getenv("GENERATE_LICENSES", "false").lower() == "true"


def activate_venv():
    """Find and activate virtual environment"""
    venv_paths = [".venv", "venv", "env", ".env"]

    for venv_dir in venv_paths:
        if os.path.isdir(venv_dir):
            # Check for Unix-style activation
            activate_script = os.path.join(venv_dir, "bin", "activate")
            if os.path.isfile(activate_script):
                print(f"Activating virtual environment: {venv_dir}")
                # Source the activation script
                result = subprocess.run(f"source {activate_script} && env", shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    # Update current environment with activated env vars
                    for line in result.stdout.strip().split("\n"):
                        if "=" in line:
                            key, value = line.split("=", 1)
                            os.environ[key] = value
                return True

            # Check for Windows-style activation
            activate_script = os.path.join(venv_dir, "Scripts", "activate")
            if os.path.isfile(activate_script):
                print(f"Activating virtual environment: {venv_dir}")
                # For Windows, we'll use the environment as-is since we're in a bash shell
                return True

    print("No virtual environment found. Will use system Python environment.")
    return False


def extract_dependencies(pyproject_file="pyproject.toml"):
    """Extract dependencies from pyproject.toml"""
    if not os.path.isfile(pyproject_file):
        print(f"Warning: {pyproject_file} not found")
        return []

    with open(pyproject_file, "rb") as f:
        data = tomllib.load(f)

    dependencies = data.get("project", {}).get("dependencies", [])
    # Extract package names from dependency specs
    package_names = []
    for dep in dependencies:
        # Match patterns like: "package>=1.0,<2.0" or "package==1.0"
        match = re.match(r"^([a-zA-Z0-9_-]+)", dep.strip("\"'"))
        if match:
            package_names.append(match.group(1))

    return package_names


def generate_license_report():
    """Generate license report using pip-licenses"""
    print("Generating license report...")

    # Try to install pip-licenses if not available
    try:
        subprocess.run([sys.executable, "-m", "pip", "show", "pip-licenses"], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("Installing pip-licenses...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pip-licenses"], check=True)

    # Get project dependencies
    project_deps = extract_dependencies()

    print("Running pip-licenses...")
    if project_deps:
        print(f"Scanning only project dependencies: {' '.join(project_deps)}")
        # Use --packages to scan only specific packages and their dependencies
        result = subprocess.run(
            ["pip-licenses", "--format=markdown", "--output-file=" + INPUT_FILE, "--packages"] + project_deps,
            capture_output=True,
            text=True,
        )
    else:
        print("Could not extract project dependencies, scanning all packages...")
        result = subprocess.run(
            ["pip-licenses", "--format=markdown", "--output-file=" + INPUT_FILE], capture_output=True, text=True
        )

    if result.returncode == 0:
        if project_deps:
            print(f"License report generated successfully for project dependencies: {INPUT_FILE}")
        else:
            print(f"License report generated successfully: {INPUT_FILE}")
        return True
    else:
        print(f"pip-licenses command failed: {result.stderr}")
        return False


def analyze_licenses():
    """Analyze licenses for disallowed patterns"""
    if not os.path.isfile(INPUT_FILE):
        print(f"Warning: {INPUT_FILE} not found")
        return []

    disallowed_found = []
    with open(INPUT_FILE) as f:
        lines = f.readlines()

    # Skip header lines (first 2 lines)
    for line in lines[2:]:
        if "|" not in line:
            continue

        # Extract the license column (3rd column)
        parts = [part.strip() for part in line.split("|")]
        if len(parts) >= 4:  # Make sure we have enough columns
            license_col = parts[2]
            if DISALLOWED_PATTERN.search(license_col):
                disallowed_found.append(line.strip())

    return disallowed_found


def main():
    # Check if input file exists, create it if it doesn't
    if not os.path.isfile(INPUT_FILE):
        if GENERATE_LICENSES:
            print("License file not found. Attempting to generate it...")

            # Try to activate venv (but continue even if none found)
            activate_venv()

            # Try to generate license report
            print("Attempting to generate license report...")
            if generate_license_report():
                print("Successfully generated license report.")
            else:
                print("Warning: Failed to generate license report, creating empty template...")
                with open(INPUT_FILE, "w") as f:
                    f.write("""# Dependency License Report

| Package | Version | License | URL |
|---------|---------|---------|-----|
""")
        else:
            print("Warning: licenses.md not found, creating empty license file...")
            print("Tip: Set GENERATE_LICENSES=true to auto-generate from installed packages.")
            with open(INPUT_FILE, "w") as f:
                f.write("""# Dependency License Report

| Package | Version | License | URL |
|---------|---------|---------|-----|
""")

    # Read the content
    with open(INPUT_FILE) as f:
        content = f.read()

    # Find disallowed licenses
    disallowed_found = analyze_licenses()

    # Create enhanced report
    with open(OUTPUT_FILE, "w") as f:
        f.write(content)

        if disallowed_found:
            f.write("\n\n## ⚠️ WARNING: Disallowed Licenses Found\n\n")
            f.write("The following dependencies use disallowed licenses:\n\n")
            for item in disallowed_found:
                f.write(f"- {item}\n")
            f.write("\n**Disallowed licenses:** GPL, AGPL, EPL\n")

    print(f"License analysis complete. Found {len(disallowed_found)} disallowed licenses.")

    # Clean up generated files since this script is only meant for CI
    cleanup_files = [INPUT_FILE, OUTPUT_FILE]
    for file_path in cleanup_files:
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"Cleaned up: {file_path}")
            except OSError as e:
                print(f"Warning: Could not remove {file_path}: {e}")


if __name__ == "__main__":
    main()
