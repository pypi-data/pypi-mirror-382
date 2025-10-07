"""
Chart visualization web API routes.

/viz/chart/<chart_type>?data=<data>
"""

# pylint: disable=missing-function-docstring

# Std
import json
from typing import Literal
from urllib.parse import unquote


# FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.responses import Response, HTMLResponse
from fastapi import APIRouter, Request, HTTPException
from fastapi import status, Query, Body, Depends

# 3rd party
try:
    import kaleido  # pylint: disable=unused-import
    import plotly.graph_objects as go
except ImportError:
    pass

# OMGUI
from omgui import config
from omgui.chartviz.types import ChartType, OutputType
from omgui.chartviz import render
from omgui.util.logger import get_logger
from omgui.chartviz import chart_sampler
from omgui.util import exceptions as omg_exc
from omgui.util.general import deep_merge, is_dates, hash_data


# Setup
# ------------------------------------

# Router
chartviz_router = APIRouter()

# Set up templates and static files
from pathlib import Path

parent_dir = Path(__file__).parent
templates = Jinja2Templates(directory=parent_dir / "templates")

# Logger
logger = get_logger()


# ------------------------------------
# region - Auxiliary functions
# ------------------------------------


# ⚠️ Keep in sync with _common_params() in chartviz_routes.py
def query_params(
    # fmt: off
    output: OutputType = Query("html", description="Output format: html, png or svg"),
    title: str | None = Query(None, description="Chart title"),
    subtitle: str | None = Query(None, description="Chart subtitle"),
    body: str | None = Query(None, description="Paragraph displayed below the chart. Only used with output='html'."),
    x_title: str | None = Query(None, description="Title for the x-axis."),
    y_title: str | None = Query(None, description="Title for the y-axis."),
    x_prefix: str | None = Query(None, description="Prefix for x-axis tick labels, eg. '€'."),
    y_prefix: str | None = Query(None, description="Prefix for y-axis tick labels, eg. '€'."),
    x_suffix: str | None = Query(None, description="Suffix for x-axis tick labels, eg. '%'."),
    y_suffix: str | None = Query(None, description="Suffix for y-axis tick labels, eg. '%'."),
    width: int | Literal['auto'] | None = Query(None, description="Width of the chart in pixels."),
    height: int | Literal['auto'] | None = Query(None, description="Height of the chart in pixels."),
    scale: int | None = Query(None, description="Scaling factor for the png pixel output. Set to 2 for high-resolution displays. Only used when output='png'."),
    omit_legend: bool | None = Query(False, description="If True, do not display the legend."),
    return_data: bool | None = Query(False, description="Whether to return raw data (True) or display the svg/png (False) in Jupyter Notebook. Only used when output='svg/png'."),
    # Chart-specific options
    # barmode: Literal["stack", "group", "overlay", "relative"] | None = Query(None, description="Bar mode for bar/histogram charts."),
    # boxmode: Literal["group", "overlay"] | None = Query(None, description="Box mode for box plot chart."),
    # fmt: on
):
    """
    Shared query parameters for the chart routes.

    Exposed via:
        options: dict = Depends(query_params),
    """
    return {
        "output": output if output in ["html", "png", "svg"] else "html",
        "title": title,
        "subtitle": subtitle,
        "body": body,
        "x_title": x_title,
        "y_title": y_title,
        "x_prefix": x_prefix,
        "y_prefix": y_prefix,
        "x_suffix": x_suffix,
        "y_suffix": y_suffix,
        "width": None if width == "auto" else width,
        "height": None if height == "auto" else height,
        "scale": scale,
        "omit_legend": omit_legend,
        "return_data": return_data,
        ##
        # "barmode": barmode,
        # "boxmode": boxmode,
    }


