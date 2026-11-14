"""The loop. Everything you did by hand in step 4, now written as rules."""
import json

from llm import SYSTEM, ask_groq
from tools import CARDS, run_tool


def ask(question: str, cards: list = CARDS, system: str = SYSTEM, run=run_tool) -> dict:
    """Asks the model, runs whatever tool it requests, hands the result back, until it answers.
    Returns the answer and the record: every call, its arguments and its result."""
    messages = [{"role": "system", "content": system}, {"role": "user", "content": question}]
    record = []
    for _ in range(5):                                            # the server decides when the loop stops
        reply = ask_groq(messages, tools=cards)
        if not reply.get("tool_calls"):                           # no request: this is the answer
            return {"question": question, "answer": reply["content"], "record": record}
        messages.append(reply)
        for call in reply["tool_calls"]:                          # the model asked; the server acts
            name = call["function"]["name"]
            arguments = json.loads(call["function"]["arguments"])
            result = run(name, arguments)
            record.append({"tool": name, "arguments": arguments, "result": result,
                           "status": "error" if "error" in result else "success"})
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": json.dumps(result)})
    return {"question": question, "answer": "I could not finish in five rounds.", "record": record}

