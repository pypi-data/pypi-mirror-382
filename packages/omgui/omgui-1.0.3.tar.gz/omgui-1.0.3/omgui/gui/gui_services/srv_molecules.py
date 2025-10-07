"""
Molecule functions for OMGUI API endpoints.
"""

import os
import json
import shutil

# OMGUI - Small molecule functions
from omgui.gui.workers.smol_functions import (
    get_smol_from_pubchem,
    create_molset_cache_file,
    get_smol_name,
    assemble_cache_path,
    read_molset_from_cache,
    find_smol,
    get_smol_from_mws,
    get_best_available_identifier,
    get_best_available_smiles,
    merge_smols,
)
from omgui.gui.workers.smol_transformers import (
    smol2svg,
    smol2mdl,
    molset2dataframe,
    write_dataframe2sdf,
    write_dataframe2csv,
    identifiers2molset,
)


# OMGUI - Macromolecule functions
from omgui.gui.workers.mmol_functions import mmol_from_identifier
from omgui.gui.workers.mmol_transformers import mmol2pdb, mmol2cif, cif2mmol

# OMGUI
from omgui import ctx
from omgui.mws.mws_core import mws_core
from omgui.util.json_decimal_encoder import JSONDecimalEncoder
from omgui.util.mol_utils import create_molset_response
from omgui.util import exceptions as omg_exc
from omgui.spf import spf


# ------------------------------------
# region - Small molecules
# ------------------------------------


def get_smol_data(identifier):
    """
    Get molecule data, plus MDL and SVG.
    Used when requesting a molecule by its identifier.
    """
    smol = find_smol(identifier, enrich=True)

    # Fail
    if not smol:
        raise omg_exc.NoResult(
            f"No small molecule found with identifier '{identifier}'"
        )

    # Success
    return smol


def get_smol_viz_data(inchi_or_smiles):
    """
    Get a molecule's SVG and MDL data, which can be used to render 2D and 3D visualizations.
    """
    try:
        svg = smol2svg(inchi_or_smiles=inchi_or_smiles)
        mdl = smol2mdl(inchi_or_smiles=inchi_or_smiles)

    except (TypeError, ValueError) as err:
        raise omg_exc.InvalidMoleculeInput(
            f"Failed to generate visualisation data for '{inchi_or_smiles}'. Input should be SMILES or InChI."
        ) from err

    if not svg and not mdl:
        raise omg_exc.NoResult(
            f"Failed to generate visualisation data for '{inchi_or_smiles}'. No valid data could be generated."
        ) from err

    return {"mdl": mdl, "svg": svg}


def get_mol_data_from_molset(cache_id, index=1):
    """
    Get a molecule from a molset file.
    """
    cache_path = assemble_cache_path("molset", cache_id)

    with open(cache_path, "r", encoding="utf-8") as f:
        molset = json.load(f)

    return molset[index - 1]


def enrich_smol(smol):
    """
    Enrich a molecule with PubChem data.
    """

    # Get best available identifier.
    _, identifier = get_best_available_identifier(smol)

    # Enrich molecule withg PubChem data.
    smol_enriched = get_smol_from_pubchem(identifier)
    if smol_enriched:
        smol = merge_smols(smol, smol_enriched)

    return smol


# endregion
# ------------------------------------
# region - Macromolecules
# ------------------------------------


def get_mmol_data(identifier):
    """
    Get macromolecule data.
    Used when requesting a macromolecule by its identifier.
    """
    success, cif_data = mmol_from_identifier(identifier)

    if not success:
        raise omg_exc.NoResult(f"No macromolecule found with identifier '{identifier}'")
    else:
        mmol = cif2mmol(cif_data)
        return mmol


# endregion
# ------------------------------------
# region - Molecules shared
# ------------------------------------


