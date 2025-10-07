"""
This file contains all the API endpoints consumed by the GUI.

http://0.0.0.0:8024/api/v1/<endpoint>
"""

# pylint: disable=missing-function-docstring

# Std
from urllib.parse import unquote

# FastAPI
from fastapi import APIRouter, Request, status

# OMGUI - Service modules
from omgui.gui.gui_services import srv_general
from omgui.gui.gui_services import srv_file_system
from omgui.gui.gui_services import srv_molecules
from omgui.gui.gui_services import srv_mws
from omgui.gui.gui_services import srv_result
from omgui.gui.gui_services import srv_dataframe

# OMGUI
from omgui import ctx, config
from omgui.mws.mws_core import mws_core
from omgui.util.logger import get_logger
from omgui.util import exceptions as omg_exc


logger = get_logger()

gui_router = APIRouter()

api_v1 = "/api/v1"

# ------------------------------------
# region - General
# ------------------------------------


@gui_router.get(f"{api_v1}/")
async def landing():
    return srv_general.landing()


@gui_router.get(f"{api_v1}/health")
async def health():
    return srv_general.health()


@gui_router.post(f"{api_v1}/exec-command")
async def exec_command(request: Request):
    body = await request.json()
    command = body.get("command")
    return srv_general.exec_command(command)


# endregion
# ------------------------------------
# region - Context / Config / Workspace
# ------------------------------------


@gui_router.get(f"{api_v1}/config")
async def get_config():
    return config.get_dict()


@gui_router.get(f"{api_v1}/context")
async def context():
    return ctx().get_dict()


@gui_router.get(f"{api_v1}/workspace/name")
async def get_workspace_name():
    return ctx().workspace


@gui_router.get(f"{api_v1}/workspace/list")
async def get_workspaces():
    current_workspace = ctx().workspace
    workspaces = ctx().workspaces()
    return {"current_workspace": current_workspace, "workspaces": workspaces}


@gui_router.post(f"{api_v1}/workspace/set")
async def set_workspace(request: Request):
    body = await request.json()
    workspace_name = body.get("workspace", "")
    return ctx().set_workspace(workspace_name)


@gui_router.post(f"{api_v1}/workspace/create")
async def create_workspace(request: Request):
    body = await request.json()
    workspace_name = body.get("workspace", "")
    return ctx().create_workspace(workspace_name)


# endregion
# ------------------------------------
# region - File system
# ------------------------------------


@gui_router.post(f"{api_v1}/file/list")
async def get_files(request: Request):
    body = await request.json()
    path = unquote(body.get("path", ""))
    return srv_file_system.get_files(path)


@gui_router.post(f"{api_v1}/file/get")
async def get_file(request: Request):
    body = await request.json()
    print(body.get("path"))
    print(unquote(body.get("path")))
    path = unquote(body.get("path", ""))
    query = body.get("query", {})
    return srv_file_system.get_file(path, query)


@gui_router.post(f"{api_v1}/file/open-os")
async def open_file_os(request: Request):
    body = await request.json()
    path_absolute = unquote(body.get("path_absolute", ""))
    success = srv_file_system.open_file_os(path_absolute)
    if not success:
        return {"success": False}, 400
    return {"success": True}


@gui_router.post(f"{api_v1}/file/delete")
async def delete_file(request: Request):
    body = await request.json()
    path_absolute = unquote(body.get("path_absolute", ""))
    return srv_file_system.delete_file(path_absolute)


# endregion
# ------------------------------------
# region - Molecules - Small molecules
# ------------------------------------


@gui_router.post(f"{api_v1}/smol")
async def get_smol_data(request: Request):
    body = await request.json()
    identifier = body.get("identifier")
    return srv_molecules.get_smol_data(identifier)


@gui_router.post(f"{api_v1}/smol/viz", status_code=status.HTTP_200_OK)
async def get_smol_viz_data(request: Request):
    body = await request.json()
    inchi_or_smiles = body.get("inchi_or_smiles")
    return srv_molecules.get_smol_viz_data(inchi_or_smiles)


@gui_router.post(f"{api_v1}/smol/enrich")
async def enrich_smol(request: Request):
    body = await request.json()
    smol = body.get("smol")
    return srv_molecules.enrich_smol(smol)


