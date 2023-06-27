from os import getenv
from fastapi import FastAPI, Request
from strawberry.fastapi import GraphQLRouter
from ..auth.middleware import authentication_middleware, graphql_api_path
from services.financial.schema.advisor import schema
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


@app.middleware('http')
async def authenticate(request: Request, call_next):
    return await authentication_middleware(request, call_next, 'financial')

graphql_app = GraphQLRouter(schema, path=graphql_api_path,
                            graphiql=bool(int(getenv("NWM_DEBUG_MODE", default="1"))))

app.include_router(graphql_app)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