def save_mol(mol, path, new_file=True, force=False, format_as="mol_json"):
    """
    Save a molecule to a file, in the specified format.

    Parameters
    ----------
    mol: dict
        molecule object (smol or mmol)
    path: str
        destination file path
    new_file: bool
        whether to create a new file or update an existing one (default: True)
    force: bool
        whether to overwrite existing files (default: False)
    format_as: str
        file format to save as (default: "mol_json")
    """

    # Note: the new_file parameter is always true for now, but later on
    # when we let users add comments etc, we'll want to be able to update
    # existing files.

    # Detect smol or mmol format
    # TODO: implement a strict schema that can be validated
    smol = mol if "identifiers" in mol else None
    mmol = mol if "data" in mol else None

    if not smol and not mmol:
        raise omg_exc.InvalidMoleculeInput

    # Compile path
    workspace_path = ctx().workspace_path()
    file_path = workspace_path / path

    # Throw error when detination file (does not) exist(s).
    if path:
        if new_file:
            if os.path.exists(file_path) and not force:
                raise FileExistsError(f"File path: {file_path}")
        else:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File path: {file_path}")

    # Small molecules
    # ------------------------------------
    if smol:

        # Save as .smol.json file.
        if format_as == "mol_json":
            # Write to file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(smol, f, ensure_ascii=False, indent=4, cls=JSONDecimalEncoder)

        # Save as .sdf file.
        elif format_as == "sdf":
            df = molset2dataframe([smol], include_romol=True)
            write_dataframe2sdf(df, file_path)

        # Save as .csv file.
        elif format_as == "csv":
            df = molset2dataframe([smol])
            write_dataframe2csv(df, file_path)

        # Save as .mol file.
        elif format_as == "mdl":
            smol2mdl(smol, path=file_path)

        # Save as .smi file.
        elif format_as == "smiles":
            smiles = get_best_available_smiles(smol)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(smiles)

    # Macromolecules
    # ------------------------------------
    elif mmol:

        # Save as .mmol.json file.
        if format_as == "mmol_json":
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(mmol, f, ensure_ascii=False, indent=4, cls=JSONDecimalEncoder)

        # Save as .cif file.
        elif format_as == "cif":
            mmol2cif(mmol, path=file_path)

        # Save as .pdb file.
        elif format_as == "pdb":
            mmol2pdb(mmol, path=file_path)

    return True


# endregion
# ------------------------------------
# region - Molsets
# -----------------------------


def get_molset(cache_id, query=None):
    """
    Get a cached molset, filtered by the query.
    Note: opening molset files is handled by _attach_file_data() in gui_services/file_system.py
    """
    # Read molset from cache
    molset = read_molset_from_cache(cache_id)

    # Formulate response object
    return create_molset_response(molset, query, cache_id)


def get_molset_adhoc(inchi_or_smiles, query=None, return_cache_id=False):
    """
    Get an ad-hoc molset from a list of identifiers provided in the query.
    """
    if len(inchi_or_smiles) == 0:
        raise ValueError("No identifiers provided")

    molset = identifiers2molset(inchi_or_smiles)

    if len(molset) == 0:
        raise omg_exc.NoResult("No molecules found for the provided identifiers")

    # Add index
    for i, smol in enumerate(molset):
        smol["index"] = i + 1

    # Create cache working copy
    cache_id = create_molset_cache_file(molset)

    # When posting a molset, we just need the cache ID to serve it
    if return_cache_id:
        return cache_id

    # Read molset from cache
    molset = read_molset_from_cache(cache_id)

    # Formulate response object
    return create_molset_response(molset, query, cache_id)


def post_molset_adhoc(inchi_or_smiles, query=None):
    """
    Post an ad-hoc molset provided in the request body.
    This is needed when the molset is too large to be passed as a query parameter.
    """
    # unique_id = hash_data(str(inchi_or_smiles))
    # key = f"input_data:{unique_id}"

    # Assemble molset
    cache_id = get_molset_adhoc(inchi_or_smiles, query, return_cache_id=True)

    return {
        "id": cache_id,
        "url": f"/molset/id/{cache_id}",
    }


##


