# Std
import json
from pathlib import Path

# OMGUI
from omgui.util.logger import get_logger
from omgui.configuration import config

# Logger
logger = get_logger()


def mws_core():
    """
    Get the MWS singleton instance.
    """
    return MoleculeWorkingSet()


class MoleculeWorkingSet:
    """
    Manages the molecule working set (MWS).
    """

    # Singleton instance
    _instance = None
    _initialized = False

    # Data
    _mws: list = None

    # ------------------------------------
    # region - Initialization
    # ------------------------------------

    def __new__(cls, session: bool = None):
        """
        Control singleton instance creation.
        """
        if cls._instance is None or session is True:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the MWS manager.
        """
        # Prevent re-initialization of singleton
        if self._initialized:
            return

        self._mws = self._load_mws_file()
        self.save()
        self._initialized = True

    def __len__(self):
        """
        Returns the number of molecules in the current working set.
        Usage: len(mws)
        """
        return len(self._mws) if self._mws is not None else 0

    def __repr__(self):
        """
        The official string representation of the object.
        Usage: repr(mws) or print(mws) or mws in a console.
        """
        return str(self._mws)

    def __iter__(self):
        """
        Make instance iterable.
        Usage: for x in mws: ...
        """
        return iter(self._mws)

    def _load_mws_file(self):
        """
        Loads the molecule working set for the current workspace into memory.
        """
        mws_path = self.file_path()

        # Read molecules from file
        if mws_path.exists():
            try:
                with open(mws_path, "r", encoding="utf-8") as file:
                    return json.load(file)
            except Exception as err:  # pylint: disable=broad-except
                logger.error(
                    "An error occurred while loading the molecule working set: %s",
                    err,
                )
                return []

        # Create file if missing
        else:
            mws_path.parent.mkdir(parents=True, exist_ok=True)
            with open(mws_path, "w", encoding="utf-8") as file:
                json.dump([], file, indent=4)
            return []

    # endregion
    # ------------------------------------
    # region - Core
    # ------------------------------------

    def file_path(self, workspace=None) -> Path:
        """
        Returns the current molecule working set path.
        """
        from omgui import ctx

        return ctx().workspace_path(workspace) / "._system" / "mws.json"

    def open(self) -> None:
        """
        Open the current molecule working set in the GUI.
        """
        from omgui.main import gui_init

        return gui_init(path="mws")

    def save(self) -> None:
        """
        Saves the mws data to the mws file in the data directory.
        """
        from omgui import ctx

        # In session context, mws is not saved to disk
        if ctx().session:
            return

        try:
            mws_path = self.file_path()
            with open(mws_path, "w", encoding="utf-8") as file:
                json.dump(self._mws, file, indent=4)

        except Exception as err:  # pylint: disable=broad-except
            logger.error("An error occurred while saving the mws file: %s", err)

    # endregion
    # ------------------------------------
    # region - Getters
    # ------------------------------------

    def get(self):
        """
        Returns the current molecule working set.
        """
        return self._mws

    def get_smiles(self):
        """
        Returns the SMILES of all molecules in the current working set.
        """
        from omgui.gui.workers.smol_transformers import molset_to_smiles_list

        return molset_to_smiles_list(self._mws)

    def get_names(self):
        """
        Returns the names of all molecules in the current working set.
        """
        from omgui.gui.workers.smol_transformers import molset_to_names_list

        return molset_to_names_list(self._mws)

    def count(self):
        """
        Returns the number of molecules in the current working set.
        """
        return len(self._mws)

    def is_empty(self) -> bool:
        """
        Returns whether the current molecule working set is empty.
        """
        return len(self._mws) == 0

    def is_mol_present(self, smol):
        """
        Check if a molecule is stored in your molecule working set.
        """
        from omgui.gui.workers.smol_functions import (
            get_best_available_identifier,
            get_smol_from_mws,
        )

        # Get best available identifier
        _, identifier = get_best_available_identifier(smol)

        # Check if it's in the working set
        present = bool(get_smol_from_mws(identifier))
        return present

    # endregion
    # ------------------------------------
    # region - Setters
    # ------------------------------------

    def add(self, smol):
        """
        Adds a molecule to the current molecule working set.
        """
        self._mws.append(smol.copy())
        self.save()

    def add_batch(self, molset: list, append: bool = False):
        """
        Load a molset into the molecule working set.
        """
        if append:
            self._mws.extend(molset)
        else:
            self._mws = molset
        self.save()
        return True

    def add_prop(self, *args, **kwargs) -> None:
        """
        Add properties to molecules in the current working set.
        """
        from omgui.mws.mws_add_prop import add_prop

        return add_prop(*args, **kwargs)

    def remove(self, i):
        """
        Removes a molecule from the current molecule working set.
        """
        self._mws.pop(i)
        self.save()

    def clear(self, force: bool = False) -> None:
        """
        Clears the current molecule working set.
        """
        self._mws = []
        self.save()

    # endregion
    # ------------------------------------
