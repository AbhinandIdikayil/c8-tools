"""The deterministic side: two functions that read the curriculum sheet, and the cards that describe them to the model."""
from data import fetch_lectures

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
