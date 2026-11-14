"""The model side: one call to Groq, and the loop around it. Each step of the lecture is one word.

python ask.py bare               the model with a system prompt and nothing else
python ask.py paste              the whole curriculum pasted under the question
python ask.py hand               one tool call. You press Enter to run it
python ask.py "your question"    the loop runs the tools and keeps the record
python ask.py mcp "question"     the tools come from an address (first: python tools.py serve)
"""
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

MODEL = "openai/gpt-oss-120b"
SYSTEM = "You answer questions about the 100xEngineers Cohort 8 course. Answer in a few plain sentences."
RULE = (" For anything about the course, its tracks or its lectures, call a tool first and answer only from what it returns."
        " Never answer those from memory.")
USED = {"tokens": 0}                                             # a running count, so you can see what a run costs


# ---------------------------------------------------------------- one call to the model

def ask_groq(messages: list, tools: list | None = None) -> dict:
    """The request you built by hand in Lecture 5, with one new field: tools. Returns the model's message."""
    package = {"model": MODEL, "messages": messages}
    if tools:
        package["tools"] = tools
    tries = 0
    while True:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
            json=package,
            timeout=60,
        )
        if r.status_code == 429:                                  # the free tier asking you to slow down
            wait = float(r.headers.get("retry-after", 10)) + 1
            print(f"(rate limit, waiting {wait:.0f} seconds)")
            time.sleep(wait)
        elif r.status_code == 400 and tools and tries < 2:        # the model wrote a tool call Groq could not read
            tries += 1
            print("(the model wrote a call Groq could not read, asking again)")
        else:
            break
    r.raise_for_status()
    USED["tokens"] += r.json()["usage"]["total_tokens"]
    return r.json()["choices"][0]["message"]


# ---------------------------------------------------------------- the loop

def ask(question: str, cards: list | None = None, run=None, system: str = SYSTEM, pause: bool = False) -> dict:
    """Asks the model, runs whatever tool it requests, hands the result back, until it answers.
    Returns the answer and the record: every call, its arguments and its result."""
    messages = [{"role": "system", "content": system}, {"role": "user", "content": question}]
    record = []
    for _ in range(5):                                            # your code decides when the loop stops
        reply = ask_groq(messages, tools=cards)
        if not reply.get("tool_calls"):                           # no request: this is the answer
            return {"question": question, "answer": reply["content"], "record": record}
        messages.append(reply)
        for call in reply["tool_calls"]:                          # the model asked; your code acts
            name = call["function"]["name"]
            arguments = json.loads(call["function"]["arguments"])
            if pause:                                             # by hand: nothing has touched the sheet yet
                print("The model sent back:\n", json.dumps(reply, indent=2))
                input(f"\nRun {name}({arguments})? Press Enter. ")
            result = run(name, arguments)
            record.append({"tool": name, "arguments": arguments, "result": result,
                           "status": "error" if "error" in result else "success"})
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": json.dumps(result)})
    return {"question": question, "answer": "I could not finish in five rounds.", "record": record}


# ---------------------------------------------------------------- MCP: the tools come from an address

ADDRESS = "http://localhost:8000/mcp"


def mcp(method: str, params: dict | None = None) -> dict:
    """One MCP message: a POST with a JSON package, like every request since Lecture 4."""
    r = requests.post(ADDRESS, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}})
    return r.json()["result"]


def cards_from_server() -> list:
    """Ask the server what it can do. The cards come back."""
    return [{"type": "function", "function": {"name": t["name"], "description": t["description"],
                                              "parameters": t["inputSchema"]}} for t in mcp("tools/list")["tools"]]


def run_on_server(name: str, arguments: dict) -> dict:
    """Send the call to the server instead of running a local function."""
    result = mcp("tools/call", {"name": name, "arguments": arguments})
    if result["isError"]:
        return {"error": result["content"][0]["text"]}
    return result["structuredContent"]


# ---------------------------------------------------------------- the steps

QUESTION = "Which track should I choose in the 100xEngineers cohort?"

if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else QUESTION

    if step == "bare":                                            # no cards, so the model has nothing to ask for
        out = ask(QUESTION)

    elif step == "paste":                                         # every row of both tabs, on every question
        from tools import fetch_lectures
        pasted = ""
        for track in ("code", "no-code"):
            pasted += f"\n\n{track} track\nnumber,date,title,type,tools\n"
            pasted += "\n".join(f"{x['number']},{x['date']},{x['title']},{x['type']},{x['tools']}" for x in fetch_lectures(track))
        out = ask(QUESTION + pasted)

    elif step == "hand":                                          # one card, and you are the Enter key
        from tools import CARDS, run_tool
        out = ask("Which tools does the no-code track use?", CARDS[:1], run_tool, pause=True)

    elif step == "mcp":                                           # this step never imports tools.py
        cards = cards_from_server()
        print("The server offers:", [c["function"]["name"] for c in cards], "\n")
        out = ask(sys.argv[2] if len(sys.argv) > 2 else QUESTION, cards, run_on_server, system=SYSTEM + RULE)

    else:                                                         # the loop, with the cards and the functions
        from tools import CARDS, run_tool
        out = ask(step, CARDS, run_tool)

    for call in out["record"]:
        print("tool     ", call["tool"])
        print("arguments", call["arguments"])
        print("result   ", call["result"])
        print("status   ", call["status"], "\n")
    print("answer   ", out["answer"])
    print(f"\n{USED['tokens']} tokens used")

    with open("log.jsonl", "a") as f:                             # one line per question, kept as evidence
        f.write(json.dumps(out) + "\n")
