from typing import Literal


def _process(
    # fmt: off
    # Shared 2D & 3D parameters
    smiles: str,
    highlight: str | None = None,
    width: int | None = None,
    height: int | None = None,
    png: bool | None = None,
    url: bool = False,
    data: bool = False,
    # 3D parameters
    _d3: bool | None = None,
    d3_style: Literal["BALL_AND_STICK", "SPACEFILLING", "TUBE", "WIREFRAME"] | None = None,
    d3_look: Literal["CARTOON", "GLOSSY"] | None = None,
    d3_rot_random: bool | None = None,
    d3_rot_x: int | None = None,
    d3_rot_y: int | None = None,
    d3_rot_z: int | None = None,
    # fmt: on
) -> bytes | str:
    """
    Generate a 2D or 3D molecule visualization.

    Extra Args:
        d3: Whether to generate a 3D visualization (True) or 2D (False).
    """
    import requests
    from urllib.parse import urlencode

    import omgui
    from omgui import config
    from omgui.util.jupyter import nb_mode
    from omgui.util.logger import get_logger

    logger = get_logger()

    omgui.launch(block_thread=False)

    # Compile URL
    host_url = config.host_url()
    query_data = {}
    if highlight is not None:
        query_data["highlight"] = highlight
    if width is not None:
        query_data["width"] = width
    if height is not None:
        query_data["height"] = height
    if png is not None:
        query_data["png"] = png
    if _d3:
        query_data["d3"] = _d3
    if _d3 and d3_style is not None:
        query_data["d3_style"] = d3_style
    if _d3 and d3_look is not None:
        query_data["d3_look"] = d3_look
    if _d3 and d3_rot_random is not None:
        query_data["d3_rot_random"] = d3_rot_random
    if _d3 and d3_rot_x is not None:
        query_data["d3_rot_x"] = d3_rot_x
    if _d3 and d3_rot_y is not None:
        query_data["d3_rot_y"] = d3_rot_y
    if _d3 and d3_rot_z is not None:
        query_data["d3_rot_z"] = d3_rot_z

    query_string = urlencode(query_data, doseq=True)
    url_query = f"?{query_string}" if query_string else ""
    viz_url = f"{host_url}/viz/mol/{smiles}{url_query}"
    logger.info(f"Generated molecule viz URL: {viz_url}")

    # Return URL
    if url:
        return viz_url

    # Return or display image
    else:
        r = requests.get(viz_url)
        r.raise_for_status()

        # Jupyter notebook display
        if not data and nb_mode():
            from IPython.display import Image, SVG, display

            if png:
                display(Image(r.content))
            else:
                display(SVG(r.content))

        # Raw return
        else:
            return r.content


def d2(
    smiles: str,
    highlight: str | None = None,
    width: int | None = None,
    height: int | None = None,
    png: bool | None = None,
    url: bool = False,
    return_data: bool = False,
):
    """
    Generate a 2D molecule visualization.

    Args:
        smiles: The SMILES string of the molecule to visualize.
        highlight: A substructure to highlight, as a SMARTS string.
        width: The width of the image in pixels.
        height: The height of the image in pixels.
        png: Whether to return a PNG (True) or SVG (False).
        url: Whether to return the URL (True) or the raw content (False).
        return_data: Whether to return raw data (True) or display svg/png (False) in Jupyter Notebook.
    """
    return _process(smiles, highlight, width, height, png, url, return_data)


def d3(
    # fmt: off
    # 2D parameters
    smiles: str,
    highlight: str | None = None,
    width: int | None = None,
    height: int | None = None,
    png: bool | None = None,
    url: bool = False,
    data: bool = False,
    # 3D parameters
    d3_style: Literal["BALL_AND_STICK", "SPACEFILLING", "TUBE", "WIREFRAME"] | None = None,
    d3_look: Literal["CARTOON", "GLOSSY"] | None = None,
    d3_rot_random: bool | None = None,
    d3_rot_x: int | None = None,
    d3_rot_y: int | None = None,
    d3_rot_z: int | None = None,
    # fmt: on
) -> bytes | str:
    """
    Generate a 3D molecule visualization.

    Args:
        smiles: The SMILES string of the molecule to visualize.
        highlight: A substructure to highlight, as a SMARTS string.
        width: The width of the image in pixels.
        height: The height of the image in pixels.
        png: Whether to return a PNG (True) or SVG (False).
        url: Whether to return the URL (True) or the raw content (False).
        d3_style: The 3D rendering style.
        d3_look: The 3D rendering look.
        d3_rot_random: Whether to apply random rotation.
        d3_rot_x: The rotation angle around the X axis.
        d3_rot_y: The rotation angle around the Y axis.
        d3_rot_z: The rotation angle around the Z axis.
    """
    return _process(
        smiles,
        highlight,
        width,
        height,
        png,
        url,
        data,
        True,  # 3D toggle _d3
        d3_style,
        d3_look,
        d3_rot_random,
        d3_rot_x,
        d3_rot_y,
        d3_rot_z,
    )
