"""
File system functions for OMGUI API endpoints.
"""

# Std
import os
import json
from pathlib import Path

# OMGUI
from omgui import ctx
from omgui.util.logger import get_logger
from omgui.util.paths import resolve_path
from omgui.util.mol_utils import create_molset_response
from omgui.gui.workers import smol_transformers, smol_functions
from omgui.gui.workers.mmol_transformers import cif2mmol, pdb2mmol

# Logger
logger = get_logger()

# File and directory names to hide in the file browser.
IGNORE_FILES = [".DS_Store", "._system"]


def open_file_os(path: Path | str):
    """
    Open a file in its designated OS application.
    """
    try:
        path = resolve_path(path)
        os.system(f"open '{path}'")
        logger.info("Opening file: %s", path)
        return True
    except OSError as err:
        logger.error("Failed to open file in OS: %s - %s", path, err)
        return False


def delete_file(path_absolute=""):
    """
    Move a file to the workspace trash.
    The trash gets cleared at the end of a session.
    """
    trash_dir = ctx().workspace_path() / ".trash"
    os.makedirs(trash_dir, exist_ok=True)
    os.system(f"mv '{path_absolute}' '{trash_dir}'")

    return "ok", 200


def get_files(path=""):
    """
    Returns your active workspace's content as a JSON object.
    """

    # Get workspace path.
    workspace_path = ctx().workspace_path()
    dir_path = workspace_path / path

    # Dict structure for one level.
    level = {
        "_meta": {
            "empty": False,
            "empty_hidden": False,
        },
        "dirname": "",
        "files": [],
        "filesHidden": [],  # Filenames starting with .
        "dirs": [],
        "dirsHidden": [],  # Dir names starting with .
    }

    # Organize file & directory names into dictionary.
    for filename in os.listdir(dir_path):
        is_hidden = filename.startswith(".")
        # is_system = filename.startswith("__")
        is_file = os.path.isfile(os.path.join(dir_path, filename))

        if is_file:
            if filename in IGNORE_FILES:
                continue
            elif is_hidden:
                level["filesHidden"].append(filename)
            else:
                level["files"].append(filename)
        else:
            is_dir = os.path.isdir(os.path.join(dir_path, filename))
            if is_dir:
                if filename in IGNORE_FILES:
                    continue
                if is_hidden:
                    level["dirsHidden"].append(filename)
                else:
                    level["dirs"].append(filename)

    # Sort the lists
    level["files"].sort()
    level["filesHidden"].sort()
    level["dirs"].sort()
    level["dirsHidden"].sort()

    # Expand every dir & filename into a dictionary: {_meta, filename, path}
    for category, items in level.items():
        if category == "_meta":
            continue
        for index, filename in enumerate(items):
            file_path = path + "/" + filename if path else filename
            items[index] = _compile_filedir_obj(file_path)

    #
    #

    # Attach workspace name
    workspace_name = ctx().workspace
    dir_name = path.split("/")[-1]
    level["dirname"] = workspace_name if not path else dir_name

    # Mark empty directories.
    if not level["files"] and not level["dirs"]:
        level["_meta"]["empty"] = True
    if level["_meta"]["empty"] and not level["filesHidden"] and not level["dirsHidden"]:
        level["_meta"]["empty_hidden"] = True

    return level


def get_file(path="", query=None):
    """
    Fetch a file's content as a JSON object.
    """
    if not query:
        query = {}

    # Compile filedir object
    file_obj = _compile_filedir_obj(path)
    file_type = file_obj.get("_meta", {}).get("fileType")

    # Attach data for files
    if file_type and file_type != "dir":
        file_obj = _attach_file_data(file_obj, query)

    return file_obj


def _compile_filedir_obj(path):
    """
    Compile universal file object that cen be parsed by the frontend.

    Used by the file browser (FileBroswer.vue) and the file viewers (FileStore).
    The file content is added later, under the "data" key - see fs_get_file_data().

    Parameters
    ----------
    path: str
        The path of the file relative to the workspace, including the filename.

    """
    workspace_path = ctx().workspace_path()
    path_absolute = os.path.join(workspace_path, path)
    filename = os.path.basename(path)

    # Get file exists or error code.
    f_stats = os.stat(path_absolute)

    # TODO: review, no longer used since we moved away from file_stats()

    # # No file/dir found
    # if err_code:
    #     return {
    #         "_meta": {"errCode": err_code},
    #         "filename": filename,
    #         "path": path,
    #         "pathAbsolute": path_absolute,
    #     }

    # File
    if os.path.isfile(path_absolute):
        size = f_stats.st_size
        time_edited = f_stats.st_mtime * 1000  # Convert to milliseconds for JS.
        time_created = f_stats.st_ctime * 1000  # Convert to milliseconds for JS.
        ext = _get_file_ext(filename)
        ext2 = _get_file_ext2(filename)
        file_type = _get_file_type(ext, ext2)
        return {
            "_meta": {
                "fileType": file_type,
                "ext": ext,
                "ext2": ext2,  # Secondary file extension, eg. foobar.mol.json --> mol
                "size": size,
                "timeCreated": time_created,
                "timeEdited": time_edited,
                "errCode": None,
            },
            "data": None,  # Just for reference, this is added when opening file.
            "filename": filename,
            "path": path,  # Relative to workspace.
            "pathAbsolute": path_absolute,  # Absolute path
        }

    # Directory
    elif os.path.isdir(path_absolute):
        return {
            "_meta": {
                "fileType": "dir",
            },
            "filename": filename,
            "path": path,
            "pathAbsolute": path_absolute,
        }


