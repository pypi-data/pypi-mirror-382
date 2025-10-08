# Astra MCP Server

A Model Context Protocol (MCP) server for interacting with Astra DB (DataStax Astra).

![Astra MCP Server Overview](docs/astra-mcp-server-overview.png)

## Running it as MCP Server with STDIO

To run the astra-mcp-server as MCP Server with STDIO, you can use the following command:

```bash
uvx astra-mcp-server -tr stdio --astra_token <astra_token> --astra_endpoint <astra_endpoint>
```

## Running it as MCP Server with HTTP

To run the astra-mcp-server as MCP Server with STDIO, you can use the following command:

```bash
uvx astra-mcp-server
```
## App options

- `--transport <transport>`: The transport to use for the MCP Server. Valid values are `stdio` and `http`. Default is `stdio`.
- `--astra_token <astra_token>`: The Astra token to use for the Astra DB connection. If not filled, the app will try to get the token from the `ASTRA_DB_APPLICATION_TOKEN` environment variable.
- `--astra_endpoint <astra_endpoint>`: The Astra endpoint to use for the Astra DB connection. If not filled, the app will try to get the endpoint from the `ASTRA_DB_API_ENDPOINT` environment variable.
- `--tags <tags>`: The tags to filter the tools for the MCP Server. 

## Catalog options
- `--catalog_file <catalog_file>`: The catalog file to use for the MCP Server. Default is `tools_config.json`. If not filled, the app will try to get the catalog from the `ASTRA_DB_CATALOG_COLLECTION` environment variable.
- `--catalog_collection <catalog_collection>`: The catalog collection to use for the MCP Server. Default is `tool_catalog`. If not filled, the app will try to get the catalog from the `ASTRA_DB_CATALOG_COLLECTION` environment variable.

Options valid for the HTTP transport:

When running the app as HTTP, you can use the following options:
- `--host <host>`: The host to use for the MCP Server. Default is `127.0.0.1`.
- `--port <port>`: The port to use for the MCP Server. Default is `8000`.
- `--workers <workers>`: The number of worker processes to use for the MCP Server. Default is `1`.
- `--log-level <log_level>`: The log level to use for the MCP Server. Valid values are `debug`, `info`, `warning`, and `error`. Default is `info`.
- `--log-file <log_file>`: The log file to use for the MCP Server. Default is `logs/astra_mcp_server.log`.
    

## 1. Set up environment variables

If you are running the app with some MCP Client that allows you to define environment variables, you can set the same variables in the MCP Client.

If you prefer, you can create a `.env` file in app directory with the following variables:

```env
# Astra DB Configuration
ASTRA_DB_APPLICATION_TOKEN=your_astra_db_token
ASTRA_DB_API_ENDPOINT=your_astra_db_endpoint
ASTRA_DB_CATALOG_COLLECTION=tool_catalog
LOG_LEVEL=DEBUG
LOG_FILE=./logs/logs.log
# Logging Configuration (optional)
LOG_LEVEL=INFO
LOG_FILE=logs/astra_mcp_server.log

#Embedding Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=your_openai_base_url
IBM_WATSONX_API_KEY=your_ibm_watsonx_api_key
IBM_WATSONX_BASE_URL=your_ibm_watsonx_base_url
IBM_WATSONX_PROJECT_ID=your_ibm_watsonx_project_id
```

# Creating tools

Tools are created based on a json specification. It can be save to a file or to a Astra DB collection (preferable for production use cases).

A tools specifiction json needs the following fields:
```json
{
        "tags": ["products"], // The tags of the tool - Filter if needed
        "type": "tool", // The type of the tool
        "name": "search_products", // The name of the tool
        "description": "Search for products", // The description of the tool to the MCP Client
        "limit": 10, // The limit of the tool
        "method": "find_documents", // The method to use to execute the tool
        "collection_name": "products", // The collection to use to execute the tool
        "projection": {"$vectorize": 1, "metadata": 0}, // The projection of the tool
        "parameters": [ // The parameters of the tool
            {  
                "param": "search_query", // The name of the parameter
                "description": "Query to search for products", // The description of the parameter
                "attribute": "$vectorize", // The attribute of the parameter... or $vectorize
                "type": "string", // The type of the parameter
                "required": 1, // Whether the parameter is required
                "operator": "$eq", // The operator to use to filter the parameter - if not filled, the operator is $eq
                "enum": ["baggage", "boarding", "check-in", "flight-status", "other"], // The enum of the parameter
                "embedding_model": "text-embedding-3-small" // The embedding model to use to generate the embedding
            },
            {  
                "param": "in_stock", // The name of the parameter 
                "value": true, // The value of the parameter - IF FILLED, THE PARAMETER IS NOT SENT TO THE MCP CLIENT and applied by the server
                "attribute": "in_stock" // The attribute of the parameter
            }
        ],

    }
```

Save the json document to the file or to the Astra DB collection. When the server is started, it will load the tools from the file or the Astra DB collection.

After storing on Astra DB, the tools will appear in the Astra DB collection like this:

![MCP Tool stored on Astra](docs/astra-mcp-server-tool.png)

# Updating tools

To update the tools, you can update the json document and save it to the file or to the Astra DB collection.

```bash
python catalog.py -f tools_config_example.json -t tool_catalog
```

# Local Development

```bash
# Install dependencies
uv sync

# Run the server
uv run astra-mcp-server --host 127.0.0.1 --port 5150 --reload --log-level debug
```

### Alternative: Direct uvicorn (for development)

```bash
# Run directly with uvicorn
uv run uvicorn server:main --factory --reload --port 5150 --log-level debug
```


## Using MCP Inspector (STDIO)

```bash
npx @modelcontextprotocol/inspector uv run astra-mcp-server --log-level debug -tr stdio
```

