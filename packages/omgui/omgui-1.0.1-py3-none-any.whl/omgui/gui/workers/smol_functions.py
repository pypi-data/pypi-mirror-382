"""
Molecule management functions
"""

# Std
import os
import re
import time
import json
import shutil
import random
import logging
import asyncio
from pathlib import Path
from copy import deepcopy

# 3rd party
import pandas
import requests
import aiofiles
import pubchempy as pcy
from rdkit import Chem, rdBase, RDLogger
from rdkit.Chem.rdchem import Mol
from rdkit.Chem.Descriptors import MolWt, ExactMolWt

# OMGUI
from omgui import ctx
from omgui.spf import spf
from omgui.mws.mws_core import mws_core
from omgui.gui.workers import smol_transformers
from omgui.gui.workers.data_structures import OPENAD_SMOL_DICT
from omgui.util.spinner import Spinner
from omgui.util.paths import resolve_path
from omgui.util.json_decimal_encoder import JSONDecimalEncoder
from omgui.util.general import pretty_date, is_numeric, merge_dict_lists
from omgui.util.logger import get_logger

# Logger
logger = get_logger()

# Silcence RDKit errors
RDLogger.DisableLog("rdApp.error")
RDLogger.DisableLog("rdApp.warning")

# Silence pubchempy logger
logging.getLogger("pubchempy").handlers.clear()
logging.getLogger("pubchempy").propagate = False
logging.getLogger("pubchempy").setLevel(logging.WARNING)

# This doesn't seem to work anymore... is upposed to live inside the function scope.
# rdBase.BlockLogs()  # pylint: disable=c-extension-no-member

# PubChem accepted molecule identifiers
PCY_IDFR = {
    "name": "name",
    "smiles": "smiles",
    "inchi": "inchi",
    "inchikey": "inchikey",
    "cid": "cid",
    "formula": "formula",
}
# [{'urn': {'label': 'SMILES', 'name': 'Absolute', 'datatype': 1, 'version': '2.3.0', 'software': 'OEChem', 'source': 'OpenEye Scientific Software', 'release': '2025.04.14'}, 'value': {'sval': 'CCCCCCO'}}, {'urn': {'label': 'SMILES', 'name': 'Connectivity', 'datatype': 1, 'version': '2.3.0', 'software': 'OEChem', 'source': 'OpenEye Scientific Software', 'release': '2025.06.30'}, 'value': {'sval': 'CCCCCCO'}}]
MOL_PROPERTY_SOURCES = {
    "Log P-XLogP3-AA": "xlogp",
    "Log P-XLogP3": "xlogp",
    # "SMILES-Isomeric": "isomeric_smiles",
    # "SMILES-Canonical": "canonical_smiles",
    "SMILES-Absolute": "isomeric_smiles",
    "SMILES-Connectivity": "canonical_smiles",
    "Molecular Weight": "molecular_weight",
    "Compound Complexity": "complexity",
    "Count-Rotatable Bond": "rotatable_bond_count",
    "Compound-Canonicalized": "complexity",
    "Count-Hydrogen Bond Acceptor": "h_bond_acceptor_count",
    "Count-Hydrogen Bond Donor": "h_bond_donor_count",
    "IUPAC Name-Preferred": "iupac_name",
    "Fingerprint-SubStructure Keys": "",
    "InChI-Standard": "inchi",
    "InChIKey-Standard": "inchikey",
    "Mass-Exact": "exact_mass",
    "Weight-MonoIsotopic": "monoisotopic_mass",
    "Molecular Formula": "molecular_formula",
    "Topological-Polar Surface Area": "tpsa",
}

# Molecule properties with machine data which we omit
# when displaying the molecule properties in the CLI
SMOL_PROPS_IGNORE = [
    "atoms",
    "bonds",
    "cactvs_fingerprint",
    "elements",
    "fingerprint",
    "record",
]

# @@Todo: retire thsi in favor of SMOL_PROPS_IGNORE?
SMOL_PROPERTIES = sorted(
    [
        "atom_stereo_count",
        "bond_stereo_count",
        "canonical_smiles",
        "charge",
        "cid",
        "complexity",
        "conformer_count_3d",
        "conformer_id_3d",
        "conformer_model_rmsd_3d",
        "conformer_rmsd_3d",
        "coordinate_type",
        "covalent_unit_count",
        "defined_atom_stereo_count",
        "defined_bond_stereo_count",
        "effective_rotor_count_3d",
        "exact_mass",
        "feature_acceptor_count_3d",
        "feature_anion_count_3d",
        "feature_cation_count_3d",
        "feature_count_3d",
        "feature_donor_count_3d",
        "feature_hydrophobe_count_3d",
        "feature_ring_count_3d",
        "h_bond_acceptor_count",
        "h_bond_donor_count",
        "heavy_atom_count",
        "inchi",
        "inchikey",
        "isomeric_smiles",
        "isotope_atom_count",
        "iupac_name",
        "mmff94_energy_3d",
        "mmff94_partial_charges_3d",
        "molecular_formula",
        "molecular_weight_exact",
        "molecular_weight",
        "monoisotopic_mass",
        "multipoles_3d",
        "multipoles_3d",
        "pharmacophore_features_3d",
        "pharmacophore_features_3d",
        "rotatable_bond_count",
        "sol_classification",
        "sol",
        "tpsa",
        "undefined_atom_stereo_count",
        "undefined_bond_stereo_count",
        "volume_3d",
        "x_steric_quadrupole_3d",
        "xlogp",
        "y_steric_quadrupole_3d",
        "z_steric_quadrupole_3d",
    ]
)
INPUT_MAPPINGS = {
    "NAME": "chemical_name",
    "xlogp3": "xlogp",
    "molecular weight": "molecular_weight",
    "complexity": "complexity",
    "rotatable bond count": "rotatable_bond_count",
    "hydrogen bond acceptor count": "h_bond_acceptor_count",
    "hydrogen bond donor count": "h_bond_donor_count",
    "exact mass": "exact_mass",
    "monoisotopic mass": "monoisotopic_mass",
    "topological polar surface area": "tpsa",
    "heavy atom count": "heavy_atom_count",
    "formal charge": "formal_charge",
    "isotope atom count": "isotope_atom_count",
    "defined atom stereocenter count": "defined_atom_stereo_count",
    "undefined atom stereocenter count": "undefined_atom_stereo_count",
    "covalently-bonded unit count": "covalent_unit_count",
    "compound is canonicalized": "compound_canonicalized",
    "SOL_classification": "sol_classification",
    "SOL": "sol",
}

mol_name_cache = {}

spinner = Spinner()

#
#

# ------------------------------------
# region - Lookup / creation
# ------------------------------------


