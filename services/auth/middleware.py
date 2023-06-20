from fastapi import status, Request, HTTPException
from .authorization import authorization_service
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from os import getenv

graphql_api_path = '/'


async def authentication_middleware(request: Request, call_next):
    if bool(int(getenv("NWM_DEBUG_MODE", default="1"))):
        return await call_next(request)
    authenticate_header = {"WWW-Authenticate": "Bearer"}
    invalid_credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers=authenticate_header
    )
    if request.url.path != graphql_api_path:
        return await call_next(request)
    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Unauthorized"},
            headers=authenticate_header,
        )
    auth_token = auth_header.strip().split(" ")
    try:
        token_payload = jwt.decode(auth_token[1], getenv(
            "SECRET_KEY", default=""), algorithms=[getenv("ALGORITHM", default="")])
        username = token_payload["sub"]
        if username is None:
            raise invalid_credentials_exception
        user = await authorization_service.get_user(username)
        if user is None:
            raise invalid_credentials_exception
        return await call_next(request)
    except JWTError:
        raise invalid_credentials_exception
