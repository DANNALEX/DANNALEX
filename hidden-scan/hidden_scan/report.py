from __future__ import annotations
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from hidden_scan.model import Report

_ENV = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    autoescape=True,   # necondiționat — protejează împotriva XSS din evidence
)


def render_html(reports: list[Report]) -> str:
    return _ENV.get_template("report.html.j2").render(
        reports=[r.as_dict() for r in reports])