def find_smol(
    identifier: str,
    name: str = None,
    enrich: bool = False,
    show_spinner: bool = False,
) -> dict | None:
    """
    Find a molecule across the available resources.
    First we check our working set, then PubChem, then RDKit.

    Parameters
    ----------
    identifier: str
        The molecule identifier to search for.
        Valid inputs: InChI, SMILES, InChIKey, name, CID.
    name: str
        Optional name for the molecule.
    rich: bool
        If True, fetch molecule data from PubChem, otherwise just
        create a basic molecule dict with RDKit (no API calls).
    show_spinner: bool
        If True, show a spinner while searching for the molecule.

    Returns
    -------
    smol: dict
        The OpenAD small molecule dictionary if found, otherwise None.
    """

    # Look for molecule in the working set
    smol = get_smol_from_mws(identifier)

    # Look for molecule on PubChem
    if not smol and enrich:
        smol = get_smol_from_pubchem(identifier, show_spinner)

    # Try creating molecule object with RDKit.
    if not smol:
        if show_spinner:
            spinner.start("Creating molecule with RDKit")
        smol = new_smol(identifier, name=name)
        if show_spinner:
            spinner.stop()

    # Fail - invalid
    if not smol:
        if enrich:
            spf.error(f"Unable to identify molecule <yellow>{identifier}</yellow>")
        else:
            spf.error(f"Invalid InChI or SMILES string <yellow>{identifier}</yellow>")

    return smol


def get_smol_from_mws(identifier: str, ignore_synonyms: bool = False) -> dict | None:
    """
    Retrieve a molecule from the molecule working set.

    Parameters
    ----------
    identifier: str
        The molecule identifier to search for.
        Valid inputs: InChI, SMILES, InChIKey, name, CID.
    ignore_synonyms: bool
        If True, ignore synonyms in the search.

    Returns
    -------
    dict
        The OpenAD smol dictionary if found, otherwise None.
    """

    smol = get_smol_from_list(
        identifier, mws_core().get(), ignore_synonyms=ignore_synonyms
    )
    if smol is not None:
        return deepcopy(smol)
    return None


def get_smol_from_pubchem(identifier: str, show_spinner: bool = False) -> dict | None:
    """
    Fetch small molecule from PubChem.

    Parameters
    ----------
    identifier: str
        The small molecule identifier to search for.
        Valid inputs: InChI, SMILES, InChIKey, name, CID.
    """
    smol = None

    # Smiles
    if possible_smiles(identifier):
        if show_spinner:
            spinner.start("Searching PubChem for SMILES")
        smol = _get_pubchem_compound(identifier, PCY_IDFR["smiles"])
        if not smol and show_spinner:
            spinner.stop()
    # InChI
    if not smol and identifier.startswith("InChI="):
        if show_spinner:
            spinner.start("Searching PubChem for InChI")
        smol = _get_pubchem_compound(identifier, PCY_IDFR["inchi"])
        if not smol and show_spinner:
            spinner.stop()

    # InChIKey
    if not smol and len(identifier) == 27:
        if show_spinner:
            spinner.start("Searching PubChem for inchikey")
        smol = _get_pubchem_compound(identifier, PCY_IDFR["inchikey"])
        if not smol and show_spinner:
            spinner.stop()

    # CID
    if not smol and is_numeric(identifier):
        if show_spinner:
            spinner.start("Searching PubChem for CID")
        smol = _get_pubchem_compound(identifier, PCY_IDFR["cid"])
        if not smol and show_spinner:
            spinner.stop()

    # Name
    if not smol:
        if show_spinner:
            spinner.start("Searching PubChem for name")
        smol = _get_pubchem_compound(identifier, PCY_IDFR["name"])
        if not smol and show_spinner:
            spinner.stop()

    # Formula - may result in timeouts from PubChem
    if not smol:
        if show_spinner:
            spinner.start("Searching PubChem for formula")
        smol = _get_pubchem_compound(identifier, PCY_IDFR["formula"])
        if not smol and show_spinner:
            spinner.stop()

    if show_spinner:
        spinner.stop()

    if smol:
        return _sep_identifiers_from_properties(smol)

    return None


def get_mol_rdkit(inchi_or_smiles: str, identifier_type: str = None) -> dict | None:
    """
    Parse identifier into an RDKit molecule.

    Parameters
    ----------
    inchi_or_smiles: str
        An InChI or SMILES molecule identifier
    identifier_type: str
        Either "inchi" or "smiles"
    """

    mol_rdkit = None

    try:
        if (
            identifier_type
            and isinstance(identifier_type, str)
            and identifier_type.lower() == "smiles"
        ):
            mol_rdkit = Chem.MolFromSmiles(inchi_or_smiles)  # pylint: disable=no-member
        else:
            mol_rdkit = Chem.MolFromInchi(inchi_or_smiles)
            if not mol_rdkit:
                mol_rdkit = Chem.MolFromSmiles(  # pylint: disable=no-member
                    inchi_or_smiles
                )
            if not mol_rdkit:
                mol_rdkit = Chem.MolFromInchi("InChI=1S/" + inchi_or_smiles)
            if not mol_rdkit:
                return None
    except Exception:  # pylint: disable=broad-exception-caught
        return None

    return mol_rdkit


# region--local
def _get_pubchem_compound(identifier: str, identifier_type: str) -> dict | None:
    """
    Fetch small molecule from PubChem based on an identifier.

    Parameters
    ----------
    identifier: str
        The small molecule identifier to search for.
        Valid inputs: InChI, SMILES, InChIKey, name, CID.
    identifier_type: str
        The type of identifier to search for (see PCY_IDFR).
    """

    mol_pcy = None

    try:
        # Find molecule on PubChem
        logger.info("Searching PubChem for %s: %s", identifier_type, identifier)
        compounds = pcy.get_compounds(identifier, identifier_type)
        if len(compounds) == 0:
            logger.warning("--> ❌ PubChem search returned no results: %s", identifier)
            return None
        else:
            mol_pcy = compounds[0].to_dict()
            logger.info(
                "--> ✅ PubChem compound found: CID %s / %s",
                mol_pcy.get("cid"),
                identifier,
            )

        # Create OpenAD smol dict
        if mol_pcy:
            smol = deepcopy(OPENAD_SMOL_DICT)
            smol = _add_pcy_data(smol, mol_pcy, identifier, identifier_type)
            return smol

    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.error("Error _get_pubchem_compound(): %s", err)

        # # Keep here for debugging
        # spf.error(
        #     [
        #         "Error _get_pubchem_compound()",
        #         f"identifier: {identifier}",
        #         f"identifier_type: {identifier_type}",
        #         err,
        #     ]
        # )

    return None


