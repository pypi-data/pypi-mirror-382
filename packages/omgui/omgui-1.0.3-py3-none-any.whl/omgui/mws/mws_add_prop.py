"""
Adding property to molecules in the current working set.

- Sequential input (format A and B):
    Update all molecules at once, where the length of the
    input should match the length of the MWS.
- Non-sequential input (format C and D):
    Update molecules based on a unique identifier
    (only canonical smiles for now)

Supported data structures
-------------------------

Format A:
    mws.add_prop([1,2,3], "my_prop")

Format B:
    mws.add_prop([
        { "my_prop": 1 },
        { "my_prop": 2 },
        { "my_prop": 3 }
    ])

Format C:
    mws.add_prop([
        { "my_prop": 1, "subject": "CCO" },
        { "my_prop": 2, "subject": "CCN" },
        { "my_prop": 3, "subject": "C=C" }
    ])

Format D:
    mws.add_prop(df)
    Where df is a pandas DataFrame with the following columns:
      - subject/smiles: SMILES molecule identifier
      - prop/property: property name
      - val/value/result: property value
"""

# Std
import pandas as pd
from typing import Literal

# OMGUI
from omgui.spf import spf
from omgui.types import PropDataType
from omgui.mws.mws_core import mws_core
from omgui.util.logger import get_logger
from omgui.gui.workers import smol_functions


# Logger
logger = get_logger()


def add_prop(prop_data: PropDataType, prop_name: str = None) -> None:
    """
    Add property to molecules in the current working set.
    """
    mws = mws_core().get()

    # Format A
    if _is_format_a(prop_data, prop_name):
        logger.info("<green>Format A detected</green>")
        if _validate_list_length(mws, prop_data, prop_name):
            _add_from_format_a(mws, prop_data, prop_name)
            mws_core().save()
            return True

    # Format B
    if _is_format_b(prop_data):
        logger.info("<green>Format B detected</green>")
        if _validate_list_length(mws, prop_data):
            _add_from_format_b(mws, prop_data)
            mws_core().save()
            return True
        else:
            return False

    # Format C
    if _is_format_c(prop_data):
        logger.info("<green>Format C detected</green>")
        _add_from_format_c(mws, prop_data)
        mws_core().save()
        return True

    # Format D
    if isinstance(prop_data, pd.DataFrame):
        if _valid_df(prop_data):
            logger.info("<green>Format D detected</green>")
            _add_from_format_d(mws, prop_data)
            mws_core().save()
            return True
        else:
            spf.error("DataFrame structure is invalid")
            return False

    # FAIL - No valid format detected
    spf.error(
        [
            "Failed to add property to your working set - invalid input format",
            "Data should be formatted in one of four ways:",
            "A. List of property values with a property name, eg:",
            "   add_props(['val1', 'val2'], prop_name='my_prop')",
            "B. List of dictionaries with property name and value, eg:",
            "   add_props([{'my_prop': 'val1'}, {'my_prop': 'val2'}])",
            "C. List of dictionaries with property name, value and subject, eg:",
            "   add_props([{'my_prop': 'val1', 'subject': 'CCO'}, {'my_prop': 'val2', 'subject': 'CCN'}])",
            "D. Pandas DataFrame with required columns, eg:",
            "   add_props(df) where df has the required 'subject', 'prop' and 'val' columns",
        ]
    )
    return False


# ------------------------------------
# region - Detect format of input data
# ------------------------------------


def _is_format_a(prop_data: any, prop_name: str) -> bool:
    """
    Validates format A
    ------------------
    [ <val_1>, <val_2>, <val_3> ], prop_name
    """
    if isinstance(prop_data, list) and prop_name:
        return True
    return False


def _is_format_b(prop_data: any) -> bool:
    """
    Validates format B
    ------------------
    [
        { 'my_prop': <val_1> },
        { 'my_prop': <val_2> },
        { 'my_prop': <val_3> }
    ]
    """
    if isinstance(prop_data, list):
        if all(isinstance(item, dict) for item in prop_data):
            return True
    return False


def _is_format_c(prop_data: any) -> bool:
    """
    Validates format C
    ------------------
    [
        {
            'subject': <smiles_1>,
            'my_prop': <val_1>,
        },
        {
            'subject': <smiles_2>,
            'my_prop': <val_2>,
        }
    ]
    """
    if isinstance(prop_data, list):
        if all(isinstance(item, dict) for item in prop_data):
            if all("subject" in item for item in prop_data):
                return True
    return False


# endregion
# ------------------------------------
# region - Validate input data
# ------------------------------------


def _valid_df(prop_data: any) -> bool:
    """
    Validates format D
    ------------------
    Pandas DataFrame with columns:
    - subject / smiles
    - prop / property
    - val / value / result
    """
    if isinstance(prop_data, pd.DataFrame):
        df_columns_lower = [col.lower() for col in prop_data.columns]
        is_valid = True

        # Validate structure
        # fmt: off
        if not any(val in df_columns_lower for val in ["subject", "smiles"]):
            is_valid = False
            logger.error("DataFrame must contain a <yellow>subject<yellow> column with SMILES values")
        if not any(val in df_columns_lower for val in ["prop", "property"]):
            is_valid = False
            logger.error("DataFrame must contain a <yellow>prop<yellow> column with property names")
        if not any(val in df_columns_lower for val in ["val", "value", "result"]):
            is_valid = False
            logger.error("DataFrame must contain a <yellow>val<yellow> column with property values")
        # fmt: on

        return is_valid


