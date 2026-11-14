# Lecture 12: a tool call, then an MCP server

Notes: https://100x-curriculum.vercel.app/c8/module-2/lecture-12-building-with-tool-calling-and-mcp/notes

Two files, two steps.

| Step | File | What it shows |
|---|---|---|
| 1 | `tool_call.py` | The model asks for your function, your code runs it, the model answers from the result |
| 2 | `mcp_server.py` | The same function as an MCP server, so any MCP client can use it |

## Setup

```bash
pip install requests python-dotenv fastmcp
```

Make a file called `.env` next to the two files, with one line: `GROQ_API_KEY=your key`.

## Step 1

```bash
python tool_call.py
```

## Step 2

```bash
python mcp_server.py
```

Leave it running. In a second terminal, ask the server what it offers, then call the tool:

```bash
fastmcp list http://localhost:8000/mcp
fastmcp call http://localhost:8000/mcp get_lectures track=code
```

## If something goes wrong

| You see | Fix |
|---|---|
| `No GROQ_API_KEY found` | Make the `.env` file from Setup, next to `tool_call.py` |
| `429` from Groq | You hit the free rate limit. Wait a minute and run again |
| `Port 8000 is already in use` | A server from an earlier run is still on. Press Ctrl+C in its terminal, or run `kill $(lsof -t -i:8000)` |
| `Input should be 'code' or 'no-code'` | `track` only takes those two values |
