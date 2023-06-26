from os import getenv
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from ..auth.middleware import authentication_middleware, graphql_api_path
from services.financial.schema.advisor import schema

app = FastAPI()


@app.middleware('http')
async def authenticate(request: Request, call_next):
    return await authentication_middleware(request, call_next, 'financial')

graphql_app = GraphQLRouter(schema, path=graphql_api_path,
                            graphiql=bool(int(getenv("NWM_DEBUG_MODE", default="1"))))

app.include_router(graphql_app)

origins = [
    "https://studio.apollographql.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

# https://github.com/tiangolo/fastapi/issues/1663
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
