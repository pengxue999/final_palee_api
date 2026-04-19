from typing import Any, Optional
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def success_response(data: Any, message: str, status_code: int = 200) -> JSONResponse:
    operation_map = {
        200: "GET_SUCCESSFULLY" if data is not None else "UPDATE_SUCCESSFULLY" if data is None else "SUCCESSFULLY",
        201: "CREATE_SUCCESSFULLY",
        204: "DELETE_SUCCESSFULLY"
    }

    if data is None and status_code == 200:
        code = "DELETE_SUCCESSFULLY"
    else:
        code = operation_map.get(status_code, "SUCCESSFULLY")

    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "messages": message,
            "data": jsonable_encoder(data),
        },
    )


def error_response(code: str, message: str, status_code: int, data: Any = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "messages": message,
            "data": jsonable_encoder(data) if data else None,
        },
    )
