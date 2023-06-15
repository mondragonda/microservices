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
source .env.example
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

### Datadog Installation and Configuration

This guide provides step-by-step instructions to configure and install Datadog in Ubuntu.

**Prerequisites**

- Ubuntu environment

**Steps**

1. **Create a Datadog account**

   - Go to the Datadog website (https://www.datadoghq.com/)
   - Click on "Start Monitoring for Free" to create a new account
   - Follow the prompts to complete the signup process

2. **Obtain the API key**

   - After creating an account, navigate to "Integrations" > "Agent" in the Datadog dashboard
   - Copy your API key from the page

3. **Install the Datadog agent**

   - Open a terminal in your Ubuntu environment
   - Run the following command to download and install the Datadog agent:

     ```
     DD_API_KEY=<your_api_key> DD_SITE="us5.datadoghq.com" bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script_agent7.sh)"
     ```

     Replace `<your_api_key>` with the API key you obtained from your Datadog account

4. **Configure the agent**

   - Open the agent configuration file by running the command:

     ```
     sudo nano /etc/datadog-agent/datadog.yaml
     ```

   - Uncomment the `api_key` parameter by removing the `#` symbol, and replace the placeholder value with your API key:

     ```
     api_key: <your_api_key>
     ```

   - Uncomment the `hostname` parameter by removing the `#` symbol, and replace the placeholder value with your desired hostname for your host:

     ```
     hostname: <desired-hostname>
     ```

   - Save the changes and exit the editor

5. **Start the agent**

   - Restart the Datadog agent service by running the command:

     ```
     sudo systemctl restart datadog-agent
     ```

6. **Verify installation**

   - Run the following command to check the status of the agent:

     ```
     sudo datadog-agent status
     ```

   - This command will display the status of the agent and confirm if it is running and connected to the Datadog platform

Once you have successfully configured and installed Datadog in Ubuntu, the agent will now begin collecting system metrics, logs, and other relevant data from your Ubuntu environment.

**Additional Resources**

- [Datadog Documentation](https://docs.datadoghq.com/)