"""Step 2: the same function as an MCP server.  Run: python mcp_server.py"""
import csv, io
import requests
from fastmcp import FastMCP

SHEET = "https://docs.google.com/spreadsheets/d/1Kg6T-dJWaYx_JCPiRk3u0nBuAQcsCVRDPj1NFKP4WzM/gviz/tq?tqx=out:csv&gid="
TABS = {"code": "368290478", "no-code": "0"}

mcp = FastMCP("100x curriculum")

# The same function as step 1. The decorator writes the card for you,
# from the name, the docstring and the type hint.
@mcp.tool
def get_lectures(track: str) -> list[str]:
    """Lists every lecture of one 100xEngineers Cohort 8 track, with the tools it uses. track is 'code' or 'no-code'."""
    rows = csv.reader(io.StringIO(requests.get(SHEET + TABS[track]).text))
    return [row[1] + ": " + row[3] for row in rows if row[1][:1].isdigit()]

# Any MCP client can now reach it at http://localhost:8000/mcp
if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
