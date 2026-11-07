from hidden_scan.model import Report, Finding
from hidden_scan.report import render_html


def test_html_escapes_evidence():
    r = Report(file="doc", analyzed_at="t")
    r.findings.append(Finding(
        scanner="s", category="c", severity="low", title="t",
        evidence="<script>alert(1)</script>"))
    html = render_html([r])
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html
