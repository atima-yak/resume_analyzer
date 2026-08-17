"""
run: uvicorn api:app --reload
test: POST /analyze-resume ที่ http://localhost:8000/docs 
"""

import json
import re
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse

from resume_parser import extract_text_from_bytes, UnsupportedFileTypeError
from llm_analyzer import analyze_resume
import os

BASE_DIR = Path(__file__).resolve().parent

if os.environ.get("VERCEL"):
    RESULTS_DIR = Path("/tmp/results")
else:
    RESULTS_DIR = BASE_DIR / "results"

RESULTS_DIR.mkdir(exist_ok=True)
app = FastAPI(
    title="Resume-JD Matching Analyzer",
    description="วิเคราะห์ Resume (ไทย/อังกฤษ) เทียบกับตำแหน่ง AI & Data Solution",
    version="1.0.0",
)


def _slugify(filename: str) -> str:
    name = Path(filename).stem
    return re.sub(r"[^\w\-]", "_", name)[:50]  # จำกัดความยาวกันชื่อไฟล์ยาวเกินไป


def _save_result(original_filename: str, result: dict) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = _slugify(original_filename)
    saved_filename = f"{timestamp}_{slug}.json"

    output_path = RESULTS_DIR / saved_filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return saved_filename


# หน้าเว็บ UI ที่ root path
@app.get("/")
async def serve_ui():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.post("/analyze-resume")
async def analyze_resume_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="รองรับเฉพาะไฟล์ PDF เท่านั้น",
        )

    try:
        file_bytes = await file.read()
        resume_text = extract_text_from_bytes(file_bytes)

        analysis_result = analyze_resume(resume_text)

        saved_filename = _save_result(file.filename, analysis_result)
        analysis_result["_saved_as"] = saved_filename  

        return JSONResponse(content=analysis_result, status_code=200)

    except UnsupportedFileTypeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการประมวลผล: {str(e)}")


@app.get("/results")
async def list_results():
    summaries = []
    for path in sorted(RESULTS_DIR.glob("*.json"), reverse=True):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            summaries.append({
                "filename": path.name,
                "position": data.get("position"),
                "overall_score": data.get("overall_score"),
                "resume_language": data.get("resume_language"),
            })
        except (json.JSONDecodeError, OSError):
            continue  # ข้ามไฟล์ที่เสียหาย ไม่ให้ endpoint ทั้งตัวพังเพราะไฟล์เดียว

    return {"count": len(summaries), "results": summaries}


@app.get("/results/{filename}")
async def get_result(filename: str):
    safe_name = Path(filename).name
    file_path = RESULTS_DIR / safe_name

    if not file_path.exists() or file_path.suffix != ".json":
        raise HTTPException(status_code=404, detail="ไม่พบไฟล์ผลวิเคราะห์นี้")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return JSONResponse(content=data)


@app.get("/health")
async def health_check():
    return {"status": "ok"}