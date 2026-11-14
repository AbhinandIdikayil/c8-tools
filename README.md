# Lecture 12: Give the model a tool, then give the tool an address

One question since Lecture 9: which track should I choose in the 100xEngineers cohort? The model can't know. A function that reads the curriculum sheet can. Notes: https://100x-curriculum.vercel.app/c8/module-2/lecture-12-building-with-tool-calling-and-mcp/notes

Three files. Run them in this order.

| Step | Run | What it shows |
|---|---|---|
| 1 | `python ask.py bare` | A system prompt alone: the model has no numbers |
| 2 | `python ask.py paste` | Paste the whole curriculum: right, and you pay for all of it on every question |
| 3 | `python tools.py` | Just the function. No model |
| 4 | `python ask.py hand` | One tool call. You press Enter to run it |
| 5 | `python ask.py "your question"` | The loop runs the tools and keeps the record |
| 6 | `python verify.py` | Six cases written before the run. Two are there to fail |
| 7 | `python tools.py serve` | The same tools at an address: an MCP server |
| 8 | `python ask.py mcp "your question"` | In a second terminal. The tools come from the address |

| File | Holds |
|---|---|
| `tools.py` | The two functions, their cards, and the MCP server |
| `ask.py` | The one call to Groq, the loop, and the MCP client |
| `verify.py` | The cases and the check |

## Setup

```bash
pip install requests python-dotenv fastmcp
```

Make a file called `.env` next to the three files, with one line: `GROQ_API_KEY=your key`.

The tools read the live curriculum sheet, so you need to be online.

On the free Groq tier you will see `(rate limit, waiting N seconds)`. That is the code waiting for you. Step 6 takes a few minutes. The free tier also allows 200,000 tokens a day; one run of step 6 uses about 8,000.
