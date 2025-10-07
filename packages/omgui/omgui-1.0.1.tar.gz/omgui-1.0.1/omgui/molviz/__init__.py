from dataclasses import dataclass
from omgui.molviz import types as t
from omgui.molviz import defaults as d
from omgui.molviz.molviz_util import handle_invalid_width_height


@dataclass
class RenderParams:
    """Parameters for molecule rendering."""

    smiles: str
    output: t.OutputType = d.OUTPUT
    width: int = d.WIDTH
    height: int = d.HEIGHT
    highlight: str | None = None
    return_data: bool = False


@dataclass
class D3Params:
    """Additional parameters for 3D rendering."""

    d3_style: t.D3StyleType = d.D3_STYLE
    d3_look: t.D3LookType = d.D3_LOOK
    d3_rot_random: bool = d.D3_ROT_RANDOM
    d3_rot_x: float | None = None
    d3_rot_y: float | None = None
    d3_rot_z: float | None = None


# ------------------------------------
# region - Public API
# ------------------------------------


def d2(
    smiles: str,
    #
    output: t.OutputType = d.OUTPUT,
    width: int = d.WIDTH,
    height: int = d.HEIGHT,
    highlight: str | None = None,
    #
    return_data: bool = False,
) -> bytes | str | None:
    """
    Generate a 2D molecule visualization.

    Args:
        smiles         (str):                   The SMILES string of the molecule to visualize.

        output         (OutputType, optional):  The output format: 'png', 'svg' or 'url'.
        width          (int, optional):         The width of the image in pixels.
        height         (int, optional):         The height of the image in pixels.
        highlight      (str, optional):         A substructure to highlight, as a SMARTS string.

        return_data    (bool, optional):   Whether to return raw data (True) or display svg/png (False) in Jupyter Notebook.
    """
    params = RenderParams(
        smiles=smiles,
        output=output,
        width=width,
        height=height,
        highlight=highlight,
        return_data=return_data,
    )
    return _render(params)


def d3(
    smiles: str,
    # Shared 2D & 3D parameters
    output: t.OutputType = d.OUTPUT,
    width: int = d.WIDTH,
    height: int = d.HEIGHT,
    highlight: str | None = None,
    # 3D parameters
    d3_style: t.D3StyleType = d.D3_STYLE,
    d3_look: t.D3LookType = d.D3_LOOK,
    d3_rot_random: bool = d.D3_ROT_RANDOM,
    d3_rot_x: float | None = None,
    d3_rot_y: float | None = None,
    d3_rot_z: float | None = None,
    #
    return_data: bool = False,
) -> bytes | str | None:
    """
    Generate a 3D molecule visualization.

    Args:
        smiles         (str):                   The SMILES string of the molecule to visualize.

        output         (OutputType, optional):  The output format: 'png', 'svg' or 'url'.
        width          (int, optional):         The width of the image in pixels.
        height         (int, optional):         The height of the image in pixels.
        highlight      (str, optional):         A substructure to highlight, as a SMARTS string.

        d3_style       (D3StyleType, optional): The 3D rendering style.
        d3_look        (D3LookType, optional):  The 3D rendering look.
        d3_rot_random  (bool, optional):        Whether to apply random rotation.
        d3_rot_x       (float, optional):       The rotation angle around the X axis.
        d3_rot_y       (float, optional):       The rotation angle around the Y axis.
        d3_rot_z       (float, optional):       The rotation angle around the Z axis.

        return_data    (bool, optional):   Whether to return raw data (True) or display svg/png (False) in Jupyter Notebook.
    """
    params = RenderParams(
        smiles=smiles,
        output=output,
        width=width,
        height=height,
        highlight=highlight,
        return_data=return_data,
    )
    d3_params = D3Params(
        d3_style=d3_style,
        d3_look=d3_look,
        d3_rot_random=d3_rot_random,
        d3_rot_x=d3_rot_x,
        d3_rot_y=d3_rot_y,
        d3_rot_z=d3_rot_z,
    )
    return _render(params, d3_params)


# endregion
# ------------------------------------
# region - Compilation
# ------------------------------------


