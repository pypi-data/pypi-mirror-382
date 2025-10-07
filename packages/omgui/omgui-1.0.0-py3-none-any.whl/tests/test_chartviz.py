"""
Comprehensive tests for omgui.chartviz module.

Tests chart visualization functionality including:
- All chart types (bar, line, scatter, bubble, pie, boxplot, histogram)
- Parameter validation and handling
- Output format handling (SVG, PNG, URL, interactive)
- Chart-specific parameters
- Error handling
- Integration with omgui server
"""

import pytest
from omgui import chartviz
from omgui.chartviz import chart_sampler


class TestChartvizBasicFunctionality:
    """Test basic chart visualization functionality for all chart types."""

    # ------------------------------------
    # region - Bar
    # ------------------------------------

    def test_bar_default_output(self):
        """Test default bar chart SVG generation."""
        data = chart_sampler.bar()
        result = chartviz.bar(data)

        assert result is not None
        assert isinstance(result, str)
        assert _is_svg_str(result)

    def test_bar_svg_output(self):
        """Test explicit bar chart SVG generation."""
        data = chart_sampler.bar()
        result = chartviz.bar(data, output="svg")

        assert result is not None
        assert isinstance(result, str)
        assert _is_svg_str(result)

    def test_bar_png_output(self):
        """Test bar chart PNG generation."""
        data = chart_sampler.bar()
        result = chartviz.bar(data, output="png")

        assert result is not None
        assert isinstance(result, bytes)
        assert result.startswith(b"\x89PNG\r\n\x1a\n")

    def test_bar_url_output(self):
        """Test bar chart URL generation."""
        data = chart_sampler.bar()
        result = chartviz.bar(data, output="url")

        assert result is not None
        assert isinstance(result, str)
        assert result.startswith("viz/chart/bar")

    # endregion
    # ------------------------------------
    # region - Line
    # ------------------------------------

    def test_line_default_output(self):
        """Test default line chart SVG generation."""
        data = chart_sampler.line()
        result = chartviz.line(data)

        assert result is not None
        assert isinstance(result, str)
        assert _is_svg_str(result)

    def test_line_svg_output(self):
        """Test explicit line chart SVG generation."""
        data = chart_sampler.line()
        result = chartviz.line(data, output="svg")

        assert result is not None
        assert isinstance(result, str)
        assert _is_svg_str(result)

    def test_line_png_output(self):
        """Test line chart PNG generation."""
        data = chart_sampler.line()
        result = chartviz.line(data, output="png")

        assert result is not None
        assert isinstance(result, bytes)
        assert result.startswith(b"\x89PNG\r\n\x1a\n")

    def test_line_url_output(self):
        """Test line chart URL generation."""
        data = chart_sampler.line()
        result = chartviz.line(data, output="url")

        assert result is not None
        assert isinstance(result, str)
        assert result.startswith("viz/chart/line")

    # endregion
    # ------------------------------------
    # region - Scatter
    # ------------------------------------

    def test_scatter_default_output(self):
        """Test default scatter plot SVG generation."""
        data = chart_sampler.scatterplot()
        result = chartviz.scatterplot(data)

        assert result is not None
        assert isinstance(result, str)
        assert _is_svg_str(result)

    def test_scatter_svg_output(self):
        """Test explicit scatter plot SVG generation."""
        data = chart_sampler.scatterplot()
        result = chartviz.scatterplot(data, output="svg")

        assert result is not None
        assert isinstance(result, str)
        assert _is_svg_str(result)

    def test_scatter_png_output(self):
        """Test scatter plot PNG generation."""
        data = chart_sampler.scatterplot()
        result = chartviz.scatterplot(data, output="png")

        assert result is not None
        assert isinstance(result, bytes)
        assert result.startswith(b"\x89PNG\r\n\x1a\n")

    def test_scatter_url_output(self):
        """Test scatter plot URL generation."""
        data = chart_sampler.scatterplot()
        result = chartviz.scatterplot(data, output="url")

        assert result is not None
        assert isinstance(result, str)
        assert result.startswith("viz/chart/scatter")

    # endregion
    # ------------------------------------
    # region - Bubble
    # ------------------------------------

    def test_bubble_default_output(self):
        """Test default bubble chart SVG generation."""
        data = chart_sampler.bubble()
        result = chartviz.bubble(data)

        assert result is not None
        assert isinstance(result, str)
        assert _is_svg_str(result)

    def test_bubble_svg_output(self):
        """Test explicit bubble chart SVG generation."""
        data = chart_sampler.bubble()
        result = chartviz.bubble(data, output="svg")

        assert result is not None
        assert isinstance(result, str)
        assert _is_svg_str(result)

    def test_bubble_png_output(self):
        """Test bubble chart PNG generation."""
        data = chart_sampler.bubble()
        result = chartviz.bubble(data, output="png")

        assert result is not None
        assert isinstance(result, bytes)
        assert result.startswith(b"\x89PNG\r\n\x1a\n")

    def test_bubble_url_output(self):
        """Test bubble chart URL generation."""
        data = chart_sampler.bubble()
        result = chartviz.bubble(data, output="url")

        assert result is not None
        assert isinstance(result, str)
        assert result.startswith("viz/chart/bubble")

    # endregion
    # ------------------------------------
    # region - Pie
    # ------------------------------------

    def test_pie_default_output(self):
        """Test default pie chart SVG generation."""
        data = chart_sampler.pie()
        result = chartviz.pie(data)

        assert result is not None
        assert isinstance(result, str)
        assert _is_svg_str(result)

    def test_pie_svg_output(self):
        """Test explicit pie chart SVG generation."""
        data = chart_sampler.pie()
        result = chartviz.pie(data, output="svg")

        assert result is not None
        assert isinstance(result, str)
        assert _is_svg_str(result)

    def test_pie_png_output(self):
        """Test pie chart PNG generation."""
        data = chart_sampler.pie()
        result = chartviz.pie(data, output="png")

        assert result is not None
        assert isinstance(result, bytes)
        assert result.startswith(b"\x89PNG\r\n\x1a\n")

    def test_pie_url_output(self):
        """Test pie chart URL generation."""
        data = chart_sampler.pie()
        result = chartviz.pie(data, output="url")

        assert result is not None
        assert isinstance(result, str)
        assert result.startswith("viz/chart/pie")

    # endregion
    # ------------------------------------
    # region - Boxplot
    # ------------------------------------

    def test_boxplot_default_output(self):
        """Test default boxplot SVG generation."""
        data = chart_sampler.boxplot()
        result = chartviz.boxplot(data)

        assert result is not None
        assert isinstance(result, str)
        assert _is_svg_str(result)

    def test_boxplot_svg_output(self):
        """Test explicit boxplot SVG generation."""
        data = chart_sampler.boxplot()
        result = chartviz.boxplot(data, output="svg")

        assert result is not None
        assert isinstance(result, str)
        assert _is_svg_str(result)

    def test_boxplot_png_output(self):
        """Test boxplot PNG generation."""
        data = chart_sampler.boxplot()
        result = chartviz.boxplot(data, output="png")

        assert result is not None
        assert isinstance(result, bytes)
        assert result.startswith(b"\x89PNG\r\n\x1a\n")

    def test_boxplot_url_output(self):
        """Test boxplot URL generation."""
        data = chart_sampler.boxplot()
        result = chartviz.boxplot(data, output="url")

        assert result is not None
        assert isinstance(result, str)
        assert result.startswith("viz/chart/boxplot")

    # endregion
    # ------------------------------------
    # region - Histogram
    # ------------------------------------

    def test_histogram_default_output(self):
        """Test default histogram SVG generation."""
        data = chart_sampler.histogram()
        result = chartviz.histogram(data)

        assert result is not None
        assert isinstance(result, str)
        assert _is_svg_str(result)

    def test_histogram_svg_output(self):
        """Test explicit histogram SVG generation."""
        data = chart_sampler.histogram()
        result = chartviz.histogram(data, output="svg")

        assert result is not None
        assert isinstance(result, str)
        assert _is_svg_str(result)

    def test_histogram_png_output(self):
        """Test histogram PNG generation."""
        data = chart_sampler.histogram()
        result = chartviz.histogram(data, output="png")

        assert result is not None
        assert isinstance(result, bytes)
        assert result.startswith(b"\x89PNG\r\n\x1a\n")

    def test_histogram_url_output(self):
        """Test histogram URL generation."""
        data = chart_sampler.histogram()
        result = chartviz.histogram(data, output="url")

        assert result is not None
        assert isinstance(result, str)
        assert result.startswith("viz/chart/histogram")

    # endregion
    # ------------------------------------


