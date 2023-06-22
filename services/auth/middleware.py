from fastapi import status, Request, Response
from .authorization import authorization_service
from os import getenv
from .authorization import authorization_service, authenticate_header
import json
import typing

email_password_register_path = '/email_password_register'
email_password_login = '/email_password_login'
user_account_verification = '/account_verification'
user_account_verification_resend = '/account_verification_resend'
graphql_api_path = '/'

allowed_unauthenticated_paths = [
    email_password_register_path,
    email_password_login
]

allowed_unactivated_account_paths = [
    user_account_verification,
    user_account_verification_resend
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
    unauthorized_response = Response(
        get_parsable_graphql_error(
            status_code=status.HTTP_401_UNAUTHORIZED, service=service),
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers=authenticate_header
    )
    forbidden_response = Response(
        get_parsable_graphql_error(
            status_code=status.HTTP_403_FORBIDDEN, service=service),
        status_code=status.HTTP_403_FORBIDDEN,
    )
    if request.url.path in allowed_unauthenticated_paths:
        return await call_next(request)
    access_token_claims = authorization_service.get_access_token_claims(request)
    if access_token_claims is None:
        return unauthorized_response
    username = access_token_claims["sub"]
    if username is None:
        return unauthorized_response
    user: typing.Any = await authorization_service.get_user(username)
    if user is None:
        return unauthorized_response
    if user["_verified"] is False and request.url.path not in allowed_unactivated_account_paths:
        return forbidden_response
    return await call_next(request)
