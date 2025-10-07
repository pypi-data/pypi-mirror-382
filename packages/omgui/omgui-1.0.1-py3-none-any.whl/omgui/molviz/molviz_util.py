def handle_invalid_width_height(width: int, height: int) -> None:
    """
    Handle negative width & height input.
    """
    from omgui.molviz import defaults as d
    from omgui.util.logger import get_logger

    logger = get_logger()

    if width < 0:
        logger.warning("Invalid negative width has been ignored")
        width = d.WIDTH
    elif width == 0:
        logger.warning("Invalid zero width has been ignored")
        width = d.WIDTH

    if height < 0:
        logger.warning("Invalid negative height has been ignored")
        height = d.HEIGHT
    elif height == 0:
        logger.warning("Invalid zero height has been ignored")
        height = d.HEIGHT

    return width, height
