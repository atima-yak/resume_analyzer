import io
import pdfplumber
from pathlib import Path


class UnsupportedFileTypeError(Exception):
    """error raised when the uploaded file is not a supported type (e.g., not PDF)"""
    pass


def _pages_to_text(pdf) -> str:
    """ดึงข้อความจากทุกหน้าของ pdfplumber object แล้ว join กันเป็นข้อความเดียว"""
    extracted_text = []
    for page in pdf.pages:
        # extract_text() อาจคืน None ถ้าหน้านั้นไม่มีข้อความ (เช่น เป็นรูปภาพ) จึงต้องกันไว้
        page_text = page.extract_text()
        if page_text:
            extracted_text.append(page_text)
    return "\n".join(extracted_text).strip()


def extract_text_from_pdf(file_path: str) -> str:
    """
    แกะข้อความทั้งหมดจากไฟล์ PDF resume (ใช้เมื่อมีไฟล์อยู่บน disk แล้ว)

    Args:
        file_path: path ของไฟล์ resume

    Returns:
        ข้อความทั้งหมดในไฟล์ (รวมทุกหน้า)

    Raises:
        UnsupportedFileTypeError: ถ้าไฟล์ไม่ใช่ .pdf
        FileNotFoundError: ถ้าไม่พบไฟล์
        ValueError: ถ้าแกะข้อความไม่ได้เลย
    """
    path = Path(file_path)

    if path.suffix.lower() != ".pdf":
        raise UnsupportedFileTypeError(
            f"รองรับเฉพาะไฟล์ PDF เท่านั้น ได้รับไฟล์ประเภท: {path.suffix}"
        )

    if not path.exists():
        raise FileNotFoundError(f"ไม่พบไฟล์: {file_path}")

    with pdfplumber.open(path) as pdf:
        full_text = _pages_to_text(pdf)

    if not full_text:
        raise ValueError(
            "ไม่สามารถแกะข้อความจาก PDF ได้ อาจเป็นไฟล์ scan/รูปภาพที่ไม่มี text layer "
            "(ในระบบจริงควรเพิ่ม OCR fallback เช่น pytesseract)"
        )

    return full_text


def extract_text_from_bytes(file_bytes: bytes) -> str:
    """
    เวอร์ชันสำหรับรับไฟล์เป็น bytes โดยตรง (ใช้ตอนรับไฟล์ผ่าน FastAPI upload
    ซึ่งไม่ได้ถูกเซฟลง disk ก่อน)
    """
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        full_text = _pages_to_text(pdf)

    if not full_text:
        raise ValueError("ไม่สามารถแกะข้อความจาก PDF ได้ (อาจเป็นไฟล์ scan)")

    return full_text