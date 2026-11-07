from hidden_scan.scanners import images


def test_trailing_bytes_png(fixtures):
    assert images.trailing_bytes(str(fixtures / "acropalypse.png")) > 0


def test_trailing_bytes_jpeg(fixtures):
    assert images.trailing_bytes(str(fixtures / "trailing.jpg")) > 0


def test_clean_png(tmp_path):
    from PIL import Image
    p = tmp_path / "clean.png"
    Image.new("RGB", (8, 8)).save(p)
    assert images.trailing_bytes(str(p)) == 0


def test_clean_jpeg(tmp_path):
    from PIL import Image
    p = tmp_path / "clean.jpg"
    Image.new("RGB", (8, 8)).save(p, "JPEG")
    assert images.trailing_bytes(str(p)) == 0
