from os import getenv
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from ..auth.middleware import authentication_middleware, graphql_api_path
from services.financial.schema.advisor import schema

app = FastAPI()

# origins = [
#     "https://studio.apollographql.com",
# ]

# https://github.com/tiangolo/fastapi/issues/1663


@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "https://silly-stop-sandbox.up.railway.app/, http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

origins = [
    'https://silly-stop-sandbox.up.railway.app/',
    'http://localhost:3000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware('http')
async def authenticate(request: Request, call_next):
    return await authentication_middleware(request, call_next, 'financial')

graphql_app = GraphQLRouter(schema, path=graphql_api_path,
                            graphiql=bool(int(getenv("NWM_DEBUG_MODE", default="1"))))

app.include_router(graphql_app)

# @app.middleware("http")
# async def check_router_security(
#     request: Request, call_next: Callable[[Request], Awaitable[Response]]
# ) -> Response:
#     router_secret = environ.get("ROUTER_SECRET")
#     if router_secret is None:
#         return await call_next(request)
#     if request.headers.get("Router-Authorization") != router_secret:
#         return Response(status_code=HTTPStatus.UNAUTHORIZED)
#     return await call_next(request)