def _add_pcy_data(smol, smol_pcy, identifier, identifier_type):
    """
    Add PubChem molecule data to the OpenAD molecule dict.

    Parameters
    ----------
    smol: dict
        The OpenAD small molecule dictionary to which we add the PubChem data.
    mol_pcy: dict
        The PubChem molecule data.
    identifier: str
        The molecule identifier.
    identifier_type: str
        The type of identifier to search for (see PCY_IDFR).
    """

    smol["enriched"] = True

    # Add synonyms
    synonyms = pcy.get_synonyms(smol_pcy["iupac_name"], "name")
    smol["synonyms"] = (
        synonyms[0].get("Synonym") if synonyms and len(synonyms) > 0 else []
    )

    if identifier_type == PCY_IDFR["name"]:
        smol["identifiers"]["name"] = identifier
    elif len(smol.get("synonyms", [])) > 1:
        smol["identifiers"]["name"] = smol["synonyms"][0]
    elif (
        len(smol_pcy["iupac_name"]) < 40
    ):  # The iupac_name can be very long, so we only use it if it's short.
        smol["identifiers"]["name"] = smol_pcy["iupac_name"]

    # Add properties
    smol["properties"] = smol_pcy

    # Add canonical smiles
    if identifier_type == PCY_IDFR["smiles"]:
        # fmt: off
        smol["identifiers"]["canonical_smiles"] = canonicalize(identifier)  # pylint: disable=no-member
        # fmt: on

    # Loop through PubChem properties and update our own property_sources
    # when PubChem has its own 3rd party source for a property.
    # - - -
    # For example the property_sources["iupac_name"] value when looking up dopamine:
    # - Before: {"source": "pubchem"}
    # - After: { 'label': 'IUPAC Name', 'name': 'Preferred', 'datatype': 1, 'version': '2.7.0',
    #            'software': 'Lexichem TK', 'source': 'OpenEye Scientific Software', 'release': '2021.10.14'}

    for x in SMOL_PROPERTIES:
        smol["property_sources"][x] = {"source": "PubChem"}
        for prop_name, prop_name_key in MOL_PROPERTY_SOURCES.items():
            if prop_name_key == x:
                if len(prop_name.split("-")) > 0:

                    for y in smol_pcy.get("record", {}).get("props", []):

                        if "label" not in y["urn"]:

                            pass
                        elif (
                            y["urn"]["label"] == prop_name.split("-", maxsplit=1)[0]
                            and "name" not in y["urn"]
                        ):
                            smol["property_sources"][x] = y["urn"]
                        elif (
                            y["urn"]["label"] == prop_name.split("-", maxsplit=1)[0]
                            and y["urn"]["name"] == prop_name.split("-", maxsplit=2)[1]
                        ):
                            smol["property_sources"][x] = y["urn"]

    return smol


def _sep_identifiers_from_properties(smol: dict) -> dict:
    """
    Separate molecules identifiers from properties.

    This is the final step when processing external molecule data
    from a file like MDL, SDF, CSV, etc. or from an API call, so
    a molecule is in the correct OpenAD format.

    Parameters
    ----------
    smol: dict
        The molecule object to modify.
    """

    # Move all identifiers to the identifiers key.
    smol["identifiers"] = _get_identifiers(smol)

    # Remove identifiers from properties.
    # Create a lowercase version of the properties dictionary
    # so we can scan for properties in a case-insensitive way.
    molIdfrs = {k.lower(): v for k, v in smol["identifiers"].items()}
    for prop in list(smol["properties"]):
        if prop.lower() in molIdfrs:
            del smol["properties"][prop]

    # This is a Workaround for Pub Chempy and Pubchem being out of sync
    for src in smol.get("properties", {}).get("record", {}).get("props", []):
        if "urn" in src:
            if src["urn"]["label"] == "SMILES" and src["urn"]["name"] == "Absolute":
                smol["identifiers"]["isomeric_smiles"] = src["value"]["sval"]
            elif (
                src["urn"]["label"] == "SMILES" and src["urn"]["name"] == "Connectivity"
            ):
                smol["identifiers"]["canonical_smiles"] = src["value"]["sval"]

    return smol


def _get_identifiers(smol: dict) -> dict:
    """
    Pull the identifiers from a molecule.
    """

    identifier_keys = OPENAD_SMOL_DICT.get("identifiers").keys()

    # # In case this smol has the identifiers already separated.
    # if smol.get("identifiers"):
    #     for key, val in smol.get("identifiers").items():
    #         if val and key != "name":
    #             return smol["identifiers"]

    identifier_dict = {"name": smol["identifiers"].get("name", None)}

    # Create a lowercase version of the properties dictionary
    # so we can scan for properties in a case-insensitive way.
    smol_props = {k.lower(): v for k, v in smol["properties"].items()}

    # Separate idenfitiers from properties.
    for key in identifier_keys:
        if key in smol_props:
            identifier_dict[key] = smol_props[key]

    return identifier_dict


# endregion


# Takes any identifier and creates a minimal molecule object
# on the fly using RDKit, without relying on PubChem or API calls.
# - - -
# Note: in our molecule data structure, identifiers are all stored
# under properties. The GUI and possibly other parts of the
# application consume a slightly modified format, where identifiers
# are stored separately from properties. This is a cleaner / more
# correct way of organizing the molecule object, since identifiers
# are not properties, and they are treated differently (eg. no sort).
# But we can't change the main molecule datastructure without creating
# a formatter to ensure backwards compatibilty, so for now you can
# use molformat_v2() to convert the molecule object to the new format.
# - - -
# It is recommended to start using the new format elsewhere in new code,
# so we'll have less to refactor once we switch to the new format.
def new_smol(inchi_or_smiles: str = None, mol_rdkit: Mol = None, name: str = None):
    """
    Create a basic molecule object without relying on API calls.

    Parameters
    ----------
    inchi_or_smiles: str
        Source option A: An InChI or SMILES identifier.
    mol_rdkit: RDKit ROMol
        Source option B: An RDKit molecule object.
    name: str
        Optional name for the molecule.
    """

    smol = deepcopy(OPENAD_SMOL_DICT)
    timestamp = pretty_date()
    prop_src = {"source": "RDKit", "date": timestamp}

    # Create RDKit molecule object
    if mol_rdkit is None:
        try:
            mol_rdkit = Chem.MolFromInchi(inchi_or_smiles)
            if not mol_rdkit:
                mol_rdkit = Chem.MolFromSmiles(  # pylint: disable=no-member
                    inchi_or_smiles
                )
            if not mol_rdkit:
                mol_rdkit = Chem.MolFromInchi("InChI=1S/" + inchi_or_smiles)
            if not mol_rdkit:
                return None
        except Exception:  # pylint: disable=broad-exception-caught
            return None

    # Parse properties
    props = mol_rdkit.GetPropsAsDict()
    for key in props:
        smol["properties"][key] = props[key]
        smol["property_sources"][key] = prop_src

    # Figure out the best name
    mol_formula = Chem.rdMolDescriptors.CalcMolFormula(
        mol_rdkit
    )  # pylint: disable=c-extension-no-member
    if name is None:
        name = smol["identifiers"].get("name", mol_formula)

    # fmt: off
    # Store identifiers
    smol["identifiers"]["name"] = name
    smol["identifiers"]["inchi"] = Chem.MolToInchi(mol_rdkit) # See note below **
    smol["identifiers"]["inchikey"] = Chem.inchi.InchiToInchiKey(smol["identifiers"]["inchi"])
    smol["identifiers"]["canonical_smiles"] = Chem.MolToSmiles(mol_rdkit)  # pylint: disable=no-member
    smol["identifiers"]["isomeric_smiles"] = Chem.MolToSmiles(mol_rdkit, isomericSmiles=True)  # pylint: disable=no-member
    smol["identifiers"]["molecular_formula"] = mol_formula
    smol["properties"]["molecular_weight"] = MolWt(mol_rdkit)

    # ** Note:
    # This will print error messages to the console which we can't
    # seem to suppress using RDLogger.DisableLog("rdApp.error").
    # Error example for smiles CC(CC1=CC2=C(C=C1)OCO2)NC:
    # [14:38:48] WARNING: Omitted undefined stereo
    
    # Store property sources
    smol["property_sources"]["name"] = prop_src
    smol["property_sources"]["inchi"] = prop_src
    smol["property_sources"]["inchikey"] = prop_src
    smol["property_sources"]["canonical_smiles"] = prop_src
    smol["property_sources"]["isomeric_smiles"] = prop_src
    smol["property_sources"]["molecular_formula"] = prop_src
    smol["property_sources"]["molecular_weight"] = prop_src

    # Disabled this for consistency, because molecular_weight_exact is not included in PubChem data.
    # See: pcy.Compound.from_cid(cid).to_dict()
    # mol["properties"]["molecular_weight_exact"] = ExactMolWt(mol_rdkit)
    # mol["property_sources"]["molecular_weight_exact"] = {"source": "RDKit", "date": timestamp}
    # fmt: on

    # So the UI can recognize when a molecule has been enriched.
    smol["enriched"] = False

    return smol


