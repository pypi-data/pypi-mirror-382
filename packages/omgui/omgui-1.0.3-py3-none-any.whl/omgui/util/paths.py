#  if file_path.lower().endswith(".mol.json"):

# Std
import re
from pathlib import Path

# OMGUI
from omgui import ctx
from omgui.util.logger import get_logger
from omgui.util.general import confirm_prompt
from omgui.spf import spf

# Logger
logger = get_logger()


NOT_ALLOWED_ERR = [
    "Absolute paths are not allowed here",
    "To import this file into your workspace, run <cmd>import '{file_path}'</cmd>",
]


def path_type(file_path_input: Path | str) -> str:
    """
    Return how a path will be parsed by parse_path:
    - cwd
    - absolute
    - workspace
    """
    file_path: Path = Path(file_path_input)
    is_absolute = file_path.expanduser().is_absolute()
    is_cwd = str(file_path_input).startswith("./") or str(file_path_input).startswith(
        "../"
    )

    # if not file_path_input:
    #     return None
    if is_cwd:
        return "cwd"
    elif is_absolute:
        return "absolute"
    else:
        return "workspace"


def prepare_file_path(
    file_path_input: Path | str, fallback_ext=None, force_ext=None
) -> Path | None:
    """
    prepare a file path for saving.

    - Parse the path and turn into absolute path
    - Check if there is already a file at this location
        - If yes, ask to overwrite:
            - if yes, return the file path
            - if no, return the file path with the next available filename
        - If no, check if the folder structure exists
            - if yes, return the file path
            - if no, ask to create the folder structure
                - if yes, return the file path
                - if no, print error and return None
    """
    file_path: Path | None = resolve_path(file_path_input, fallback_ext, force_ext)
    file_path: Path | bool = _ensure_file_path(file_path)
    # if not file_path:
    #     spf.error("Directory does not exist")
    #     return None
    return file_path


def resolve_path(
    file_path_input: Path | str,
    fallback_ext: str = None,
    force_ext: str = None,
) -> Path | None:
    """
    Custom path resolver that points to the workspace by default.

    - foo:  workspace path
    - /foo: absolute path
    - ~/foo: absolute path
    - ./foo: current working directory path
    - ../foo: current working directory path
    """

    if not file_path_input:
        return ctx().workspace_path()

    file_path = Path(file_path_input)

    # Detect path type
    is_absolute = file_path.expanduser().is_absolute()
    is_cwd = str(file_path_input).startswith("./") or str(file_path_input).startswith(
        "../"
    )

    # Expand user path: ~/... --> /Users/my-username/...
    file_path = file_path.expanduser()

    # Separate filename from path
    path = file_path.parent
    filename = file_path.name

    # Force extension
    new_ext = None
    if force_ext:
        stem = file_path.stem
        ext = file_path.suffix
        filename = stem + "." + force_ext
        if ext and ext[1:] != force_ext:
            new_ext = force_ext

    # Fallback to default extension if none provided
    elif fallback_ext:
        ext = file_path.suffix
        filename = filename if ext else filename + "." + fallback_ext

    # Current working directory path
    if is_cwd:
        path = Path.cwd() / path / filename

    # -- Resolve path --

    # Absolute path
    elif is_absolute:
        path = path / filename

    # Default: workspace path
    else:
        path = ctx().workspace_path() / path / filename

    # Display wrning when file extension is changed
    if new_ext:
        spf.warning(
            [
                f"⚠️  File extension changed to <reset>{new_ext}</reset>",
                f"--> {path if is_absolute else filename}",
            ]
        )
    return path.resolve()


def _ensure_file_path(file_path: Path, force: bool = False) -> Path | bool:
    """
    Ensure a file_path is valid.

    - Make sure we won't override an existing file
    - Create folder structure if it doesn't exist yet
    """

    # File already exists? --> overwrite?
    if file_path.exists():
        if not force and not confirm_prompt(
            "The destination file already exists, overwrite?"
        ):
            return _next_available_filename(file_path)

    # Parent directory doesn't exist --> create?
    if not file_path.parent.exists():
        if not force and confirm_prompt(
            f"The destination directory <reset>{file_path.parent.name}</reset> does not exist, create it?"
        ):
            try:
                logger.info("Creating directory: %s", file_path.parent)
                file_path.parent.mkdir(parents=True, exist_ok=True)
                return file_path
            except OSError as err:
                spf.error(["Error creating directory", err])

        return False

    return file_path


def _next_available_filename(file_path: Path) -> str:
    """
    Returns the file path with next available filename by appending a number to the filename.
    """
    if not file_path.exists():
        return file_path

    if file_path.suffix == ".json" and file_path.suffixes[-2] in [
        ".mol",
        ".smol",
        ".mmol",
        ".molset",
    ]:
        # Double suffix: "foo.bar", ".mol.json"
        stem, ext = __split_double_suffix_filename(file_path)
    else:
        # Regular single suffix: "foo.bar", ".txt"
        stem, ext = [file_path.stem, file_path.suffix]

    i = 1
    while (file_path.parent / f"{stem}-{i}{ext}").exists():
        i += 1
    return file_path.parent / f"{stem}-{i}{ext}"


def __split_double_suffix_filename(file_path: Path):
    """
    Returns the filename stem plus two suffixes.

    Eg.
    foo.mol.json --> "foo.bar", ".mol.json"
    foo.bar.mol.json --> "foo.bar", ".txt"
    """
    stem = file_path.name
    # Remove two suffixes from the stem
    for suffix in reversed(file_path.suffixes[-2:]):
        stem = stem.removesuffix(suffix)
    return stem, "".join(file_path.suffixes[-2:])


# -- Below not used --


def is_abs_path(file_path) -> bool:
    """
    Check if a path is absolute.
    """
    if file_path.startswith(("/", "./", "~/", "\\", ".\\", "~\\")):
        return True
    return False


def fs_success(
    path_input,  # Destination user input, eg. foo.csv or /home/foo.csv or ./foo.csv
    path_resolved,  # Destination parsed through parse_path, eg. /home/user/foo.csv
    subject="File",
    action="saved",  # saved / removed
):
    """
    Path-type aware success message for saving files.
    """
    # Absolute path
    if is_abs_path(path_input):
        spf.success(f"{subject} {action}: <yellow>{path_resolved}</yellow>")

    # Workspace path
    else:
        # Filename may have been modifier with index and extension,
        # so we need to parse it from the file_path instead.
        workspace_path = ctx().workspace_path()
        within_workspace_path = path_resolved.replace(workspace_path, "").lstrip("/")
        if action == "saved":
            spf.success(
                f"{subject} saved to workspace as <yellow>{within_workspace_path}</yellow>"
            )
        elif action == "removed":
            spf.success([f"{subject} removed from workspace", within_workspace_path])
