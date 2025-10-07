"""
Comprehensive tests for omgui.molviz module.

Tests both 2D and 3D molecule visualization functionality including:
- Parameter validation
- Output format handling (SVG, PNG, URL)
- 3D specific parameters
- Error handling
- Integration with omgui server
"""

import pytest
from omgui import molviz
from omgui.molviz import defaults as d


class TestMolvizBasicFunctionality:
    """Test basic 2D and 3D molecule visualization."""

    def test_d2_default_output(self):
        """Test default 2D SVG generation."""
        result = molviz.d2("CCO")

        assert result is not None
        assert isinstance(result, str)
        assert _is_svg_str(result)

    def test_d2_svg_output(self):
        """Test explicit 2D SVG generation."""
        result = molviz.d2("CCO", output="svg")

        assert result is not None
        assert isinstance(result, str)
        assert _is_svg_str(result)

    def test_d2_png_output(self):
        """Test 2D PNG generation."""
        result = molviz.d2("CCO", output="png")

        assert result is not None
        assert isinstance(result, bytes)
        assert result.startswith(b"\x89PNG\r\n\x1a\n")

    def test_d2_url_output(self):
        """Test 2D URL generation."""
        result = molviz.d2("CCO", output="url")

        assert result is not None
        assert isinstance(result, str)
        assert result.startswith("http")
        assert "CCO" in result
        assert "viz/mol" in result

    def test_d3_default_output(self):
        """Test default 3D SVG generation."""
        result = molviz.d3("CCO")

        assert result is not None
        assert isinstance(result, str)
        assert _is_svg_str(result)

    def test_d3_svg_output(self):
        """Test explicit 3D SVG generation."""
        result = molviz.d3("CCO")

        assert result is not None
        assert isinstance(result, str)
        assert _is_svg_str(result)

    def test_d3_png_output(self):
        """Test 3D PNG generation."""
        result = molviz.d3("CCO", output="png")

        assert result is not None
        assert isinstance(result, bytes)
        assert result.startswith(b"\x89PNG\r\n\x1a\n")

    def test_d3_url_output(self):
        """Test 3D URL generation."""
        result = molviz.d3("CCO", output="url")

        assert result is not None
        assert isinstance(result, str)
        assert result.startswith("http")
        assert "CCO" in result
        assert "d3=1" in result.lower()


class TestMolvizParameters:
    """Test parameter validation and handling."""

    def test_custom_dimensions(self):
        """Test custom width and height parameters."""
        url = molviz.d2("CCO", width=800, height=600, output="url")

        assert "width=800" in url
        assert "height=600" in url

    def test_highlight_parameter(self):
        """Test SMARTS highlighting functionality."""
        # Test with CO substructure
        url = molviz.d2("CCO", highlight="CO", output="url")
        assert "highlight=CO" in url

        # Test with more complex SMARTS
        url = molviz.d2("CC(C)O", highlight="O", output="url")
        assert "highlight=O" in url

    def test_d3_style_parameters(self):
        """Test all 3D style options."""
        styles = ["BALL_AND_STICK", "SPACEFILLING", "TUBE", "WIREFRAME"]

        for style in styles:
            url = molviz.d3("CCO", d3_style=style, output="url")
            if style == d.D3_STYLE:
                assert "d3_style" not in url
            else:
                assert f"d3_style={style}" in url

    def test_d3_look_parameters(self):
        """Test 3D look options."""
        looks = ["CARTOON", "GLOSSY"]

        for look in looks:
            url = molviz.d3("CCO", d3_look=look, output="url")
            if look == d.D3_LOOK:
                assert "d3_look" not in url
            else:
                assert f"d3_look={look}" in url

    def test_d3_rotation_parameters(self):
        """Test 3D rotation parameters."""
        url = molviz.d3(
            "CCO",
            d3_rot_x=1.0,
            d3_rot_y=1.5,
            d3_rot_z=2.0,
            output="url",
        )

        assert "d3_rot_x=1.0" in url
        assert "d3_rot_y=1.5" in url
        assert "d3_rot_z=2.0" in url