def get_human_properties(smol: dict) -> dict:
    """
    Pull subset of properties from a molecule,
    ignoring all the data meant for machines.

    Used to display a molecules's properties in the CLI.

    Parameters
    ----------
    smol: dict
        The OpenAD small molecule dictionary to extract properties from.

    Returns
    -------
    dict
        The extracted properties.
    """

    props = {}
    for prop in smol["properties"]:
        if prop not in SMOL_PROPS_IGNORE:
            props[prop] = smol["properties"][prop]
    return props


def get_molset_mols(path_absolute: Path) -> dict | None:
    """
    Return the list of molecules from a molset file,
    with an index added to each molecule.

    Parameters
    ----------
    path_absolute: str
        The absolute path to the molset file.

    Returns
    -------
    molset
        The list of molecules.
    err_code
        The open_file error code if an error occurred.
    """

    # Read file contents
    if path_absolute.exists():
        with open(path_absolute, "r", encoding="utf-8") as file:
            molset = json.load(file)

        return molset

    return None


# endregion
# ------------------------------------
# region - Validation
# ------------------------------------


def valid_identifier(identifier: str, rich=False) -> bool:
    """
    Verify if a string is a valid molecule identifier.

    Parameters
    ----------
    identifier: str
        The molecule identifier to validate
    rich: bool
        If True, check PubChem
    """

    if possible_smiles(identifier) and valid_smiles(identifier):
        return True
    if valid_inchi(identifier):
        return True
    if is_numeric(identifier):
        return True

    # Check pubchem
    if rich:
        try:
            pcy.get_compounds(identifier, "name")
            return True
        except Exception:
            pass

    return False


def possible_smiles(smiles: str) -> bool:
    """
    Verify is a string *could* be a SMILES definition.

    Parameters
    ----------
    smiles: str
        The SMILES string to validate
    """
    return bool(
        re.search(
            r"[BCNOFPSI](?:[a-df-z0-9#=@+%$:\[\]\(\)\\\/\.\-])*", smiles, flags=re.I
        )
    )


def valid_smiles(smiles: str) -> bool:
    """
    Verify if a string is valid SMILES definition.

    Parameters
    ----------
    smiles: str
        The SMILES string to validate
    """

    if not smiles or not possible_smiles(smiles):
        return False

    try:
        m = Chem.MolFromSmiles(smiles, sanitize=False)  # pylint: disable=no-member
    except Exception:  # pylint: disable=broad-exception-caught
        return False

    if m is None:
        return False
    else:
        try:
            Chem.SanitizeMol(m)  # pylint: disable=no-member
        except Exception:  # pylint: disable=broad-exception-caught
            return False

    return True


def valid_inchi(inchi: str) -> bool:
    """
    Verify if a string is valid InChI definition.

    Parameters
    ----------
    inchi: str
        The InChI string to validate
    """

    try:
        m = Chem.inchi.InchiToInchiKey(inchi)
    except Exception:  # pylint: disable=broad-exception-caught
        return False

    if m is None:
        return False
    else:
        return True


# endregion
# ------------------------------------
# region - Reading / Saving
# ------------------------------------


def load_mols_from_file(file_path):
    """
    Load list of molecules from a source file.

    Supported source files:
    - molset (.molset.json)
    - SDF (.sdf)
    - CSV (.csv)
    - SMILES (.smi)
    """

    file_path = resolve_path(file_path)
    molset = None

    try:
        # Molset.json
        if file_path.endswith(".molset.json"):
            with open(file_path, "r", encoding="utf-8") as file:
                molset = file.read()
            molset = json.loads(molset) if molset else None

        # SDF
        elif file_path.endswith(".sdf"):
            molset = smol_transformers.sdf_path2molset(file_path)

        # CSV
        elif file_path.endswith(".csv"):
            molset = smol_transformers.csv_path2molset(file_path)

        # SMILES
        elif file_path.endswith(".smi"):
            molset = smol_transformers.smiles_path2molset(file_path)

        # Unsupported file type
        else:
            spf.error(
                [
                    "Unsupported file type",
                    "Accepted file extensions are: .molset.json / .sdf / .csv / .smi",
                ]
            )

    except (
        FileNotFoundError,
        PermissionError,
        IsADirectoryError,
        UnicodeDecodeError,
        IOError,
    ) as err:
        filename = file_path.split("/")[-1]
        spf.error(
            [f"Failed to load molecules from file <yellow>{filename}</yellow>", err]
        )

    # Return
    if molset:
        return molset
    else:
        return None


def save_molset_as_json(molset: list, file_path: str):
    """
    Save a molset as a molset JSON file.
    """

    # Add/fix extension if missing
    if file_path.endswith(".molset.json"):
        pass
    elif file_path.endswith(".json"):
        file_path = file_path[:-4] + "molset.json"

    # Remove any invalid extension
    elif len(file_path.split(".")) > 1 and 2 < len(file_path.split(".")[-1]) < 5:
        file_path = file_path[: -len(file_path.split(".")[-1])]

    # Write json to disk
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(molset, f, cls=JSONDecimalEncoder, indent=4)
            return True, None
    except Exception as err:  # pylint: disable=broad-except
        return False, {"error_msg": f"Error writing molset.json file: {err}"}


def save_molset_as_sdf(molset: list, path: str, remove_invalid_mols=False):
    """
    Save a molset as an SDF file.
    """
    try:
        df = smol_transformers.molset2dataframe(
            molset, remove_invalid_mols=remove_invalid_mols, include_romol=True
        )
        smol_transformers.write_dataframe2sdf(df, path)
        return True, None
    except ValueError as err:
        return False, {
            "error_msg": str(err),
            "invalid_mols": err.args[1],
        }


def save_molset_as_csv(molset: list, path: str, remove_invalid_mols=False):
    """
    Save a molset as a CSV file.
    """
    try:
        df = smol_transformers.molset2dataframe(molset, remove_invalid_mols)
        smol_transformers.write_dataframe2csv(df, path)
        return True, None
    except ValueError as err:
        return False, {
            "error_msg": str(err),
            "invalid_mols": err.args[1],
        }


