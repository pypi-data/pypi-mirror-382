"""
Public methods for the omgui library.

Sub modules:
    - mws: Molecule working set

Usage:
    import omgui

    omgui.launch()
    omgui.shutdown()

    omgui.mws.add("CCO")
    etc.
"""

# Expose sub-modules for the public API
from omgui import mws
from omgui.configuration import configure

from omgui.context import ctx
from omgui.startup import startup as _startup
from omgui.configuration import config as _config

config = _config()
_startup()

# ------------------------------------
# region - General
# ------------------------------------


def get_context() -> dict:
    """
    Get the current context as a dictionary.
    """
    ctx_dict = ctx().get_dict()
    return ctx_dict


def launch(*args, **kwargs) -> None:
    """
    Launch the GUI server.
    """
    from omgui.main import gui_init as _gui_init

    return _gui_init(*args, **kwargs)


def shutdown(*args, **kwargs) -> None:
    """
    Shutdown the GUI server.
    """
    from omgui.main import gui_shutdown as _gui_shutdown

    return _gui_shutdown(*args, **kwargs)


# endregion
# ------------------------------------
# region - Molecules
# ------------------------------------


def show_mol(molecule_identifier: str = "") -> None:
    """
    Open the molecule viewer for a given molecule identifier.
    """
    import urllib
    from omgui.main import gui_init as _gui_init

    path = "mol/" + urllib.parse.quote(molecule_identifier, safe="/")
    _gui_init(path)


def show_mols(smiles_or_inchi: list[str]) -> None:
    """
    Open the molecule set viewer for a list of SMILES or InChI strings.
    """
    import urllib
    from omgui.main import gui_init as _gui_init

    path = "molset/" + urllib.parse.quote("~".join(smiles_or_inchi), safe="/")
    _gui_init(path)


# endregion
# ------------------------------------
# region - Workspaces
# ------------------------------------


def get_workspace() -> str:
    """
    Get the current workspace.
    """
    return ctx().workspace


def get_workspaces() -> list[str]:
    """
    Get  the list of available workspaces.
    """
    return ctx().workspaces()


def set_workspace(name: str) -> bool:
    """
    Set the current workspace.
    """
    return ctx().set_workspace(name)


def create_workspace(name: str) -> bool:
    """
    Create a new workspace.
    """
    return ctx().create_workspace(name)


# endregion
# ------------------------------------
# region - Files
# ------------------------------------


def show_files(*args, **kwargs) -> None:
    """
    Open the file browser.
    """
    from omgui.main import gui_init as _gui_init

    return _gui_init(*args, **kwargs)


def open_file(path: str = "") -> None:
    """
    Open the appropriate viewer for a given file path.
    """
    import urllib
    from omgui.main import gui_init as _gui_init

    path = "~/" + urllib.parse.quote(path, safe="/")
    _gui_init(path)


def open_file_os(path: str = "") -> None:
    """
    Open the appropriate viewer for a given file path.
    """
    from omgui.gui.gui_services import srv_file_system

    srv_file_system.open_file_os(path)


# endregion
# ------------------------------------