@gui_router.post(f"{api_v1}/smol/save-as-{{ext}}")
async def save_smol_as(ext: str, request: Request):
    body = await request.json()
    smol = body.get("smol")
    path = unquote(body.get("path", ""))
    new_file = body.get("newFile", False)
    force = body.get("force", False)

    # fmt: off
    # Map ext to the correct molecules_api method
    if ext == "json":
        return srv_molecules.save_mol(smol, path, new_file, force, format_as="mol_json")
    elif ext == "sdf":
        return srv_molecules.save_mol(smol, path, new_file, force, format_as="sdf")
    elif ext == "csv":
        return srv_molecules.save_mol(smol, path, new_file, force, format_as="csv")
    elif ext == "mdl":
        return srv_molecules.save_mol(smol, path, new_file, force, format_as="mdl")
    elif ext == "smiles":
        return srv_molecules.save_mol(smol, path, new_file, force, format_as="smiles")
    else:
        return f"Unknown file extension: {ext}", 400
    # fmt: on


# endregion
# ------------------------------------
# region - Molecules - Molsets
# ------------------------------------


@gui_router.post(f"{api_v1}/molset")
async def get_molset(request: Request):
    body = await request.json()
    cache_id = body.get("cacheId")
    query = body.get("query", {})
    return srv_molecules.get_molset(cache_id, query)


@gui_router.post(f"{api_v1}/molset/adhoc")
async def get_molset_adhoc(request: Request):
    body = await request.json()
    identifiers = body.get("identifiers", [])
    query = body.get("query", {})
    return srv_molecules.get_molset_adhoc(identifiers, query)


@gui_router.post(f"{api_v1}/molset/mol")
async def get_mol_data_from_molset(request: Request):
    body = await request.json()
    cache_id = body.get("cacheId")
    index = body.get("index", 1)
    return srv_molecules.get_mol_data_from_molset(cache_id, index)


@gui_router.post(
    f"{api_v1}/molset/adhoc-post",
    summary="Create an on-the-fly molset and return the Redis/memory ID",
)
async def post_molset_adhoc(request: Request):
    body = await request.json()
    identifiers = body.get("identifiers", [])
    query = body.get("query", {})
    return srv_molecules.post_molset_adhoc(identifiers, query)


@gui_router.post(f"{api_v1}/molset/remove-mol")
async def remove_from_molset(request: Request):
    body = await request.json()
    cache_id = body.get("cacheId")
    indices = body.get("indices", [])
    query = body.get("query", {})
    return srv_molecules.remove_from_molset(cache_id, indices, query)


@gui_router.post(f"{api_v1}/molset/clear-working-copy")
async def clear_molset_working_copy(request: Request):
    body = await request.json()
    cache_id = body.get("cacheId")
    return srv_molecules.clear_molset_working_copy(cache_id)


@gui_router.post(f"{api_v1}/molset/update")
async def update_molset(request: Request):
    body = await request.json()
    cache_id = body.get("cacheId")
    path = unquote(body.get("path", ""))
    new_file = False
    return srv_molecules.save_molset(cache_id, path, new_file)


@gui_router.post(f"{api_v1}/molset/save-as-json")
async def save_molset_as_json(request: Request):
    body = await request.json()
    cache_id = body.get("cacheId")
    path = unquote(body.get("path", ""))
    new_file = body.get("newFile", False)
    format_as = "molset_json"
    return srv_molecules.save_molset(cache_id, path, new_file, format_as)


@gui_router.post(f"{api_v1}/molset/save-as-sdf")
async def save_molset_as_sdf(request: Request):
    body = await request.json()
    cache_id = body.get("cacheId")
    path = unquote(body.get("path", ""))
    new_file = body.get("newFile", False)
    format_as = "sdf"
    remove_invalid_mols = body.get("removeInvalidMols", False)
    return srv_molecules.save_molset(
        cache_id, path, new_file, format_as, remove_invalid_mols
    )


@gui_router.post(f"{api_v1}/molset/save-as-csv")
async def save_molset_as_csv(request: Request):
    body = await request.json()
    cache_id = body.get("cacheId")
    path = unquote(body.get("path", ""))
    new_file = body.get("newFile", False)
    format_as = "csv"
    return srv_molecules.save_molset(cache_id, path, new_file, format_as)


@gui_router.post(f"{api_v1}/molset/save-as-smiles")
async def save_molset_as_smiles(request: Request):
    body = await request.json()
    cache_id = body.get("cacheId")
    path = unquote(body.get("path", ""))
    new_file = body.get("newFile", False)
    format_as = "smiles"
    return srv_molecules.save_molset(cache_id, path, new_file, format_as)


