"""
!! WARNING POTENTIAL DESTRUCTIVE ACTION !!

To create an updated tar file from the samples directory
in the DEFAULT workspace, cd to the omgui root and run:

    python omgui/dev/tar_samples.py

"""

from pathlib import Path


def create_tar_from_dir(dir_path, tar_path):
    """
    Create a tar.gz archive from a directory.
    """
    import tarfile
    import os

    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(dir_path, arcname=os.path.basename(dir_path))


if __name__ == "__main__":
    src_path = Path("~/.omgui/workspaces/DEFAULT/samples").expanduser()
    dest_path = Path(__file__).parents[1] / "gui" / "data" / "samples.tar.gz"
    create_tar_from_dir(src_path, dest_path)
