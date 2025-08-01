# server.py (Optimized for Langflow MCP via STDIO)

import asyncio
import logging
import os
import sys
from mysql.connector import connect, Error
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
from pydantic import AnyUrl
from mcp.server.stdio import stdio_server

# --- Logging setup: log to stderr (not STDIO)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("mysql_mcp_server")

# --- Database config from environment
def get_db_config():
    config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE"),
        "charset": os.getenv("MYSQL_CHARSET", "utf8mb4"),
        "collation": os.getenv("MYSQL_COLLATION", "utf8mb4_unicode_ci"),
        "autocommit": True,
        "sql_mode": os.getenv("MYSQL_SQL_MODE", "TRADITIONAL")
    }
    config = {k: v for k, v in config.items() if v is not None}
    if not all([config.get("user"), config.get("password"), config.get("database")]):
        logger.error("Missing required database configuration: MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE")
        raise ValueError("Missing required database configuration")
    return config

# --- MCP Server Setup
app = Server("mysql_mcp_server")

@app.list_resources()
async def list_resources() -> list[Resource]:
    config = get_db_config()
    try:
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                return [
                    Resource(
                        uri=f"mysql://{table[0]}/data",
                        name=f"Table: {table[0]}",
                        mimeType="text/plain",
                        description=f"Data in table: {table[0]}"
                    )
                    for table in tables
                ]
    except Error as e:
        logger.error(f"Error listing resources: {e} | Code: {e.errno}, SQL state: {e.sqlstate}")
        return []

@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    config = get_db_config()
    uri_str = str(uri)

    if not uri_str.startswith("mysql://"):
        raise ValueError(f"Invalid URI: {uri_str}")
    table = uri_str[8:].split('/')[0]

    try:
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table} LIMIT 100")
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                result = [",".join(map(str, row)) for row in rows]
                return "\n".join([",".join(columns)] + result)
    except Error as e:
        logger.error(f"Error reading {uri_str}: {e} | Code: {e.errno}, SQL state: {e.sqlstate}")
        raise RuntimeError(f"Database error: {str(e)}")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="execute_sql",
            description="Execute an SQL query on the MySQL server",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL query to execute"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    config = get_db_config()

    if name != "execute_sql":
        raise ValueError(f"Unknown tool: {name}")

    query = arguments.get("query")
    if not query:
        raise ValueError("Missing query")

    try:
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)

                # Result sets (SELECT, SHOW, etc.)
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    try:
                        rows = cursor.fetchall()
                        result = [",".join(map(str, row)) for row in rows]
                        return [TextContent(type="text", text="\n".join([",".join(columns)] + result))]
                    except Error as e:
                        logger.warning(f"Query executed but fetch failed: {e}")
                        return [TextContent(type="text", text=f"Fetch error: {e}")]

                # Non-result queries
                conn.commit()
                return [TextContent(type="text", text=f"Query executed. Rows affected: {cursor.rowcount}")]
    except Error as e:
        logger.error(f"SQL execution error: {e} | Code: {e.errno}, SQL state: {e.sqlstate}")
        return [TextContent(type="text", text=f"Error executing query: {str(e)}")]

# --- Entry point
async def main():
    print("Starting MySQL MCP Server...", file=sys.stderr)
    config = get_db_config()
    print(f"🔧 DB Config -> Host: {config['host']} | User: {config['user']} | DB: {config['database']}", file=sys.stderr)

    try:
        async with stdio_server() as (reader, writer):
            await app.run(reader, writer, app.create_initialization_options())
    except Exception as e:
        logger.error(f"Fatal server error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
