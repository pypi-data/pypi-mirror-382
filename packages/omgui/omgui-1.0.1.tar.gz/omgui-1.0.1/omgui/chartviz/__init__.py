from typing import Callable
from omgui.chartviz import types as t
from omgui.chartviz import defaults as d


# ------------------------------------
# region - Common Options Decorator
# ------------------------------------


# pylint: disable=unused-argument
# ---
# ⚠️ Keep in sync with query_params() in chartviz_routes.py
def _common_params(
    *,  # Force keyword-only arguments
    title: str | None = d.TITLE,
    subtitle: str | None = d.SUBTITLE,
    body: str | None = d.BODY,
    x_title: str | None = d.X_TITLE,
    y_title: str | None = d.Y_TITLE,
    x_prefix: str | None = d.X_PREFIX,
    y_prefix: str | None = d.Y_PREFIX,
    x_suffix: str | None = d.X_SUFFIX,
    y_suffix: str | None = d.Y_SUFFIX,
    width: int = d.WIDTH,
    height: int = d.HEIGHT,
    scale: float = d.SCALE,
    omit_legend: bool = d.OMIT_LEGEND,
    return_data: bool = d.RETURN_DATA,
):
    """
    Common parameters for chart rendering functions.

    Args:
        title        (str, optional):    Title of the chart.
        subtitle     (str, optional):    Subtitle of the chart.
        body         (str, optional):    Paragraph displayed below the chart. Only used with output='html'.
        x_title      (str, optional):    Title for the x-axis.
        y_title      (str, optional):    Title for the y-axis.
        x_prefix     (str, optional):    Prefix for x-axis tick labels, eg. '€'.
        y_prefix     (str, optional):    Prefix for y-axis tick labels, eg. '€'.
        x_suffix     (str, optional):    Suffix for x-axis tick labels, eg. '%'.
        y_suffix     (str, optional):    Suffix for y-axis tick labels, eg. '%'.
        width        (int, optional):    Width of the chart in pixels.
        height       (int, optional):    Height of the chart in pixels.
        scale        (float, optional):  Scaling factor for the png pixel output. Set to 2 for high-resolution displays. Only used when output='png'.
        omit_legend  (bool, optional):   If True, do not display the legend.
        return_data  (bool, optional):   Whether to return raw data (True) or display the svg/png (False) in Jupyter Notebook. Only used when output='svg/png'.
    """
    # This function is never called, it only provides the shared options
    # signature and documentation. See @with_common_options decorator below.


# @decorator
def with_common_params(func: Callable) -> Callable:
    """
    Decorator that combines the function's signature with common_params'
    signature for documentation, and handles argument separation at runtime.

    This applies the common parameters to every chart function.
    """
    import inspect
    from functools import wraps

    # Get signatures
    common_sig = inspect.signature(_common_params)
    func_sig = inspect.signature(func)

    # Combine parameters
    new_parameters = list(func_sig.parameters.values()) + list(
        common_sig.parameters.values()
    )

    # # Debug: Print the new combined parameters
    # for p in new_parameters:
    #     print(f"{p.name:15} {p.kind}")

    # Create the new signature object
    new_signature = inspect.Signature(new_parameters)

    @wraps(func)
    def wrapper(*args: any, **kwargs: any) -> any:
        # Bind incoming args/kwargs to the new,
        # combined signature and apply defaults
        bound_args = new_signature.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Function arguments: 'data', 'horizontal', etc.
        # Common arguments: become the 'options' dict
        func_args = {}
        common_options = {}

        # Separate the arguments based on where they were defined (func vs common)
        for name, value in bound_args.arguments.items():
            if name in func_sig.parameters:
                func_args[name] = value
            elif value is not None:
                common_options[name] = value

        # Ensure 'data' and 'output' are always first,
        # remove 'options' to avoid doubling in func_args
        data = func_args.pop("input_data")
        output = func_args.pop("output", None)
        func_args.pop("options", None)

        # Call the original function with the transformed arguments
        return func(data, output, common_options, **func_args)

    # Assign the new signature for documentation
    wrapper.__signature__ = new_signature
    return wrapper


# endregion
# ------------------------------------
# region - Auxiliary Functions
# ------------------------------------


