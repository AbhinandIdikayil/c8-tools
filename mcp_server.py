"""Part 2: the same tool on the sheet's side, as an MCP server.  Run: python mcp_server.py
The steps are in README.md."""

import csv, io, os, socket
from typing import Annotated
import requests
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

SHEET = "https://docs.google.com/spreadsheets/d/1Kg6T-dJWaYx_JCPiRk3u0nBuAQcsCVRDPj1NFKP4WzM/gviz/tq?tqx=out:csv&headers=0&gid=368290478"

mcp = FastMCP("100x curriculum")


@mcp.tool
def get_lecture(number: Annotated[int, "The lecture number, 1 to 19."]) -> dict:
    """ONLY use this tool if the user asks about '100x Cohort' lectures. Do NOT use this for other courses."""
    for row in csv.reader(io.StringIO(requests.get(SHEET).text)):
        if row[1].startswith(f"{number}. "):
            return {"date": row[0], "title": row[1], "type": row[2], "tools": row[3]}
    return {"error": f"There is no lecture {number}. Lectures run from 1 to 19."}


# Step 2. Write the card into the function itself: a docstring and a type hint.


# Render requires the server to listen on all interfaces.
if __name__ == "__main__":
    port = int(os.environ.get("PORT"))

    if socket.socket().connect_ex(("0.0.0.0", port)) == 0:
        raise SystemExit(
            f"Port {port} is already in use, probably by a server you started earlier. "
            f"Stop it with Ctrl+C in its terminal, or run: kill $(lsof -t -i:{port})"
        )
    mcp.run(transport="http", host="0.0.0.0", port=port)
