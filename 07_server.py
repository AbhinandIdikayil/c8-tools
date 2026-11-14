"""Step 7. The loop behind a route, as in Lecture 7. The key and the tools stay on the server."""
from fastapi import FastAPI
from pydantic import BaseModel

from agent import ask
from llm import RULE, SYSTEM

app = FastAPI()


class QuestionIn(BaseModel):
    question: str
    track: str | None = None                                     # the app knows who is asking; the model does not


@app.post("/api/ask")
def ask_route(body: QuestionIn):
    context = f" The student asking is on the {body.track} track." if body.track else ""
    return ask(body.question, system=SYSTEM + RULE + context)           # the answer and the record, together
