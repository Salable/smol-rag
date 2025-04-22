from api.main import app

if __name__ == '__main__':
    from fastmcp import FastMCP

    mcp_server = FastMCP.from_fastapi(app)
    mcp_server.run(transport='stdio')
