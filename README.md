![Tests](https://github.com/designcomputer/mysql_mcp_server/actions/workflows/test.yml/badge.svg)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mysql-mcp-server)
[![smithery badge](https://smithery.ai/badge/mysql-mcp-server)](https://smithery.ai/server/mysql-mcp-server)
[![MseeP.ai Security Assessment Badge](https://mseep.net/mseep-audited.png)](https://mseep.ai/app/designcomputer-mysql-mcp-server)
# MySQL MCP Server
A Model Context Protocol (MCP) implementation that enables secure interaction with MySQL databases running on python server. This server component facilitates communication between AI applications (hosts/clients) and MySQL databases, making database exploration and analysis safer and more structured through a controlled interface.

> **Note**: MySQL MCP Server is not designed to be used as a standalone server, but rather as a communication protocol implementation between AI applications and MySQL databases. This modified version of MySQL MCP Server is compatible with [Langflow](https://github.com/langflow-ai/langflow) MCPTools component via STDIO protocol. 

## Features
- List available MySQL tables as resources
- Read table contents
- Execute SQL queries with proper error handling
- Secure database access through environment variables
- Comprehensive logging

## Installation 
### Manual Installation

1. Open up Windows CMD, cd to desktop location.
```bash
cd desktop
```
   
2. Cloning the repo
```bash
git clone https://github.com/CHuiV123/mysql_mcp_server_LangflowCompatible.git
```

3. Get into the folder directory:
```bash
cd mysql_mcp_server_LangflowCompatible
```

4. Install dependencies
```bash
pip install -r requirements.txt
```

5. set up environment variable as below, replace all the "<-CHANGE THIS" section:
```bash
set MYSQL_HOST="YOUR_DATABASE_HOST" <-CHANGE THIS
set MYSQL_PORT=3306 <-CHANGE THIS IF YOUR DATABASE IS NOT RUNNING ON 3306
set MYSQL_USER="YOUR_USER_NAME" <-CHANGE THIS
set MYSQL_PASSWORD="YOUR_PASSWORD" <-CHANGE THIS
set MYSQL_DATABASE="yOUR_DATABASE_NAME" <-CHANGE THIS
```

6. Start the server:
```bash
uv --directory . run mysql_mcp_server
```

Upon successful server start up, you shall see "mysql_mcp_server - INFO - Starting MCP STDIO server..."

## Setting up in Langflow MCPTools
*** pre-requisite, at this point MySQL MCP server should be already up and running. 

1. Go to Langflow setting, look for MCP server.
2. Click **Add MCP Server**
3. Select **STDIO**
4. Server name **MySQL_MCP**
5. Command **python**
6. Arguments **your directory path of server.py**
7. Add environment variable
```
MYSQL_HOST= **YOUR_HOST**
MYSQL_PORT= **YOUR_PORT**
MYSQL_USER= **YOUR_USER_NAME**
MYSQL_PASSWORD= **YOUR_PASSWORD**
MYSQL_DATABASE= **YOUR_DATABASE_NAME**
```
8. Click **Add server**
9. Restart Langflow


### Debugging with MCP Inspector
While MySQL MCP Server isn't intended to be run standalone or directly from the command line with Python, you can use the MCP Inspector to debug it.

The MCP Inspector provides a convenient way to test and debug your MCP implementation:

```bash
# Install dependencies
pip install -r requirements.txt
# Use the MCP Inspector for debugging (do not run directly with Python)
```

The MySQL MCP Server is designed to be integrated with AI applications like Claude Desktop and should not be run directly as a standalone Python program.

## Development
```bash
# Clone the repository
git clone https://github.com/designcomputer/mysql_mcp_server.git
cd mysql_mcp_server
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
# Install development dependencies
pip install -r requirements-dev.txt
# Run tests
pytest
```

## Security Considerations
- Never commit environment variables or credentials
- Use a database user with minimal required permissions
- Consider implementing query whitelisting for production use
- Monitor and log all database operations

## Security Best Practices
This MCP implementation requires database access to function. For security:
1. **Create a dedicated MySQL user** with minimal permissions
2. **Never use root credentials** or administrative accounts
3. **Restrict database access** to only necessary operations
4. **Enable logging** for audit purposes
5. **Regular security reviews** of database access

See [MySQL Security Configuration Guide](https://github.com/designcomputer/mysql_mcp_server/blob/main/SECURITY.md) for detailed instructions on:
- Creating a restricted MySQL user
- Setting appropriate permissions
- Monitoring database access
- Security best practices

⚠️ IMPORTANT: Always follow the principle of least privilege when configuring database access.

## License
MIT License - see LICENSE file for details.

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
