"""
Massage the input data for Plotly consumption.
"""

from typing import Literal


def bar(input_data: list[dict], horizontal: bool = False):
    """
    Restructure the bar chart input data for Plotly consumption.
    """
    chart_data = []
    for [_, ds] in enumerate(input_data):
        if horizontal:
            chart_data.append(
                {
                    "type": "bar",
                    "name": ds.get("name"),
                    "y": ds.get("keys"),
                    "x": ds.get("values"),
                    "orientation": "h",
                    # "opacity": 0.5,
                }
            )
        else:
            chart_data.append(
                {
                    "type": "bar",
                    "name": ds.get("name"),
                    "x": ds.get("keys"),
                    "y": ds.get("values"),
                    # "opacity": 0.5,
                }
            )

    return chart_data


def line(input_data: list[dict], horizontal: bool = False):
    """
    Restructure the line chart input data for Plotly consumption.
    """
    chart_data = []
    for [_, ds] in enumerate(input_data):
        if horizontal:
            chart_data.append(
                {
                    "type": "scatter",
                    "mode": "lines",  # <--
                    "name": ds.get("name"),
                    "x": ds.get("y"),
                    "y": ds.get("x"),
                }
            )
        else:
            chart_data.append(
                {
                    "type": "scatter",
                    "mode": "lines",  # <--
                    "name": ds.get("name"),
                    "x": ds.get("x"),
                    "y": ds.get("y"),
                }
            )
    return chart_data


def scatter(input_data: list[dict]):
    """
    Restructure the scatter plot input data for Plotly consumption.
    """
    chart_data = []
    for [_, ds] in enumerate(input_data):
        chart_data.append(
            {
                "type": "scatter",
                "mode": "markers",  # <--
                "name": ds.get("name"),
                "x": ds.get("x"),
                "y": ds.get("y"),
            }
        )
    return chart_data


def bubble(input_data: list[dict]):
    """
    Restructure the bubble chart input data for Plotly consumption.
    """
    chart_data = []
    for [_, ds] in enumerate(input_data):
        chart_data.append(
            {
                "type": "scatter",
                "mode": "markers",  # <--
                "name": ds.get("name"),
                "x": ds.get("x"),
                "y": ds.get("y"),
                "marker": {"size": ds.get("size")},
            }
        )
    return chart_data


def pie(input_data: list[dict]):
    """
    Restructure the pie chart input data for Plotly consumption.
    """
    chart_data = []
    for [_, ds] in enumerate(input_data):
        chart_data.append(
            {
                "type": "pie",
                "values": ds.get("values"),
                "labels": ds.get("labels"),
            }
        )
    return chart_data


def boxplot(
    input_data: list[dict],
    horizontal: bool = False,
    show_points: bool = False,
    boxmean: bool | Literal["sd"] = False,
):
    """
    Restructure the box plot input data for Plotly consumption.
    """
    chart_data = []
    for [_, ds] in enumerate(input_data):
        # fmt: off
        x = ds.get("data") if horizontal else ds.get("groups")
        y = ds.get("data") if not horizontal else ds.get("groups")
        # fmt: on
        chart_data.append(
            {
                "type": "box",
                "name": ds.get("name"),
                "x": x,
                "y": y,
                "orientation": "h" if horizontal else "v",
                #
                # Box styling
                "line": {
                    "width": 1,
                },
                #
                # Data points
                "boxpoints": "all" if show_points else False,
                "pointpos": -2,
                "jitter": 0.3,
                "marker": {
                    "size": 3,
                    "opacity": 1,
                },
                #
                # Show mean/standard deviation
                "boxmean": boxmean,
            }
        )
    return chart_data


def histogram(
    input_data: list[dict],
    horizontal: bool = False,
    barmode: Literal["stack", "group", "overlay", "relative"] = "overlay",
):
    """
    Restructure the histogram input data for Plotly consumption.
    """
    chart_data = []
    for [_, ds] in enumerate(input_data):
        if horizontal:
            chart_data.append(
                {
                    "type": "histogram",
                    "name": ds.get("name"),
                    "y": ds.get("values"),
                    "opacity": 1 if barmode == "stack" else 0.5,
                }
            )
        else:
            chart_data.append(
                {
                    "type": "histogram",
                    "name": ds.get("name"),
                    "x": ds.get("values"),
                    "opacity": 1 if barmode == "stack" else 0.5,
                }
            )
    return chart_data
