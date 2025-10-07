import shutil
from pathlib import Path


def remove_dist():
    """Remove dist directory if it exists."""
    dir_path = Path(__file__).parents[1] / "dist"
    if dir_path.exists():
        shutil.rmtree(dir_path)
        print("✅ Removed existing /dist directory")
    else:
        print("No /dist directory to remove")


if __name__ == "__main__":
    remove_dist()
