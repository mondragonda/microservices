# NWM Microservices 

## Next Steps

You can now run the following commands to get started:

```bash
python -m venv .virtualenv
source .virtualenv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### Running the server

From `services` directory. 
Initialize `PYTHONPATH` environment variable with the path of `services` package:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

Set the MongoDB environment variables
```bash
source ./.env.example
```

From project root run:

```bash
uvicorn services.auth.main:app --reload
```

Service GraphQL explorer will be running on: http://localhost:8000

### Apollo Studio Configuration

The GitHub actions for this template are configured to publish the subgraph to Apollo Studio. But they are disabled by default. To enable them, you'll need to add the following secrets to your repository:

- `APOLLO_KEY`: An Apollo Studio API key for the supergraph to enable schema
  checks and publishing of the subgraph.
- `APOLLO_GRAPH_REF`: The name of the graph in Apollo Studio to publish the
  subgraph to. This should be in the format `graph-name@variant-name`.
- `PRODUCTION_URL`: The URL of the deployed subgraph that the supergraph gateway
  will route to.
- `SUBGRAPH_NAME`: The name of the subgraph in Apollo Studio.

And remove the `if: false` from the `publish` step in the `publish-schema.yml`
and `check-schema.yml` workflows.

### Subgraph security

Typically, you do not want to allow the public to query your subgraph. To configure the subgraph to only accept requests from your Router, send the `Router-Authorization` header [from your Cloud router](https://www.apollographql.com/docs/graphos/routing/cloud-configuration#managing-secrets) and set the `ROUTER_SECRET` environment variable wherever you deploy this to.

[apollo federation]: https://www.apollographql.com/docs/federation/
[strawberry graphql]: https://strawberry.rocks/
[rover]: https://www.apollographql.com/docs/rover/getting-started
