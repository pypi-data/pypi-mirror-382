"""
SVG rendering function for 2D molecular structures.
"""

# 3rd party
from rdkit import Chem
from rdkit import RDLogger
from rdkit.Chem.Draw import rdMolDraw2D


# OMGUI
from omgui.molviz import defaults as d
from omgui.util.logger import get_logger
from omgui.molviz.molviz_util import handle_invalid_width_height

# Suppress RDKit errors
RDLogger.DisableLog("rdApp.error")
RDLogger.DisableLog("rdApp.warning")

# Logger
logger = get_logger()


def render(
    smiles: str,
    width: int = d.WIDTH,
    height: int = d.HEIGHT,
    highlight: str | None = None,
) -> str:
    """
    Render a 2D molecule from SMILES string to SVG format.

    Args:
        smiles (str): The SMILES string of the molecule (InChI also accepted)
        highlight (str, optional): A SMARTS pattern to highlight specific substructures

    Returns:
        str: SVG representation of the molecule
    """
    try:
        if not smiles:
            raise ValueError("Please provide valid SMILES")

        # Handle negative and zero width/height
        width, height = handle_invalid_width_height(width, height)

        # Generate RDKit molecule object.
        mol_rdkit = Chem.MolFromInchi(smiles)
        mol_rdkit = Chem.MolFromSmiles(smiles)  # pylint: disable=no-member
        if not mol_rdkit:
            mol_rdkit = Chem.MolFromInchi(smiles)

        if highlight:
            substructure = Chem.MolFromSmarts(highlight)  # pylint: disable=no-member
            matches = mol_rdkit.GetSubstructMatches(substructure)

            # Flatten the tuple of tuples into a list of atom indices
            highlight_atoms = [atom_index for match in matches for atom_index in match]
        else:
            highlight_atoms = None

        mol_drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
        mol_drawer.DrawMolecule(mol_rdkit, highlightAtoms=highlight_atoms)
        mol_drawer.FinishDrawing()
        return mol_drawer.GetDrawingText()

    except Exception as err:
        logger.error("Error generating 2D SVG for '%s': %s", smiles, err)
        return None
