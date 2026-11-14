# Lecture 12: Give the model a tool, then move the tool to an address

One question since Lecture 9: which track should I choose in the 100xEngineers cohort? The model can't know. A function that reads the curriculum sheet can. Notes: https://100x-curriculum.vercel.app/c8/module-2/lecture-12-building-with-tool-calling-and-mcp/notes

| Step | Run | What it shows |
|---|---|---|
| 01 | `python 01_bare.py` | A system prompt alone: the model has no numbers |
| 02 | `python 02_paste.py` | Paste the whole curriculum: right, and you pay for all of it on every question |
| 03 | `python 03_function.py` | Just the function. No model |
| 04 | `python 04_by_hand.py` | One tool call. You press Enter to run it |
| 05 | `python 05_loop.py "your question"` | The server runs the loop and keeps the record |
| 06 | `python 06_verify.py` | Six cases written before the run. Two are there to fail |
| 07 | `uvicorn 07_server:app --port 8001` then `python 07_chat.py` | The loop behind a route, a Gradio chat in front |
| 08 | `python 08_mcp_server.py` | The same tools at an address: an MCP server |
| 09 | `python 09_second_app.py` | A second app that only knows the address |

`tools.py` holds the two functions and their cards. `agent.py` is the loop. `llm.py` is the one call to Groq. `data.py` reads the curriculum sheet.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env        # paste your Groq key
```

The tools read the live curriculum sheet. If it can't be reached, they use the saved copies, `curriculum-code.csv` and `curriculum-no-code.csv`.

On the free Groq tier you will see `(rate limit, waiting N seconds)`. That is the code waiting for you. Step 06 takes a few minutes. The free tier also allows 200,000 tokens a day; one run of step 06 uses about 8,000.
