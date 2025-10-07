# pylint: disable=missing-function-docstring

"""
Proxy test server to debug proxy routing of the GUI.

About:
    You may not always have the ability to provide access to another port,
    eg. when hosting this as part of a web service. In this case, you can set
    a BASE_PATH environment variable, and this will be used to proxy requests.

Basic Example:
    Let's say your web app is hosted at example.com, and the GUI is hosted
    on port 8024. Then you can set BASE_PATH=omgui/ and proxy all requests
    to example.com/omgui/ to port 8024.

Dynamic Example:
    In some cases, your app may want to access multiple OMGUI services with
    isolated context, for example if you host a number of Jupyter Notebooks.
    In this case, you can dynamically set the BASE_PATH to include the port you
    want to access. This approach is used by this example proxy server.

Instructions:
    1. Set the BASE_PATH environment variable to `proxy/8024/`:
    2. Start your OMGUI server (runs on port 8024 by default):

        OMGUI_BASE_PATH=proxy/8024/ python -c "import omgui; omgui.launch()"

    3. Start this proxy server in a separate terminal:

        uvicorn omgui.dev.proxy_server:proxy_app --port 9000

    4. Access the proxied GUI at http://localhost:9000/proxy/8024
"""


import os
import httpx
from fastapi import FastAPI, Request
from starlette.responses import StreamingResponse

proxy_app = FastAPI()
methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]


@proxy_app.api_route("/proxy/{port}/{path:path}", methods=methods)
async def catch_all(request: Request, port: int, path: str):
    base_path = f"/proxy/{port}/"
    os.environ["OMGUI_BASE_PATH"] = base_path
    url = f"http://127.0.0.1:{port}/{path}"

    async with httpx.AsyncClient() as client:
        # Use a dictionary to get the request body, which will be None for GET/HEAD
        body = await request.body() or None

        proxy_response = await client.request(
            method=request.method,
            url=url,
            headers=request.headers,
            content=body,
        )

    return StreamingResponse(
        proxy_response.aiter_bytes(),
        status_code=proxy_response.status_code,
        headers=proxy_response.headers,
    )
