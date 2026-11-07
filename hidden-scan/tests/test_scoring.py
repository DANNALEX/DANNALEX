from hidden_scan.model import Finding
from hidden_scan.core import _score


def test_single_high_is_high():
    assert _score([Finding("s", "c", "high", "t")]) == "HIGH"


def test_probable_halves_weight():
    assert _score([Finding("s", "c", "high", "t", confidence="probable")]) == "MEDIUM"


def test_empty_is_low():
    assert _score([]) == "LOW"