def save_molset_as_smiles(molset: list, path: str, remove_invalid_mols=False):
    """
    Save a molset as a SMILES file.
    """
    # Collect SMILES.
    smiles_list = []
    missing_smiles = []
    for smol in molset:
        smiles = get_best_available_smiles(smol)
        if smiles:
            smiles_list.append(smiles)
        else:
            missing_smiles.append(smol["index"])

    # Return error if there are missing SMILES.
    if missing_smiles and not remove_invalid_mols:
        return False, {
            "error_msg": "Some molecules are missing SMILES.",
            "invalid_mols": missing_smiles,
        }

    # Write to file.
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(smiles_list))
        return True, None

    # Fail
    except Exception as err:  # pylint: disable=broad-except
        return False, {
            "error_msg": f"Error writing SMILES file: {err}",
        }


# endregion
# ------------------------------------
# region - Utility
# ------------------------------------


def flatten_smol(smol: dict) -> dict:
    """
    Flatten identifiers, properties, name and synonyms onto
    the root of the molecule dictionary, so the molecule can
    be displayed in a table.

    Parameters
    ----------
    smol: dict
        The OpenAD small molecule dictionary to flatten.

    Returns
    -------
    dict
        The flattened molecule dictionary.
    """
    if smol is None:
        return None

    smol_flat = {**smol.get("identifiers"), **smol.get("properties")}
    smol_flat["name"] = smol.get("name", None)
    smol_flat["synonyms"] = "\n".join(smol.get("synonyms", []))
    return smol_flat


def canonicalize(smiles: str) -> str | None:
    """
    Turn any SMILES into its canonical equivalent per RDKit.

    Parameters
    ----------
    smiles: str
        The SMILES string to canonicalize
    """
    if not smiles:
        return None

    return Chem.MolToSmiles(
        Chem.MolFromSmiles(smiles), isomericSmiles=True
    )  # pylint: disable=no-member


def df_has_molecules(df: pandas.DataFrame) -> bool:
    """
    Check if a dataframe has molecules.
    """

    cols_lowercase = [col.lower() for col in df.columns]
    if "smiles" in cols_lowercase:
        return True
    elif "inchi" in cols_lowercase:
        return True
    else:
        return False


def get_smol_from_list(identifier, molset, ignore_synonyms=False):
    """
    Scan a molset for a given identifier.
    Returns the molecule dict if found, otherwise None.

    Parameters
    ----------
    identifier: str
        The molecule identifier to search for.
        Valid inputs: InChI, SMILES, InChIKey, name, CID.
    molset: list
        A list of OpenAD small molecule objects.
    ignore_synonyms: bool
        If True, ignore synonyms in the search.
        This is only used when renaming a molecule to one of its synonyms.
        Without it, the search would return the original molecule and abort.

    """

    identifier = str(identifier).strip()

    for openad_mol in molset:
        identifiers_dict = openad_mol.get("identifiers")
        synonyms = openad_mol.get("synonyms", [])
        if not identifiers_dict:
            spf.error("get_smol_from_list(): Invalid molset input")
            return None

        # Name match
        if identifier.upper() == (identifiers_dict.get("name") or "").upper():
            return openad_mol

        # CID match
        if (
            is_numeric(identifier)
            and identifiers_dict.get("cid")
            and int(identifier) == int(identifiers_dict.get("cid"))
        ):
            return openad_mol

        # InChI match
        if identifier == identifiers_dict.get("inchi"):
            return openad_mol

        # InChIKey match
        if identifier == identifiers_dict.get("inchikey"):
            return openad_mol

        # SMILES match
        try:
            idfr_canonical = canonicalize(identifier)
            if idfr_canonical == canonicalize(
                identifiers_dict.get("canonical_smiles", None)
            ):
                return openad_mol
            elif idfr_canonical == canonicalize(
                identifiers_dict.get("isomeric_smiles", None)
            ):
                return openad_mol
            elif idfr_canonical == canonicalize(identifiers_dict.get("smiles", None)):
                return openad_mol
        except Exception:  # pylint: disable=broad-except
            pass

        # Synonym match
        if not ignore_synonyms:
            for syn in synonyms:
                if identifier.upper() == syn.upper():
                    return openad_mol

    # Fail
    return None


def get_best_available_identifier(smol: dict) -> tuple:
    """
    Get whatever identifier is available from a molecule.

    Parameters
    ----------
    smol: dict
        The OpenAD small molecule dictionary.

    Returns
    -------
    tuple
        The identifier type and the identifier string.
    """

    identifiers_dict = smol.get("identifiers", {})
    if not identifiers_dict:
        return None, None

    # InChIKey
    inchikey = identifiers_dict.get("inchikey")
    if inchikey:
        return "inchikey", inchikey

    # Canonical SMILES
    canonical_smiles = identifiers_dict.get("canonical_smiles")
    if canonical_smiles:
        return "canonical_smiles", canonical_smiles

    # InChI
    inchi = identifiers_dict.get("inchi")
    if inchi:
        return "inchi", inchi

    # Isomeric SMILES
    isomeric_smiles = identifiers_dict.get("isomeric_smiles")
    if isomeric_smiles:
        return "isomeric_smiles", isomeric_smiles

    # SMILES
    smiles = identifiers_dict.get("smiles")
    if smiles:
        return "smiles", smiles

    # Name
    name = identifiers_dict.get("name")
    if name:
        return "name", name

    # CID
    cid = identifiers_dict.get("cid")
    if cid:
        return "cid", cid

    # Fail
    return None, None


def get_best_available_smiles(smol: dict) -> str | None:
    """
    Get the best available SMILES string from a molecule.

    Parameters
    ----------
    smol: dict
        The OpenAD small molecule dictionary.

    Returns
    -------
    str
        The best available SMILES string.
    """

    identifiers_dict = smol.get("identifiers")

    # Canonical SMILES
    canonical_smiles = identifiers_dict.get("canonical_smiles")
    if canonical_smiles:
        return canonical_smiles

    # Isomeric SMILES
    isomeric_smiles = identifiers_dict.get("isomeric_smiles")
    if isomeric_smiles:
        return isomeric_smiles

    # SMILES
    smiles = identifiers_dict.get("smiles")
    if smiles:
        return smiles

    # Fail
    return None