@gui_router.post(f"{api_v1}/molset/replace-mol")
async def replace_mol_in_molset(request: Request):
    body = await request.json()
    cache_id = body.get("cacheId")
    path = unquote(body.get("path", ""))
    mol = body.get("mol")
    _context = body.get("context")
    format_as = "molset_json" if _context == "json" else _context
    return srv_molecules.replace_mol_in_molset(cache_id, path, mol, format_as)


# endregion
# ------------------------------------
# region - Molecules - Macromolecules
# ------------------------------------


@gui_router.post(f"{api_v1}/mmol")
async def get_mmol_data(request: Request):
    body = await request.json()
    identifier = body.get("identifier")
    return srv_molecules.get_mmol_data(identifier)


@gui_router.post(f"{api_v1}/mmol/save-as-{{ext}}")
async def save_mmol_as(ext: str, request: Request):
    body = await request.json()
    mmol = body.get("mmol")
    path = unquote(body.get("path", ""))
    new_file = body.get("newFile", False)
    force = body.get("force", False)

    # fmt: off
    # Map ext to the correct molecules_api method
    if ext == "json":
        return srv_molecules.save_mol(mmol, path, new_file, force, format_as="mmol_json")
    elif ext == "cif":
        return srv_molecules.save_mol(mmol, path, new_file, force, format_as="cif")
    elif ext == "pdb":
        return srv_molecules.save_mol(mmol, path, new_file, force, format_as="pdb")
    else:
        return f"Unknown extension: {ext}", 400
    # fmt: on


# endregion
# ------------------------------------
# region - Result
# ------------------------------------


@gui_router.post(f"{api_v1}/result")
async def get_result(request: Request):
    body = await request.json()
    query = body.get("query", {})
    return srv_result.get_result(query)


@gui_router.post(f"{api_v1}/result/update")
async def update_result_molset(request: Request):
    body = await request.json()
    cache_id = body.get("cacheId", "")
    return srv_result.update_result_molset(cache_id)


# endregion
# ------------------------------------
# region - Molecule Working Set
# ------------------------------------


@gui_router.post(f"{api_v1}/mws")
async def get_mws(request: Request):
    body = await request.json()
    query = body.get("query", {})
    return srv_mws.get_cached_mws(query)


@gui_router.post(f"{api_v1}/mws/update")
async def update_mws(request: Request):
    body = await request.json()
    cache_id = body.get("cacheId")
    path = unquote(body.get("path", ""))
    new_file = False
    format_as = "mws"
    srv_molecules.save_molset(cache_id, path, new_file, format_as)
    return {"success": True}


@gui_router.post(f"{api_v1}/mws/add-mol")
async def add_mol_to_mws(request: Request):
    body = await request.json()
    smol = body.get("mol")
    success = srv_mws.add_mol(smol=smol)
    if not success:
        raise omg_exc.FailedOperation("Failed to add molecule to your working set.")
    return {"success": True}


@gui_router.post(f"{api_v1}/mws/remove-mol")
async def remove_mol_from_mws(request: Request):
    body = await request.json()
    smol = body.get("mol")
    success = srv_mws.remove_mol(smol=smol)
    if not success:
        raise omg_exc.FailedOperation(
            "Failed to remove molecule from your working set."
        )
    return {"success": True}


@gui_router.post(f"{api_v1}/mws/mol-present")
async def check_mol_present_in_mws(request: Request):
    body = await request.json()
    smol = body.get("mol")
    present = mws_core().is_mol_present(smol)
    return {"present": present}


@gui_router.post(f"{api_v1}/mws/clear")
async def clear_mws():
    if mws_core().is_empty():
        return {"success": True}, 204
    mws_core().clear()
    return {"success": True}


# endregion
# ------------------------------------
# region - Dataframes
# ------------------------------------


@gui_router.post(f"{api_v1}/dataframe/{{df_name}}")
async def get_dataframe(df_name: str, request: Request):
    body = await request.json()
    query = body.get("query", {})
    return srv_dataframe.get_dataframe(df_name, query)


@gui_router.post(f"{api_v1}/dataframe/update/{{df_name}}")
async def update_dataframe_molset(df_name: str, request: Request):
    body = await request.json()
    cache_id = body.get("cacheId")
    return srv_dataframe.update_dataframe_molset(df_name, cache_id)


# endregion
# ------------------------------------
