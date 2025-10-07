"""
Core chart rendering functions.
"""

# Std
import json
from typing import Literal

# 3rd party
from urllib.parse import urlencode

# OMGUI
from omgui.chartviz import prep
from omgui.chartviz import types as t
from omgui.chartviz import defaults as d
from omgui.util.logger import get_logger
from omgui.util.general import deep_merge, is_dates, prune_dict

# Check for [viz] optional dependencies
# See config._viz_deps
try:
    import kaleido  # pylint: disable=unused-import
    import plotly.graph_objects as go
except ImportError:
    pass

# Logger
logger = get_logger()


def _generate_chart_image(
    chart_data: t.ChartDataType,
    layout: dict,
    options: dict,
    output: t.OutputType,
):
    """
    Generate SVG or PNG from Plotly chart data.
    """
    fig = go.Figure(data=chart_data)

    default_width = 1200 if output == "interactive" else d.WIDTH
    default_height = 900 if output == "interactive" else d.HEIGHT

    # Set width and height to defaults
    layout["width"] = (
        options.get("width", default_width)
        if options.get("width") != "auto"
        else default_width
    )
    layout["height"] = (
        options.get("height", default_height)
        if options.get("height") != "auto"
        else default_height
    )

    # Apply layout
    fig.update_layout(layout)

    # Generate PNG image
    if output == "png":
        img_bytes = fig.to_image(
            format="png",
            width=layout["width"],
            height=layout["height"],
            scale=options.get("scale", 1),
        )
        return img_bytes

    # Generate SVG string
    elif output == "svg":
        svg_str = fig.to_image(
            format="svg", width=layout["width"], height=layout["height"]
        ).decode("utf-8")
        return svg_str


# ------------------------------------
# region - Output Formatting
# ------------------------------------


def _chart_output(
    chart_type: t.ChartType,
    input_data: t.ChartDataType,
    chart_data: t.ChartDataType,
    output: t.OutputType,
    options: t.OptionsType,
):
    """
    Shared output handling for all charts.
    """
    if not chart_data:
        logger.error("No data available to render chart.")
        return None

    # Return URL
    if output in ["url", "interactive"]:
        url = __compile_url(chart_type, input_data, options)
        return url

    # Compile Plotly layout dict
    layout = __compile_layout(chart_type, chart_data, options)

    # Return image
    if output in ["png", "svg"]:
        return _generate_chart_image(chart_data, layout, options, output)

    # Return data for HTML template
    elif output == "html":
        return {
            "chart_data": chart_data,
            "layout": layout,
        }