async def parse_input_data(
    request: Request,
    data_json: str | None,  # Data passed in the URL
    data_id: str,  # Data stored in Redis
):
    """
    Parse the input data from the URL or from Redis (or in-memory fallback).
    """

    # From Redis or in-memory fallback
    if data_id:
        redis_client = request.app.state.redis
        key = f"input_data:{data_id}"

        if redis_client:
            input_data_raw = await redis_client.get(key)
            if not input_data_raw:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Chart data with ID '{data_id}' not found. It may have expired.",
                )
            input_data = json.loads(input_data_raw)
        else:
            # in-memory fallback (only for dev/demo; volative and not shared between processes)
            cache = getattr(request.app.state, "in_memory_cache", {})
            input_data_raw = cache.get(key)
            if not input_data_raw:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Chart data with ID '{data_id}' not found (no Redis configured).",
                )
            input_data = json.loads(input_data_raw)

    # From URL
    elif data_json:
        input_data = json.loads(unquote(data_json))
        if not input_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The 'data_json' query parameter cannot be empty.",
            )

    else:
        # Nothing provided
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No chart data provided (use 'data' param or post data to / to get an id).",
        )

    return input_data


def compile_response(
    request: Request,
    output: OutputType,
    result: any,
    input_data: list[dict],
    options: dict,
):
    """
    Compile the response based on the output type.
    """

    # Return HTML template
    if output == "html":
        return _compile_response_html(
            request,
            result,
            input_data,
            options,
        )

    # PNG
    if output == "png":
        return Response(
            content=result,
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename='pie_chart.png'"},
        )

    # SVG
    elif output == "svg":
        return Response(
            content=result,
            media_type="image/svg+xml",
            headers={"Content-Disposition": "inline; filename='pie_chart.svg'"},
        )


def _compile_response_html(
    request: Request,
    result: dict,
    input_data: list[dict] = None,
    options: dict = None,
    additional_options: dict = None,
):
    """
    Shared template response for all charts.
    """

    chart_data = result.get("chart_data", [])
    layout = result.get("layout", {})
    options = options or {}

    return templates.TemplateResponse(
        "chart.jinja",
        {
            "request": request,
            "chart_data": chart_data,
            "input_data": input_data,
            "layout": layout,
            # Options
            "width": options.get("width"),
            "height": options.get("height"),
            "title": options.get("title"),
            "subtitle": options.get("subtitle"),
            "body": options.get("body"),
            # Additional options for specific charts
            **(additional_options if additional_options is not None else {}),
        },
    )


# endregion
# ------------------------------------
# region - Routes: Demonstration
# ------------------------------------


@chartviz_router.get(
    "", response_class=HTMLResponse, summary="Interactive demo UI for the charts API"
)
def demo_charts(request: Request):
    """
    Interactive HTML demo page for the Charts API.
    Provides a user interface with controls for all API parameters.
    """
    if not config._viz_deps:
        raise omg_exc.MissingDependenciesViz

    return templates.TemplateResponse("demo-charts.html", {"request": request})


@chartviz_router.get(
    "/generate/{chart_type}",
    summary="Generate random dummy data for various chart types",
)
async def random_data(
    request: Request, chart_type: ChartType | Literal["boxplot-group"]
):
    if not config._viz_deps:
        raise omg_exc.MissingDependenciesViz

    chart_data = None
    if chart_type == ChartType.SCATTER:
        chart_data = chart_sampler.scatterplot()
    elif chart_type == ChartType.LINE:
        chart_data = chart_sampler.line()
    elif chart_type == ChartType.BUBBLE:
        chart_data = chart_sampler.bubble()
    elif chart_type == ChartType.PIE:
        chart_data = chart_sampler.pie()
    elif chart_type == ChartType.BAR:
        chart_data = chart_sampler.bar()
    elif chart_type == ChartType.BOXPLOT:
        chart_data = chart_sampler.boxplot()
    elif chart_type == "boxplot-group":
        chart_data = chart_sampler.boxplot(group_count=3)
    elif chart_type == ChartType.HISTOGRAM:
        chart_data = chart_sampler.histogram()
    else:
        return f"Invalid chart type '{chart_type}'"

    return chart_data


# endregion
# ------------------------------------
# region - Routes: Chart Types
# ------------------------------------


