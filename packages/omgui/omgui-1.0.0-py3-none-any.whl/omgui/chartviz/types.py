"""
Types used in chartviz module.
"""

from enum import Enum
from typing import Literal


class ChartType(Enum):
    """
    Supported chart types
    More available: https://plotly.com/javascript/#basic-charts
    """

    BAR = "bar"
    LINE = "line"
    SCATTER = "scatter"
    BUBBLE = "bubble"
    PIE = "pie"
    BOXPLOT = "boxplot"
    HISTOGRAM = "histogram"


# Function parameters - main
ChartDataType = list[dict[str, str | list[str] | list[float]]]
OutputType = Literal["html", "png", "svg", "url", "interactive"]  # (*)
OptionsType = dict[str, str | int | float | bool]

# Function parameters - specific
BarModeType = Literal["stack", "group", "overlay", "relative"]
BoxMeanType = Literal[True, "True", "true", "1", False, "False", "false", "0", "sd"]

# (*) OutputType:
# This type is used by both the web API and the python library,
# but not all options are valid for both:
#
# Python lib exclusive:
# - "url": returns a URL string to the chart (hosted on omgui.com)
# - "interactive": opens a browser window with the interactive chart
#
# Web API exclusive:
# - "html": returns an HTML page with the interactive chart
#
# To avoid misuse, invalid types are filtered out in both apis.
