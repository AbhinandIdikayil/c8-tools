"""Step 5. The server runs the loop, and keeps the record."""
import json
import sys

from agent import ask
from llm import USED

question = sys.argv[1] if len(sys.argv) > 1 else "Which track should I choose in the 100xEngineers cohort?"
out = ask(question)

for step in out["record"]:
    print("tool     ", step["tool"])
    print("arguments", step["arguments"])
    print("result   ", step["result"])
    print("status   ", step["status"], "\n")
print("answer   ", out["answer"])
print(f"\n{USED['tokens']} tokens used")

with open("log.jsonl", "a") as f:                                 # one line per question, kept as evidence
    f.write(json.dumps(out) + "\n")