def _render(
    params: RenderParams, d3_params: D3Params | None = None
) -> bytes | str | None:
    """
    Generate a 2D or 3D molecule visualization.
    """
    # 3rd party
    from IPython.display import Image, SVG, display

    # OMGUI
    from omgui.util.jupyter import nb_mode
    from omgui.molviz import svgmol_2d, svgmol_3d
    from omgui.util.logger import get_logger

    logger = get_logger()

    is_3d = d3_params is not None
    params.output = _validate_output(params.output)

    # Render URL
    if params.output == "url":
        return _compile_url(params, d3_params)

    # Render molecule SVG
    try:
        if is_3d:
            logger.info("Rendering 3D molecule for SMILES: %s", params.smiles)
            svg_str = svgmol_3d.render(
                params.smiles,
                width=params.width,
                height=params.height,
                highlight=params.highlight,
                style=d3_params.d3_style,
                look=d3_params.d3_look,
                rot_random=d3_params.d3_rot_random,
                rot_x=d3_params.d3_rot_x,
                rot_y=d3_params.d3_rot_y,
                rot_z=d3_params.d3_rot_z,
            )
            if not svg_str:
                svg_str = _render_invalid_svg(params, "Invalid SMILES input")
        else:
            logger.info("Rendering 2D molecule for SMILES: %s", params.smiles)
            svg_str = svgmol_2d.render(
                params.smiles,
                width=params.width,
                height=params.height,
                highlight=params.highlight,
            )
            if not svg_str:
                svg_str = _render_invalid_svg(params, "Invalid SMILES input")

    except Exception as e:
        logger.error(
            "Unexpected error rendering molecule for SMILES '%s': %s",
            params.smiles,
            str(e),
        )
        svg_str = _render_invalid_svg(params, "Unexpected rendering error")

    # Jupyter notebook -> display images
    if nb_mode() and not params.return_data:
        if params.output == "png":
            png_data = _svg2png(svg_str)
            display(Image(png_data))
        elif params.output == "svg":
            display(SVG(svg_str))
        return

    # Return SVG
    if params.output == "svg":
        return svg_str

    # Return PNG
    elif params.output == "png":
        return _svg2png(svg_str)


def _compile_url(params: RenderParams, d3_params: D3Params | None = None) -> str:
    """
    Returns the URL for the molecule visualization with the given parameters.
    """
    # Std
    from urllib.parse import urlencode

    # OMGUI
    from omgui import config
    from omgui.util.logger import get_logger

    logger = get_logger()

    # Handle negative and zero width/height
    _width, _height = handle_invalid_width_height(params.width, params.height)
    params.width = _width
    params.height = _height

    query_data = {}
    if params.output != d.OUTPUT:
        query_data["output"] = params.output
    if params.width != d.WIDTH:
        query_data["width"] = params.width
    if params.height != d.HEIGHT:
        query_data["height"] = params.height
    if params.highlight:
        query_data["highlight"] = params.highlight

    if d3_params:
        query_data["d3"] = 1
        if d3_params.d3_style != d.D3_STYLE:
            query_data["d3_style"] = d3_params.d3_style
        if d3_params.d3_look != d.D3_LOOK:
            query_data["d3_look"] = d3_params.d3_look
        if d3_params.d3_rot_random:
            query_data["d3_rot_random"] = d3_params.d3_rot_random
        if d3_params.d3_rot_x:
            query_data["d3_rot_x"] = d3_params.d3_rot_x
        if d3_params.d3_rot_y:
            query_data["d3_rot_y"] = d3_params.d3_rot_y
        if d3_params.d3_rot_z:
            query_data["d3_rot_z"] = d3_params.d3_rot_z

    host_url = config.host_url()
    query_string = urlencode(query_data, doseq=True)
    url_query = f"?{query_string}" if query_string else ""
    url = f"{host_url}/viz/mol/{params.smiles}{url_query}"
    logger.info("Compiled molecule viz URL: %s", url)

    return url


def _svg2png(svg_str: str) -> bytes:
    """
    Convert an SVG string to PNG bytes.
    """
    from io import BytesIO

    try:
        from cairosvg import svg2png
    except ImportError as err:
        raise ImportError(
            "cairosvg is required for PNG conversion. Install it with: pip install cairosvg"
        ) from err

    png_data = BytesIO()
    svg2png(bytestring=svg_str.encode("utf-8"), write_to=png_data)
    png_data.seek(0)  # Rewind to the beginning of the BytesIO object
    return png_data.getvalue()


def _render_invalid_svg(params: RenderParams, error_message: str):
    """Create a simple SVG with error message."""
    return f"""<svg width="{params.width}" height="{params.height}" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="#f8f8f8" stroke="#ddd" stroke-width="2"/>
    <text x="50%" y="50%" text-anchor="middle" dy="0.3em" 
          font-family="Arial, sans-serif" font-size="14" fill="#666">
        {error_message}
    </text>
</svg>"""


# endregion
# ------------------------------------
# region - Auxiliary
# ------------------------------------


def _validate_output(output: str):
    """
    Ensure the output type is valid.
    """
    from omgui.util.logger import get_logger

    logger = get_logger()
    if output not in ["png", "svg", "url"]:
        logger.warning(
            "Invalid output type '%s', using 'svg' instead. Other options are: 'png' or 'url'",
            output,
        )
        return "svg"
    return output


# endregion
# ------------------------------------