# Bar chart
# - - -
# https://plotly.com/javascript/bar-charts/
@chartviz_router.get("/bar", summary="Render a bar chart from URL data")
@chartviz_router.get("/bar/{data_id}", summary="Render a bar chart from Redis data")
async def chart_bar(
    # fmt: off
    request: Request,
    data_id: str | None = None, # Redis or in-memory ID for the input data
    input_data: str | None = Query(None, alias="data", description="JSON-encoded chart data"),
    options: dict = Depends(query_params),
    # Bar chart specific options
    horizontal: bool = Query(False, alias="h", description="Render bar chart horizontally"),
    # fmt: on
):
    if not config._viz_deps:
        raise omg_exc.MissingDependenciesViz

    # Fetch data from URL or Redis/in-memory
    input_data = await parse_input_data(request, input_data, data_id)

    # Render chart
    output = options.get("output")
    result = render.bar(input_data, output, options, horizontal)

    # Response
    return compile_response(
        request,
        output,
        result,
        input_data,
        options,
    )


# Line chart
# - - -
# https://plotly.com/javascript/line-charts/
@chartviz_router.get("/line", summary="Render a line chart from URL data")
@chartviz_router.get("/line/{data_id}", summary="Render a line chart from Redis data")
async def chart_line(
    # fmt: off
    request: Request,
    data_id: str | None = None, # Redis or in-memory ID for the input data
    input_data: str | None = Query(None, alias="data", description="JSON-encoded chart data"),
    options: dict = Depends(query_params),
    # Line chart specific options
    horizontal: bool = Query(False, alias="h", description="Render line chart horizontally"),
    # fmt: on
):
    if not config._viz_deps:
        raise omg_exc.MissingDependenciesViz

    # Fetch data from URL or Redis/in-memory
    input_data = await parse_input_data(request, input_data, data_id)

    # Render chart
    output = options.get("output")
    result = render.line(input_data, output, options, horizontal)

    # Response
    return compile_response(
        request,
        output,
        result,
        input_data,
        options,
    )


# Scatter chart
# - - -
# https://plotly.com/javascript/line-and-scatter/
@chartviz_router.get("/scatter", summary="Render a scatter plot from URL data")
@chartviz_router.get(
    "/scatter/{data_id}", summary="Render a scatter plot from Redis data"
)
async def chart_scatter(
    # fmt: off
    request: Request,
    data_id: str | None = None, # Redis or in-memory ID for the input data
    input_data: str | None = Query(None, alias="data", description="JSON-encoded chart data"),
    options: dict = Depends(query_params),
    # fmt: on
):
    if not config._viz_deps:
        raise omg_exc.MissingDependenciesViz

    # Fetch data from URL or Redis/in-memory
    input_data = await parse_input_data(request, input_data, data_id)

    # Render chart
    output = options.get("output")
    result = render.scatter(input_data, output, options)

    # Response
    return compile_response(
        request,
        output,
        result,
        input_data,
        options,
    )


# Bubble chart
# - - -
# https://plotly.com/javascript/bubble-charts/
@chartviz_router.get("/bubble", summary="Render a bubble chart from URL data")
@chartviz_router.get(
    "/bubble/{data_id}", summary="Render a bubble chart from Redis data"
)
async def chart_bubble(
    # fmt: off
    request: Request,
    data_id: str | None = None, # Redis or in-memory ID for the input data
    input_data: str | None = Query(None, alias="data", description="JSON-encoded chart data"),
    options: dict = Depends(query_params),
    # fmt: on
):
    if not config._viz_deps:
        raise omg_exc.MissingDependenciesViz

    # Fetch data from URL or Redis/in-memory
    input_data = await parse_input_data(request, input_data, data_id)

    # Render chart
    output = options.get("output")
    result = render.bubble(input_data, output, options)

    # Response
    return compile_response(
        request,
        output,
        result,
        input_data,
        options,
    )


# Pie chart
# - - -
# https://plotly.com/javascript/pie-charts/
@chartviz_router.get("/pie", summary="Render a pie chart from URL data")
@chartviz_router.get("/pie/{data_id}", summary="Render a pie chart from Redis data")
async def chart_pie(
    # fmt: off
    request: Request,
    data_id: str | None = None, # Redis or in-memory ID for the input data
    input_data: str | None = Query(None, alias="data", description="JSON-encoded chart data"),
    options: dict = Depends(query_params),
    # fmt: on
):
    if not config._viz_deps:
        raise omg_exc.MissingDependenciesViz

    # Fetch data from URL or Redis/in-memory
    input_data = await parse_input_data(request, input_data, data_id)

    # Render chart
    output = options.get("output")
    result = render.pie(input_data, output, options)

    # Response
    return compile_response(
        request,
        output,
        result,
        input_data,
        options,
    )


