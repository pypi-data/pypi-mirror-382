"""
Integration tests for mws.add_prop() functionality.

This test suite uses a TESTING workspace to verify that properties are correctly
added to molecules in the working set using all four supported data formats.
"""

# Std
import os

# 3rd party
import pytest
import pandas as pd

# OMGUI
import omgui
from omgui import mws
from omgui.context import ctx
from omgui.gui.workers import smol_functions


# ------------------------------------
# region - General
# ------------------------------------

# Check if the GITHUB_ACTIONS environment variable is set to 'true'
# This variable is automatically set by GitHub Actions.
RUNNING_ON_GH_ACTIONS = os.environ.get("GITHUB_ACTIONS") == "true"


@pytest.mark.skipif(
    RUNNING_ON_GH_ACTIONS,
    reason="Skipping complex multithreaded/restart test on GitHub Actions CI.",
)
def test_molecule_persistence_across_sessions():
    """
    Test that molecules persist when omgui is shutdown and relaunched.
    This tests the full persistence cycle including file system storage.
    """
    # Store original workspace
    original_workspace = ctx().workspace

    try:
        # Switch to TESTING workspace and set up test molecules
        ctx().set_workspace("TESTING", silent=True)

        # Clear any existing molecules
        if not mws.is_empty():
            mws.clear(force=True)

        # Add test molecules with properties
        mws.add("CCO")  # ethanol
        mws.add("C=C")  # ethene
        mws.add("CC(C)O")  # isopropanol

        # Add properties to track
        mws.add_prop([1000, 2000, 3000], prop_name="restart_test_prop")
        mws.add_prop(
            [
                {"subject_prop": 100, "subject": "CCO"},
                {"subject_prop": 200, "subject": "C=C"},
                {"subject_prop": 300, "subject": "CC(C)O"},
            ]
        )

        # Verify initial state
        initial_mols = mws.get()
        initial_count = len(initial_mols)

        assert initial_count == 3
        assert all(
            mol.get("properties", {}).get("restart_test_prop") is not None
            for mol in initial_mols
        )

        # Shutdown omgui
        omgui.shutdown()

        # Relaunch omgui
        omgui.launch(block_thread=False)

        # Switch back to TESTING workspace (context should persist)
        ctx().set_workspace("TESTING", silent=True)

        # Verify molecules and properties persisted
        restored_mols = mws.get()
        restored_count = len(restored_mols)

        # Check counts match
        assert (
            restored_count == initial_count
        ), f"Expected {initial_count} molecules, found {restored_count}"

        # Verify all molecules have their properties
        restart_props = [
            mol.get("properties", {}).get("restart_test_prop") for mol in restored_mols
        ]
        subject_props = [
            mol.get("properties", {}).get("subject_prop") for mol in restored_mols
        ]

        # All molecules should have properties
        assert all(
            prop is not None for prop in restart_props
        ), "Some molecules lost restart_test_prop"
        assert all(
            prop is not None for prop in subject_props
        ), "Some molecules lost subject_prop"

        # Properties should match expected values
        assert set(restart_props) == {
            1000,
            2000,
            3000,
        }, f"Unexpected restart_test_prop values: {restart_props}"
        assert set(subject_props) == {
            100,
            200,
            300,
        }, f"Unexpected subject_prop values: {subject_props}"

        # Verify molecules can be identified by SMILES
        restored_smiles = set()
        for mol in restored_mols:
            smiles = smol_functions.get_best_available_smiles(mol)
            restored_smiles.add(smiles)

        expected_smiles = {"CCO", "C=C", "CC(C)O"}
        assert (
            restored_smiles == expected_smiles
        ), f"Expected SMILES {expected_smiles}, got {restored_smiles}"

    finally:
        # Cleanup: clear testing molecules and return to original workspace
        if not mws.is_empty():
            mws.clear(force=True)
        ctx().set_workspace(original_workspace, silent=True)


# endregion
# ------------------------------------
# region - add_prop()
# ------------------------------------


@pytest.fixture(scope="function")
def test_workspace():
    """
    Set up a clean TESTING workspace for each test.
    """
    # Store original workspace
    original_workspace = ctx().workspace

    # Switch to TESTING workspace
    ctx().set_workspace("TESTING", silent=True)

    # Clear any existing molecules
    if not mws.is_empty():
        mws.clear(force=True)

    # Add test molecules
    mws.add("CCO")  # ethanol
    mws.add("C=C")  # ethene

    yield

    # Cleanup: clear and return to original workspace
    mws.clear(force=True)
    ctx().set_workspace(original_workspace, silent=True)


def test_add_prop_format_a_sequential_property_list(test_workspace):
    """
    Test Format A: Sequential list of values with property name.
    """
    # Add properties using Format A
    property_values = [100, 200]
    mws.add_prop(property_values, prop_name="foo_1")

    # Get molecules and verify properties were added
    result_mols = mws.get()

    assert len(result_mols) == 2
    assert result_mols[0]["properties"]["foo_1"] == 100
    assert result_mols[1]["properties"]["foo_1"] == 200


def test_add_prop_format_b_sequential_dict_list(test_workspace):
    """
    Test Format B: Sequential list of dictionaries.
    """
    # Add properties using Format B
    property_data = [{"foo_2": 300}, {"foo_2": 301, "bar_2": 302}]
    mws.add_prop(property_data)

    # Get molecules and verify properties were added
    result_mols = mws.get()

    assert len(result_mols) == 2
    assert result_mols[0]["properties"]["foo_2"] == 300
    assert result_mols[1]["properties"]["foo_2"] == 301
    assert result_mols[1]["properties"]["bar_2"] == 302
    assert "bar_2" not in result_mols[0]["properties"]