class TestChartvizParameters:
    """Test parameter validation and handling."""

    def test_url_parameters(self):
        """Test chart and axis title parameters."""
        data = chart_sampler.bar()
        url = chartviz.bar(
            data,
            width=800,
            height=600,
            title="Test Chart",
            subtitle="Test Subtitle",
            x_title="X Axis",
            y_title="Y Axis",
            x_prefix="X-prefix",
            y_prefix="Y-prefix",
            x_suffix="X-suffix",
            y_suffix="Y-suffix",
            output="url",
            omit_legend=True,
            scale=2.0,
        )

        assert "width=800" in url
        assert "height=600" in url
        assert "title=Test+Chart" in url
        assert "subtitle=Test+Subtitle" in url
        assert "x_title=X+Axis" in url
        assert "y_title=Y+Axis" in url
        assert "x_prefix=X-prefix" in url
        assert "y_prefix=Y-prefix" in url
        assert "x_suffix=X-suffix" in url
        assert "y_suffix=Y-suffix" in url
        assert "omit_legend=1" in url
        assert "scale=2.0" in url

    def test_horizontal_parameter(self):
        """Test horizontal orientation for applicable charts."""
        data = chart_sampler.bar()

        # Bar chart horizontal
        url_bar = chartviz.bar(data, horizontal=True, output="url")
        assert "horizontal=1" in url_bar

        # Line chart horizontal
        line_data = chart_sampler.line()
        url_line = chartviz.line(line_data, horizontal=True, output="url")
        assert "horizontal=1" in url_line

        # Histogram horizontal
        hist_data = chart_sampler.histogram()
        url_hist = chartviz.histogram(hist_data, horizontal=True, output="url")
        assert "horizontal=1" in url_hist

        # Boxplot horizontal
        box_data = chart_sampler.boxplot()
        url_box = chartviz.boxplot(box_data, horizontal=True, output="url")
        assert "horizontal=1" in url_box


