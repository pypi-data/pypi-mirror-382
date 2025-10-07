# NOT YET IMPLEMENTED - this is specific openad magic
# command handling and may need to be rethought.

"""
Dataframe functions for OMGUI API endpoints.
"""

import pandas as pd
from IPython import get_ipython


# from openad.helpers.files import open_file
def open_file(cache_path, return_err):
    pass  # Placeholder, to be replaced


from omgui import ctx
from omgui.gui.workers.smol_functions import (
    df_has_molecules,
    flatten_smol,
    create_molset_cache_file,
    assemble_cache_path,
    read_molset_from_cache,
)
from omgui.gui.workers.smol_transformers import dataframe2molset
from omgui.util.mol_utils import create_molset_response


def get_dataframe(df_name, query):
    """
    Fetch the data from a dataframe referred to in a magic command.
    """

    if ctx().vars:
        df = ctx().vars.get(df_name)
        if df is not None and not df.empty:
            # Dataframe has molecules -> load as molset
            if df_has_molecules(df):
                # Turn dataframe into molset
                molset = dataframe2molset(df)

                # Create cache working copy
                cache_id = create_molset_cache_file(molset)

                # Read molset from cache
                try:
                    molset = read_molset_from_cache(cache_id)
                except ValueError as err:
                    return f"get_result() -> {err}", 500

                return {
                    "type": "molset",
                    "data": create_molset_response(molset, query, cache_id),
                }, 200

            # Dataframe has no molecules -> load dataviewer
            else:
                table = []
                for i, row in df.iterrows():
                    mol = {}
                    for col in df.columns:
                        mol[col] = None if pd.isna(row[col]) else row[col]
                    table.append(mol)

                # TO DO: Implement dataviewer here
                return {"type": "data", "data": table}, 200

    return {"type": "empty"}, 200


def update_dataframe_molset(df_name, cache_id):
    """
    Save changes to a datraframe referred to in a magic command.
    """

    if not cache_id:
        return (
            f"update_dataframe_molset() -> Unrecognized cache_id: {cache_id}",
            500,
        )

    # Read data from cache.
    cache_path = assemble_cache_path("molset", cache_id)
    molset, err_code = open_file(cache_path, return_err="code")
    if err_code:
        return err_code, 500

    # Flatten the mol dictionaries.
    molset = [flatten_smol(mol) for mol in molset]

    # Store the columns of the current result table,
    # so we can recreate them when overwriting the result.
    df = ctx().vars.get(df_name)
    columns = df.columns.tolist()

    # Create new table.
    table = []
    for mol in molset:
        row = {}
        for i, col in enumerate(columns):
            row[col] = mol.get(col)
        table.append(row)

    # Write data back to the Notebook variable.
    df = pd.DataFrame(table)
    ipython = get_ipython()
    ipython.user_ns[df_name] = df

    return "ok", 200