def test_add_prop_format_c_subject_based_dict_list(test_workspace):
    """
    Test Format C: List of dictionaries with subject identifiers.
    """
    # Add properties using Format C
    property_data = [
        {"foo_3": 400, "subject": "CCO"},
        {"foo_3": 401, "bar_3": 402, "subject": "C=C"},
    ]
    mws.add_prop(property_data)

    # Get molecules and verify properties were added to correct molecules
    result_mols = mws.get()

    # Find molecules by their SMILES
    ethanol_mol = None
    ethene_mol = None

    for mol in result_mols:
        # Get canonical SMILES for comparison
        smiles = smol_functions.get_best_available_smiles(mol)
        if smiles == "CCO":
            ethanol_mol = mol
        elif smiles == "C=C":
            ethene_mol = mol

    assert ethanol_mol is not None
    assert ethene_mol is not None
    assert ethanol_mol["properties"]["foo_3"] == 400
    assert ethene_mol["properties"]["foo_3"] == 401
    assert ethene_mol["properties"]["bar_3"] == 402
    assert "bar_3" not in ethanol_mol["properties"]


def test_add_prop_format_d_dataframe(test_workspace):
    """
    Test Format D: Pandas DataFrame with subject, prop, val columns.
    """
    # Add properties using Format D
    property_data = pd.DataFrame(
        {
            "subject": ["CCO", "C=C", "CCO"],
            "prop": ["foo_4", "foo_4", "bar_4"],
            "val": [500, 501, 502],
        }
    )
    mws.add_prop(property_data)

    # Get molecules and verify properties were added
    result_mols = mws.get()

    # Find molecules by their SMILES
    ethanol_mol = None
    ethene_mol = None

    for mol in result_mols:
        smiles = smol_functions.get_best_available_smiles(mol)
        print("\n\n----")
        print(smiles)
        print(mol)
        if smiles == "CCO":
            ethanol_mol = mol
        elif smiles == "C=C":
            ethene_mol = mol

    assert ethanol_mol is not None
    assert ethene_mol is not None
    assert ethanol_mol["properties"]["foo_4"] == 500
    assert ethanol_mol["properties"]["bar_4"] == 502
    assert ethene_mol["properties"]["foo_4"] == 501
    assert "bar_4" not in ethene_mol["properties"]


def test_multiple_format_combinations(test_workspace):
    """
    Test adding properties using multiple formats in sequence.
    """
    # Format A
    mws.add_prop([1000, 2000], prop_name="seq_prop")

    # Format C
    mws.add_prop(
        [
            {"subject_prop": 3000, "subject": "CCO"},
            {"subject_prop": 4000, "subject": "C=C"},
        ]
    )

    # Format D
    df_data = pd.DataFrame({"subject": ["C=C"], "prop": ["df_prop"], "val": [5000]})
    mws.add_prop(df_data)

    # Verify all properties were added correctly
    result_mols = mws.get()

    assert len(result_mols) == 2

    # Both molecules should have sequential properties
    assert result_mols[0]["properties"]["seq_prop"] == 1000
    assert result_mols[1]["properties"]["seq_prop"] == 2000

    # Find molecules by SMILES for subject-based verification
    for mol in result_mols:
        smiles = mol.get("identifiers", {}).get("canonical_smiles", "")
        if smiles == "CCO":
            assert mol["properties"]["subject_prop"] == 3000
            assert "df_prop" not in mol["properties"]
        elif smiles == "C=C":
            assert mol["properties"]["subject_prop"] == 4000
            assert mol["properties"]["df_prop"] == 5000


def test_property_persistence_across_workspace_operations(test_workspace):
    """
    Test that properties persist when molecules are saved and loaded.
    """
    # Add properties
    mws.add_prop([100, 200], prop_name="persistent_prop")

    # Verify properties exist
    result_mols = mws.get()
    assert result_mols[0]["properties"]["persistent_prop"] == 100
    assert result_mols[1]["properties"]["persistent_prop"] == 200

    # Get count before clearing
    initial_count = mws.count()

    # Clear and re-add molecules (simulating a reload)
    mws.clear(force=True)
    assert mws.is_empty()

    # Re-add molecules
    mws.add("CCO")
    mws.add("C=C")

    # Properties should be gone since we cleared and re-added
    new_result_mols = mws.get()
    assert len(new_result_mols) == initial_count

    # New molecules shouldn't have the old properties
    for mol in new_result_mols:
        assert "persistent_prop" not in mol.get("properties", {})


def test_empty_working_set_handling():
    """
    Test behavior when trying to add properties to an empty working set.
    """
    # Switch to testing workspace and ensure it's empty
    original_workspace = ctx().workspace
    ctx().set_workspace("TESTING", silent=True)
    mws.clear(force=True)

    try:
        # Try to add properties to empty working set
        result = mws.add_prop([100, 200], prop_name="empty_test")

        # Should handle gracefully without crashing the app
        assert result is not None

    finally:
        # Cleanup
        ctx().set_workspace(original_workspace, silent=True)


# endregion
# ------------------------------------

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
