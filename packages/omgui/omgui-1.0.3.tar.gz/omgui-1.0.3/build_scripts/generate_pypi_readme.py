#!/usr/bin/env python3
"""
Script to generate README-pypi.md from README.md with proper GitHub links for PyPI.
"""

import re
from pathlib import Path


def generate_pypi_readme():
    """Generate README-pypi.md with GitHub links for PyPI distribution."""

    # Get the project root directory
    project_root = Path(__file__).parents[1]
    readme_path = project_root / "README.md"
    pypi_readme_path = project_root / "README-pypi.md"

    # GitHub repository base URL
    github_base = "https://github.com/acceleratedscience/omgui"
    github_base_raw = "https://raw.githubusercontent.com/acceleratedscience/omgui"

    if not readme_path.exists():
        raise FileNotFoundError(f"README.md not found at {readme_path}")

    # Read the original README
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Perform the link replacements
    # ---
    # fmt:off
    # 1. Image links
    content = re.sub(r"\]\(docs/assets/", f"]({github_base_raw}/main/docs/assets/", content)
    content = re.sub(r'<img src="docs/assets/', f'<img src="{github_base_raw}/main/docs/assets/', content)
    # 2. Links to docs
    content = re.sub(r"\]\(docs/", f"]({github_base}/blob/main/docs/", content)
    # 3. Anchor links
    content = re.sub(r"\]\(#", f"]({github_base}#", content)
    # fmt:on

    # Write the modified content to README-pypi.md
    with open(pypi_readme_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Generated {pypi_readme_path} with GitHub links for PyPI")
    return pypi_readme_path


if __name__ == "__main__":
    generate_pypi_readme()