def _attach_file_data(file_obj, query=None):
    """
    Read the content of a file and attach it to the file object.

    This content will then be attached to the "data" key of the file object
    to be consumed by the frontend. For most file types, this is just the
    raw text content of the file, but for certain files like a molset, this
    will be a parsed object that includes additional data like pagination etc.

    This entry point is only used for opening files, once a molset (or potentially
    other editable file formats later) is opened, further querying and editing
    is handled by its own API endpoint - i.e. get_molset()

    Parameters
    ----------
    path: str
        The path of the file relative to the workspace, including the filename.
    query: dict
        The query object, used to filter and sort the molset, and possible other
        file formats in the future.
    """

    path_absolute = Path(file_obj.get("pathAbsolute"))
    file_type = file_obj.get("_meta", {}).get("fileType")
    ext = file_obj.get("_meta", {}).get("ext")

    molset = None
    err_code = None
    data = None

    # Molset files --> Load molset object with first page data
    if file_type in ["molset", "sdf", "smi"]:
        # Step 1: Load or assemble the molset.
        # - - -

        # From molset JSON file, no formatting required.
        if ext == "json":
            molset = smol_functions.get_molset_mols(path_absolute)

        # From SMILES file
        elif ext == "smi":
            molset = smol_transformers.smiles_path2molset(path_absolute)

        # From SDF file
        elif ext == "sdf":
            molset = smol_transformers.sdf_path2molset(path_absolute)

        if molset:
            # Step 2: Store a working copy of the molset in the cache.
            # - - -

            # For JSON files, we can simply copy the original file (fast).
            if ext == "json":
                cache_id = smol_functions.create_molset_cache_file(
                    ctx(), path_absolute=path_absolute
                )

            # All other cases, write file from memory.
            else:
                cache_id = smol_functions.create_molset_cache_file(molset=molset)

            # Step 3: Create the response object.
            # - - -

            # Filter, sort & paginate the molset, wrap it into
            # a response object and add the cache_id so further
            # operations can be performed on the working copy.
            data = create_molset_response(molset, query, cache_id)

        else:
            data = None

    # Molecule files --> convert to molecule JSON
    elif file_type in ["mdl", "pdb", "cif"]:
        # From MOL file
        if ext == "mol":
            data = smol_transformers.mdl_path2smol(path_absolute)

        # From PDB file
        if ext == "pdb":
            data = pdb2mmol(pdb_path=path_absolute)

        # From CIF file
        if ext == "cif":
            data = cif2mmol(cif_path=path_absolute)

    # JSON files --> Load file content as JSON
    elif file_type in ["json", "smol", "mmol"]:
        with open(path_absolute, "r", encoding="utf-8") as file:
            data = json.load(file)

    # Everything else --> Load file content as text
    else:
        with open(path_absolute, "r", encoding="utf-8") as file:
            data = file.read()

    # Attach file content or error code
    file_obj["_meta"]["errCode"] = err_code
    file_obj["data"] = data

    return file_obj


def _get_file_ext(filename):
    """
    Get the file extension from a filename.
    """
    if filename.find(".") == -1:
        return ""
    else:
        return filename.split(".")[-1]


def _get_file_ext2(filename):
    """
    Get the secondary file extension from a filename.

    Secondary file extensions are used to indicate subformats, eg:
    - foobar.json --> JSON file
    - foobar.mol.json --> molecule JSON file
    - foobar.molset.json --> molecule set JSON file
    """
    has_ext2 = len(filename.split(".")) >= 3
    if has_ext2:
        parts = filename.split(".")
        parts.pop()
        return parts.pop() or None
    else:
        return None


def _get_file_type(ext, ext2):
    """
    Deduct the fileType from the file's primary and secondary extensions.

    The file type is used in the frontend to determine:
    - What icon to display
    - What viewer to use when opening the file

    In the frontend the fileType is mapped to its respective
    display name and module name via _map_FileType.

    Any changes here should also be reflected in the FileType TypeScript type.
    """
    # Small molecule files
    if ext in [
        "mol"
    ]:  # Future support: "molecule", "pdb", "cif", "xyz", "mol2", "mmcif", "cml", "inchi"
        return "mdl"

    # Macromolecule files
    if ext in ["pdb"]:
        return "pdb"
    if ext in ["cif"]:
        return "cif"

    # Molecule set files
    if ext in ["smi"]:
        return "smi"

    # JSON files --> parse secondary extension
    elif ext in ["json", "cjson"]:
        # Small molecule
        if ext2 == "smol":
            return "smol"
        elif ext2 == "mol":  # backward compatibility for mol.json files
            return "smol"
        elif ext2 == "mmol":
            return "mmol"
        # Molecule set
        elif ext2 == "molset":
            return "molset"
        # JSON files
        else:
            return "json"

    # Data files
    elif ext in ["csv"]:
        return "data"

    # Text files
    elif ext in ["txt", "md", "yaml", "yml"]:
        return "text"

    # HTML files
    elif ext in ["html", "htm"]:
        return "html"

    # Image formats
    elif ext in ["jpg", "jpeg", "png", "gif", "bmp", "webp"]:
        return "img"

    # Video formats
    elif ext in ["mp4", "avi", "mov", "mkv", "webm"]:
        return "vid"

    # Individually recognized file formats (have their own icon)
    elif ext in ["sdf", "xml", "pdf", "svg", "run", "rxn", "md"]:
        return ext

    # # Yaml files
    # elif ext in ["yaml", "yml"]:
    #     return "yaml"

    else:
        # Unrecognized file formats
        return "unk"
