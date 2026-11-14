"""Step 9. A second app. It has never seen tools.py: it only knows the server's address."""
import json
import sys

import requests

from agent import ask
from llm import RULE, SYSTEM

ADDRESS = "http://localhost:8000/mcp"


def mcp(method: str, params: dict | None = None) -> dict:
    """One MCP message: a POST with a JSON package, like every request since Lecture 4."""
    r = requests.post(ADDRESS, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}})
    return r.json()["result"]


# 1. Ask the server what it can do. The cards come back.
listed = mcp("tools/list")["tools"]
cards = [{"type": "function", "function": {"name": t["name"], "description": t["description"],
                                           "parameters": t["inputSchema"]}} for t in listed]
print("The server offers:", [t["name"] for t in listed], "\n")


# 2. When the model asks for a tool, send the call to the server instead of running a local function.
def run_on_server(name: str, arguments: dict) -> dict:
    result = mcp("tools/call", {"name": name, "arguments": arguments})
    if result["isError"]:
        return {"error": result["content"][0]["text"]}
    return result["structuredContent"]


# 3. The loop is the one from step 5. Only the cards and the runner changed.
question = sys.argv[1] if len(sys.argv) > 1 else "Which track should I choose in the 100xEngineers cohort?"
out = ask(question, cards=cards, run=run_on_server, system=SYSTEM + RULE)
print(json.dumps(out["record"], indent=2))
print("\nanswer   ", out["answer"])