class TestMolvizMoleculeTypes:
    """Test different types of molecule inputs."""

    def test_simple_molecules(self):
        """Test simple molecule SMILES."""
        molecules = [
            "CCO",  # ethanol
            "C=C",  # ethene
            "C1=CC=CC=C1",  # benzene
            "CC(C)O",  # isopropanol
        ]

        for smiles in molecules:
            # Test 2D
            result_2d = molviz.d2(smiles)
            assert result_2d is not None
            assert isinstance(result_2d, str)

            # Test 3D
            result_3d = molviz.d3(smiles)
            assert result_3d is not None
            assert isinstance(result_3d, str)

    def test_complex_molecules(self):
        """Test more complex molecule SMILES."""
        complex_molecules = [
            "CC(C)(C)c1ccc(O)cc1",  # BHT (antioxidant)
            "CN1CCC[C@H]1c2cccnc2",  # nicotine
            "CC(=O)Oc1ccccc1C(=O)O",  # aspirin
        ]

        for smiles in complex_molecules:
            # Should not raise exceptions
            url = molviz.d2(smiles, output="url")
            assert url is not None
            assert smiles in url


class TestMolvizErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_smiles(self):
        """Test graceful handling of invalid SMILES strings for both 2D and 3D."""
        invalid_smiles = [
            "INVALID",
            "C(C(C",  # unbalanced parentheses
            "",  # empty string
        ]

        for invalid in invalid_smiles:
            # Should handle gracefully without raising exceptions
            result_2d_svg = molviz.d2(invalid, output="svg")
            result_2d_png = molviz.d2(invalid, output="png")
            result_2d_url = molviz.d2(invalid, output="url")
            result_3d_svg = molviz.d3(invalid, output="svg")
            result_3d_png = molviz.d3(invalid, output="png")
            result_3d_url = molviz.d3(invalid, output="url")

            # All should return something (error content)
            results = [
                result_2d_svg,
                result_2d_png,
                result_2d_url,
                result_3d_svg,
                result_3d_png,
                result_3d_url,
            ]
            for result in results:
                assert result is not None

            # Test 2D SVG error format
            assert isinstance(result_2d_svg, str)
            assert _is_svg_str(result_2d_svg)
            assert "Invalid SMILES input" in result_2d_svg
            assert f'width="{d.WIDTH}"' in result_2d_svg  # default width
            assert f'height="{d.HEIGHT}"' in result_2d_svg  # default height
            assert 'fill="#f8f8f8"' in result_2d_svg  # background color
            assert 'stroke="#ddd"' in result_2d_svg  # border color

            # Test 3D SVG error format
            assert isinstance(result_3d_svg, str)
            assert _is_svg_str(result_3d_svg)
            assert "Invalid SMILES input" in result_3d_svg

            # Test PNG error format (both 2D and 3D)
            assert isinstance(result_2d_png, bytes)
            assert result_2d_png.startswith(b"\x89PNG\r\n\x1a\n")
            assert isinstance(result_3d_png, bytes)
            assert result_3d_png.startswith(b"\x89PNG\r\n\x1a\n")

            # Test URL format (both 2D and 3D)
            assert isinstance(result_2d_url, str)
            assert isinstance(result_3d_url, str)

        # Test custom dimensions are preserved in error SVGs
        custom_result = molviz.d2("INVALID", output="svg", width=800, height=600)
        assert 'width="800"' in custom_result
        assert 'height="600"' in custom_result

    def test_invalid_parameters(self):
        """Test invalid parameter handling with graceful fallback to defaults."""
        # Test negative width - should fallback to default width
        result_neg_width = molviz.d2("CCO", width=-100, output="url")
        assert result_neg_width is not None
        assert isinstance(result_neg_width, str)
        assert "width" not in result_neg_width

        # Test zero width - should fallback to default width
        result_zero_width = molviz.d2("CCO", width=0, output="url")
        assert result_zero_width is not None
        assert isinstance(result_zero_width, str)
        assert "width" not in result_zero_width

        # Test negative height - should fallback to default height
        result_neg_height = molviz.d2("CCO", height=-50, output="url")
        assert result_neg_height is not None
        assert isinstance(result_neg_height, str)
        assert "height" not in result_neg_height

        # Test zero height - should fallback to default height
        result_zero_height = molviz.d2("CCO", height=0, output="url")
        assert result_zero_height is not None
        assert isinstance(result_zero_height, str)
        assert "height" not in result_zero_height

        # Test that 2D SVG output also respects the corrected dimensions
        result_svg = molviz.d2("CCO", width=-100, height=0, output="svg")
        assert result_svg is not None
        assert isinstance(result_svg, str)
        # Note different rendering between 2D and 3D libs (see below)
        assert f"width='{d.WIDTH}px'" in result_svg
        assert f"height='{d.HEIGHT}px'" in result_svg

        # Test that 3D SVG output also respects the corrected dimensions
        result_svg = molviz.d3("CCO", width=-100, height=0, output="svg")
        assert result_svg is not None
        assert isinstance(result_svg, str)
        # Note different rendering between 2D and 3D libs (see above)
        assert f'width="{d.WIDTH}"' in result_svg
        assert f'height="{d.HEIGHT}"' in result_svg

    def test_invalid_output_format(self):
        """Test invalid output format handling."""
        # Invalid output format should fallback to 'svg' with warning
        result = molviz.d2("CCO", output="invalid")
        assert result is not None
        assert isinstance(result, str)
        assert _is_svg_str(result)

        # Test 3D as well
        result_3d = molviz.d3("CCO", output="invalid")
        assert result_3d is not None
        assert isinstance(result_3d, str)
        assert _is_svg_str(result)


