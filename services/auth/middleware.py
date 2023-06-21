from fastapi import status, Request, HTTPException, Response
from .authorization import authorization_service
from jose import JWTError, jwt
from os import getenv
import json

email_password_register_path = '/email_password_register'
email_password_login = '/email_password_login'


allowed_unauthenticated_paths = [
    email_password_register_path,
    email_password_login
]


def get_parsable_graphql_error(status_code, service):
    status_message = f'{status_code}: {[status_message for status_message in status.__all__ if status_message.find(str(status_code)) > -1].pop(0)}'
    return json.dumps({
        "data": None,
        "errors": [{
            "message": f'HTTP fetch failed from \'{service}\' service: {status_message}',
            "path": [],
            "extensions": {
                "code": "SUBREQUEST_HTTP_ERROR",
                "service": service,
                "reason": f'{status_message}',
                "http": {
                    "status": status_code
                }
            }
        }]
    })


async def authentication_middleware(request: Request, call_next, service):
    if bool(int(getenv("NWM_DEBUG_MODE", default="1"))):
        return await call_next(request)
    authenticate_header = {"WWW-Authenticate": "Bearer"}
    unauthorized_response = Response(
        get_parsable_graphql_error(
            status_code=status.HTTP_401_UNAUTHORIZED, service=service),
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers=authenticate_header
    )
    if request.url.path in allowed_unauthenticated_paths:
        return await call_next(request)
    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        return unauthorized_response
    auth_token = auth_header.strip().split(" ")
    if len(auth_token) != 2:
        return unauthorized_response
    token_payload = jwt.decode(auth_token[1], getenv(
        "SECRET_KEY", default=""), algorithms=[getenv("ALGORITHM", default="")])
    username = token_payload["sub"]
    if username is None:
        return unauthorized_response
    user = await authorization_service.get_user(username)
    if user is None:
        return unauthorized_response
    return await call_next(request)
