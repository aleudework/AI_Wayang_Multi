"""
Entrypoint
"""
import sys
from pathlib import Path

# Add src folder so modules can be found
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from src.ai_wayang_multi.server.mcp_server import mcp

def main():
    """
    Starts the MCP-server, default is port 9500
    """

    mcp.run(transport="sse")
    print(f"Starts MCP-server")

if __name__ == "__main__":
    main()