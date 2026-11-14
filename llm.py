"""One call to the model. The same request you built by hand in Lecture 5, with one new field: tools."""
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

MODEL = "openai/gpt-oss-120b"
RULE = (" For anything about the course, its tracks or its lectures, call a tool first and answer only from what it returns."
        " Never answer those from memory.")
USED = {"tokens": 0}                                             # a running count, so you can see what a run costs
SYSTEM = "You answer questions about the 100xEngineers Cohort 8 course. Answer in a few plain sentences."


def ask_groq(messages: list, tools: list | None = None) -> dict:
    """Sends the conversation, and the tool cards if there are any. Returns the model's message."""
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
