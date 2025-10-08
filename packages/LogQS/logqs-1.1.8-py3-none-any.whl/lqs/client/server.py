import os
import json
import base64
from textwrap import dedent
from typing import Optional

import uvicorn
from mangum import Mangum
from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from lqs.interface.dsm.models import EventCreateRequest


def validate(headers: dict, expected_secret: Optional[str] = None):
    """
    Validate the authorization header.

    If expected_secret is None, then no validation is performed.
    Otherwise, the authorization header must be present and must
    match the expected_secret.

    The authorization header must be of the form:

        Bearer <base64 encoded secret>

    The base64 encoded secret must be the expected_secret.
    """
    if expected_secret is None:
        return True
    token = headers.get("authorization")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
        )
    assert type(token) is str, "Authorization header must be a string"
    assert token.startswith("Bearer "), "Authorization header must start with 'Bearer '"
    encoded_secret = token.split(" ")[1]
    received_secret = base64.b64decode(encoded_secret).decode("utf-8")
    if received_secret != expected_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization token",
        )
    return True


def get_server(
    event_callback: callable,
    pre_validate_callback: callable = None,
    expected_secret: str = None,
    path: str = "/events",
):
    """
    Get a FastAPI server that can be run with uvicorn, Mangum, etc.
    """
    if expected_secret is None:
        expected_secret = os.environ.get("LQS_EXPECTED_SECRET")

    description = dedent(
        """
    A small server that listens for workflow hook events from LogQS and forwards them to a callback function.

    This server has a single endpoint, /events, which only accepts POST requests.
    The body of the request must be a JSON object that matches the EventCreateRequest model.
    This is what can be expected from a LogQS workflow hook event.

    If configured, the server will validate the authorization header. The authorization header must be of the form:

        Bearer <base64 encoded secret>

    The base64 encoded secret must be the expected_secret.
    """
    )

    app = FastAPI(
        title="LogQS Event Listener", description=description, version="1.0.0"
    )

    @app.post(path, name="Receive Event", tags=["Event"], operation_id="receive_event")
    async def receive_event(event: EventCreateRequest, request: Request):
        headers = dict(request.headers)
        if pre_validate_callback is not None:
            headers = pre_validate_callback(headers)
        validate(headers, expected_secret)
        return event_callback(event)

    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"message": f"[InternalServerError] {exc}"},
        )

    return app


def run(
    event_callback: callable,
    pre_validate_callback: callable = None,
    expected_secret: str = None,
    host: str = "0.0.0.0",
    port: int = 80,
    path: str = "/events",
):
    server = get_server(
        event_callback=event_callback,
        pre_validate_callback=pre_validate_callback,
        expected_secret=expected_secret,
        path=path,
    )
    uvicorn.run(server, host=host, port=port)


def lambda_handler_handler(
    event,
    context,
    event_callback: callable,
    pre_validate_callback: callable = None,
    expected_secret: str = None,
    path: str = "/events",
):
    try:
        server = get_server(
            event_callback=event_callback,
            pre_validate_callback=pre_validate_callback,
            expected_secret=expected_secret,
            path=path,
        )
        handler = Mangum(server)
        response = handler(event, context)
        return response
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"status": "error", "message": str(e)}),
        }


if __name__ == "__main__":

    def event_callback(**params):
        print(params)
        return {"status": "ok"}

    run(event_callback=event_callback, host="localhost", port=8081)
