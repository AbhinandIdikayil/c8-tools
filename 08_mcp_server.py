"""Step 8. The same two tools, moved out of your app and put at an address. This is an MCP server."""
from typing import Annotated

from fastmcp import FastMCP

import tools

mcp = FastMCP("100x curriculum")
Track = Annotated[str, "Which track: code or no-code."]


@mcp.tool
def get_track_tools(track: Track) -> dict:
    """Returns every tool one track of the 100xEngineers Cohort 8 course uses, from the curriculum sheet.
    Use it for any question about what a track teaches or which track to choose.
    Call it once for each track you need."""
    return tools.get_track_tools(track)


@mcp.tool
def get_lecture(number: Annotated[int, "The lecture number, 1 to 19."], track: Track) -> dict:
    """Returns one lecture of the 100xEngineers Cohort 8 course: its date, title, type and tools.
    Use it when someone asks about a specific lecture by number. Not for general questions."""
    return tools.get_lecture(number, track)


if __name__ == "__main__":
    # stateless_http and json_response keep every message a plain POST with a JSON answer, so you can read them.
    mcp.run(transport="http", port=8000, stateless_http=True, json_response=True)
