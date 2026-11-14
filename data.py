"""Where the curriculum lives: the public 100xEngineers Cohort 8 Google Sheet, one tab per track.
The same sheet the map and the Tool Bench read. If the sheet can't be reached, a saved copy is used."""
import csv
import io
import re
from pathlib import Path

import requests

SHEET = "https://docs.google.com/spreadsheets/d/1Kg6T-dJWaYx_JCPiRk3u0nBuAQcsCVRDPj1NFKP4WzM/gviz/tq?tqx=out:csv&headers=0"
TABS = {"no-code": "0", "code": "368290478"}                      # the tab ids in the sheet's address


def fetch_lectures(track: str) -> list[dict]:
    """Every lecture of one track: number, date, title, type and the tools cell, as written in the sheet."""
    try:
        text = requests.get(SHEET + "&gid=" + TABS[track], timeout=10).text
    except requests.RequestException:
        text = (Path(__file__).parent / f"curriculum-{track}.csv").read_text()
    lectures = []
    for row in csv.reader(io.StringIO(text)):
        numbered = re.match(r"(\d+)\.\s*(.+)", row[1]) if len(row) > 3 else None
        if numbered:                                              # holidays and the hackathon have no number
            lectures.append({"number": int(numbered.group(1)), "date": row[0], "title": numbered.group(2).strip(),
                             "type": row[2], "tools": row[3].strip()})
    return lectures
