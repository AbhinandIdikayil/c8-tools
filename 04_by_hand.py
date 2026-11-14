"""Step 4. One tool call, carried by hand. You are the server."""
import json

from llm import SYSTEM, ask_groq
from tools import CARDS, run_tool

QUESTION = "Which tools does the no-code track use?"
messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": QUESTION}]

# 1. Send the question and one card.
reply = ask_groq(messages, tools=CARDS[:1])
print("The model sent back:\n", json.dumps(reply, indent=2))

# 2. The model has stopped. Nothing has touched the table yet.
call = reply["tool_calls"][0]
name, arguments = call["function"]["name"], json.loads(call["function"]["arguments"])
input(f"\nRun {name}({arguments})? Press Enter. ")

# 3. Your code runs it.
result = run_tool(name, arguments)
print("The table returned:\n", result)

# 4. Hand the result back, with the whole conversation so far.
messages.append(reply)
messages.append({"role": "tool", "tool_call_id": call["id"], "content": json.dumps(result)})
answer = ask_groq(messages, tools=CARDS[:1])
print("\nThe model's answer:\n", answer["content"])
