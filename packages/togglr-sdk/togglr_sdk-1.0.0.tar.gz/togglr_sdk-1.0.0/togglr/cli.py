"""CLI utilities for togglr-sdk-python."""

import subprocess
import sys
from pathlib import Path


def generate_client() -> None:
    """Generate client from OpenAPI specification."""
    project_root = Path(__file__).parent.parent
    spec_file = project_root / "specs" / "sdk.yml"
    output_dir = project_root / "internal" / "generated"
    
    if not spec_file.exists():
        print(f"Error: Specification file not found at {spec_file}")
        sys.exit(1)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run openapi-generator
    cmd = [
        "openapi-generator-cli",
        "generate",
        "-i", str(spec_file),
        "-g", "python",
        "-o", str(output_dir),
        "--package-name", "togglr_client",
        "--additional-properties", "packageName=togglr_client,projectName=togglr-sdk-python,packageVersion=1.0.0"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("Client generated successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error generating client: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: openapi-generator-cli not found. Please install it first.")
        sys.exit(1)


if __name__ == "__main__":
    generate_client()
