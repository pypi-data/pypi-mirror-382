import argparse
import os,json
from dotenv import load_dotenv
from fastmcp import FastMCP
from load_tools import ToolLoader
from database import AstraDBManager
from fastmcp.server.dependencies import get_context
from logger import get_logger
from run_tool import RunToolMiddleware
import uvicorn
import asyncio
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier

load_dotenv(override=True)

# Define development tokens and their associated claims

# Initialize logger
logger = get_logger("astra_mcp_server",level=os.getenv("LOG_LEVEL"))

async def main():
    
    # Parse arguments
    parser = argparse.ArgumentParser(conflict_handler="resolve")
    
       # ---- Uvicorn standard params ----
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Bind socket to this host")
    parser.add_argument("--port", type=int, default=8000, help="Bind socket to this port")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    parser.add_argument("--log-level", type=str, default="info", help="Logging level")
    parser.add_argument("--log-file", type=str, default="logs.log", help="Logging file")
    parser.add_argument("--transport", "-tr", default="stdio")

    # ---- Astra MCP Server params ----
    parser.add_argument("--astra_token", "-t", default=os.getenv("ASTRA_DB_APPLICATION_TOKEN"))
    parser.add_argument("--astra_endpoint", "-e", default=os.getenv("ASTRA_DB_API_ENDPOINT"))
    parser.add_argument("--catalog_file", "-f")
    parser.add_argument("--catalog_collection", "-c", default=os.getenv("ASTRA_DB_CATALOG_COLLECTION") or "tool_catalog")
    
    parser.add_argument("--tags", "-tags")
    
    args = parser.parse_args()
    
    
    # Configure JWT verifier
    # verifier = StaticTokenVerifier(
    #     tokens={
    #         "astra-mcp-server-token": {
    #             "client_id": "astra-mcp-server",
    #             "scopes": ["read:data", "write:data", "admin:users"]
    #         },
    #     },
    #     required_scopes=["read:data", "write:data", "admin:users"]
    # ) 
    
    # Initialize MCP
    mcp = FastMCP("Astra MCP Server")
    # mcp = FastMCP("Astra MCP Server", auth=verifier)
    
    astra_db_manager = AstraDBManager(args.astra_token, args.astra_endpoint)
    
    # Load tools config content
    tools_config_content = None
    if args.catalog_file:
        logger.info(f"Loading tools config from {args.catalog_file}")
        tools_config_content = json.load(open(args.catalog_file))
    else:
        logger.info(f"Loading tools Astra collection {args.catalog_collection}")
        tools_config_content = astra_db_manager.get_catalog_content(collection_name=args.catalog_collection, tags=args.tags)

    logger.info(f"Tools config content: {tools_config_content}")
       
    # Add middleware to process tool calling   
    mcp.add_middleware(RunToolMiddleware(astra_db_manager,tools_config_content))
    
    logger.info("Initializing Astra MCP Server")
    logger.info(f"Starting Astra MCP Server on port {args.port}")
    
    # Generate tools based on tools config content
    tool_loader = ToolLoader(mcp, astra_db_manager,tools_config_content)
    tool_loader.load_all_tools()
    
    logger.info("All tools loaded successfully")
    
    app = None
    # Return the appropriate transport app
    if args.transport == "http" or args.transport == "sse":
        await mcp.run_async(transport=args.transport, host=args.host, port=args.port, log_level=args.log_level)
    elif args.transport == "stdio":
        await mcp.run_async(transport=args.transport, log_level=args.log_level)
    else:
        raise ValueError(f"Invalid transport: {args.transport}")
    logger.info("Astra MCP Server started successfully")

def run_server():
    """Synchronous entry point for the astra-mcp-server command."""
    asyncio.run(main())

if __name__ == "__main__":
    run_server()