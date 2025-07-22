# server.py (MCP STDIO-Compatible)
import asyncio
import logging
import os
import sys
from mysql.connector import connect, Error
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
from pydantic import AnyUrl
from mcp.server.stdio import stdio_server

# Log to stderr to not interfere with STDIO stream
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("mysql_mcp_server")

def get_db_config():
    config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE"),
        "charset": os.getenv("MYSQL_CHARSET", "utf8mb4"),
        "collation": os.getenv("MYSQL_COLLATION", "utf8mb4_unicode_ci"),
        "sql_mode": os.getenv("MYSQL_SQL_MODE", "TRADITIONAL")
    }
    config = {k: v for k, v in config.items() if v is not None}

    if not all([config.get("user"), config.get("password"), config.get("database")]):
        logger.error("Missing required database configuration.")
        raise ValueError("Missing required database configuration")

    return config

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
        logger.error(f"Error listing resources: {e}")
        return []

@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    config = get_db_config()
    table = str(uri)[8:].split("/")[0]
    try:
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table} LIMIT 100")
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return "\n".join([",".join(columns)] + [",".join(map(str, row)) for row in rows])
    except Error as e:
        logger.error(f"Error reading resource: {e}")
        raise RuntimeError(f"Error: {e}")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="execute_sql",
            description="Run custom SQL queries.",
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
    logger.info(f"Tool called: {name} with arguments: {arguments}")

    if name != "execute_sql":
        raise ValueError(f"Unknown tool: {name}")

    query = arguments.get("query")
    if not query:
        raise ValueError("Missing 'query' parameter")

    try:
        conn = connect(**config)
        conn.autocommit = True  # ✅ Explicitly enable autocommit

        with conn:
            with conn.cursor() as cursor:
                logger.info(f"Executing query: {query}")
                cursor.execute(query)

                if cursor.description:
                    # SELECT query
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    result = [",".join(columns)] + [",".join(map(str, row)) for row in rows]
                    return [TextContent(type="text", text="\n".join(result))]
                else:
                    # INSERT / UPDATE / DELETE
                    return [TextContent(type="text", text=f"Success. Rows affected: {cursor.rowcount}")]

    except Error as e:
        logger.error(f"SQL Error: {e}")
        return [TextContent(type="text", text=f"SQL Error: {e}")]

async def main():
    logger.info("Starting MCP STDIO server...")
    async with stdio_server() as (reader, writer):
        await app.run(reader, writer, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
