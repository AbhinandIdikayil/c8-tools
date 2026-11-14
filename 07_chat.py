"""Step 7. The client only asks. It shows the answer, and the record under it as the evidence."""
import gradio as gr
import requests


def chat(message, history):
    out = requests.post("http://127.0.0.1:8001/api/ask", json={"question": message, "track": "code"}).json()
    evidence = "\n".join(f"- `{s['tool']}({s['arguments']})` → `{s['result']}`" for s in out["record"])
    return out["answer"] + ("\n\n**What the server did**\n" + evidence if evidence else "\n\n*No tool was called.*")


gr.ChatInterface(fn=chat, title="Ask about the 100x curriculum").launch()