def _validate_list_length(mws, prop_list: list, prop_name: str = None):
    """
    Make sure the length of the property list matches the working set.
    """
    if len(prop_list) != len(mws):
        qt = "'"
        spf.error(
            [
                f"Failed to add property {qt + prop_name + qt if prop_name else 'data'} to your working set.",
                f"Items in property list ({len(prop_list)}) does not match number of molecules in working set ({len(mws)}).",
            ]
        )
        return False
    return True


# endregion
# ------------------------------------
# region - Apply values
# ------------------------------------


def _add_from_format_a(mws, prop_data: list, prop_name: str) -> None:
    """
    Add property to molecules in the current working set
    from a list of values and a property name.

    Input:
        mws.add_prop([1,2,3], "my_prop")
    """
    _log_method(mws, "A", prop_name)
    for mol in mws:
        val = prop_data.pop(0)
        mol["properties"][prop_name] = val
        _log_prop(
            len(mws) - len(prop_data),
            None,
            prop_name,
            val,
            mol.get("name", smol_functions.get_best_available_smiles(mol)),
        )

    return True


def _add_from_format_b(mws, prop_data: list) -> None:
    """
    Add property to molecules in the current working set
    from a list of key-value dictionaries.

    Input:
        mws.add_prop([{ "my_prop": 1 }, { "my_prop": 2 }, { "my_prop": 3 }])
    """

    _log_method(mws, "B")
    for mol in mws:
        data = prop_data.pop(0)
        for i, (key, value) in enumerate(data.items()):
            mol["properties"][key] = value
            _log_prop(
                len(mws) - len(prop_data),
                i,
                key,
                value,
                mol.get("name", smol_functions.get_best_available_smiles(mol)),
            )

    return True


def _add_from_format_c(mws, prop_data: list) -> None:
    """
    Add property to molecules in the current working set
    from a list of key-value dictionaries with a subject.

    Input:
        mws.add_prop([
            { "my_prop": 1, "subject": "CCO" },
            { "my_prop": 2, "subject": "CCN" },
            { "my_prop": 3, "subject": "C=C" }
        ])
    """

    _log_method(mws, "C")
    for i, item in enumerate(prop_data, start=1):
        subject = item.get("subject")
        # Find the molecule in the working set
        mol_found = False
        for mol in mws:
            if (
                mol.get("name") == subject
                or smol_functions.get_best_available_smiles(mol) == subject
            ):  # TODO: revisit unique id
                for j, (key, val) in enumerate(item.items()):
                    if key == "subject":
                        continue
                    mol["properties"][key] = val
                    _log_prop(
                        i,
                        j,
                        key,
                        val,
                        subject,
                    )
                    mol_found = True
                break
        if not mol_found:
            logger.warning(
                "Skipping molecule with identifier <yellow>%s</yellow>, not found in working set.",
                subject,
            )

    return True


def _add_from_format_d(mws, prop_data: pd.DataFrame):
    df = prop_data

    # Define column names
    subject_col = "subject" if "subject" in df.columns else "smiles"
    property_col = "prop" if "prop" in df.columns else "property"
    value_col = (
        "val"
        if "val" in df.columns
        else ("value" if "value" in df.columns else "result")
    )

    _log_method(mws, "D")
    for i, row in df.iterrows():
        subject = row[subject_col]
        prop_name = row[property_col]
        val = row[value_col]

        # Find the molecule in the working set
        mol_found = False
        for mol in mws:
            if (
                mol.get("name") == subject
                or smol_functions.get_best_available_smiles(mol) == subject
            ):  # TODO: revisit unique id
                mol["properties"][prop_name] = val
                _log_prop(i, None, prop_name, val, subject)
                mol_found = True
                break
        if not mol_found:
            logger.warning(
                "Skipping <yellow>%s</yellow>, not found in working set.", subject
            )


# endregion
# ------------------------------------
# region - Logging
# ------------------------------------


def _log_method(
    mws: list[dict], fmt: Literal["A", "B", "C", "D"], prop_name: str = None
) -> None:
    prop = f"property '{prop_name}'" if prop_name else "property data"
    logger.info(
        "<yellow>Format %s --> Adding %s to %s molecules:</yellow>",
        fmt,
        prop,
        len(mws),
    )


def _log_prop(i: int, j: int | None, key: str, val: any, subject: str) -> None:
    j = f"{j}." if j is not None else ""
    logger.info(
        "%s.%s <yellow>%s</yellow>: <magenta>%s</magenta> - %s",
        i,
        j,
        key,
        val,
        subject,
    )


# endregion
# ------------------------------------