class TestMolvizIntegration:
    """Test integration with omgui server."""

    def test_server_url_generation(self):
        """Test that URLs point to correct server endpoints."""
        url = molviz.d2("CCO", output="url")

        # Should contain proper server endpoint
        assert "/viz/mol/" in url
        assert "CCO" in url

    def test_url_accessibility(self):
        """Test that generated URLs are properly formatted."""
        molecules = ["CCO", "C=C", "C1=CC=CC=C1"]

        for smiles in molecules:
            url_2d = molviz.d2(smiles, output="url")
            url_3d = molviz.d3(smiles, output="url")

            # URLs should be properly formatted
            assert url_2d.startswith("http")
            assert url_3d.startswith("http")
            assert smiles in url_2d
            assert smiles in url_3d

            # 3D URL should have d3 parameter
            assert "d3=1" in url_3d.lower()


class TestMolvizDocumentationExamples:
    """Test all examples from the documentation."""

    def test_tldr_examples(self):
        """Test the Tl;dr examples from documentation."""
        # These are the exact examples from the docs

        # URL examples
        url_2d = molviz.d2("CCO", highlight="CO", output="url")
        url_3d = molviz.d3("CCO", highlight="CO", output="url")

        assert isinstance(url_2d, str)
        assert isinstance(url_3d, str)
        assert "highlight=CO" in url_2d
        assert "highlight=CO" in url_3d

        # SVG examples
        svg_2d = molviz.d2("CCO", highlight="CO")
        assert isinstance(svg_2d, str)
        assert _is_svg_str(svg_2d)

        # PNG examples
        png_2d = molviz.d2("CCO", highlight="CO", output="png")
        assert isinstance(png_2d, bytes)

        # 3D examples
        svg_3d = molviz.d3("CCO", width=300, height=200)
        assert isinstance(svg_3d, str)

        # Fixed rotation example
        svg_3d_fixed = molviz.d3(
            "CCO",
            width=300,
            height=200,
            d3_rot_x=1,
            d3_rot_y=1.5,
            d3_rot_z=2,
        )
        assert isinstance(svg_3d_fixed, str)

    def test_parameter_table_examples(self):
        """Test parameter combinations from the documentation table."""
        # Test all parameter combinations work
        result = molviz.d2("CCO", output="svg", width=800, height=600, highlight="CO")
        assert result is not None

        # Test 3D parameters
        result_3d = molviz.d3(
            "CCO",
            output="svg",
            width=400,
            height=300,
            highlight="O",
            d3_style="SPACEFILLING",
            d3_look="GLOSSY",
            d3_rot_random=True,
            d3_rot_x=2.0,
            d3_rot_y=3.0,
            d3_rot_z=1.5,
        )
        assert result_3d is not None


class TestMolvizTypes:
    """Test type annotations and return types."""

    def test_return_types(self):
        """Test that functions return expected types."""
        # SVG should return string
        svg_result = molviz.d2("CCO", output="svg")
        assert isinstance(svg_result, str)

        # PNG should return bytes
        png_result = molviz.d2("CCO", output="png")
        assert isinstance(png_result, bytes)

        # URL should return string
        url_result = molviz.d2("CCO", output="url")
        assert isinstance(url_result, str)

    def test_parameter_types(self):
        """Test parameter type handling."""
        # Test that numeric parameters accept different types
        result = molviz.d2("CCO", width=600, height=450)
        assert result is not None

        # Test float rotations
        result_3d = molviz.d3("CCO", d3_rot_x=1.5, d3_rot_y=2.0, d3_rot_z=0.5)
        assert result_3d is not None


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