# Box plot chart
# - - -
# https://plotly.com/javascript/box-plots/
@chartviz_router.get("/boxplot", summary="Render a box plot chart from URL data")
@chartviz_router.get(
    "/boxplot/{data_id}", summary="Render a box plot chart from Redis data"
)
async def chart_boxplot(
    # fmt: off
    request: Request,
    data_id: str | None = None, # Redis or in-memory ID for the input data
    input_data: str | None = Query(None, alias="data", description="JSON-encoded chart data"),
    options: dict = Depends(query_params),
    # Boxplot specific options
    horizontal: bool = Query(False, alias="h", description="Render box plot horizontally"),
    show_points: bool = Query(False, description="Show data points on the box plot"),
    boxmean: Literal[True, "True", "true", "1", False, "False", "false", "0", "sd"]
        = Query(False, description="Show mean and standard deviation on the box plot"),
    # fmt: on
):
    if not config._viz_deps:
        raise omg_exc.MissingDependenciesViz

    # Fetch data from URL or Redis/in-memory
    input_data = await parse_input_data(request, input_data, data_id)

    # Render chart
    output = options.get("output")
    result = render.boxplot(
        input_data, output, options, horizontal, show_points, boxmean
    )

    # Response
    return compile_response(
        request,
        output,
        result,
        input_data,
        options,
    )


# Histogram chart
# - - -
# https://plotly.com/javascript/histograms/
@chartviz_router.get("/histogram", summary="Render a histogram chart from URL data")
@chartviz_router.get(
    "/histogram/{data_id}", summary="Render a histogram chart from Redis data"
)
async def chart_histogram(
    # fmt: off
    request: Request,
    data_id: str | None = None, # Redis or in-memory ID for the input data
    input_data: str | None = Query(None, alias="data", description="JSON-encoded chart data"),
    options: dict = Depends(query_params),
    # Histogram specific options
    horizontal: bool = Query(False, alias="h", description="Render histogram chart horizontally"),
    barmode: Literal["stack", "group", "overlay", "relative"] = Query("overlay", description="Bar mode for histogram chart"),
    # fmt: on
):
    if not config._viz_deps:
        raise omg_exc.MissingDependenciesViz

    # Fetch data from URL or Redis/in-memory
    input_data = await parse_input_data(request, input_data, data_id)

    # Render chart
    output = options.get("output")
    result = render.histogram(input_data, output, options, horizontal, barmode)

    # Response
    return compile_response(
        request,
        output,
        result,
        input_data,
        options,
    )


# Redis POST
@chartviz_router.post(
    "/{chart_type}", summary="Render different chart types from POST data"
)
async def post_chart_data(
    request: Request,
    chart_type: ChartType,
    data: list[dict] = Body(...),
):
    """
    Takes chart data from the request body, stores it in Redis (or in-memory fallback),
    and returns a unique ID for the data.
    """
    if not config._viz_deps:
        raise omg_exc.MissingDependenciesViz

    unique_id = hash_data(data)
    key = f"input_data:{unique_id}"

    # Use Redis when available
    redis_client = request.app.state.redis
    if redis_client:
        await redis_client.set(key, json.dumps(data), ex=86400)
        logger.info("Chart data stored in Redis as '%s'", unique_id)
        return {"id": unique_id, "url": f"/{chart_type.value}/{unique_id}"}

    # In-memory fallback
    cache = getattr(request.app.state, "in_memory_cache", None)
    if cache is None:
        request.app.state.in_memory_cache = {}
        cache = request.app.state.in_memory_cache

    cache[key] = json.dumps(data)

    logger.info(
        "Chart data stored in in-memory cache as '%s' (no Redis configured)", unique_id
    )

    return {
        "id": unique_id,
        "url": f"/viz/chart/{chart_type.value}/{unique_id}",
        "note": "Data stored in in-memory cache (no expiry, not persistent). Configure config.redis_url to enable Redis storage.",
    }


# endregion
# ------------------------------------
