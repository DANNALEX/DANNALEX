from hidden_scan.scanners import unicode_scan


def test_tag_block_detected():
    findings = unicode_scan.scan_text("hi" + chr(0xE0041))
    assert any("tag block" in f.evidence for f in findings)
    assert any(f.severity == "high" for f in findings)


def test_bidi_detected():
    findings = unicode_scan.scan_text("a" + chr(0x202E) + "b")
    assert any("bidi" in f.evidence for f in findings)


def test_variation_selectors_are_probable():
    text = "abc" + "".join(chr(0xE0100 + i) for i in range(5))
    vs = [f for f in unicode_scan.scan_text(text) if "variation" in f.evidence]
    assert vs and all(f.confidence == "probable" for f in vs)


def test_clean_text_no_findings():
    assert unicode_scan.scan_text("text complet curat, fara pasageri") == []
