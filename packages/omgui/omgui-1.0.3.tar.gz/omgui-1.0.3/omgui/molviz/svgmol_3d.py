"""
SVG rendering function for 3D molecular structures.
"""

# Std
import re
import time
from random import randint

# 3rd party
from rdkit import Chem
from rdkit.Chem import AllChem
from cinemol.api import Atom, Bond, Look, Style, draw_molecule

# OMGUI
from omgui.molviz import types as t
from omgui.molviz import defaults as d
from omgui.util.logger import get_logger
from omgui.molviz.molviz_util import handle_invalid_width_height

# Logger
logger = get_logger()


def render(
    # fmt: off
    smiles: str,
    width: int = d.WIDTH,
    height: int = d.HEIGHT,
    highlight: str | None = None,
    # 3D specific options
    style: t.D3StyleType = d.D3_STYLE,
    look: t.D3LookType = d.D3_LOOK,
    rot_random: bool = d.D3_ROT_RANDOM,
    rot_x: float | None = None,
    rot_y: float | None = None,
    rot_z: float | None = None,
    # fmt: on
) -> str:
    """
    Render 3D molecule from SMILES string to SVG format.

    Args:
        smiles (str): The SMILES string of the molecule
        width (int): Width of the rendered image in pixels
        height (int): Height of the rendered image in pixels
        substructure (str): Optional SMARTS substructure to highlight in the molecule

    Returns:
        str: 3D SVG representation of the molecule
    """
    try:
        if not smiles:
            raise ValueError("Please provide valid SMILES")

        # Handle negative and zero width/height
        width, height = handle_invalid_width_height(width, height)

        # Create RDKit molecule
        mol = Chem.MolFromSmiles(smiles)

        # Get coordinates for 3D rendering
        conformer = _get_conformer(mol)
        pos = conformer.GetPositions()

        # Parse atoms and bonds from molecule
        atoms, bonds = [], []

        # Set substructure colors
        atom_colors = {}

        # Highlight substructure if provided
        if highlight:
            for atom_index in find_substructure(mol, highlight):
                atom_colors[atom_index] = (230, 25, 75)

        base_color = (220, 220, 220)  # _random_pastel_color()
        for atom in mol.GetAtoms():
            color = atom_colors.get(atom.GetIdx(), base_color)
            atoms.append(
                Atom(atom.GetIdx(), atom.GetSymbol(), pos[atom.GetIdx()], color=color)
            )

        for bond in mol.GetBonds():
            start_index, end_index = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
            bonds.append(Bond(start_index, end_index, int(bond.GetBondTypeAsDouble())))

        t0 = time.time()

        # Set rotation angles
        rot_x = rot_x if rot_x is not None else randint(0, 360) if rot_random else 0
        rot_y = rot_y if rot_y is not None else randint(0, 360) if rot_random else 0
        rot_z = rot_z if rot_z is not None else randint(0, 360) if rot_random else 0

        # Draw molecule.
        svg = draw_molecule(
            atoms=atoms,
            bonds=bonds,
            style=_parse_style(style),
            look=_parse_look(look),
            resolution=50,
            # Not obvious: rotation is in increments of 60°, so 6 = 360°
            rotation_over_y_axis=rot_x / 60,
            rotation_over_x_axis=rot_y / 60,
            rotation_over_z_axis=rot_z / 60,
            # view_box=(0, -0, 2000, 2000),  # (x, y, width, height)
            scale=50,
        )

        # Success
        svg_str = svg.to_svg()

        # Add width & height
        regex_pattern = r'(<svg[^>]*?viewBox="[^"]*?")'
        replacement_string = rf'\1 width="{width}" height="{height}">'
        svg_str = re.sub(regex_pattern, replacement_string, svg_str)

        # Report
        svg_size = len(svg.to_svg()) / 1000
        logger.debug("Runtime: %s ms", 1000 * (time.time() - t0))
        logger.debug("File size: %s kb", svg_size)

        return svg_str

    except Exception as err:
        logger.error("Error generating 3D SVG for '%s': %s", smiles, err)
        return None


def _get_conformer(mol: Chem.Mol) -> Chem.Conformer:
    """
    Generate the molecule's conformer.
    """
    AllChem.EmbedMolecule(mol, useRandomCoords=True, randomSeed=0xF00D)
    AllChem.MMFFOptimizeMolecule(mol)
    return mol.GetConformer()


def _random_pastel_color() -> tuple[int, int, int]:
    """
    Generate a random pastel color.
    """
    r = randint(200, 215)
    g = randint(200, 215)
    b = randint(200, 215)
    return (r, g, b)


def _parse_style(style_string: str) -> Style:
    """
    Convert string style parameter to Style enum
    """
    try:
        return Style[style_string]
    except KeyError:
        return Style.BALL_AND_STICK


def _parse_look(look_string: str) -> Look:
    """
    Convert string look parameter to Look enum
    """
    try:
        return Look[look_string]
    except KeyError:
        return Look.CARTOON


def find_substructure(mol: Chem.Mol, smarts: str) -> list[int]:
    """
    Find a substructure in a molecule.

    Args:
        mol (Chem.Mol): Molecule to find a substructure in.
        smarts (str): SMARTS string to use for substructure search.

    Returns:
        List of atom indices that match the substructure.
    """
    substructure = Chem.MolFromSmarts(smarts)
    matches = mol.GetSubstructMatches(substructure)
    return [atom_index for match in matches for atom_index in match]