def __compile_layout(
    chart_type: t.ChartType,
    chart_data: t.ChartDataType,
    options: t.OptionsType,
):
    """
    Compile the Plotly layout dictionary for all charts.
    """

    options = options or {}

    # Constants
    color_text = "#777"
    color_text_dark = "#444"
    color_line = "#CCC"
    color_line_soft = "#EEE"
    family = '"IBM Plex Sans", sans-serif'
    weight = 400
    weight_bold = 600
    palette_chromatic = [
        "#CB8897",
        "#D4B0A2",
        "#DBCDA9",
        "#BFCBA8",
        "#99CACD",
        "#94ADE0",
        "#B187D8",
        "#CD8ADE",
        "#E76069",
        "#EE936D",
        "#F3BA70",
        "#D0B96F",
        "#9BB99E",
        "#9991C1",
        "#C660BF",
        "#E861C1",
    ]
    palette = []
    for i in range(0, len(palette_chromatic)):
        c = palette_chromatic[(i * 5) % len(palette_chromatic)]
        palette.append(c)
    # palette_ibm = [
    #     "#6929c4",
    #     "#1192e8",
    #     "#005d5d",
    #     "#9f1853",
    #     "#fa4d56",
    #     "#570408",
    #     "#198038",
    #     "#002d9c",
    #     "#ee538b",
    #     "#b28600",
    #     "#009d9a",
    #     "#012749",
    #     "#8a3800",
    #     "#a56eff",
    # ]

    # Base layout object
    layout = {
        "colorway": palette,
        "paper_bgcolor": "#fff",
        "plot_bgcolor": "#fff",
        # Replace auto with None to avoid unwanted Plotly default size
        "width": options.get("width") if not options.get("width") == "auto" else None,
        "height": (
            options.get("height") if not options.get("height") == "auto" else None
        ),
    }

    # Title and subtitle
    layout_title = {
        "title": {
            "text": options.get("title"),
            "x": 0.5,
            "xanchor": "center",
            "y": 1,
            "yanchor": "top",
            "pad": {
                "t": 40,
            },
            "yref": "container",
            "font": {
                "family": family,
                "weight": weight_bold,
                "color": color_text_dark,
            },
            "subtitle": {
                "text": options.get("subtitle"),
                "font": {
                    "family": family,
                    "weight": weight,
                    "color": color_text,
                },
            },
        },
    }

    # X/Y axis
    layout_xy = {
        "xaxis": {
            "title": {
                "text": options.get("x_title"),
                "standoff": 20,
            },
            "rangemode": "tozero",
            "rangeslider": {
                "visible": False,
            },
            "showline": True,
            "mirror": "ticks",
            "color": color_text,
            # "gridcolor": color_line_soft,
            "linecolor": color_line,
            "ticks": "outside",
            "ticklen": 5,
            "tickcolor": "rgba(0,0,0,0)",
            "tickfont": {
                "family": family,
                "weight": weight,
            },
            "tickprefix": options.get("x_prefix"),
            "ticksuffix": options.get("x_suffix"),
        },
        "yaxis": {
            "title": {
                "text": options.get("y_title"),
                "standoff": 15,
            },
            "rangemode": "tozero",
            "showline": True,
            "mirror": "ticks",
            "color": color_text,
            "gridcolor": color_line_soft,
            "linecolor": color_line,
            "ticks": "outside",
            "ticklen": 5,
            "tickcolor": "rgba(0,0,0,0)",
            "tickfont": {
                "family": family,
                "weight": weight,
            },
            "tickprefix": options.get("y_prefix"),
            "ticksuffix": options.get("y_suffix"),
        },
    }

    # Legend
    layout_legend = {
        "legend": {
            "orientation": "h",
            # "xanchor": "left",
            # "x": 0,
            "xanchor": "center",
            "x": 0.5,
            "y": 1.03,
            "yanchor": "bottom",
            "yref": "paper",
            "font": {
                "family": family,
                "weight": weight,
                "color": color_text,
            },
            "visible": True,
        },
    }

    # Hover box
    layout_hover = {
        "hovermode": "x unified",  # Show hover information for all traces at a single x-coordinate
        "hoverlabel": {
            "bordercolor": "#CCC",
            "font": {
                "color": "#777",
            },
        },
    }

    # Mode bar - unused
    layout_modebar = {
        "modebar": {
            "remove": ["zoomin", "zoomout", "lasso", "resetScale2d", "select"],
        },
    }

    # Margins
    # Default for x/y charts has optical correction for ticks and labels
    layout_margin = {
        "margin": {
            "l": 80,
            "r": 80,
            "t": 80,
            "b": 80,
        },
    }

    #
    #

    # Merge pie chart specific layout
    if chart_type == t.ChartType.PIE:
        layout = deep_merge(
            layout,
            {
                "margin": {
                    "l": 40,
                    "r": 40,
                    "t": 40,
                    "b": 40,
                },
            },
        )

    # Merge x/y chart specific layout
    else:
        layout = deep_merge(
            layout,
            layout_xy,
        )
        layout = deep_merge(
            layout,
            layout_margin,
        )

        # Detect & format date x-axis
        x_values = chart_data[0].get("x", []) or []
        is_date_axis = is_dates(x_values[:20]) if chart_data else False
        if is_date_axis:
            layout["xaxis"]["type"] = "date"
            layout["xaxis"]["hoverformat"] = "%d %b, %Y"

    # Set barmode for bar charts & histograms
    if chart_type in [t.ChartType.BAR]:
        layout["barmode"] = options.get("barmode", "group") or "group"
    elif chart_type == t.ChartType.HISTOGRAM:
        layout["barmode"] = options.get("barmode", "overlay") or "overlay"

    # Set boxmode for box plots
    if chart_type == t.ChartType.BOXPLOT:
        layout["boxmode"] = options.get("boxmode", "group")

    # Merge title options
    if options.get("title"):
        layout = deep_merge(
            layout,
            layout_title,
        )
        if options.get("subtitle"):
            layout["margin"]["t"] = 160
        else:
            layout["margin"]["t"] = 120

    # Merge legend options
    if options.get("omit_legend") is True:
        layout["legend"] = {"visible": False}
    else:
        layout = deep_merge(
            layout,
            layout_legend,
        )

    # Merge hover options
    if chart_type == t.ChartType.LINE:
        layout = deep_merge(
            layout,
            layout_hover,
        )

    # Merge mode bar options
    layout = deep_merge(
        layout,
        layout_modebar,
    )

    # print("\n", json.dumps(layout, indent=2), "\n")

    return layout


def __compile_url(chart_type: t.ChartType, input_data: t.ChartDataType, options):
    """
    Generate URL to render chart.
    """
    query = {}
    for key, value in options.items():
        default_value = eval("d." + key.upper()) if hasattr(d, key.upper()) else None
        if value is not None and value != default_value:  # ignore defaults
            if isinstance(value, bool):
                query[key] = 1 if value else 0
            else:
                query[key] = value

    query["data"] = json.dumps(input_data, separators=(",", ":"))
    query_str = f"?{urlencode(query, doseq=True)}" if query else ""
    url = f"viz/chart/{chart_type.value}{query_str}"
    return url