def normalize_mol_df(mol_df: pandas.DataFrame, batch: bool = False) -> pandas.DataFrame:
    """
    Normalize the column names of a molecule dataframe
    """

    has_name = False
    contains_name = None

    for col in mol_df.columns:
        # Find the name column.
        if str(col.upper()) == "NAME" or str(col.lower()) == "chemical_name":
            has_name = True
        if contains_name is None and "NAME" in str(col.upper()):
            contains_name = col
        if contains_name is None and "CHEMICAL_NAME" in str(col.upper()):
            contains_name = col

        # Normalize any columns we'll be referring to later.
        if str(col.upper()) == "SMILES":
            mol_df.rename(columns={col: "SMILES"}, inplace=True)
        if str(col.upper()) == "ROMOL":
            mol_df.rename(columns={col: "ROMol"}, inplace=True)
        if str(col.upper()) == "IMG":
            mol_df.rename(columns={col: "IMG"}, inplace=True)
        if col in INPUT_MAPPINGS:
            mol_df.rename(columns={col: INPUT_MAPPINGS[col]}, inplace=True)

    # Normalize name column.
    if has_name is False and contains_name is not None:
        mol_df.rename(columns={contains_name: "NAME"}, inplace=True)

    # Add names when missing.
    try:
        if has_name is False:
            spf.warning("No name column identifed in data set")

            if not batch:
                spinner.start("Downloading names")

            mol_df["NAME"] = "unknown"
            for col in mol_df.itertuples():
                mol_df.loc[col.Index, "NAME"] = _smiles_to_iupac(
                    mol_df.loc[col.Index, "SMILES"]
                )

            if not batch:
                spinner.succeed("Names downloaded")
                spinner.start()
                spinner.stop()

    except Exception as err:  # pylint: disable=broad-exception-caught
        spinner.fail("There was an issue loading the molecule names.")
        spinner.start()
        spinner.stop()
        print(err)

    return mol_df


def _smiles_to_iupac(smiles):
    """
    Get the official IUPAC(*) name of a molecules based on its SMILES.

    (*) International Union of Pure and Applied Chemistry
    """

    if smiles in mol_name_cache:
        return mol_name_cache[smiles]
    try:
        compounds = pcy.get_compounds(smiles, namespace="smiles")
        match = compounds[0]
        mol_name_cache[smiles] = str(match)
    except Exception:  # pylint: disable=broad-exception-caught
        match = smiles
    return str(match)


def get_smol_name(smol: dict) -> str:
    """
    Get the best available name for a molecule.

    Parameters
    ----------
    smol: dict
        The small molecule dictionary.

    Returns
    -------
    str
        The best available name.
    """

    identifiers_dict = smol.get("identifiers", {})

    # Name
    name = identifiers_dict.get("name")
    if name:
        return name

    # Synonyms
    synonyms = smol.get("synonyms", [])
    if synonyms and len(synonyms) > 0:
        return synonyms[0]

    # InChIKey
    inchikey = identifiers_dict.get("inchikey")
    if inchikey:
        return inchikey

    # SMILES
    smiles = get_best_available_smiles(smol)
    if smiles:
        return smiles

    # InChI
    inchi = identifiers_dict.get("inchi")
    if inchi:
        return inchi

    # Fail
    return "Unknown"


def random_smiles(count: int = 10, max_cid=150_000_000):
    """
    Fetch a specified number of random molecule SMILES.

    Args:
        count (int): Number of SMILES to fetch

    Returns:
        list: List of strings
    """
    results = []
    retries = 0
    max_retries = 20
    i = 1
    while len(results) < count and retries < max_retries:
        cid, smiles = _fetch_random_compound(max_cid, i)
        if cid and smiles:
            results.append(smiles)
            i += 1
            retries = 0
        else:
            retries += 1
    return results


def _fetch_random_compound(max_cid, i, max_retries=20, debug=True):
    """
    Fetch a random molecule's CID and Canonical SMILES from PubChem.

    Args:
        max_cid (int): The upper limit for random CID generation. PubChem CIDs go
                       into the hundreds of millions.
        max_retries (int): Maximum attempts to find an existing compound.

    Returns:
        tuple: (cid, smiles) if successful, otherwise (None, None).
    """
    pubchem_api_base = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid"
    headers = {"Accept": "text/plain"}  # Request plain text for SMILES

    for attempt in range(max_retries):
        random_cid = random.randint(1, max_cid)
        url = f"{pubchem_api_base}/{random_cid}/property/CanonicalSMILES/TXT"
        icon = "❌" if attempt + 1 == max_retries else "🔄"

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            smiles = response.text.strip()
            if smiles:
                if debug:
                    print(
                        f"✅ #{i} Attempt {attempt + 1}/{max_retries}: {random_cid:>10} --> SMILES: {smiles}"
                    )
                return random_cid, smiles
            else:
                if debug:
                    print(
                        f"{icon} Attempt {attempt + 1}/{max_retries}: {random_cid:>10} --> no result"
                    )

        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 404:
                if debug:
                    print(
                        f"{icon} Attempt {attempt + 1}/{max_retries}: {random_cid:>10} --> not found"
                    )
            else:
                if debug:
                    print(
                        f"{icon} Attempt {attempt + 1}/{max_retries}: {random_cid:>10} --> HTTP error"
                    )
        except requests.exceptions.ConnectionError:
            if debug:
                print(
                    f"{icon} Attempt {attempt + 1}/{max_retries}: {random_cid:>10} --> connection error"
                )
        except requests.exceptions.Timeout:
            if debug:
                print(
                    f"{icon} Attempt {attempt + 1}/{max_retries}: {random_cid:>10} --> timeout error"
                )
        except requests.exceptions.RequestException as err:
            if debug:
                print(
                    f"{icon} Attempt {attempt + 1}/{max_retries}: {random_cid:>10} --> unexpected error"
                )
            if debug:
                print(f"ℹ️ Error details: {err}")

        # PubChem API advises max 5 requests per second
        time.sleep(0.2)

    if debug:
        print(f"Failed to find a random molecule after {max_retries} attempts.")
    return None, None


# endregion
# ------------------------------------
# region - GUI operations
# ------------------------------------


def assemble_cache_path(file_type: str, cache_id: str) -> str:
    """
    Compile the file path to a cached working copy of a file.

    Parameters
    ----------
    file_type: 'molset'
        The type of file, used to name the cache file. For now only molset.
    cache_id: str
        The cache ID of the file.
    """

    workspace_path = ctx().workspace_path()
    return workspace_path / "._system" / "wc_cache " / f"{file_type}-{cache_id}.json"


def create_molset_cache_file(molset: dict = None, path_absolute: Path = None) -> str:
    """
    Store molset as a cached file so we can manipulate it in the GUI,
    return its cache_id so we can reference it later.

    Parameters
    ----------
    molset: dict
        The molset to cache.
    path_absolute: Path
        The absolute path to the molset file, if it exists.

    Returns
    -------
    str
        The cache ID of the molset file.
    """

    cache_id = str(int(time.time() * 1000))
    cache_path = assemble_cache_path("molset", cache_id)

    # Creaste the /._openad/wc_cache directory if it doesn't exist.
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    # For JSON files, we can simply copy the original file (fast).
    if path_absolute:
        # timeit("copy_file")
        shutil.copy(path_absolute, cache_path)
        # timeit("copy_file", True)

        # Add indices to molecules in our working copy,
        # without blocking the thread.
        # timeit("index_wc")
        # index_molset_file_async(cache_path) # %%%
        # timeit("index_wc", True)

    # For all other cases, i.e. other file formats or molset data from memory,
    # we need to write the molset object to disk (slow).
    else:
        # timeit("write_cache")
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(molset, f)
        # timeit("write_cache", True)

    return cache_id


