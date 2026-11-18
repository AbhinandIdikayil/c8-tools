"""Part 2: the same tool on the sheet's side, as an MCP server.  Run: python mcp_server.py
The steps are in README.md."""

import csv, io, os, socket  # noqa: I001
from typing import Annotated
import requests
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

SHEET = "https://docs.google.com/spreadsheets/d/1Kg6T-dJWaYx_JCPiRk3u0nBuAQcsCVRDPj1NFKP4WzM/gviz/tq?tqx=out:csv&headers=0&gid=368290478"
ABHINAND_RESUME = {
    "summary": "https://docs.google.com/spreadsheets/d/1LmRr3bSKjHLaSVaPWwm7b05dE8Wxbos43qa1LwQ2V8U/export?format=csv&gid=862421201",
    "work_exp": "https://docs.google.com/spreadsheets/d/1LmRr3bSKjHLaSVaPWwm7b05dE8Wxbos43qa1LwQ2V8U/export?format=csv&gid=0",
    "education": "https://docs.google.com/spreadsheets/d/1LmRr3bSKjHLaSVaPWwm7b05dE8Wxbos43qa1LwQ2V8U/export?format=csv&gid=1436390820",
    "skills": "https://docs.google.com/spreadsheets/d/1LmRr3bSKjHLaSVaPWwm7b05dE8Wxbos43qa1LwQ2V8U/export?format=csv&gid=588835937",
    "projects": "https://docs.google.com/spreadsheets/d/1LmRr3bSKjHLaSVaPWwm7b05dE8Wxbos43qa1LwQ2V8U/export?format=csv&gid=1460252361",
}
mcp = FastMCP("100x curriculum")


@mcp.tool
def get_lecture(number: Annotated[int, "The lecture number, 1 to 19."]) -> dict:
    """ONLY use this tool if the user asks about '100x Cohort' lectures. Do NOT use this for other courses."""
    for row in csv.reader(io.StringIO(requests.get(SHEET).text)):
        if row[1].startswith(f"{number}. "):
            return {"date": row[0], "title": row[1], "type": row[2], "tools": row[3]}
    return {"error": f"There is no lecture {number}. Lectures run from 1 to 19."}


def _fetch_rows(url: str) -> list[dict]:
    """Read one sheet as CSV and turn every row into a dict keyed by its header row."""
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    rows = []
    for raw in csv.DictReader(io.StringIO(response.text)):
        row = {
            key.strip(): (value or "").strip()
            for key, value in raw.items()
            if key and key.strip()  # drop unnamed trailing columns
        }
        if any(row.values()):  # skip blank rows
            rows.append(row)
    print(rows)
    return rows


def _fetch_key_value(url: str, label_key: str = "Field Label") -> dict:
    """Read a two-column sheet into a flat {label: value} dict."""
    result = {}

    for row in _fetch_rows(url):
        label = row.get(label_key)
        value = row.get("Value")
        if label and value:
            result[label] = value

    return result


@mcp.tool
def get_summary() -> dict:
    """Abhinand's profile: name, title, summary, experience, focus, contact email."""
    return _fetch_key_value(ABHINAND_RESUME["summary"])


@mcp.tool
def get_experience_info() -> list[dict]:
    """Abhinand's work experience, one entry per role with dates, impact and tech stack."""
    return _fetch_rows(ABHINAND_RESUME["work_exp"])


@mcp.tool
def get_project_info() -> list[dict]:
    """Abhinand's projects with architecture, tech stack, deployment, live and GitHub links."""
    return _fetch_rows(ABHINAND_RESUME["projects"])


@mcp.tool
def get_skills_info() -> dict:
    """Abhinand's skills grouped by area (frontend, backend, devops, AI, languages)."""
    return _fetch_key_value(ABHINAND_RESUME["skills"])


get_skills_info()


@mcp.tool
def get_education_info() -> list[dict]:
    """Abhinand's education with institution, dates and status."""
    return _fetch_rows(ABHINAND_RESUME["education"])


@mcp.tool
def get_resume() -> dict:
    """Abhinand's whole resume in one call: summary, experience, projects, skills, education."""
    return {
        "summary": _fetch_key_value(ABHINAND_RESUME["summary"]),
        "experience": _fetch_rows(ABHINAND_RESUME["work_exp"]),
        "projects": _fetch_rows(ABHINAND_RESUME["projects"]),
        "skills": _fetch_key_value(ABHINAND_RESUME["skills"]),
        "education": _fetch_rows(ABHINAND_RESUME["education"]),
    }


# Render requires the server to listen on all interfaces.
if __name__ == "__main__":
    port = int(os.environ.get("PORT"))

    if socket.socket().connect_ex(("0.0.0.0", port)) == 0:
        raise SystemExit(
            f"Port {port} is already in use, probably by a server you started earlier. "
            f"Stop it with Ctrl+C in its terminal, or run: kill $(lsof -t -i:{port})"
        )
    mcp.run(transport="http", host="0.0.0.0", port=port)
