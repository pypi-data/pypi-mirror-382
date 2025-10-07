#!/usr/bin/env python3
"""
Setup script that automatically generates README-pypi.md and cleans build directories.
"""

import subprocess
import sys
from pathlib import Path
from setuptools import setup
from setuptools.command.build_py import build_py


def create_pypi_readme():
    """Clean build directories and generate README-pypi.md."""
    project_root = Path(__file__).parent

    script_path = project_root / "build_scripts" / "generate_pypi_readme.py"
    if script_path.exists():
        subprocess.run([sys.executable, str(script_path)], check=True)
        print("✅ Generated README-pypi.md for PyPI")


class CustomBuildPy(build_py):
    """Custom build command that cleans and prepares before building."""

    def run(self):
        create_pypi_readme()
        super().run()


setup(cmdclass={"build_py": CustomBuildPy})
