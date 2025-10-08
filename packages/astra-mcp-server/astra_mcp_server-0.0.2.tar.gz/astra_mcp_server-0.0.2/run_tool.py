from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import ToolError
from fastmcp.tools.tool import ToolResult
from logger import get_logger
import mcp.types as types
import json
from database import AstraDBManager
import os


class RunToolMiddleware(Middleware):
    logger = get_logger("RunToolMiddleware", level=os.getenv("LOG_LEVEL"))

    def __init__(self, astra_db_manager: AstraDBManager, tools_config: dict):
        self.astra_db_manager = astra_db_manager
        self.tools_config = tools_config

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        # Access the tool object to check its metadata
        if not context.fastmcp_context:
            ToolError("No context found")

        tool_name = context.message.name

        self.logger.info(f"Tool name: {tool_name}")

        arguments = context.message.arguments
        self.logger.debug(f"Arguments: {arguments}")

        tool_config = next(
            (t for t in self.tools_config if t['name'] == tool_name), None)

        if not tool_config:
            ToolError(f"Tool {tool_name} not found")
        else:
            self.logger.debug(f"Tool config: {tool_config}")

        filter_dict = {}
        for param in tool_config["parameters"]:

            if param["attribute"] == "$vector" or param["attribute"] == "$vectorize":
                continue

            operator = "$eq"
            if "operator" in param:
                operator = param["operator"]

            if "value" in param:
                filter_dict[param["attribute"]] = {operator: param["value"]}
            elif param["param"] not in arguments and param.get("required", False) == True:
                ToolError(f"Parameter {param['param']} is required")
            elif param["param"] in arguments:
                filter_dict[param["attribute"]] = {
                    operator: arguments[param["param"]]}

        if tool_config["method"] == "find_documents":
            result = self.astra_db_manager.find_documents(
                search_query=arguments.get("search_query", None),
                filter_dict=filter_dict,
                limit=tool_config.get("limit", 10),
                projection=tool_config.get("projection", {}),
                collection_name=tool_config["collection_name"],
                tool_config=tool_config)

            self.logger.debug(f"Result: {result}")
            return ToolResult(result)

        if tool_config["method"] == "list_collections":
            result = self.astra_db_manager.list_collections()
            self.logger.debug(f"Result: {result}")
            return ToolResult(result)
        else:
            ToolError(f"Method {tool_config['method']} not allowed")
