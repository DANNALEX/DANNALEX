from __future__ import annotations

# --- metadate sensibile, pe niveluri de risc (substring, case-insensitive) ---
# HIGH: scurgeri directe de identitate/locație/hardware
META_HIGH = (
    "GPS", "SerialNumber", "Author", "CreatorTool", "OwnerName",
    "CameraOwnerName", "Artist", "Copyright", "dc:creator",
)
# MEDIUM: identitate organizațională / istoric de editare
META_MEDIUM = (
    "LastModifiedBy", "TotalEditTime", "TotalTime", "Company", "Manager",
    "History", "Revision", "Comments", "Subject", "Title", "Template",
    "cp:lastModifiedBy", "cp:revision",
)
# LOW: câmpuri cvasi-ubicue (aproape orice fișier le are) → probable, ca să nu
#      ridice singure documente benigne la HIGH
META_LOW = (
    "Creator", "Producer", "Software", "Keywords", "Application",
    "CreateDate", "ModifyDate", "CreationDate", "ModDate",
    "dcterms:created", "dcterms:modified",
)
SENSITIVE_META_KEYS = META_HIGH + META_MEDIUM + META_LOW

# --- markeri de prompt injection pentru dual-extraction ---
INJECTION_MARKERS = {
    "ignore", "disregard", "override", "instructions",
    "jailbreak", "exfiltrate", "sudo",
}

# --- scoring ---
RISK_WEIGHTS = {"info": 0.0, "low": 1.0, "medium": 2.5, "high": 5.0}
RISK_THRESHOLDS = {"medium": 2.5, "high": 5.0}

# --- extensii suportate pentru parcurgerea directoarelor ---
SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".xlsx", ".pptx",
    ".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp",
    ".txt", ".md", ".csv", ".json", ".py", ".js", ".ts", ".yaml", ".yml",
}

IGNORED_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules",
    "_CURATATE", "_BACKUP_ORIGINALE",
}
