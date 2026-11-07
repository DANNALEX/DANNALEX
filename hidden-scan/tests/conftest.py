import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
FIX = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session", autouse=True)
def fixtures():
    if not FIX.exists() or not any(FIX.iterdir()):
        subprocess.run([sys.executable, str(ROOT / "scripts" / "make_fixtures.py")], check=True)
    return FIX
