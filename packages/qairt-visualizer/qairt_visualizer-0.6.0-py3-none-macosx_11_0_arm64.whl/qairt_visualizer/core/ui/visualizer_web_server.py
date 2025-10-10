# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""Visualizer Web Server"""

import argparse
import asyncio
import os
from contextlib import asynccontextmanager
from typing import Any, Awaitable, Callable, Dict

import socketio
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from qairt_visualizer.core.ui.contexts.autoshutdown_context import AutoShutdownContext
from qairt_visualizer.core.ui.helpers.http_helpers import extract_query_params
from qairt_visualizer.core.visualizer_logging.logger_constants import web_server_logger
from qairt_visualizer.core.visualizer_logging.logging_config import LoggingConfig
from qairt_visualizer.helpers.ui_helpers import find_ui_path_to
from qairt_visualizer.schemas.view_schemas import ViewRequest

LoggingConfig.setup_logging()
# ==============================================================================
# Inactivity Handlers
# ==============================================================================

sio_server = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[], namespaces=["*"])


def no_websocket_clients_connected() -> bool:
    """Returns true when no clients are still connected via websocket, false if there are clients connected"""
    web_server_logger.debug("There are %d socket.io rooms still active.", len(sio_server.manager.rooms))
    return len(sio_server.manager.rooms) < 1


MAX_INACTIVITY_SECONDS = 120
web_server_logger.debug(
    "Initializing automatic shutdown handler. The server will shut down after %d seconds of inactivity.",
    MAX_INACTIVITY_SECONDS,
)
autoshutdown_context = AutoShutdownContext(MAX_INACTIVITY_SECONDS, no_websocket_clients_connected)


@asynccontextmanager
async def _lifespan(_: FastAPI):
    """
    Custom lifespan handler. All code before the "yield" will be executed on startup. Any code
    after the yield will be performed when app is shutdown.

    reference: https://fastapi.tiangolo.com/advanced/events/#lifespan
    """
    autoshutdown_context.reset_shutdown_timer()
    yield


# ==============================================================================
# End Inactivity Handlers
# ==============================================================================

app = FastAPI(lifespan=_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=50000)
socketio_fastapi_bridge = socketio.ASGIApp(socketio_server=sio_server, other_asgi_app=app)


# ==============================================================================
# Web Server Endpoints
# ==============================================================================
@app.get("/status", status_code=status.HTTP_200_OK)
async def get_status():
    """
    Endpoint used to verify application is running and health

    :return: Object with status property set to OK
    """
    return {"status": "ok"}


@app.post("/view/{window_id}", status_code=status.HTTP_202_ACCEPTED)
async def notify_view_request(window_id: str, view_request: ViewRequest):
    """
    Sends a view request notification to the given window id.
    :param window_id: Id of the UI view to notify
    :param view_request: The ViewRequest that is attempting to be displayed
    """
    web_server_logger.info("Verifying UI ready to receive view request.")
    debug_info = f"Target window id: {window_id}. Request: {view_request.model_dump_json()}"
    web_server_logger.debug(debug_info)
    if not await _client_can_be_notified(sio_server, window_id):
        web_server_logger.error("Window never connected to socket server")
        web_server_logger.debug(debug_info)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Window id {window_id} never connected to server. Cannot notify with view request.",
        )

    event = "file-data"
    files_to_visualize = view_request.reports if view_request.reports else []

    if view_request.path_to_model:
        # Models should always go first to ensure they are
        # on the left-hand side of the workspace view
        files_to_visualize.insert(0, view_request.path_to_model)

    if len(files_to_visualize):
        visualize_request = []
        for path_to_file in files_to_visualize:
            if not os.path.exists(path_to_file):
                web_server_logger.error("File path %s does not exist. Cannot visualize file.", path_to_file)
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            filename = os.path.basename(path_to_file)
            load_url = f"/load?file_path={path_to_file}"
            visualize_request.append({"filename": filename, "load_url": load_url})

            web_server_logger.debug(
                "Event: %s. Load URL: %s. Filename: %s. %s",
                event,
                load_url,
                filename,
                debug_info,
            )
        web_server_logger.info("Sending notification to UI to load file/s.")

        await sio_server.emit(
            event,
            data=(visualize_request, view_request.options.model_dump()),
            room=window_id,
        )
    else:
        web_server_logger.error(
            "View window ID %s with request %s did not provide any paths to visualize",
            window_id,
            view_request,
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@app.get("/load", status_code=status.HTTP_200_OK)
async def load(file_path: str) -> FileResponse:
    """
    Returns a FileResponse based on the given file path. A 404 is returned if the file is not found
    :param file_path: The file path
    :return: The file
    """
    if not os.path.exists(file_path):
        web_server_logger.error("Cannot send file to UI, file does not exist: %s", file_path)
        raise HTTPException(status_code=404)
    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=os.path.basename(file_path),
    )


async def _client_can_be_notified(sio: socketio.AsyncServer, window_id: str, max_retries: int = 5) -> bool:
    can_be_notified = False
    for attempt in range(max_retries):
        can_be_notified = len(sio.manager.rooms) > 0 and window_id in sio.manager.rooms["/"]
        if can_be_notified:
            return True

        web_server_logger.debug(
            "Window %s has not connected to room yet. Waiting...(%d/%d)",
            window_id,
            attempt + 1,
            max_retries,
        )
        await asyncio.sleep(0.5)
    return False


# ==============================================================================
# End Web Server Endpoints
# ==============================================================================

# ==============================================================================
# Middleware
# ==============================================================================


@app.middleware("http")
async def reset_shutdown_timer_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """
    Resets the shutdown timer on every http request
    """
    autoshutdown_context.reset_shutdown_timer()
    return await call_next(request)


# ==============================================================================
# End Middleware
# ==============================================================================


# ==============================================================================
# Socket Server Endpoints
# ==============================================================================
@sio_server.event
async def connect(sid: str, environ: Dict[str, str], _: Any):
    """
    Built-in socket.io connect event that is triggered whenever a client connects to the websocket. Creates
    a room to allow for direct messaging to specific a window with the given id.
    :param sid: the socket id that has connected
    :param environ: Contains request information in WSGI format
    :param _: Unused authentication argument
    """
    parsed_query_params = extract_query_params(query_string=environ["QUERY_STRING"], params_list=["id"])
    window_id = str(parsed_query_params["id"])
    web_server_logger.debug("Window id %s connected to web socket.", window_id)
    await sio_server.enter_room(sid, window_id)


# ==============================================================================
# End Socket Server Endpoints
# ==============================================================================

if __name__ == "__main__":
    try:
        ASSETS_DIRECTORY = find_ui_path_to("dist/browser")
        app.mount("/", StaticFiles(directory=ASSETS_DIRECTORY, html=True), name="static")
    except Exception as e:
        web_server_logger.critical(
            "Failed to locate or mount static assets required for UI launch. Unable to start the web server."
        )
        raise e
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run(
        socketio_fastapi_bridge,
        host="0.0.0.0",
        port=args.port,
        log_config=LoggingConfig.get_py_logging_config(),
    )
