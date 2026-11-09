import os
import sys
import io

DEFAULT_PDF_PATH = r"C:\Users\dumit\Dropbox\0000.EU\0000.Claude acces\00000.LUCRU\00000.Scoli pentru viitor\000.DOC. DE EVALUARE SI SELECTIE_DK\Crt1.1_CV+doc_Bradatan D.pdf"


def ensure_deps():
    try:
        import fitz  # PyMuPDF
        from PIL import Image, ImageEnhance
        return fitz, Image, ImageEnhance
    except ImportError:
        import subprocess
        print("Se instaleaza bibliotecile necesare (PyMuPDF, Pillow)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "pymupdf", "Pillow"])
        import fitz
        from PIL import Image, ImageEnhance
        return fitz, Image, ImageEnhance


def compress_pdf_profile(fitz, Image, ImageEnhance, input_path, output_path, dpi=130, quality=65, contrast_boost=1.18):
    src_doc = fitz.open(input_path)
    out_doc = fitz.open()

    for page_index in range(len(src_doc)):
        page = src_doc[page_index]
        rect = page.rect
        pix = page.get_pixmap(dpi=dpi, alpha=False)

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        if contrast_boost and contrast_boost != 1.0:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast_boost)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True, progressive=True)
        jpg_bytes = buf.getvalue()

        new_page = out_doc.new_page(width=rect.width, height=rect.height)
        new_page.insert_image(rect, stream=jpg_bytes)

    out_doc.save(output_path, garbage=4, deflate=True, clean=True)
    out_doc.close()
    src_doc.close()


def format_mb(size_bytes):
    return f"{size_bytes / (1024 * 1024):.2f} MB ({size_bytes / 1024:.0f} KB)"


def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PDF_PATH
    if not os.path.isfile(input_path):
        print(f"Eroare: Fisierul nu a fost gasit la calea:\n{input_path}")
        sys.exit(1)

    fitz, Image, ImageEnhance = ensure_deps()
    orig_size = os.path.getsize(input_path)
    base_dir = os.path.dirname(input_path)
    base_name, _ = os.path.splitext(os.path.basename(input_path))

    profiles = [
        ("OPTIM_LIZIBIL", 130, 65, 1.18),
        ("MAXIM_COMPRIMAT", 96, 52, 1.22),
    ]

    print(f"Fisier original: {os.path.basename(input_path)}")
    print(f"Dimensiune initiala: {format_mb(orig_size)}\n")

    for label, dpi, quality, contrast in profiles:
        out_path = os.path.join(base_dir, f"{base_name}_{label}.pdf")
        print(f"Se genereaza varianta {label} ({dpi} DPI, calitate JPEG {quality}%)...")
        compress_pdf_profile(fitz, Image, ImageEnhance, input_path, out_path, dpi=dpi, quality=quality, contrast_boost=contrast)
        new_size = os.path.getsize(out_path)
        reduction = ((orig_size - new_size) / orig_size) * 100 if orig_size > 0 else 0
        print(f" -> Salvat: {out_path}")
        print(f" -> Dimensiune noua: {format_mb(new_size)} (Reducere: {reduction:.1f}%)\n")


if __name__ == "__main__":
    main()
