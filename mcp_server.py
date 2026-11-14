"""Step 2: the same function as an MCP server.  Run: python mcp_server.py"""
import csv, io, socket
from typing import Literal
import requests
from fastmcp import FastMCP

SHEET = "https://docs.google.com/spreadsheets/d/1Kg6T-dJWaYx_JCPiRk3u0nBuAQcsCVRDPj1NFKP4WzM/gviz/tq?tqx=out:csv&gid="
TABS = {"code": "368290478", "no-code": "0"}
NOT_SET = {"", "None", "TBD", "[TO NAME]"}   # the sheet's placeholders for "no tools yet"

mcp = FastMCP("100x curriculum")

# The same function as step 1. The decorator writes the card for you,
# from the name, the docstring and the type hint. Literal becomes the enum.
@mcp.tool
def get_lectures(track: Literal["code", "no-code"]) -> list[str]:
    """Lists every lecture of one 100xEngineers Cohort 8 track, with the tools it uses."""
    rows = csv.reader(io.StringIO(requests.get(SHEET + TABS[track]).text))
    lectures = []
    for row in rows:
        if row[1][:1].isdigit():
            title, tools = row[1].strip(), row[3].strip()
            lectures.append(title if tools in NOT_SET else title + ": " + tools)
    return lectures

# Any MCP client can now reach it at http://localhost:8000/mcp
if __name__ == "__main__":
    if socket.socket().connect_ex(("127.0.0.1", 8000)) == 0:
        raise SystemExit("Port 8000 is already in use, probably by a server you started earlier. "
                         "Stop it with Ctrl+C in its terminal, or run: kill $(lsof -t -i:8000)")
    mcp.run(transport="http", port=8000)
