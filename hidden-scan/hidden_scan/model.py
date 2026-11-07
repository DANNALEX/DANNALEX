from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any


SEVERITIES = ("info", "low", "medium", "high")
CONFIDENCES = ("confirmed", "probable")


@dataclass
class Finding:
    """O singură constatare, produsă de un scaner."""
    scanner: str                       # "metadata", "pdf", ...
    category: str                      # "hidden-text", "prompt-injection", ...
    severity: str                      # vezi SEVERITIES
    title: str                         # rezumat pe o linie
    detail: str = ""                   # explicație
    evidence: str = ""                 # fragmentul brut care justifică
    confidence: str = "confirmed"      # vezi CONFIDENCES

    def __post_init__(self) -> None:
        if self.severity not in SEVERITIES:
            raise ValueError(f"severity invalid: {self.severity}")
        if self.confidence not in CONFIDENCES:
            raise ValueError(f"confidence invalid: {self.confidence}")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CleanResult:
    """Rezultatul operațiunii de ștergere metadate / curățare pe un fișier."""
    source_file: str
    output_file: str = ""
    cleaned: bool = False
    removed_items: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    before_findings_count: int = 0
    after_findings_count: int = 0

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Report:
    file: str
    analyzed_at: str                   # ISO 8601
    sha256: str = ""
    filetype: str = ""
    size_bytes: int = 0
    tool_versions: dict[str, str] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    risk: str = "LOW"                  # LOW | MEDIUM | HIGH
    errors: list[str] = field(default_factory=list)
    clean_result: CleanResult | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
