"""Step 2. Paste the curriculum into the prompt, as in Lecture 10."""
from data import fetch_lectures
from llm import SYSTEM, USED, ask_groq

QUESTION = "Which track should I choose in the 100xEngineers cohort?"

pasted = ""
for track in ("code", "no-code"):
    pasted += f"\n\n{track} track\nnumber,date,title,type,tools\n"
    pasted += "\n".join(f"{x['number']},{x['date']},{x['title']},{x['type']},{x['tools']}" for x in fetch_lectures(track))

answer = ask_groq([
    {"role": "system", "content": SYSTEM},
    {"role": "user", "content": QUESTION + pasted},
])
print(answer["content"])
print(f"\n{USED['tokens']} tokens used")
