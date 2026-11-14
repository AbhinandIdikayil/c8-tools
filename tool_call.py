"""Step 1: one tool call.  Run: python tool_call.py"""
import csv, io, json, os
import requests
from dotenv import load_dotenv

load_dotenv()

# 1. A plain Python function. It reads one track's tab of the public curriculum sheet.
SHEET = "https://docs.google.com/spreadsheets/d/1Kg6T-dJWaYx_JCPiRk3u0nBuAQcsCVRDPj1NFKP4WzM/gviz/tq?tqx=out:csv&gid="
TABS = {"code": "368290478", "no-code": "0"}

def get_lectures(track):
    rows = csv.reader(io.StringIO(requests.get(SHEET + TABS[track]).text))
    return [row[1] + ": " + row[3] for row in rows if row[1][:1].isdigit()]

# 2. A card that tells the model this function exists.
card = {"type": "function", "function": {
    "name": "get_lectures",
    "description": "Lists every lecture of one 100xEngineers Cohort 8 track, with the tools it uses.",
    "parameters": {"type": "object",
                   "properties": {"track": {"type": "string", "enum": ["code", "no-code"]}},
                   "required": ["track"]},
}}

def ask_groq(messages):
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                      headers={"Authorization": "Bearer " + os.environ["GROQ_API_KEY"]},
                      json={"model": "openai/gpt-oss-120b", "messages": messages, "tools": [card]})
    r.raise_for_status()                                          # 429 means wait a minute and run again
    return r.json()["choices"][0]["message"]

# 3. Ask. The model does not answer: it asks for the function.
messages = [
    {"role": "system", "content": "For any question about the course, call get_lectures first. Answer in three sentences."},
    {"role": "user", "content": "Which track should I choose in the 100xEngineers cohort?"},
]
reply = ask_groq(messages)

# 4. While the model asks for the function, your code runs it and hands the result back.
while reply.get("tool_calls"):
    messages.append(reply)
    for call in reply["tool_calls"]:
        args = json.loads(call["function"]["arguments"])
        print("The model asked for: get_lectures", args)
        result = get_lectures(**args)
        messages.append({"role": "tool", "tool_call_id": call["id"], "content": json.dumps(result)})
    reply = ask_groq(messages)

# 5. No more requests: this is the answer, written from the sheet.
print("\n" + reply["content"])
