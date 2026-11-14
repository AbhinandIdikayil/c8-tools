"""The deterministic side: two functions that read the curriculum sheet, and the cards that describe them to the model.

python tools.py          just the functions, no model anywhere
python tools.py serve    the same two tools at an address: an MCP server
"""
import csv
import io
import re
import sys

import requests

# The public 100xEngineers Cohort 8 Google Sheet, one tab per track. The same sheet the map and the Tool Bench read.
SHEET = "https://docs.google.com/spreadsheets/d/1Kg6T-dJWaYx_JCPiRk3u0nBuAQcsCVRDPj1NFKP4WzM/gviz/tq?tqx=out:csv&headers=0"
TABS = {"no-code": "0", "code": "368290478"}                      # the tab ids in the sheet's address


def fetch_lectures(track: str) -> list[dict]:
    """Every lecture of one track: number, date, title, type and the tools cell, as written in the sheet."""
    text = requests.get(SHEET + "&gid=" + TABS[track], timeout=10).text
    lectures = []
    for row in csv.reader(io.StringIO(text)):
        numbered = re.match(r"(\d+)\.\s*(.+)", row[1]) if len(row) > 3 else None
        if numbered:                                              # holidays and the hackathon have no number
            lectures.append({"number": int(numbered.group(1)), "date": row[0], "title": numbered.group(2).strip(),
                             "type": row[2], "tools": row[3].strip()})
    return lectures


# ---------------------------------------------------------------- the functions

NOT_TOOLS = {"", "None", "TBD", "[TO NAME]", "Paper exercise"}    # what the sheet writes when no tool is named


def check_track(track: str) -> str:
    if track not in ("code", "no-code"):
        raise ValueError(f"There is no track called '{track}'. track must be 'code' or 'no-code'.")
    return track


def get_track_tools(track: str) -> dict:
    """Every tool one track uses, in the order the course meets them. Only what the sheet names."""
    tools = []
    for lecture in fetch_lectures(check_track(track)):
        for tool in lecture["tools"].replace(" or ", ",").split(","):   # "Gradio or Streamlit" is two tools
            tool = tool.strip()
            if tool not in NOT_TOOLS and tool not in tools:
                tools.append(tool)
    return {"track": track, "tools": tools}


def get_lecture(number: int, track: str) -> dict:
    """One lecture of one track: its date, title, type and tools."""
    for lecture in fetch_lectures(check_track(track)):
        if lecture["number"] == number:
            return dict(lecture, track=track)
    raise ValueError(f"There is no lecture {number}. The course has lectures 1 to 19.")


FUNCTIONS = {"get_track_tools": get_track_tools, "get_lecture": get_lecture}

# ---------------------------------------------------------------- the cards

TRACK = {"type": "string", "description": "Which track: code or no-code."}

TOOLS_CARD = {"type": "function", "function": {
    "name": "get_track_tools",
    "description": "Returns every tool one track of the 100xEngineers Cohort 8 course uses, from the curriculum sheet. "
                   "Use it for any question about what a track teaches or which track to choose. "
                   "Call it once for each track you need.",
    "parameters": {"type": "object", "properties": {"track": TRACK}, "required": ["track"]},
}}

LECTURE_CARD = {"type": "function", "function": {
    "name": "get_lecture",
    "description": "Returns one lecture of the 100xEngineers Cohort 8 course: its date, title, type and tools. "
                   "Use it when someone asks about a specific lecture by number. Not for general questions.",
    "parameters": {"type": "object", "properties": {
        "number": {"type": "integer", "description": "The lecture number, 1 to 19."},
        "track": TRACK}, "required": ["number", "track"]},
}}

CARDS = [TOOLS_CARD, LECTURE_CARD]


def run_tool(name: str, arguments: dict) -> dict:
    """Runs one tool call. Anything that goes wrong comes back as an error, never as a guess."""
    if name not in FUNCTIONS:
        return {"error": f"there is no tool called {name}"}
    try:
        return FUNCTIONS[name](**arguments)
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------- MCP: the same tools, at an address

def serve():
    """Hands the same functions and the same cards to FastMCP. Nothing above this line changes."""
    from fastmcp import FastMCP
    from fastmcp.tools import FunctionTool

    mcp = FastMCP("100x curriculum")
    for card in CARDS:
        card = card["function"]
        mcp.add_tool(FunctionTool(fn=FUNCTIONS[card["name"]], name=card["name"],
                                  description=card["description"], parameters=card["parameters"]))
    # stateless_http and json_response keep every message a plain POST with a JSON answer, so you can read them.
    mcp.run(transport="http", port=8000, stateless_http=True, json_response=True)


if __name__ == "__main__":
    if sys.argv[1:] == ["serve"]:
        serve()                                                   # the address is http://localhost:8000/mcp
    else:
        print(get_track_tools("no-code"))
        print(get_track_tools("code"))
        print(get_lecture(13, "code"))