def read_molset_from_cache(cache_id: str) -> dict:
    """
    Read a cached molset file from disk.

    Parameters
    ----------
    cache_id: str
        The cache ID of the molset file.

    Returns
    -------
    dict
        The molset object.
    """

    # Read file from cache.
    cache_path = assemble_cache_path("molset", cache_id)
    molset = get_molset_mols(cache_path)

    # Return error
    if not molset:
        raise ValueError(f"Failed to read molset {cache_id} from cache")
    else:
        return molset


# endregion
# ------------------------------------
# region - Molecule working set
# ------------------------------------


def merge_smols(smol: dict, merge_smol: dict) -> dict:
    """
    Merge two molecule dictionaries into one.

    The 2nd molecule's values will get priority over the 1st,
    while preventing None values from overwriting existing ones.
    """

    for key, val in merge_smol.items():
        # Merge identifiers
        if key == "identifiers" and isinstance(val, dict):
            for idfr_key, idfr_val in val.items():
                # Skip if None
                if idfr_val is None:
                    continue
                else:
                    smol[key][idfr_key] = idfr_val

        # Merge synonyms - without duplicates regardless of case
        elif key == "synonyms" and isinstance(val, list):
            # A maps for each molecule's synonyms, linking the lowercase to the original case.
            og_case_map_1 = {item.lower(): item for item in smol[key]}
            og_case_map_2 = {item.lower(): item for item in merge_smol[key]}

            # Merge the synonyms in a case-insensitive way (skip new synonyms if they are just differently cased)
            case_insensitive_merge = list(
                set(
                    list(map(str.lower, smol[key]))
                    + list(map(str.lower, merge_smol[key]))
                )
            )

            # Loop through the case-insensitive merge list and add the original
            # case synonyms to the new molecule, prioritizing the first molecule's
            # synonyms when there's a case-insensitive match.
            output = []
            for i, syn in enumerate(case_insensitive_merge):
                if syn in og_case_map_1:
                    output.append(og_case_map_1[syn])
                elif syn in og_case_map_2:
                    output.append(og_case_map_2[syn])

            smol[key] = output

        # Merge properties & property sources
        elif key == "properties" and isinstance(val, dict):
            for prop_key, prop_val in val.items():
                # Skip if None
                if prop_val is None:
                    continue

                # Set property and property source
                else:
                    smol[key][prop_key] = prop_val
                    source = merge_smol["property_sources"].get(prop_key) or {
                        "source": "merge",
                        "date": pretty_date(),
                    }
                    smol["property_sources"][prop_key] = source

        # Merge analysis results - without duplcates
        elif key == "analysis" and isinstance(val, list):
            smol[key] = merge_dict_lists(smol[key], merge_smol[key])

        # Merge meta information
        elif key == "meta" and isinstance(val, dict):
            # import json
            # print(888, json.dumps(smol))

            # Merge notes with a separator string
            notes_1 = smol.get(key, {}).get("notes")
            notes_2 = merge_smol.get(key, {}).get("notes")
            if notes_1 and notes_2:
                smol[key]["notes"] = "\n\n- - -\n\n".join([notes_1, notes_2])
            else:
                smol[key]["notes"] = notes_1 or notes_2

            # Merge labels without duplicates and ensure they're all lowercase
            smol[key]["labels"] = list(
                set(
                    list(map(str.lower, smol[key].get("labels", [])))
                    + list(map(str.lower, merge_smol[key].get("labels", [])))
                )
            )

        # Merge enriched flag - only merge when True
        elif key == "enriched" and isinstance(val, bool):
            if val is True:
                smol[key] = val

        # - - -

        # Brute fallback for any future parameters we may have forgotten to add.

        # Dictionaries: merge
        elif key not in ["property_sources"] and isinstance(val, dict):
            if key in smol:
                smol[key].update(val)
            else:
                smol[key] = val

        # Lists: extend
        elif isinstance(val, list):
            if key in smol:
                # Temporary fix for synonyms, which are stored in a nested list in v1 dict.
                if key == "synonyms" and "Synonym" in smol[key]:
                    smol[key]["Synonym"].extend(val)
                else:
                    smol[key].extend(val)
            else:
                smol[key] = val

        # Booleans: only merge when True
        elif isinstance(val, bool):
            if val is True:
                smol[key] = val

        # Strings and numbers: overwrite
        elif isinstance(val, str) or isinstance(val, int):
            smol[key] = val

    # Return
    return smol


# @@TODO: merge function with merge_mols
def merge_molecule_properties(molecule_dict: dict, smol: dict):
    """
    Merge a dictionary with properties into a molecule's properties.

    Parameters
    ----------
    molecule_dict: dict
        The dictionary with properties to merge.
    smol: dict
        The OpenAD small molecule dictionary into which we merge the properties.
    """

    if smol is None:
        return None
    if "ROMol" in molecule_dict:
        del molecule_dict["ROMol"]
    if "subject" in molecule_dict:
        del molecule_dict["subject"]

    for key in molecule_dict:
        smol["properties"][key] = molecule_dict[key]
        smol["property_sources"][key] = {"source": "unknown", "date": pretty_date()}
        if key not in SMOL_PROPERTIES:
            SMOL_PROPERTIES.append(key)

    return smol


# @@TODO: merge function with merge_mols
def merge_molecule_REPLACE(merge_mol, mol):
    """merges a molecules property with those from a dictionary"""
    if mol is None:
        return None

    for key in merge_mol["properties"]:
        if key not in mol["properties"]:
            mol["properties"][key] = merge_mol["properties"][key]
            mol["property_sources"][key] = merge_mol["properties"][key]
        elif mol["properties"][key] is None:
            mol["properties"][key] = merge_mol["properties"][key]
            mol["property_sources"][key] = merge_mol["properties"][key]

    for x in merge_mol["analysis"]:
        if x not in mol["anaylsis"]:
            mol["anaylsis"].append()


def load_mols_to_mws(inp):
    """
    Load a batch of molecules into the molecule working set.
    """
    # Prevent circular import
    from omgui.gui.gui_services import srv_mws

    molset = None
    df_name = inp.as_dict().get("in_dataframe", None)
    file_path = inp.as_dict().get("moles_file", None)

    # Load from dataframe
    if df_name:
        df = ctx().vars.get(df_name)
        molset = smol_transformers.dataframe2molset(df)
        # molset = normalize_mol_df(ctx().vars.get(inp.as_dict().get("in_dataframe")), batch=True)
        if molset is None:
            return spf.error("The provided dataframe does not contain molecules")

    # Load from file
    elif file_path:
        molset = load_mols_from_file(file_path)
        if molset is None:
            return

    # Add PubChem data
    if "enrich_pubchem" in inp.as_dict():
        _enrich_with_pubchem_data(molset)

    # Clear mws unless append is passed
    if "append" not in inp:
        mws_core().clear()

    added_count = 0
    failed_count = 0
    for smol in molset:
        success = srv_mws.add_mol(smol=smol, silent=True)
        if success:
            added_count += 1
        else:
            failed_count += 1

    # Todo: `load mols using file` should add instead of overwrite your current mols,
    # when this is implemented, we'll need to calculate successfully loaded mols differently.
    if added_count > 0:
        spf.success(
            f"Successfully loaded <yellow>{added_count}</yellow> molecules into the working set"
        )
        if failed_count > 0:
            spf.error(f"Ignored <yellow>{failed_count}</yellow> duplicates")
    else:
        spf.error(
            f"No new molecules were added, all {failed_count} provided molecules were are already present in the working set"
        )
    return