class TestChartvizSpecificParameters:
    """Test chart-specific parameters."""

    def test_boxplot_specific_parameters(self):
        """Test boxplot-specific parameters."""
        data = chart_sampler.boxplot()

        # Test show_points parameter
        url_points = chartviz.boxplot(data, show_points=True, output="url")
        assert "show_points=1" in url_points

        # Test boxmean parameter with different values
        url_mean_true = chartviz.boxplot(data, boxmean=True, output="url")
        assert "boxmean=1" in url_mean_true

        url_mean_sd = chartviz.boxplot(data, boxmean="sd", output="url")
        assert "boxmean=sd" in url_mean_sd

    def test_histogram_specific_parameters(self):
        """Test histogram-specific parameters."""
        data = chart_sampler.histogram()

        url_overlay = chartviz.histogram(data, barmode="overlay", output="url")
        assert "barmode" not in url_overlay  # Default

        url_stack = chartviz.histogram(data, barmode="stack", output="url")
        assert "barmode=stack" in url_stack

        url_group = chartviz.histogram(data, barmode="group", output="url")
        assert "barmode=group" in url_group

        url_relative = chartviz.histogram(data, barmode="relative", output="url")
        assert "barmode=relative" in url_relative


class TestChartvizErrorHandling:
    """Test error handling and validation."""

    def test_invalid_output_format(self):
        """Test invalid output format handling."""
        data = chart_sampler.bar()

        # Invalid output format should fallback to 'svg' with warning
        result = chartviz.bar(data, output="invalid")

        assert result is not None
        assert isinstance(result, str)
        assert _is_svg_str(result)

    def test_empty_data_handling(self):
        """Test handling of empty or invalid data."""
        # Empty list
        empty_data = []
        result = chartviz.bar(empty_data)
        assert result is None

        # Invalid data structure
        invalid_data = [{"invalid": "structure"}]
        result = chartviz.bar(invalid_data)
        assert result is not None
        assert isinstance(result, str)
        assert _is_svg_str(result)

    def test_invalid_parameters(self):
        """Test invalid parameter handling."""
        data = chart_sampler.bar()

        # Test negative dimensions
        result_negative_width = chartviz.bar(data, width=-100, height=-50)
        assert result_negative_width is not None
        assert isinstance(result_negative_width, str)
        assert _is_svg_str(result_negative_width)

        # Test zero dimensions
        result_zero_dimensions = chartviz.bar(data, width=0, height=0)
        assert result_zero_dimensions is not None
        assert isinstance(result_zero_dimensions, str)
        assert _is_svg_str(result_zero_dimensions)

        # Test invalid scale
        result_negative_scale = chartviz.bar(data, scale=-1.0)
        assert result_negative_scale is not None
        assert isinstance(result_negative_scale, str)
        assert _is_svg_str(result_negative_scale)


class TestChartvizIntegration:
    """Test integration scenarios and complex usage."""

    def test_all_output_types_consistency(self):
        """Test that all output types work consistently across chart types."""
        data = chart_sampler.bar()

        # SVG should return string
        svg_result = chartviz.bar(data, output="svg")
        assert isinstance(svg_result, str)

        # PNG should return bytes
        png_result = chartviz.bar(data, output="png")
        assert isinstance(png_result, bytes)

        # URL should return string
        url_result = chartviz.bar(data, output="url")
        assert isinstance(url_result, str)

    def test_parameter_types(self):
        """Test parameter type handling."""
        data = chart_sampler.bar()

        # Test that numeric parameters accept different types
        result = chartviz.bar(data, width=600, height=450)
        assert result is not None

        # Test float scale
        result_scale = chartviz.bar(data, scale=1.5)
        assert result_scale is not None

    def test_complex_data_structures(self):
        """Test complex data structures for different chart types."""
        # Grouped boxplot data using chart_sampler with groups
        grouped_boxplot_data = chart_sampler.boxplot(trace_count=2, group_count=3)

        result = chartviz.boxplot(grouped_boxplot_data)
        assert result is not None
        assert _is_svg_str(result)


# ------------------------------------
# Helper functions
# ------------------------------------


def _is_svg_str(result: any):
    """Check if result is a valid SVG string."""
    if isinstance(result, str):
        if (
            # 2D output
            result.startswith("<?xml version='1.0' encoding='iso-8859-1'?>\n<svg")
            # 3D output
            or result.startswith('<?xml version="1.0" encoding="UTF-8"?>\n<svg')
            # Just in case
            or result.startswith("<svg")
        ):
            if "</svg>" in result:
                return True
    return False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
