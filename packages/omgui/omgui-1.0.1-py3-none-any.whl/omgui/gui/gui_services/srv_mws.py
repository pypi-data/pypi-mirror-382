"""
Molecule working set functions for OMGUI API endpoints.
"""

# Std
import json
from pathlib import Path

# OMGUI
from omgui import mws, ctx
from omgui.spf import spf
from omgui.mws.mws_core import mws_core
from omgui.util import exceptions as omg_exc
from omgui.util.mol_utils import create_molset_response
from omgui.util.paths import path_type, resolve_path, prepare_file_path
from omgui.gui.workers import smol_functions, smol_transformers


# from omgui.util.logger import get_logger
# Logger
# logger = get_logger()


def add_mol(
    identifier: str = None,
    smol: dict = None,
    enrich: bool = None,
    silent: bool = False,
) -> bool:
    """
    Add a molecule to the molecule working set.

    Takes either an identifier or a mol object.
    """

    # TODO: add pydantic type for mol and validate

    # Invalid input
    if not smol and not identifier:
        raise omg_exc.InvalidMoleculeInput(
            "Either a molecule object or an identifier must be provided."
        )

    # Default enrich to True for identifiers and False for smol objects
    enrich = (smol is None) if enrich is None else enrich

    # Smol object -> enrich if requested
    if smol:
        # Maybe enrich with PubChem data
        if enrich:
            _, identifier = smol_functions.get_best_available_identifier(smol)
            smol_enriched = smol_functions.find_smol(identifier, enrich=True)
            if smol_enriched:
                smol = smol_functions.merge_smols(smol, smol_enriched)

    # Identifier -> enrich by default
    else:
        smol = smol_functions.find_smol(identifier, enrich=enrich)

    # Fail
    if not smol:
        return False

    # -- smol is defined --

    name = smol_functions.get_smol_name(smol)
    inchikey = smol.get("identifiers", {}).get("inchikey")

    # Already in mws -> skip
    if smol_functions.get_smol_from_mws(inchikey) is not None:
        if not silent:
            spf.success(f"Molecule <yellow>{name}</yellow> already in working set")
        return True

    # Add to working set
    mws_core().add(smol)
    if not silent:
        spf.success(f"Molecule <yellow>{name}</yellow> was added")
    return True


def remove_mol(identifier: str = None, smol: dict = None, silent=False):
    """
    Remove a molecule from your molecule working set.

    Takes either an identifier or a mol object.
    Identifier is slow because the molecule data has to be loaded from PubChem.
    """
    if not smol and not identifier:
        raise omg_exc.InvalidMoleculeInput(
            "Either a molecule object or an identifier must be provided."
        )

    # Create molecule object if only identifier is provided
    if not smol:
        smol = smol_functions.get_smol_from_mws(identifier)

    # -- smol is defined --

    name = smol_functions.get_smol_name(smol)
    inchikey = smol.get("identifiers", {}).get("inchikey")

    try:
        # Find matching molecule
        for i, item in enumerate(mws_core().get()):
            if item.get("identifiers", {}).get("inchikey") == inchikey:

                # Remove from mws
                mws_core().remove(i)

                # Feedback
                if not silent:
                    spf.success(f"Molecule <yellow>{name}</yellow> was removed")
                return True

        # Not found
        if not silent:
            spf.error(f"Molecule <yellow>{name}</yellow> not found in working set")
        return False

    except Exception as err:  # pylint: disable=broad-except
        if not silent:
            spf.error([f"Molecule <yellow>{name}</yellow> failed to be removed", err])
        return False


def get_cached_mws(query=None):
    """
    Fetch the current molecule working set for GUI display.
    """
    if mws_core().count() > 0:
        # Add index
        for i, smol in enumerate(mws_core().get()):
            smol["index"] = i + 1

        # Create cache working copy
        cache_id = smol_functions.create_molset_cache_file(mws_core().get())

        # Read molset from cache
        _mws = smol_functions.read_molset_from_cache(cache_id)

        # Formulate response object
        return create_molset_response(_mws, query, cache_id)

    else:
        return None


def export(file_path_str: str = "") -> bool:
    """
    Export the current molecule working set to a file.

    Supported formats: json, csv, sdf, smi
    """

    # print(f"\n\nPath: '{path}'")

    if mws_core().is_empty():
        spf.warning("No molecules to export")
        return False

    file_path = resolve_path(file_path_str)
    default_stem = "mws_export"
    supported_formats = [".csv", ".json", ".sdf", ".smi"]

    # No extension --> default to JSON
    if not file_path.suffix:
        spf.warning("No file extension provided, defaulting to JSON format")
        file_path = (file_path / default_stem).with_suffix(".molset.json")

    # Unsupported format --> abort
    elif file_path.suffix not in supported_formats:
        spf.error(
            [
                f"Failed to export molecule working set to <yellow>{file_path_str}</yellow>",
                f"Unsupported <yellow>{file_path.suffix}</yellow> format - supported extensions are: {' / '.join(supported_formats)}",
            ]
        )
        return False

    # Prepate path
    file_path = prepare_file_path(file_path)
    if not file_path:
        return False

    # Write to disk
    try:
        if file_path.suffix == ".json":
            _export_as_json(file_path)
        elif file_path.suffix == ".csv":
            _export_as_csv(file_path)
        elif file_path.suffix == ".sdf":
            _export_as_sdf(file_path)
        elif file_path.suffix == ".smi":
            _export_as_smi(file_path)

        # Success
        if path_type(file_path_str) == "workspace":
            spf.success(
                f"Molecule working set exported to your <reset>{ctx().workspace}</reset> workspace as <yellow>{file_path.name}</yellow>"
            )
        else:
            spf.success(
                f"Molecule working set exported to <yellow>{file_path}</yellow>"
            )
        return True

    except Exception as err:  # pylint: disable=broad-except
        spf.error(
            [
                f"Failed to export molecule working set to <yellow>{file_path_str}</yellow>",
                err,
            ]
        )
        return False


def _export_as_json(file_path: Path):
    molset = mws.get()
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(molset, f, indent=2, ensure_ascii=False)


def _export_as_csv(file_path: Path):
    molset = mws.get()
    df = smol_transformers.molset2dataframe(molset)
    smol_transformers.write_dataframe2csv(df, file_path)


def _export_as_sdf(file_path: Path):
    molset = mws.get()
    df = smol_transformers.molset2dataframe(molset, include_romol=True)
    smol_transformers.write_dataframe2sdf(df, file_path)


def _export_as_smi(file_path: Path):
    smiles = mws.get_smiles()
    with open(file_path, "w", encoding="utf-8") as f:
        for smi in smiles:
            f.write(smi + "\n")