def _handle_result(result: any, output: t.OutputType, return_data: bool = False):
    """
    Shared result handling based on the output type and environment.

    In Jupyter Notebook, SVGs or PNGs are displayed directly,
    unless return_data is True. URL is always returned as is.
    """
    from omgui.main import gui_init
    from omgui.util.jupyter import nb_mode
    from IPython.display import Image, SVG, display

    # No data to render
    if result is None:
        return None

    # HTML page -> launch browser or iframe
    if output == "interactive":
        gui_init(result, ignore_headless=True)

    # Jupyter notebook -> display images
    if nb_mode() and not return_data:
        if output == "png":
            display(Image(result))
        elif output == "svg":
            display(SVG(result))
        elif output == "url":
            return result

    # Raw return
    else:
        return result


def _validate_output(output: str):
    """
    Ensure the output type is valid.
    """
    from omgui.util.logger import get_logger

    logger = get_logger()
    if output not in ["png", "svg", "url", "interactive"]:
        logger.warning(
            "Invalid output type '%s', using 'interactive' instead. Other options are 'svg', 'png' or 'url'",
            output,
        )
        return d.OUTPUT
    return output


# endregion
# ------------------------------------
# region - Chart Functions
# ------------------------------------


@with_common_params
def bar(  # pylint: disable=disallowed-name
    input_data: t.ChartDataType,
    output: t.OutputType = d.OUTPUT,
    options: dict | None = d.OPTIONS,
    ##
    horizontal: bool = d.HORIZONTAL,
):
    """
    Render a bar chart from input data.
    """
    from omgui.chartviz import render

    output = _validate_output(output)
    result = render.bar(input_data, output, options, horizontal)
    return_data = options.get("return_data") if options else False
    return _handle_result(result, output, return_data)


@with_common_params
def line(
    input_data: t.ChartDataType,
    output: t.OutputType = d.OUTPUT,
    options: dict | None = d.OPTIONS,
    ##
    horizontal: bool = d.HORIZONTAL,
):
    """
    Render a line chart from input data.
    """
    from omgui.chartviz import render

    output = _validate_output(output)
    result = render.line(input_data, output, options, horizontal)
    return_data = options.get("return_data") if options else False
    return _handle_result(result, output, return_data)


@with_common_params
def scatterplot(
    input_data: t.ChartDataType,
    output: t.OutputType = d.OUTPUT,
    options: dict | None = d.OPTIONS,
):
    """
    Render a scatter plot from input data.
    """
    from omgui.chartviz import render

    output = _validate_output(output)
    result = render.scatter(input_data, output, options)
    return_data = options.get("return_data") if options else False
    return _handle_result(result, output, return_data)


@with_common_params
def bubble(
    input_data: t.ChartDataType,
    output: t.OutputType = d.OUTPUT,
    options: dict | None = d.OPTIONS,
):
    """
    Render a bubble chart from input data.
    """
    from omgui.chartviz import render

    output = _validate_output(output)
    result = render.bubble(input_data, output, options)
    return_data = options.get("return_data") if options else False
    return _handle_result(result, output, return_data)


@with_common_params
def pie(
    input_data: t.ChartDataType,
    output: t.OutputType = d.OUTPUT,
    options: dict | None = d.OPTIONS,
):
    """
    Render a pie chart from input data.
    """
    from omgui.chartviz import render

    output = _validate_output(output)
    result = render.pie(input_data, output, options)
    return_data = options.get("return_data") if options else False
    return _handle_result(result, output, return_data)


@with_common_params
def boxplot(
    input_data: t.ChartDataType,
    output: t.OutputType = d.OUTPUT,
    options: dict | None = d.OPTIONS,
    ##
    horizontal: bool = False,
    show_points: bool = False,
    boxmean: t.BoxMeanType = False,
):
    """
    Render a boxplot from input data.
    """
    from omgui.chartviz import render

    output = _validate_output(output)
    result = render.boxplot(
        input_data, output, options, horizontal, show_points, boxmean
    )
    return_data = options.get("return_data") if options else False
    return _handle_result(result, output, return_data)


@with_common_params
def histogram(
    input_data: t.ChartDataType,
    output: t.OutputType = d.OUTPUT,
    options: dict | None = d.OPTIONS,
    ##
    horizontal: bool = d.HORIZONTAL,
    barmode: t.BarModeType = d.BARMODE,
):
    """
    Render a histogram chart from input data.
    """
    from omgui.chartviz import render

    output = _validate_output(output)
    result = render.histogram(input_data, output, options, horizontal, barmode)
    return_data = options.get("return_data") if options else False
    return _handle_result(result, output, return_data)


# endregion
# ------------------------------------