def _enrich_with_pubchem_data(molset):
    """
    Pull data from PubChem to merge in into a molset.
    """

    output_molset = []

    spinner.start("Fetching from PubChem")

    for i, smol in enumerate(molset):
        try:
            identifiers = smol["identifiers"]

            # Get name field regardless of case
            name = next(
                (value for key, value in identifiers.items() if key.lower() == "name"),
                None,
            )
            spinner.text = spf.produce(
                f"<soft>Fetching from PubChem: #{i} - {name}</soft>"
            )

            # Use fallback name is missing
            if not name:
                name = smol.get("chemical_name", None)

            # Select the identifier keys we'll look for in order of preference
            keys = [
                "inchi",
                "canonical_smiles",
                "isomeric_smiles",
                "smiles",
                "inchikey",
                "name",
                "cid",
            ]
            identifier = next(
                (
                    identifiers.get(key)
                    for key in keys
                    if identifiers.get(key) is not None
                ),
                None,
            )
            name = name or identifier or "Unknown molecule"
            if not identifier:
                spf.warning(f"#{i} - No valid identifier found for {name}")
                continue

            # Fetch enriched molecule
            smol_enriched = get_smol_from_pubchem(identifier)
            if not smol_enriched:
                spf.warning(f"#{i} - Failed to enrich {name}")

            # Merge enriched data
            smol = merge_smols(smol, smol_enriched)
            output_molset.append(smol)

        except Exception as err:  # pylint: disable=broad-except
            spinner.stop()
            spf.error(
                [
                    "Something went wrong enriching molecules with data from PubChem",
                    err,
                ]
            )

    spinner.succeed("Done")
    spinner.stop()
    return output_molset


def merge_molecule_property_data(inp=None, dataframe=None):
    """
    Merge data from a dataframe into your molecule working set.

    The dataframe should contain the following columns:
      - SMILES/subject
      - property
      - value

    The property values will then be added to each molecule's properties.
    """
    # Prevent circular import
    from omgui.gui.gui_services import srv_mws

    if dataframe is None and inp is None:
        return False

    if dataframe is None:
        # Load from dataframe
        if (
            "merge_molecules_data_dataframe" in inp.as_dict()
            or "merge_molecules_data_dataframe-DEPRECATED"  # Can be removed once the deprecated syntax has been removed
            in inp.as_dict()
        ):
            dataframe = ctx().vars.get(inp.as_dict().get("in_dataframe"))

        # Load from file (not yet implemented)
        else:
            dataframe = _load_mol_data(inp.as_dict()["moles_file"])

        if dataframe is None:
            spf.error("Source not found ")
            return True

    # Detect the SMILES/subject column
    if "subject" in dataframe.columns:
        smiles_key = "subject"
    elif "smiles" in dataframe.columns:
        smiles_key = "smiles"
    elif "SMILES" in dataframe.columns:
        smiles_key = "SMILES"
    else:
        spf.error(
            "No <yellow>subject</yellow> or <yellow>SMILES</yellow> column found in merge data"
        )
        return True

    # Detect the property column
    if "property" in dataframe.columns:
        prop_key = "property"
    elif "PROPERTY" in dataframe.columns:
        prop_key = "PROPERTY"
    else:
        spf.error("No <yellow>property</yellow> column found in merge data")
        return True

    # Detect the value column
    if "value" in dataframe.columns:
        val_key = "value"
    elif "VALUE" in dataframe.columns:
        val_key = "VALUE"
    elif "result" in dataframe.columns:
        val_key = "result"
    elif "RESULT" in dataframe.columns:
        val_key = "RESULT"
    else:
        spf.error("No <yellow>result</yellow> or <yellow>value</yellow> column found")
        return True

    # Pivot the dataframe
    dataframe = dataframe.pivot_table(
        index=smiles_key, columns=[prop_key], values=val_key, aggfunc="first"
    )
    dataframe = dataframe.reset_index()

    for row in dataframe.to_dict("records"):
        update_flag = True
        merge_smol = None

        try:
            smiles = canonicalize(row[smiles_key])
            merge_smol = get_smol_from_mws(smiles)
            # GLOBAL_SETTINGS["grammar_refresh"] = True # TODO: replace with callback
        except Exception:  # pylint: disable=broad-except
            spf.warning("unable to canonicalise:" + row[smiles_key])
            continue

        if merge_smol is None:
            merge_smol = new_smol(smiles, name=row[smiles_key])
            update_flag = False
        else:
            update_flag = True

        if merge_smol is not None:
            smol = merge_molecule_properties(row, merge_smol)
            # GLOBAL_SETTINGS["grammar_refresh"] = True # TODO: replace with callback
            if update_flag is True:
                srv_mws.remove_mol(smol=merge_smol, silent=True)
            mws_core().add(smol)

    spf.success("Data merged into your working set")
    # GLOBAL_SETTINGS["grammar_refresh"] = True # TODO: replace with callback
    return True


def _load_mol_data(file_path):
    """loads molecule data from a file where Smiles, property and values are supplied in row format"""

    file_path = resolve_path(file_path)

    # SDF
    if file_path.split(".")[-1].lower() == "sdf":
        try:
            name = file_path.split("/")[-1]
            sdf_file = ctx().workspace_path() / name
            mol_frame = Chem.PandasTools.LoadSDF(sdf_file)
            return mol_frame
        except Exception as err:  # pylint: disable=broad-except
            spf.error([f"Unable to load SDF file", err])
            return None

    # CSV
    elif file_path.split(".")[-1].lower() == "csv":
        try:
            name = file_path.split("/")[-1]
            csv_file = ctx().workspace_path() / name
            mol_frame = pandas.read_csv(csv_file, dtype="string")
            return mol_frame
        except Exception as err:
            spf.error([f"Unable to load CSV file", err])
            return None


# endregion
# ------------------------------------
# region - Unused
# ------------------------------------


# Unused. This adds an indice when it's missing, but there's no usecase
# other than dev-legacy example molsets that are missing an index.
def index_molset_file_async(path_absolute):
    """
    Add an index to each molecule of a molset file,
    without blocking the main thread.

    This is used to index a cached working copy of a molset
    right after it's created.

    Parameters
    ----------
    cache_path: str
        The path to the cached working copy of a molset.
    """

    async def _index_molset_file(cache_path):
        # Read
        async with aiofiles.open(cache_path, "r", encoding="utf-8") as f:
            content = await f.read()
        molset = json.loads(content)
        for i, mol in enumerate(molset):
            mol["index"] = i + 1
            molset[i] = mol
        # Write
        async with aiofiles.open(cache_path, "w", encoding="utf-8") as f:
            await f.write(
                json.dumps(molset, ensure_ascii=False, indent=4, cls=JSONDecimalEncoder)
            )

    asyncio.run(_index_molset_file(path_absolute))


# endregion
# ------------------------------------
