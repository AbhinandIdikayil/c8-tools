"""Step 1. The model with a system prompt and nothing else."""
from llm import SYSTEM, ask_groq

QUESTION = "Which track should I choose in the 100xEngineers cohort?"

answer = ask_groq([
    {"role": "system", "content": SYSTEM},
    {"role": "user", "content": QUESTION},
])
print(answer["content"])