def remove_from_molset(cache_id, indices, query=None):
    """
    Remove molecules from a molset's cached working copy.
    """

    if len(indices) == 0:
        raise ValueError("No indices provided")

    # Compile path
    cache_path = assemble_cache_path("molset", cache_id)

    # Read file from cache
    with open(cache_path, "r", encoding="utf-8") as f:
        molset = json.load(f)

    # Remove molecules
    molset = [mol for mol in molset if mol.get("index") not in indices]

    # Write to cache
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(molset, f, ensure_ascii=False, indent=4, cls=JSONDecimalEncoder)

    # Create response object
    return create_molset_response(molset, query, cache_id)


def clear_molset_working_copy(cache_id):
    """
    Clear a molset's cached working copy.
    """
    cache_path = assemble_cache_path("molset", cache_id)

    if os.path.exists(cache_path):
        os.remove(cache_path)

    return True


##


def save_molset(
    cache_id,
    path,
    new_file=False,
    format_as="molset_json",
    remove_invalid_mols=False,
):
    """
    Save a molset to a file, in the specified format.

    Parameters
    ----------
    new_file: bool
        Whether we're creating a new file or overwriting an existing one.
    format_as: 'molset_json' | 'sdf' | 'csv' | 'smiles'.
        The format to save the molset as.
    remove_invalid_mols: bool
        Whether to remove invalid molecules from the molset before saving.

    """
    # Compile path
    workspace_path = ctx().workspace_path()
    file_path = workspace_path / path
    cache_path = assemble_cache_path("molset", cache_id)

    # Throw error when destination file (does not) exist(s)
    if path:
        if new_file:
            if os.path.exists(file_path):
                raise FileExistsError(f"File path: {file_path}")
        else:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File path: {file_path}")

    if not os.path.exists(cache_path):
        raise omg_exc.CacheFileNotFound(f"Cache file path: {cache_path}")

    # For .molset.json files, we simply copy the cache file to the destination
    if format_as == "molset_json":
        shutil.copy(cache_path, file_path)
        return True

    # For all other formats, we need to read the
    # molset data into memory so we can transform it
    else:
        with open(cache_path, "r", encoding="utf-8") as f:
            molset = json.load(f)

    # Save as SDF file
    if format_as == "sdf":
        df = molset2dataframe(molset, remove_invalid_mols, include_romol=True)
        write_dataframe2sdf(df, file_path)

    # Save as CSV file
    elif format_as == "csv":
        df = molset2dataframe(molset, remove_invalid_mols)
        write_dataframe2csv(df, file_path)

    # Save as SMILES file
    elif format_as == "smiles":
        smiles_list = []
        missing_smiles = []
        for mol in molset:
            smiles = get_best_available_smiles(mol)
            if smiles:
                smiles_list.append(smiles)
            else:
                missing_smiles.append(mol["index"])

        # Return error if there are missing SMILES
        if missing_smiles:
            raise omg_exc.InvalidMolset(
                f"Missing SMILES for molecules: {missing_smiles}"
            )

        # Write to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(smiles_list))

    elif format_as == "mws":
        # Read file from cache
        with open(cache_path, "r", encoding="utf-8") as f:
            molset = json.load(f)

        # Compile molset
        molset = []
        for mol in molset:
            molset.append(mol)

        mws_core().add_batch(molset)

    return True


def replace_mol_in_molset(cache_id, path, mol, format_as):
    """
    Replace a molecule in a molset file.

    This first updates the cache working copy, then saves the
    changes to the actual molset file, or to the molecule working set.
    """
    # Compile path
    cache_path = assemble_cache_path("molset", cache_id)

    # Read file from cache.
    with open(cache_path, "r", encoding="utf-8") as f:
        molset = json.load(f)

    # Replace molecule in molset working copy.
    index = mol.get("index")
    molset[index - 1] = mol

    # Write to cache.
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(molset, f, ensure_ascii=False, indent=4, cls=JSONDecimalEncoder)

    # Now the working copy is updated, we also update the molset.
    return save_molset(cache_id, path, new_file=False, format_as=format_as)


# endregion
# ------------------------------------
