"""The verifier. The cases are written before the run, from the sheet, by hand.

python verify.py    six cases. Two are there to fail
"""
from ask import RULE, SYSTEM, USED, ask
from tools import CARDS, run_tool

# Change this line to try a fix, then run again. First fix to try: SYSTEM + RULE
SYSTEM_PROMPT = SYSTEM

INVENTED = ["Zapier", "Bubble", "Webflow", "JavaScript"]         # what the model made up in Lecture 10

CASES = [
    {"question": "Which tools does the no-code track use?",
     "calls": [{"tool": "get_track_tools", "arguments": {"track": "no-code"}}],
     "answer_has": ["Antigravity", "Google AI Studio"], "answer_lacks": INVENTED},
    {"question": "Which track should I choose in the 100xEngineers cohort?",
     "calls": [{"tool": "get_track_tools", "arguments": {"track": "code"}},
               {"tool": "get_track_tools", "arguments": {"track": "no-code"}}],
     "answer_has": ["Python", "Antigravity"], "answer_lacks": INVENTED},
    {"question": "When is Lecture 13 on the code track, and what is it about?",
     "calls": [{"tool": "get_lecture", "arguments": {"number": 13, "track": "code"}}],
     "answer_has": ["Retrieval"]},
    # The model should answer this one itself.
    {"question": "What is an API?",
     "calls": []},
    # The sheet has no such track, so no tool should run and no tool list should be given.
    {"question": "Which tools does the entrepreneurship track use?",
     "calls": [], "answer_lacks": ["Antigravity", "Python"]},
    # Any calls are fine here; the answer must be right. Checked in the sheet: lectures 7 and 8.
    {"question": "Which lectures on the code track use Supabase?",
     "answer_has": ["7", "8"]},
]


def plain(text: str) -> str:
    """The model writes special spaces and hyphens, and changes capitals. Make text comparable before checking it."""
    return text.replace("\u202f", " ").replace("\u00a0", " ").replace("\u2011", "-").lower()


def check(case: dict, out: dict) -> list[str]:
    """Compares what the system did with what you wrote down. Returns what is wrong."""
    wrong = []
    did = []                                              # successful calls, a repeat counted once
    for s in out["record"]:
        call = {"tool": s["tool"], "arguments": s["arguments"]}
        if s["status"] == "success" and call not in did:
            did.append(call)
    same = sorted(map(str, did)) == sorted(map(str, case.get("calls", did)))      # the order does not matter
    if not same:
        wrong.append(f"expected calls {case['calls']}, got {did}")
    answer = plain(out["answer"])
    for word in case.get("answer_has", []):
        if plain(word) not in answer:
            wrong.append(f"the answer does not say {word}")
    for word in case.get("answer_lacks", []):
        if plain(word) in answer:
            wrong.append(f"the answer says {word}")
    return wrong


passed = 0
for case in CASES:
    out = ask(case["question"], CARDS, run_tool, system=SYSTEM_PROMPT)
    wrong = check(case, out)
    passed += not wrong
    print("PASS" if not wrong else "FAIL", "", case["question"])
    for w in wrong:
        print("      ", w)
print(f"\n{passed} of {len(CASES)} passed, {USED['tokens']} tokens used")