def pre_process_options(options: dict | None, extra_options: dict | None = None):
    """
    Pre-process common options for all charts:
    - Remove None values
    - Handle negative width & height input
    - Merge additional options so they get parsed in the URL
    """
    # Remove None values
    options = prune_dict(options)

    # Handle negative width & height input
    if options.get("width", 1) < 0:
        logger.warning("Invalid negative width has been ignored")
        options["width"] = d.WIDTH
    elif options.get("width", 1) == 0:
        logger.warning("Invalid zero width has been ignored")
        options["width"] = d.WIDTH
    if options.get("height", 1) < 0:
        logger.warning("Invalid negative height has been ignored")
        options["height"] = d.HEIGHT
    elif options.get("height", 1) == 0:
        logger.warning("Invalid zero height has been ignored")
        options["height"] = d.HEIGHT

    if extra_options:
        options = {**options, **extra_options}

    return options


# endregion
# ------------------------------------
# region - Rendering Functions
# ------------------------------------


# Bar chart
# - - -
# https://plotly.com/javascript/bar-charts/
def bar(  # pylint: disable=disallowed-name
    input_data: t.ChartDataType,
    output: t.OutputType,
    options: t.OptionsType,
    ##
    horizontal: bool = False,
):
    """
    Render a bar chart from input data.
    """
    # Compile Plotly data dict
    chart_data = prep.bar(input_data, horizontal)

    # Treat options
    options = pre_process_options(options, {"horizontal": horizontal})

    # Response
    return _chart_output(t.ChartType.BAR, input_data, chart_data, output, options)


# Line chart
# - - -
# https://plotly.com/javascript/line-charts/
def line(
    input_data: t.ChartDataType,
    output: t.OutputType,
    options: t.OptionsType,
    ##
    horizontal: bool = False,
):
    """
    Render a line chart from input data.
    """
    # Compile Plotly data dict
    chart_data = prep.line(input_data, horizontal)

    # Treat options
    options = pre_process_options(options, {"horizontal": horizontal})

    # Response
    return _chart_output(t.ChartType.LINE, input_data, chart_data, output, options)


# Scatter chart
# - - -
# https://plotly.com/javascript/line-and-scatter/
def scatter(
    input_data: t.ChartDataType,
    output: t.OutputType,
    options: t.OptionsType,
):
    """
    Render a scatter chart from input data.
    """
    # Compile Plotly data dict
    chart_data = prep.scatter(input_data)

    # Treat options
    options = pre_process_options(options)

    # Response
    return _chart_output(t.ChartType.SCATTER, input_data, chart_data, output, options)


# Bubble chart
# - - -
# https://plotly.com/javascript/bubble-charts/
def bubble(
    input_data: t.ChartDataType,
    output: t.OutputType,
    options: t.OptionsType,
):
    """
    Render a bubble chart from input data.
    """
    # Compile Plotly data dict
    chart_data = prep.bubble(input_data)

    # Treat options
    options = pre_process_options(options)

    # Response
    return _chart_output(t.ChartType.BUBBLE, input_data, chart_data, output, options)


# Pie chart
# - - -
# https://plotly.com/javascript/pie-charts/
def pie(
    input_data: t.ChartDataType,
    output: t.OutputType,
    options: t.OptionsType,
):
    """
    Render a pie chart from input data.
    """
    # Compile Plotly data dict
    chart_data = prep.pie(input_data)

    # Treat options
    options = pre_process_options(options)

    # Response
    return _chart_output(t.ChartType.PIE, input_data, chart_data, output, options)


# Box plot chart
# - - -
# https://plotly.com/javascript/box-plots/
def boxplot(
    input_data: t.ChartDataType,
    output: t.OutputType,
    options: t.OptionsType,
    #
    horizontal: bool = False,
    show_points: bool = False,
    boxmean: t.BoxMeanType = False,
):
    """
    Render a box plot from input data.
    """
    # Parse boxmean
    # Because it's a boolean OR a string, it's always parsed as a string
    if boxmean in [True, "True", "true", "1"]:
        boxmean = True
    elif boxmean in [False, "False", "false", "0"]:
        boxmean = False

    # Compile Plotly data dict
    chart_data = prep.boxplot(input_data, horizontal, show_points, boxmean)

    # Treat options
    options = pre_process_options(
        options,
        {"horizontal": horizontal, "show_points": show_points, "boxmean": boxmean},
    )

    # Determine boxmode
    options["boxmode"] = "group" if "groups" in input_data[0] else "overlay"

    # Response
    return _chart_output(t.ChartType.BOXPLOT, input_data, chart_data, output, options)


# Histogram chart
# - - -
# https://plotly.com/javascript/histograms/
def histogram(
    input_data: t.ChartDataType,
    output: t.OutputType,
    options: t.OptionsType,
    #
    horizontal: bool = False,
    barmode: Literal["stack", "group", "overlay", "relative"] = "overlay",
):
    """
    Render a histogram chart from input data.
    """
    # Compile Plotly data dict
    chart_data = prep.histogram(input_data, horizontal=horizontal, barmode=barmode)

    # Treat options
    options = pre_process_options(
        options, {"horizontal": horizontal, "barmode": barmode}
    )

    # Response
    return _chart_output(t.ChartType.HISTOGRAM, input_data, chart_data, output, options)


# endregion
# ------------------------------------
