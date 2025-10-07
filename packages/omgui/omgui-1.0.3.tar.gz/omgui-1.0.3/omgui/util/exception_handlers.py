"""
Exception Handlers for OMGUI FastAPI server.

These handlers convert exceptions on any request
into user-friendly JSON responses.
"""

# pylint: disable=missing-function-docstring, unused-argument

# FastAPI exceptions
from fastapi import Request
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette import status

# OMGUI exceptions
from omgui.util import exceptions as omg_exc


# ------------------------------------
# region - OMGUI Specific
# ------------------------------------


async def invalid_mol_input_handler(
    request: Request, err: omg_exc.InvalidMoleculeInput
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": "The provided molecule is not in valid format.",
            "error": str(err),
        },
    )


async def invalid_molset_handler(request: Request, err: omg_exc.InvalidMolset):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": "The provided molset is not valid.",
            "error": str(err),
        },
    )


async def no_result_handler(request: Request, err: omg_exc.NoResult):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "No result was obtained.",
            "error": str(err),
        },
    )


async def failed_operation_handler(request: Request, err: omg_exc.FailedOperation):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "The operation failed to complete successfully.",
            "error": str(err),
        },
    )


async def cache_file_not_found_handler(
    request: Request, err: omg_exc.CacheFileNotFound
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": "The cached working copy is not found.",
            "error": str(err),
        },
    )


async def missing_dependencies_viz(
    request: Request, err: omg_exc.MissingDependenciesViz
):
    return PlainTextResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content="Optional dependencies for /viz routes are not installed. Install with `pip install omgui[viz]`.",
    )


# endregion
# ------------------------------------
# region - General
# ------------------------------------


async def value_error_handler(request: Request, err: ValueError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Invalid value provided.",
            "error": str(err),
        },
    )


async def save_file_exists_handler(request: Request, err: FileExistsError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "message": "A file with this name already exists.",
            "error": str(err),
        },
    )


async def save_file_not_found_handler(request: Request, err: FileNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "message": "The file you're trying to save is not found.",
            "error": str(err),
        },
    )


async def permission_error_handler(request: Request, err: PermissionError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"message": "Permission denied.", "error": str(err)},
    )


async def catch_all_handler(request: Request, err: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An internal server error occurred.", "error": str(err)},
    )


# endregion
# ------------------------------------


def register_exception_handlers(app):
    app.add_exception_handler(omg_exc.InvalidMoleculeInput, invalid_mol_input_handler)
    app.add_exception_handler(omg_exc.InvalidMolset, invalid_molset_handler)
    app.add_exception_handler(omg_exc.NoResult, no_result_handler)
    app.add_exception_handler(omg_exc.FailedOperation, failed_operation_handler)
    app.add_exception_handler(omg_exc.CacheFileNotFound, cache_file_not_found_handler)
    app.add_exception_handler(omg_exc.MissingDependenciesViz, missing_dependencies_viz)

    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(FileExistsError, save_file_exists_handler)
    app.add_exception_handler(FileNotFoundError, save_file_not_found_handler)
    app.add_exception_handler(PermissionError, permission_error_handler)
    app.add_exception_handler(Exception, catch_all_handler)
