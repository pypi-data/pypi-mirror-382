"""
Molecule-related API routes.
"""

# Std
from io import BytesIO
from typing import Literal

# FastAPI
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException, Query
from fastapi.responses import Response, HTMLResponse
from fastapi import APIRouter, Request

# 3rd party
try:
    from cairosvg import svg2png
except ImportError:
    pass

# OMGUI
from omgui import config
from omgui.util.logger import get_logger
from omgui.util import exceptions as omg_exc
from omgui.molviz import svgmol_2d, svgmol_3d
from omgui.molviz import types as t, defaults as d


# Setup
# ------------------------------------

# Router
molviz_router = APIRouter()

# Set up templates and static files
templates = Jinja2Templates(directory="omgui/molviz/templates")

# Logger
logger = get_logger()


# ------------------------------------
# region - Auxiliary Functions
# ------------------------------------


# endregion
# ------------------------------------
# region - Routes
# ------------------------------------


@molviz_router.get(
    "",
    response_class=HTMLResponse,
    summary="Interactive demo UI for the molecules API",
)
def demo_molecules(request: Request):
    """
    Interactive HTML demo page for the Molecule Visualization API.
    Provides a user interface with controls for all API parameters.
    """
    if not config._viz_deps:
        raise omg_exc.MissingDependenciesViz
    return templates.TemplateResponse("demo-molecules.html", {"request": request})


@molviz_router.get("/{smiles}", summary="Visualize any molecule from a SMILES string")
def visualize_molecule(
    # fmt: off
    # Input
    smiles: str,

    # Options
    output: t.OutputType = Query(d.OUTPUT, description="The output format: 'png' or 'svg'."),
    width: int = Query(d.WIDTH, description="The width of the image in pixels."),
    height: int = Query(d.HEIGHT, description="The height of the image in pixels."),
    highlight: str = Query(None, description="A substructure to highlight, as a SMARTS string."),

    # 3D options
    d3: bool = Query(False, description="Render in 3D if True, otherwise render in 2D."),
    d3_style: t.D3StyleType = Query(d.D3_STYLE, description="The 3D rendering style."),
    d3_look: t.D3LookType = Query(d.D3_LOOK, description="The 3D rendering look."),
    d3_rot_random: bool = Query(True, description="Whether to apply random rotation."),
    d3_rot_x: float | None = Query(None, description="The rotation angle around the X axis."),
    d3_rot_y: float | None = Query(None, description="The rotation angle around the Y axis."),
    d3_rot_z: float | None = Query(None, description="The rotation angle around the Z axis."),
    # fmt: on
):
    """
    Render an image of a small molecule from a SMILES string provided as query parameter.

    Examples:
    http://localhost:8034/?smiles=C1=CC=CC=C1
    """
    if not config._viz_deps:
        raise omg_exc.MissingDependenciesViz

    output = "svg" if output not in ["png", "svg"] else output

    # Render molecule SVG
    if d3 is True:
        svg_str = svgmol_3d.render(
            smiles,
            width=width,
            height=height,
            highlight=highlight,
            #
            style=d3_style,
            look=d3_look,
            rot_random=d3_rot_random,
            rot_x=d3_rot_x,
            rot_y=d3_rot_y,
            rot_z=d3_rot_z,
        )
    else:
        svg_str = svgmol_2d.render(
            smiles,
            width=width,
            height=height,
            highlight=highlight,
        )

    # Fail
    if svg_str is None:
        logger.info("ERROR generating SVG for SMILES: %s", smiles)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid SMILES string, unable to generate SVG: {smiles}",
        )

    # Return as PNG
    if output == "png":
        png_data = BytesIO()
        svg2png(bytestring=svg_str.encode("utf-8"), write_to=png_data)
        png_data.seek(0)  # Rewind to the beginning of the BytesIO object

        logger.info("Success generating PNG for SMILES: <yellow>%s</yellow>", smiles)
        return Response(
            content=png_data.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": f'inline; filename="{smiles}.png"'},
        )

    # Return as SVG
    logger.info("Success generating SVG for SMILES: <yellow>%s</yellow>", smiles)
    return Response(
        content=svg_str,
        media_type="image/svg+xml",
        headers={"Content-Disposition": f'inline; filename="{smiles}.svg"'},
    )


# endregion
# ------------------------------------
