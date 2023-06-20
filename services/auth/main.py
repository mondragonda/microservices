from .schema.user import schema
from strawberry.fastapi import GraphQLRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, status, Request
from .authorization import Token
from .database.models.user import User
from ..auth.authorization import Token, LoginEmailPassword
from .authorization import authorization_service
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.post("/email_password_register", response_model=Token)
async def register_email_password_for_access_token(
    user: User
):
    return await authorization_service.email_password_register(user)


@app.post("/email_password_login", response_model=Token)
async def login_email_password_for_access_token(
    credentials: LoginEmailPassword
):
    return await authorization_service.login_for_access_token(credentials)

graphql_app = GraphQLRouter(schema, path="/")

app.include_router(graphql_app)
