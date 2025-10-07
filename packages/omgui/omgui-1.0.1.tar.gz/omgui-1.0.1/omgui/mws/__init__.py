# Std
from typing import Any

# OMGUI
from omgui.mws.mws_core import mws_core
from omgui.types import PropDataType

# ------------------------------------
# region - Core
# ------------------------------------


def open() -> None:  # pylint: disable=redefined-builtin
    """
    Open your molecule working set in the GUI.
    """
    mws_core().open()


# endregion
# ------------------------------------
# region - Manipulation
# ------------------------------------


def add(identifier: str, basic: bool = False) -> None:
    """
    Add a molecule to the current workspace's working set.
    """
    from omgui.gui.gui_services import srv_mws

    enrich = not basic
    return srv_mws.add_mol(identifier, enrich=enrich)


def remove(identifier: str) -> None:
    """
    Remove a molecule from the current workspace's working set.
    """
    from omgui.gui.gui_services import srv_mws

    return srv_mws.remove_mol(identifier)


def add_prop(prop_data: PropDataType, prop_name: str = None) -> None:
    """
    Add properties to molecules in the current working set.
    """
    return mws_core().add_prop(prop_data, prop_name)


def clear(force: bool = False) -> None:
    """
    Clear the current molecule working set.
    """
    from omgui.spf import spf
    from omgui.util.general import confirm_prompt

    if mws_core().is_empty():
        spf.warning("No molecules to clear")
        return

    pr = f"Are you sure you want to clear {mws_core().count()} molecules?"
    if force or confirm_prompt(pr):
        mws_core().clear()
        return spf.result("✅ Molecule working set cleared")


# endregion
# ------------------------------------
# region - Getters
# ------------------------------------


def get() -> list[dict[str, Any]]:
    """
    Get the current molecule working set.
    """
    return mws_core().get()


def get_names() -> list[str]:
    """
    Get your molecule working set as a list of names.
    """
    return mws_core().get_names()


def get_smiles() -> list[str]:
    """
    Get your molecule working set as a list of SMILES.
    """
    return mws_core().get_smiles()


def count() -> int:
    """
    Get the number of molecules in your molecule working set.
    """
    return mws_core().count()


def is_empty() -> bool:
    """
    Whether the your molecule working set is empty.
    """
    return mws_core().is_empty()


def export(path: str = "") -> bool:
    """
    Export your molecule working set to a file.

    The file extension determines the format.
    Supported file extensions: csv, json, sdf
    """
    from omgui.gui.gui_services import srv_mws

    return srv_mws.export(path)


# endregion
# ------------------------------------
