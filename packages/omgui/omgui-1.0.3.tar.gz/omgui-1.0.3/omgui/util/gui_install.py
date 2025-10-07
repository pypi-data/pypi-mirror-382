"""
Install the GUI build files if they are not already installed.
"""

# Std
import os
import tarfile
import urllib.request
from pathlib import Path

# 3rd party
from dotenv import load_dotenv

# OMGUI
from omgui.spf import spf

# load version number
load_dotenv()
VERSION = os.getenv("OMGUI_FRONTEND_VERSION")


def ensure():
    """
    Check if the GUI build files are installed, and install them if not.
    """
    app_dir = Path(__file__).resolve().parents[1]  # Repo root directory
    client_dir = app_dir / "gui" / "client"
    version_file = client_dir / ".version"

    # Check reasons for install
    missing_client = not client_dir.exists()
    missing_version = not version_file.exists()
    old_version = version_file.exists() and version_file.read_text().strip() != VERSION
    needs_install = missing_client | missing_version | old_version

    if needs_install:
        _install(client_dir.parent, missing_client, missing_version, old_version)


def _install(
    destination_dir: Path,
    missing_client: bool = False,
    missing_version: bool = False,
    old_version: bool = False,
):
    """
    Download and install the GUI build files.
    """
    if missing_client:
        spf("<soft>First time, installing GUI...</soft>", pad_top=1)
    elif missing_version:
        spf("<soft>GUI version missing, reinstalling...</soft>", pad_top=1)
    elif old_version:
        prev_version = (destination_dir / "client" / ".version").read_text().strip()
        nev_version = VERSION
        spf(
            f"<soft>Updating GUI from v{prev_version} to v{nev_version}...</soft>",
            pad_top=1,
        )

    download_url = f"https://github.com/acceleratedscience/openad-gui/releases/download/v{VERSION}/dist.tar.gz"

    # Clean up existing client directory
    client_dir = destination_dir / "client"
    if client_dir.exists():
        import shutil

        shutil.rmtree(client_dir)

    # Download the tarball
    tarball_path = Path(destination_dir) / "dist.tar.gz"
    urllib.request.urlretrieve(download_url, tarball_path)

    # Unzip the tarball
    with tarfile.open(tarball_path, "r:gz") as tar:
        tar.extractall(path=destination_dir)

    # Rename "dist" to "client"
    os.rename(destination_dir / "dist", client_dir)

    # Add version file
    version_file = client_dir / ".version"
    version_file.write_text(VERSION)

    # Remove the tarball
    os.remove(tarball_path)

    spf.success("<soft>Installation complete</soft>")
